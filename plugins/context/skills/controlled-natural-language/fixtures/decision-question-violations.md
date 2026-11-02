---
cnl: decision-question
---
# Support triage questions

<!-- Fail case for lint_cnl.py with templates/decision-question.rules.yaml and
     fixtures/decision-question.vocabulary.yaml. Each numbered sentence trips one rule,
     named in its trailing comment. -->

1. Choose billing when the message is not about an outage. <!-- banned-word: negation -->
2. Answer yes when the customer is not unable to sign in. <!-- banned-word: double negation -->
3. Choose outage when the service is down and the status page is red. <!-- banned-word: two propositions -->
4. Answer yes when the invoice is more than 30 days old. <!-- banned-word: date comparison -->
5. Pick whichever team seems right. <!-- no-pattern -->
6. Choose shipping when the message asks about a parcel. <!-- unresolved-slot -->
