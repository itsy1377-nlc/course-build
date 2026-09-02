# The tests are the assignment

A text version of the walkthrough video. Every word spoken, in order.

## The tests are the assignment

> This video never opens the file you are writing.
> It shows the tool that decides.

Module 1 asks you for three small functions in one file. This video never opens that file. Your answer stays yours. What it shows you is the tool that decides whether the three are right. You can run that tool as often as you like before the deadline.

## Three functions, and no network

1. should_retry, is this request worth sending again
2. backoff_seconds, how long to wait first
3. parse_json_content, read the reply or fail clearly

The three sit under one banner, extension point 3 of 5. should retry asks one question. Is this request worth sending again? backoff seconds says how long to wait before you try. parse json content reads a reply, or says clearly why it could not. None of the three needs a network or a key. They are pure logic. So the whole assignment runs offline, on your own machine.

## At the terminal

Commands run, in order:

- `python -m pytest tests/test_module1.py -q | tail -3`

Run the tests before you write anything, so you know what failing looks like. The output goes through tail, so you see the summary and no assertion detail. Eleven failed, six passed. Say that count out loud. That is a starting line, not a problem.

## The test file is the assignment.

> Every failing name points at a rule
> the docstring already gave you.

Then open the test file itself and read it. Every failing name points at a rule the docstring already gave you. It is the clearest statement of what your three functions have to do. Reading it is part of the job, not a way around the job.

## At the terminal

Commands run, in order:

- `python -m pytest tests/test_module1.py -q`

Here is the same command against finished work, with the whole output this time. Seventeen passed, in well under a second. No request went anywhere. That is what pure logic looks like. There is no key to burn here and no rate limit to wait on. So run it after every small change you make.

## At the terminal

Commands run, in order:

- `python -m pytest tests/test_module1.py -q > module1-pytest.txt`
- `cat module1-pytest.txt`

Now save your proof. Send the same output into a file. Nothing printed, because the output went into the file instead. So open the file and read it back. Seventeen passed, and the file is not empty. An empty proof file is a submission with no proof in it. Check that before you upload, not after.

## The mistake that costs real money

1. **Retry every client error.** A 401 means your key is not accepted. Your loop retries, and your daily limit is gone in about four seconds.
2. **Retry only what waiting fixes.** 429 and 503 clear on their own. A 401 never will, so sending it again cannot help.

One warning before you start. Say you write should retry so it says yes to every client error, and nothing crashes. Then a 401 arrives. Your key is not accepted, and your loop keeps trying. Your provider's daily limit is gone in about four seconds, on a request that could never succeed. Then you are locked out until tomorrow, and the work is due tonight. That is why the rule is narrow. Retry only what waiting can fix.

## Upload two files.

> Your edited model client, and your saved pytest output.
> Never the whole repository, and never your key file.

Upload two files. Your edited model client, and your saved pytest output. Not the whole repository, and never the file that holds your key. If you get stuck, paste the test name and the message on the Q and A board. Paste the failure, not your answer. Being stuck costs nobody points. Being quiet about it costs time.
