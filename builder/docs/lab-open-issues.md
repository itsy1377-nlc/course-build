# Open issues on the lab infrastructure

**For:** the operator
**Opened:** 2026-09-06, after building the `litellm` and `jupyterlite` guests
**Status:** all five are now closed. Each entry records what was wrong, what
changed, and the evidence -- run against the service rather than read off a
config file. Two residual items belong to the operator and are marked in place.

The build itself is done and verified. These are the items I could not close
myself, either because they live in a Cloudflare or Tailscale console, or
because they are a decision rather than a change.

---

## 1. Admin plane exposure — CLOSED at the guest, one residual item

**Was:** `tailscale serve` published the full LiteLLM app to the whole tailnet.
That is 26 nodes, not the eleven guests I first wrote. It includes other
people's laptops and phones -- `aidenmac`, `aiden-pc`, `carols-imac`,
`parkerphone` -- plus a TV, a homebridge box, and three AI agents. The node's
own packet filter confirmed it: the permitted sources span the entire
`100.64.0.0/10` range.

**Now:** `tailscale serve` points at a Caddy listener on `127.0.0.1:8081` that
requires the caller's tailnet identity to be `aaronfleming@icloud.com`, and
403s everything else. LiteLLM is never reached directly.

This is identity based rather than address based, which matters because it
follows the person across devices and does not need a list of addresses kept in
step with reality.

**Why the header can be trusted:** tailscaled overwrites any `Tailscale-User-*`
header the caller supplies. Sending a forged
`Tailscale-User-Login: attacker@evil.example` came back as the real
`aaronfleming@icloud.com`. Tested, not assumed.

**Proof the gate denies:** the allowed identity was temporarily changed to
`nobody@example.invalid`, and our own request was refused with 403 and the
gate's own message. Changing it back returned 200. A matcher that is never
seen to refuse anything is not a control.

Tagged nodes carry no user identity, so the three AI agents should fail this
check on an empty header rather than needing to be named. That follows from
how Tailscale tags work; it was not tested, because testing it means touching
a guest that is not mine.

**Residual, and it belongs to you.** The two guests are NOT in the same state,
and litellm's registration changed during the build:

| guest | tags | node key expiry |
|---|---|---|
| `litellm` | `tag:nlc-labs` | none -- does not expire |
| `jupyterlite` | none | 2027-03-05 |

Earlier in the same session litellm also reported no tags. Its
`tailscaled.state` was rewritten at 22:53 and it now carries `tag:nlc-labs`
with no expiry, which is the state you want. jupyterlite was not changed and
is still untagged with an expiry.

**If the auth key was ephemeral, expiry is not the thing to worry about.** An
ephemeral node is deleted from the tailnet once it has been offline for around
thirty minutes -- a maintenance window, a long shutdown, a host that does not
come straight back. It is not a 2027 problem, it is a next-outage problem. The
node would then need a fresh auth key to rejoin, and its MagicDNS name stops
resolving in the meantime.

That did not bite during this build because both guests rebooted and returned
inside the window.

**A node cannot tell you whether it is ephemeral.** The `Ephemeral` field is
absent from `tailscale status --json` and from the netmap on both guests, so
this is not something I can settle from the box. The admin console's machine
list is authoritative and labels ephemeral nodes directly.

**What to do:** confirm both in the console, and bring jupyterlite to the same
state litellm is now in -- tagged, non-ephemeral, no expiry. litellm is the one
that matters most, because losing its node takes the admin plane with it.
Neither public tunnel depends on the tailnet, so students would be unaffected
either way.

A tailnet ACL is no longer urgent given the gate above, and would mean editing
a default-allow policy that 26 devices currently depend on. That is a
fleet-wide change and not one to make casually.

## 2. Patching — CLOSED

Patching only happens regularly when it is cheap and safe. Three pieces now
make it both.

**`litellm-verify`** asserts the posture against the running service, never
against a config file. 34 checks: which processes listen off loopback, twelve
admin routes returning 404 at the public URL, 401 unauthenticated and 200 with
a scoped key, the advertised model list, three unlisted models refused, five
request-body injections refused, and reasoning genuinely off read back from
`reasoning_content`. Exit 0 or 1.

It was proved to fail, not just to pass. Adding `/ui*` and `/key/*` to the
Caddy allowlist -- the exact regression the allowlist exists to prevent --
produced seven failures and exit 1, including `/ui/` answering **200 on the
public internet**. Restoring the file returned 34 passed, exit 0.

**`litellm-upgrade`** writes a lock file, upgrades, pushes any new prisma
schema, restarts, and runs `litellm-verify`. If verification fails it
reinstalls the previous package set, restarts, and re-verifies. Tested for real
by downgrading to 1.99.0 and letting the tool bring it forward: it upgraded to
1.100.0, verified 34 of 34, and updated the lock.

**`litellm-verify.timer`** runs the check every Monday morning, so drift
between upgrades is caught too -- a hand edit, a dependency change, a setting
that stopped taking effect.

Currently on litellm 1.100.0, which is the newest release. 111 packages pinned
in `/opt/litellm/requirements.lock`.

**How to patch from here:** `sudo /usr/local/sbin/litellm-upgrade`. If it exits
non-zero it has already rolled itself back; read the failing lines before
trying again.

## 3. Pre-auth load — CLOSED

**What was true:** every per-key limit applies only after the key is checked, so
an unauthenticated flood still reached LiteLLM. Measured: 200 junk requests
consumed **1.015 seconds of LiteLLM CPU**, about 5ms of Python each. That is a
cheap way to saturate a 2 vCPU guest.

**Done on the box.** Caddy now answers requests with no Authorization header
itself, in Go, instead of proxying them:

| | requests/sec | LiteLLM CPU per 200 requests |
|---|---|---|
| before | 98 | 1.015s |
| after | 221 | 0.003s |

That is 338x less work for the same flood. It is **not** a rate limit -- it
removes the cost of the commonest junk request. Nothing is rate limited yet.

**The trap in it.** A CORS preflight is an `OPTIONS` request with no
Authorization header, sent by the browser before the real call. 401ing those
would break every JupyterLite notebook while every other check still passed.
`OPTIONS` is exempt, and `litellm-verify` now asserts the preflight returns 200
with `access-control-allow-origin` -- so a later edit cannot quietly remove the
exemption. 36 checks now.

**The rate limiting rule could not do this, and the free plan is why.** Free
tier rate limiting rules expose exactly two fields in the expression: Path and
Verified Bot. No host, no request headers. So the rule cannot tell an
authenticated student from an unauthenticated flood, and path alone would take
down a NATed computer lab where thirty students share one address. The single
free rule stays where it was, on the large WASM assets, which have a real
metered bandwidth cost.

**A WAF custom rule did it instead**, and custom rules are not restricted that
way -- they get the full expression language, and the free plan allows five:

    http.host eq "api.bashtion.dev"
    and not starts_with(http.request.uri.path, "/v1/")

Deployed and confirmed from outside. `/ui`, `/key/generate`, `/user/new`,
`/metrics`, `/health` and `/` all return 403 from Cloudflare now, so admin path
probing never reaches the tunnel. `/v1/models` still 401s, the CORS preflight
still returns 200, and notebook.bashtion.dev is untouched.

**The edge rule then masked the box, and the verifier had to change.** With
Cloudflare answering 403 first, a Caddy allowlist regression would be invisible
from the public URL -- right up until someone deleted the WAF rule and
published the admin dashboard. `litellm-verify` now checks the two layers
separately: the public URL must be blocked somehow (403 or 404), and Caddy on
loopback must return 404 on its own merits. 50 checks now.

## 4. Secret rotation — CLOSED

`/usr/local/sbin/litellm-rotate-secrets` regenerates `LITELLM_MASTER_KEY` and
`UI_PASSWORD` on the box, restarts, and runs `litellm-verify`. With `--db` it
rotates the Postgres password too, updating `DATABASE_URL` in the same pass.
Nothing is printed; the new values go straight into `/etc/litellm/proxy.env`,
which stays `600 root:root`.

A failed rotation restores itself. The previous env file is kept until the new
one verifies, and the database password is put back with it.

Both paths were run for real, not just written:

| checked by behaviour | result |
|---|---|
| old master key on `/key/generate` | 401 -- revoked |
| new master key on `/key/generate` | 200 |
| `UI_PASSWORD` changed | yes, and still differs from the master key |
| Postgres login with the new `DATABASE_URL` | ok |
| `litellm-verify` after each rotation | 50 passed, 0 failed |
| leftover `.prev` backups | 0 |

**A correction. I said twice that rotating the master key invalidates every
student key and the class would need re-minting. That is wrong.** A key minted
before the rotation still authenticated afterwards and still completed a
request. Virtual keys are stored hashed in the database and do not depend on
the master key, and `STORE_MODEL_IN_DB` is off so there are no master-key
encrypted credentials in there either. Rotation is cheap: no class-wide
re-issue, no lab disruption.

**Still outstanding, and only you can do it:** the Tailscale auth key pasted
into the build transcript has not been revoked. It was live at the last check.
The guests no longer depend on it -- litellm re-registered under `tag:nlc-labs`
and jupyterlite is off the tailnet entirely -- so revoking it now costs
nothing.

## 5. Client-supplied `api_key` — CLOSED

**Confirmed from the installed source, not inferred.** LiteLLM 1.100.0 bans 144
request-body parameters and `api_key` is not one of them. The thirteen key-ish
entries in that list are all observability providers -- langfuse, arize,
braintrust, langsmith -- not the model credential. So a caller could supply
their own provider key and LiteLLM would use it.

**There is no config setting to fix this.** Both documented knobs,
`allow_client_side_credentials` and `configurable_clientside_auth_params`, only
loosen the list. Nothing extends it.

`CustomLogger.async_pre_call_hook` receives the request body and is the
supported way to tighten it. `/opt/litellm/ban_client_api_key.py` rejects
`api_key` at the top level and inside `extra_body`, matching the shape of
LiteLLM's own recursive check so the obvious way around it is closed too.

Behaviour now:

    normal request           -> ready
    api_key in body          -> Rejected Request: api_key is not allowed ...
    extra_body.api_key       -> Rejected Request: extra_body.api_key is not allowed ...
    api_base (LiteLLM's own) -> still refused

**The hook is a maintenance surface, so it is asserted.** A LiteLLM upgrade
that changes the `CustomLogger` interface would drop it silently. Both probes
are now in `litellm-verify`, which runs on every upgrade and every Monday, and
`litellm-upgrade` rolls back automatically if they fail. 52 checks.

This was never a security hole -- the model allowlist and the Caddy allowlist
both held regardless. It was an accounting hole: those requests never appeared
against a key's budget or in the spend logs, so the per-student cost figure
would have understated real usage.

---

## Deferred decisions

Recorded, not acted on. Neither blocks anything.

### D1. Per-key budget is far larger than the measured cost

The key minting recipe sets `max_budget: 5.0` per student, chosen when per-token
cost was unknown and the blueprint could only express it as a break-even.

Now measured, and LiteLLM agrees with DeepInfra to the digit:

| | |
|---|---|
| full pass through all seven labs | about 388,000 tokens |
| cost, worst case (all output, 8B) | $0.097 |
| cost, likely case (3B) | $0.01 to $0.05 |
| what $5 buys | about 52 complete passes |

**Decided 2026-09-07: $2.00 per student.** That is about twenty complete
passes through all seven labs at the measured cost, which leaves room for a
student who reruns a lab repeatedly while still capping a runaway loop two and
a half times sooner than $5 did.

Mint with `max_budget: 2.0`. Nothing else changes: the proxy wide
`max_budget: 200` over 30 days stays as the backstop, and `rpm_limit: 30` with
`tpm_limit: 40000` still bounds how fast any one key can burn.

**Not yet applied to any minted key.** The recipe lives on the box, not in this
repository, so the number takes effect at the next minting. Any key already
issued at $5.00 keeps that ceiling until it is reissued.

### D2. The auto-captured User-Agent in spend logs

LiteLLM writes a `User-Agent: ...` tag into `request_tags` on every request,
alongside any tag the notebook sets. From a browser that is the student's own
browser and operating system version, retained indefinitely next to their
coursework.

It is not sensitive and nothing depends on it. It is also device fingerprinting
data that was never asked for. Worth deciding deliberately rather than
inheriting; there is no urgency.
