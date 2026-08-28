::: intro
Prove your environment works, then read some real Python and predict what it
does. You do not write any code from a blank file.

Everything here runs offline. You do not need an API key for this lab.
:::

::: callout note | What you need before you start
You need three things, all of them from Week 1:

1. Python 3.11 or newer, in a virtual environment.
2. Your lab repository, with `pip install -r requirements.txt` finished.
3. A terminal open in the folder that holds `verify_env.py`.

If any of those is not true, fix it before you start. If you cannot fix it in 30
minutes, post on the Q and A board and start Part 2 anyway.
:::

::: directions
**Part 1: prove the environment works.**

Run this from the folder that holds `verify_env.py`:

```
python verify_env.py
```

Copy the whole output into your answer file. Include the failures, if you have
any. A submission with two failing checks and honest output is worth more than a
submission with nothing pasted.

You are not graded on whether every check passed. You are graded on running it
and showing the result.

**Part 2: five read-and-predict exercises.**

Rules for this part, and they are the point of the exercise:

- Write your prediction **before** you run anything.
- Then run it and paste the real output.
- If your prediction was wrong, say so and write one sentence on why. A wrong
  prediction that you explain earns full credit. Editing your prediction
  afterward earns none.

Create a file named `lab1.py` in the same folder as `verify_env.py`. Put this in
it, exactly as written:

```python
REQUIRED_PACKAGES = ["requests", "flask", "yaml", "jsonschema", "dotenv", "pytest"]
NAMES = ("sysprompt", "customer", "kb")

print("1:", len(REQUIRED_PACKAGES))
print("2:", REQUIRED_PACKAGES[0])
print("3:", REQUIRED_PACKAGES[2])
print("4:", NAMES[1])
print("5:", f"CANARY-{NAMES[2].upper()}-abc123")
```

The first two lines are copied from your lab code. `REQUIRED_PACKAGES` is real,
from `verify_env.py`. `NAMES` is real, from `common/canary.py`. Open both files
and find them.

Now, for each of the five numbered lines, write down:

1. What you predict it prints.
2. One short sentence saying why.

Then run it and paste the output:

```
python lab1.py
```

**Part 3: three questions about a dictionary lookup.**

Create a second file named `lab1_dict.py`, in the same folder. Put this in it,
exactly as written:

```python
from common.canary import all_canaries

tokens = all_canaries()

print("a:", type(tokens))
print("b:", len(tokens))
print("c:", tokens["kb"])
print("d:", sorted(tokens.keys()))
print("e:", tokens.get("password", "no such key"))
```

Run it:

```
python lab1_dict.py
```

Paste the output. Then answer these three questions in your own words. Two or
three sentences each is plenty.

1. Line `c` printed one value. What was the key you asked for, and what was the
   value you got back? Why is that value different from your classmate's?
2. Line `e` asked for a key named `password`, which does not exist. The program
   did not stop. What did it print, and what made it keep going?
3. Line `c` works. If you changed it to `tokens[2]` it would stop with a
   `KeyError`. Explain why a dictionary cannot be looked up by position the way
   a list can.

**What to hand in.** One file, markdown or plain text, with four parts in this
order:

- Your `verify_env.py` output.
- Your five predictions, each with its reason, then the real output.
- Your `lab1_dict.py` output.
- Your three written answers.
:::

::: callout warning | The two easy ways to lose points here
**Skipping the prediction.** Running the code first and then writing "I predicted
that" is the one thing this lab is designed to catch. Predicting badly is fine.
Predicting late is not.

**Pasting nothing.** Several rows below are graded on pasted output. Describing
the output in a sentence is not the same as pasting it.
:::

::: grading
| Criterion | Points |
|---|---|
| `verify_env.py` output pasted in full, failures included | 6 |
| Five predictions written, each with a one-sentence reason | 10 |
| Real output from `lab1.py` pasted, and any wrong prediction explained | 5 |
| Output from `lab1_dict.py` pasted in full | 3 |
| Question 1: names the key and the value, and says why yours is unique | 2 |
| Question 2: names the printed default and explains what prevented the error | 2 |
| Question 3: explains that a dictionary is found by key, not by position | 2 |
| **Total** | **30** |

Your instructor reads the three written answers. The pasted output is checked
against what the lab code produces for your student ID.
:::

::: submit
Upload one file. Markdown or plain text.

Name it `lab1-<your last name>.md` or `lab1-<your last name>.txt`.

Do not upload `lab1.py` or `lab1_dict.py`. Everything the grader needs is pasted
inside your one file.

Helpful resource: [Canvas Student Guide: How to Submit an Assignment](https://community.canvaslms.com/t5/Student-Guide/How-do-I-submit-an-online-assignment/ta-p/503)
:::
