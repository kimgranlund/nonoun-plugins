---
cnl: requirement
---
# Checkout requirements

<!-- Fail case for lint_cnl.py with fixtures/rules.yaml and fixtures/vocabulary.yaml.
     Each numbered sentence trips exactly one rule, named in its trailing comment.
     fixtures/rules.yaml supplies the schema, unknown-concept and no-source findings. -->

1. The cart service shall store each order. <!-- hidden-label -->
2. Orders are kept for audit. <!-- no-pattern -->
3. The billing engine shall issue a receipt. <!-- unresolved-slot -->
4. The checkout service shall retry the payment as appropriate. <!-- banned-word -->
5. The checkout shall email a receipt. <!-- alt-label -->
6. The checkout service must log each refund. <!-- deprecated-pattern -->
