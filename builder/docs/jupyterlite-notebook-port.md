# Porting the lab notebooks to JupyterLite

**For:** the course author and whoever owns the lab hosting
**Written:** 2026-09-06
**Status:** a plan, plus one worked example. **No course file was changed.**
The week 1 notebook was downloaded from Canvas, ported in a scratch copy, and
run in a real browser against the live proxy.

---

## 1. What was tested, and what it proved

The week 1 lab (Canvas assignment 50, file 1064) was pulled from
`canvas.bashtion.dev`, edited in a scratch copy, staged on the notebook server,
and executed in headless Chromium against `notebook.bashtion.dev`:

| step | result |
|---|---|
| `await piplite.install("requests")` | requests 2.33.1, resolved locally |
| corpus folder found by the existing path walk | `cwd /drive`, `COURSE_DIR /drive` |
| `parse_eml` imported, email 001 parsed | subject read back correctly |
| real call to `api.bashtion.dev` with a student key | 200, answer `ready`, 24 tokens |
| external hosts contacted | **none** |

The student key used was minted for the test and deleted afterwards.

---

## 2. The change is one cell, in fourteen files

The configuration cell is **byte identical across all seven lab notebooks and
all seven instructor solutions**. Fourteen files, one hash. That is the whole
edit. Nothing else in any notebook has to change.

    instructor/solutions/w1..w7-lab-solution.ipynb
    lab/notebooks/w1..w7-lab.ipynb

`lab/tools/check_chain.py` already polices drift between those copies, so it
will catch a partial edit.

### 2.1 What comes out of the cell

Four environment lookups, because there is no server-side environment in a
browser:

| removed | replaced by |
|---|---|
| `ITSY1377_BASE_URL` | `BASE_URL = "https://api.bashtion.dev/v1"` |
| `ITSY1377_MODEL` | `MODEL = "granite-3b"` |
| `ITSY1377_API_KEY` | a paste field, see 2.2 |
| `ITSY1377_REASONING` | nothing. The proxy sets `reasoning_effort: none` per model |
| `ITSY1377_COURSE_DIR` | nothing. The upward path walk already works |

### 2.2 What goes in

    # =====================================================================
    #  PASTE YOUR KEY BETWEEN THE QUOTES ON THE NEXT LINE, THEN RUN THIS CELL
    # =====================================================================
    API_KEY = ""
    # =====================================================================

and, at the top of the same cell, the one line that makes `requests` exist:

    try:
        import piplite
        await piplite.install("requests")
    except ImportError:
        pass  # a normal Jupyter server already has requests

The `try` matters. It keeps the same notebook runnable on a server-side Jupyter,
which is what `lab/tools/run_notebook.py` uses to prove each lab is completable.
Without it, every gate in the build breaks.

### 2.3 What does NOT change

- `send_request()`. It works unaltered. `requests` reaches
  `api.bashtion.dev` from the kernel's web worker, and CORS is already set.
- The token counter, `record_usage()`, `LAST_CALL`, `show_tokens()`.
- Every TODO cell, and every check cell.
- Every export cell.
- `parse_eml` and `triage_tools`, which import only the standard library.

The infrastructure memo prices in rewriting `send_request()` to `pyodide.http`
across fourteen files. **That is not needed.** It was tested, not assumed.

### 2.4 One two-line addition

`save_artifact()` writes into the browser's virtual drive. The printed
instructions have to say how the file reaches Canvas from there. Two lines:

    print("To hand it in: find it in the file list on the left of this page,")
    print("right-click it, choose Download, then upload it to Canvas.")

Every assignment page already says to attach the file, and that stays true.

---

## 3. What has to ship alongside the notebooks

The path walk finds the corpus because the site root is the working directory.
Laid out under the site's `files/` folder, `/drive` becomes `COURSE_DIR` and
nothing in the cell changes:

    files/w1-lab.ipynb            ... w7-lab.ipynb
    files/corpus/emails/teaching/  25 teaching emails, 172 KB
    files/corpus/data/             display_names.json, known_good_domains.json,
                                   playbook.md
    files/corpus/tools/parse_eml.py
    files/lab/tools/triage_tools.py

Only those two Python modules are needed. `corpus/tools` is 2.7 MB on disk and
almost all of it is generators that students never run.

**Building the site with custom content needs `jupyter-server` installed in the
build environment.** Without it the build stops with "jupyter-server is not
installed. You cannot add custom content to jupyterlite." It is a build time
dependency only; nothing ships to the browser.

**`course.yaml` already carries `never_ship`.** The instructor solutions and the
answer keys must not be staged into `files/`. A folder copy would ship them;
the existing allowlist is the thing that prevents it.

---

## 4. The rule this changes, and it needs recording

The build brief, lines 341 to 345, says the key is injected as an environment
variable and that students "never type, paste, see, or screenshot a key."
A browser has no server-side environment, so this design has the student paste
a key into a cell.

The brief anticipates exactly this: it allows a documented fallback where the
hosting cannot inject per-student environment variables. **This is that
fallback, and this section is the record of it.** What makes it survivable:

- The key is a LiteLLM virtual key, not the DeepInfra key. The provider
  credential never reaches a browser.
- It carries its own budget, rate limit and expiry, so a leaked key costs one
  student's allowance rather than the course's.
- It is scoped to `granite-3b` and `granite-8b` and cannot reach any other
  model, or any admin route.

Two consequences for the course text, both small:

1. Any instruction that says a key is injected, or that a screenshot must never
   show a key, needs rewording. The screenshot rule still holds and matters
   more: the key is now visible in the notebook.
2. The week 1 configuration cell prints "NOT PASTED IN YET" rather than
   "NOT FOUND", so the assignment's troubleshooting step changes with it.

---

## 5. Two things to check before this is student ready

**The reasoning observable reads the wrong field.** Week 2 prints reasoning text
length as its proof that thinking is off. Granite returns thinking in
`reasoning_content`, not `reasoning`. A check that reads `reasoning` prints 0
whether or not reasoning is on, which is a check that cannot fail. This is
independent of JupyterLite and worth fixing wherever it appears.

**Kernel start is slow.** Pyodide boots in tens of seconds before the first cell
runs, on every fresh page load. The week 1 directions say to run the
configuration cell first; they should also say the first run takes a minute and
that this is normal, or students will read it as a hang.

---

## 6. Showing a student what is left of their budget

Yes, this works, and it is now proven from a browser cell. It needs one proxy
route, which is already in place, and one function in the notebooks.

### 6.1 The route

`GET https://api.bashtion.dev/v1/key/info` returns the calling key's own
budget. A plain student key is enough; no admin credential is involved.

It is served under `/v1/` on purpose. The Cloudflare rule blocks everything on
that host outside `/v1/`, and keeping that rule a simple prefix test is worth
more than mirroring LiteLLM's own path layout. The bare `/key/info` stays
blocked: 403 at the edge, 404 at Caddy.

**Upstream lets a caller name someone else's key.** `?key=<another key>`
returns that key's budget, which was tested with two student keys and it
worked. You need the other key in hand, so it widens little, but there is no
reason to carry it. Caddy refuses any request carrying the parameter, with a
400, before authentication is even reached. Five checks in `litellm-verify`
hold that shape.

### 6.2 The cell

    def budget_left():
        """Ask the proxy how much of your allowance is left."""
        reply = requests.get(BASE_URL.rstrip("/") + "/key/info",
                             headers={"Authorization": "Bearer " + API_KEY},
                             timeout=30).json()["info"]
        left = reply["max_budget"] - reply["spend"]
        print(f"Budget: ${reply['max_budget']:.2f}  "
              f"spent ${reply['spend']:.6f}  left ${left:.6f}")
        return left

Measured from a browser cell against the live proxy:

    budget before   ->  max 5.0  spent 0.0        left 5.0
    one model call  ->  in 22  out 137
    budget after    ->  spent 1.674e-05  left 4.999983

That figure is exact, cache discount included: six uncached prompt tokens at
$0.03/M, sixteen cached at 25% of that, and 137 answer tokens at $0.12/M.

### 6.3 The call is free, in both the ways that matter

Measured, because "it should be free" is the kind of assumption that turns out
to be wrong at the worst moment:

    before:  spend=0.0  spend-log rows=0
    12 calls to /v1/key/info against an rpm_limit of 5
      status codes: 200 200 200 200 200 200 200 200 200 200 200 200
    after:   spend=0.0  spend-log rows=0

    one real model call, for contrast:
      spend=0.00000168  spend-log rows=1

**No spend.** The request never reaches DeepInfra. LiteLLM answers from its own
Postgres row, so there are no tokens to charge and no spend-log entry is
written. The contrast line is the control: one model call moves both numbers.

**No rate-limit cost.** Twelve calls against an `rpm_limit` of 5 returned twelve
200s. LiteLLM's limiter applies to the LLM routes, not to management reads.
That is the more important of the two: had budget checks consumed the student's
thirty requests a minute, a `budget_left()` call in the configuration cell would
have quietly taken from the lab's own allowance.

### 6.4 Riding along with the run, and the ten second problem

**Do not call this after every model call.** The reason is not cost, which
section 6.3 rules out. It is that the number is stale: spend takes about ten
seconds to land on the key row, so the call a student just made is not in it. A
cell that printed "left" after each answer would show a figure that lagged by
one call and looked wrong, which is worse than showing nothing.

Use two different sources for two different jobs:

| job | source | cost |
|---|---|---|
| running total during the lab | the `usage` block already in every reply | free, exact, immediate |
| authoritative remaining budget | `/v1/key/info` | one request, about 10s stale |

The notebooks already count tokens in `record_usage()`. Adding cost is two
constants and one line, and it is immediate because it reads the reply the
student just received rather than asking the proxy again.

Call `budget_left()` in the configuration cell and again in the export cell.
Twice a session, not once a call. Because the call is free, three or four times
costs nothing in a week with a heavy loop -- the limit on how often to call it
is accuracy, not price.

### 6.5 What this does not do

The number is informational. Enforcement is server side and unchanged: the key
carries `max_budget`, `rpm_limit` and `tpm_limit`, and the proxy refuses the
call when the budget is gone whether or not the notebook ever asked.
