::: intro
File one containment ticket on the incident pack you were given. Fifteen points,
due day 42. Every claim in the ticket names a file, a line and a field.
:::

::: scope | Authorization and Scope
Your pack is fixed bytes. Nothing in it is live and nothing in it is real, and
this assignment asks you to attack nothing.

Do not try to reach anything named in the pack. No address, host, account or
payment reference in it belongs to anybody. Do not contact them, look them up,
or test them.

The permitted targets have not changed: the practice target this course
supplies, the agent you built, and a model reached through the school gateway
with your own token. Clause 1 of the Rules of Engagement page in Start Here
holds the full list.
:::

::: directions | Directions
1. Open the week 6 notebook and run the setup cell. It prints your pack number
   and the alert that fired.
2. Work through the raw records walkthrough first if you have not already.
3. Read all six files before you write anything. Use the line numbers the pack
   ships with.
4. Build the sequence: every action the records support, in the order they
   support. Cite `file:line:field` for each one. Mark any action the target
   never saw, and any audit row with no trace line behind it.
5. Write one sentence saying what the agent did. Use one of the four labels from
   week 4 where it fits.
6. Make the call: incident or not an incident. Give the one citation that
   decides it. Then write one sentence naming something these records cannot
   settle.
7. Order the revocations from the credential manifest, with a reason for the
   order. Mark the one item that cannot be revoked and say what would be needed
   instead. Fill the blast radius table for your first revocation.
8. Name one place two records disagree and cite both sides. If they agree, say
   so and show the check you ran.
9. Quote the wrong sentence in the handover note, name its drift class, and cite
   the record that contradicts it.
10. Export the form from the notebook and submit it.
:::

::: callout warning | Two mistakes that cost people points
The first is treating the alert as the answer. It tells you what one system
decided. One pack in six fired on a normal action, so check it either way.

The second is citing a line with no field. A trace line can hold three facts,
and a grader cannot tell which one you meant. Where a record is missing, write
`NO SUCH RECORD` and name the file that should have held it.
:::

::: callout tip | Sometimes nothing should be revoked
`NO REVOCATION IS WARRANTED`, given with a reason, is a full answer on the packs
where the records support it. Revoking a key on a benign alert costs somebody a
working day.
:::

::: grading | Grading Criteria
| What earns it | Points |
|---|---|
| The sequence, in order, every step cited to a field | 2 |
| One sentence saying what the agent did, matching that sequence | 2 |
| The call, the citation that decides it, and one limit named | 4 |
| Containment: the order, the item you cannot revoke, the blast radius | 3 |
| Reconciliation: one disagreement cited on both sides, or the check | 2 |
| The handover note: the sentence, its drift class, and the citation | 2 |
| **Total** | **15** |

The call is graded on your citation, not on your answer. A wrong call reached
from correctly cited evidence earns that row in full. A right call with nothing
cited earns none of it.
:::

::: submit | How to Submit
Submit the form the notebook exports, as one file. Put your name and your pack
number at the top. Paste the same ticket into the text box so a grader can read
it without opening the file. Due Sunday 11:59 PM, day 42.
:::
