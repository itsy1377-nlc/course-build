#!/usr/bin/env bash
#
# Bring up a local Canvas LMS and create the ITSY 1377 course shell.
#
# This was built and verified on macOS 15 / Apple Silicon (arm64) with colima.
# It should work on Linux unchanged. Every step here was actually run; the
# comments record what went wrong so you do not repeat it.
#
# Usage:
#   ./canvas/deploy/setup.sh            # full setup from scratch
#   ./canvas/deploy/setup.sh --start    # just start an existing deployment
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CANVAS_DIR="$REPO_ROOT/canvas/canvas-lms"
CANVAS_REF="${CANVAS_REF:-master}"

ADMIN_EMAIL="${CANVAS_ADMIN_EMAIL:-admin@itsy1377.local}"
ADMIN_PASSWORD="${CANVAS_ADMIN_PASSWORD:-Itsy1377demo!}"
ACCOUNT_NAME="${CANVAS_ACCOUNT_NAME:-Northeast Lakeview College (ITSY 1377 Demo)}"
CANVAS_URL="http://localhost:3000"

say() { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
die() { printf '\n\033[1;31mERROR: %s\033[0m\n' "$*" >&2; exit 1; }

# ---------------------------------------------------------------------------
# 0. Preflight
# ---------------------------------------------------------------------------
say "Checking Docker"
docker info >/dev/null 2>&1 || die "Docker is not running.
If you use colima:  colima start
Canvas's own docs ask for at least 8GB allocated to Docker."

AVAIL_GB=$(docker run --rm alpine df -BG / 2>/dev/null | awk 'NR==2{gsub(/G/,"",$4); print $4}')
if [ -n "${AVAIL_GB:-}" ] && [ "$AVAIL_GB" -lt 25 ]; then
  echo "WARNING: only ${AVAIL_GB}GB free inside the Docker VM. Canvas needs roughly 25GB."
fi

if [ "${1:-}" = "--start" ]; then
  say "Starting existing deployment"
  cd "$CANVAS_DIR" && docker compose up -d
  echo "Canvas: $CANVAS_URL"
  exit 0
fi

# ---------------------------------------------------------------------------
# 1. Clone Canvas from the official repository
# ---------------------------------------------------------------------------
if [ ! -d "$CANVAS_DIR/.git" ]; then
  say "Cloning instructure/canvas-lms (shallow; we do not need history)"
  mkdir -p "$REPO_ROOT/canvas"
  git clone --depth 1 --single-branch --branch "$CANVAS_REF" \
    https://github.com/instructure/canvas-lms.git "$CANVAS_DIR"
else
  say "Canvas already cloned, skipping"
fi
cd "$CANVAS_DIR"

# ---------------------------------------------------------------------------
# 2. Configuration
#
# We deliberately DO NOT run ./script/docker_dev_setup.sh. On macOS that script
# installs the dinghy-http-proxy system-wide without asking, which is reported
# to break unrelated Docker setups (canvas-lms issue #2411). We do the same
# work by hand and publish a port instead of using a proxy.
# ---------------------------------------------------------------------------
say "Writing configuration"
cp -n docker-compose/config/*.yml config/ 2>/dev/null || true

if [ ! -f .env ]; then
  cat > .env <<'ENVEOF'
COMPOSE_FILE=docker-compose.yml:docker-compose.override.yml
ENVEOF
fi

# The override ships with this repo, so the port fix and the removal of the
# dinghy hooks travel with it. Copy it in if it is not already there.
if [ ! -f docker-compose.override.yml ]; then
  cp "$REPO_ROOT/canvas/deploy/docker-compose.override.yml" docker-compose.override.yml
fi

# Canvas builds absolute URLs from config/domain.yml for anything it serves
# through a redirect, and every file download is served that way. Upstream
# ships "canvas.docker", the hostname the dinghy proxy resolves, and we do not
# install that proxy. Left alone, an embedded <video> in a course page resolves
# to a hostname no browser can look up, and the player fails silently.
#
# It also has to be the address a BROWSER uses rather than localhost, because
# the demo is normally viewed from another machine on the network. Canvas only
# redirects when the request host differs from this value, so matching it to
# the LAN address means files are served inline with no redirect at all.
LAN_IP="$(ipconfig getifaddr en0 2>/dev/null || hostname -I 2>/dev/null | awk '{print $1}')"
BROWSE_HOST="${CANVAS_BROWSE_HOST:-${LAN_IP:-localhost}:3000}"
say "Setting the files domain to $BROWSE_HOST"
cat > config/domain.yml <<DOMAINEOF
production:
  domain: "canvas.docker"

test:
  domain: localhost

development:
  domain: "$BROWSE_HOST"
DOMAINEOF

docker compose config --quiet || die "docker compose config is invalid"

# ---------------------------------------------------------------------------
# 3. Build
# ---------------------------------------------------------------------------
say "Building the Canvas image (this is the slow step)"
docker compose build --pull web

ARCH=$(docker image inspect canvas-lms-web:latest --format '{{.Architecture}}')
echo "Built for: $ARCH"
[ "$ARCH" = "arm64" ] && echo "Native arm64. The base image instructure/ruby-passenger publishes an arm64 manifest, so nothing is emulated."

# ---------------------------------------------------------------------------
# 4. Gems
#
# The image ships bundler but gems live in a named volume, so bundle install
# has to run once. Skipping this gives a confusing error about a git source
# ("crystalball is not yet checked out") that looks like a repo problem but
# is really just "gems are not installed yet".
# ---------------------------------------------------------------------------
say "Installing gems"
docker compose run --rm --no-deps web bundle install

# ---------------------------------------------------------------------------
# 5. Database and admin user
#
# db:initial_setup prompts for an admin email and password interactively unless
# these environment variables are set. They are read by lib/tasks/db_load_data.rake.
# ---------------------------------------------------------------------------
say "Creating and seeding the database"
docker compose run --rm \
  -e CANVAS_LMS_ADMIN_EMAIL="$ADMIN_EMAIL" \
  -e CANVAS_LMS_ADMIN_PASSWORD="$ADMIN_PASSWORD" \
  -e CANVAS_LMS_ACCOUNT_NAME="$ACCOUNT_NAME" \
  -e CANVAS_LMS_STATS_COLLECTION=opt_out \
  web bundle exec rake db:create db:initial_setup

# ---------------------------------------------------------------------------
# 6. Assets
# ---------------------------------------------------------------------------
say "Compiling assets"
docker compose run --rm web ./script/install_assets.sh

# ---------------------------------------------------------------------------
# 7. Start
# ---------------------------------------------------------------------------
say "Starting Canvas"
docker compose up -d

printf 'Waiting for Canvas to answer'
for _ in $(seq 1 60); do
  code=$(curl -s -o /dev/null -w '%{http_code}' -m 5 "$CANVAS_URL/login" || echo 000)
  if [ "$code" != "000" ] && [ "$code" != "502" ] && [ "$code" != "503" ]; then
    printf ' got HTTP %s\n' "$code"; break
  fi
  printf '.'; sleep 5
done
[ "${code:-000}" = "000" ] && die "Canvas never answered. Check: docker compose logs web --tail 50"

# ---------------------------------------------------------------------------
# 8. API token
#
# The Access Tokens API cannot bootstrap the first token: tokens created for
# another user land in a 'pending' state that cannot be used, and there is no
# password grant. So the first token is minted from a Rails console.
# ---------------------------------------------------------------------------
say "Minting an API token"
TOKEN=$(docker compose run --rm web bundle exec rails runner '
u = Pseudonym.find_by(unique_id: ENV.fetch("ADMIN_EMAIL")).user
t = u.access_tokens.create!(purpose: "ITSY 1377 course population", workflow_state: "active")
puts "TOKEN=#{t.full_token}"' -- 2>/dev/null | grep '^TOKEN=' | cut -d= -f2 | tr -d '\r')

[ -z "$TOKEN" ] && die "Could not mint an API token"
# The admin password goes in here as well as the token, because installing the
# theme genuinely needs it. Canvas honours a bearer token only on /api/ routes
# and the theme routes are not under /api/, so an API token cannot install
# account CSS at all. This is a local demo credential and it is printed below
# anyway; the file is mode 600 and gitignored.
{
  printf 'CANVAS_URL=%s\n' "$CANVAS_URL"
  # The address a browser uses. Canvas stamps the host from the incoming
  # request into every file link it rewrites on save, so the tools write
  # through this rather than through localhost. Without it, a course saved
  # from this machine hands out links to the viewer's own computer.
  printf 'CANVAS_PUBLIC_URL=http://%s\n' "$BROWSE_HOST"
  printf 'CANVAS_TOKEN=%s\n' "$TOKEN"
  printf 'CANVAS_ADMIN_EMAIL=%s\n' "$ADMIN_EMAIL"
  printf 'CANVAS_ADMIN_PASSWORD=%s\n' "$ADMIN_PASSWORD"
} > "$REPO_ROOT/canvas/.canvas-credentials"
chmod 600 "$REPO_ROOT/canvas/.canvas-credentials"

# ---------------------------------------------------------------------------
# 9. Done
# ---------------------------------------------------------------------------
cat <<DONE

============================================================
Canvas is running.

  URL:      $CANVAS_URL
  Login:    $ADMIN_EMAIL
  Password: $ADMIN_PASSWORD

An API token was written to canvas/.canvas-credentials (mode 600).

Next:
  python -m tools.import_cartridge     build and import the course, then verify it
  python canvas/theme/apply_theme.py   make it look like a designed course
  docker compose -f $CANVAS_DIR/docker-compose.yml logs -f web

To stop:   cd $CANVAS_DIR && docker compose stop
To start:  ./canvas/deploy/setup.sh --start
============================================================
DONE
