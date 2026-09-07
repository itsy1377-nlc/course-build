::: intro
This page is the map for getting help. Find your problem, take the first step, then contact the person named beside it.
:::

::: keyfacts
| | |
|---|---|
| Reach your instructor through | The Canvas Inbox or your ACES student email |
| Reply time | 24 to 48 hours, not counting weekends and holidays |
| Lab grades and feedback | Within one week of the due date |
| Out of tokens | Email your instructor. You get more, with no penalty |
| Canvas or computer trouble | The **Help** button in the left menu |
| Help desk numbers and hours | The page **Your computer and the notebook server** |
:::

::: section | When something goes wrong in the notebook
A notebook is a web page where you write and run Python. A cell is one block in a notebook that you run on its own. Your notebook reaches the model with an API key. An API key is a secret string that proves your code may use the model. The course sets it for you.

Four problems have a first step you can take on your own.

| What you see | What to do, and who to tell |
|---|---|
| Your code stops running. A cell hangs, or the notebook stops answering at all. | Restart the notebook, then run every cell from the top. The part that runs your code is called the kernel, and restarting it clears most of these. If the same cell kills it twice, email your instructor and name that cell. |
| The page signs you out, or says your session timed out. | Sign in again and reopen your notebook. Your saved files are still there. Run the cells from the top to rebuild your variables. Nothing is lost. |
| The token counter says your budget is spent. A token is a chunk of text, roughly four characters, and every model call spends some. | Email your instructor and ask for a top-up. Say which week you are on. There is no grade penalty, and no late penalty for the days you wait. |
| A cell reports that the API key is missing, empty or refused. | Open the configuration cell. Your key goes between the two quotation marks on the line that reads `API_KEY = ""`, with no spaces around it. Run that cell again. If it still fails, email your instructor. |
| A cell says too many requests, or waits and tries again. | Nothing is broken. Your key may send 30 requests and 40,000 tokens a minute, and a busy cell can reach that. The notebook waits and retries for you. If it gives up, wait two minutes and run the cell again. No work is lost. |
:::

::: section | Writing to your instructor
Send course questions through the Canvas Inbox or your ACES student email. Those are the two channels your instructor answers. A personal email account or a text message may never arrive. Send a question that way even when you think other students share it.

Name the week, the notebook and the cell. Paste the last line of the error. That one line usually decides the answer, so it saves you a whole reply cycle.

Expect an answer in 24 to 48 hours. Weekends and holidays do not count. Lab scores and written feedback arrive within one week of the due date.
:::

::: section | Campus and Canvas support
Some problems belong to the college rather than to this course. A password reset, a browser that will not load Canvas, or a laptop you need to borrow are all help desk work.

Click **Help** in the left menu for Canvas support. The page **Your computer and the notebook server**, in Student Resources, carries the district and college help desk numbers, the email address and the hours.
:::

::: callout warning | Never post key material
Key material means an API key, or any part of one. No page, cell or screenshot in this course ever shows one. If you think a key has appeared on your screen, email your instructor and post it nowhere.
:::
