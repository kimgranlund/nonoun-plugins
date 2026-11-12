---
cnl: decision-question
---
# Support triage questions

<!-- Pass case for lint_cnl.py: templates/decision-question.rules.yaml with
     fixtures/decision-question.vocabulary.yaml. One choice, one score, one proposition. -->

## Team

Choose the one option that best describes the customer message.

- Choose billing when the message asks about a charge on an invoice.
- Choose outage when the message reports a service that is down.
- Choose account access when the message reports a failed sign-in.
- If the message reports a failed sign-in during an outage, the answer is outage.
- If the message asks for a refund, the answer is billing.

## Urgency

Choose the one level that best describes the urgency of the message.

1. Level 1 means the customer asks a question.
2. Level 2 means the customer reports a blocked task.
3. Level 3 means the customer reports a blocked team.

If the message reports one blocked task for a whole team, the answer is level 3.

## Legal escalation

Answer yes when the message names a legal deadline. If the message names a court date, the answer is yes.
