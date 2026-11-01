---
cnl: requirement
---
# Sample requirements

<!-- Pass case for lint_cnl.py: templates/rules.yaml with the knowledge-organization-system
     template vocabulary, whose one concept is "example term". -->

1. The example term shall record each failed sign-in attempt.
2. When a sign-in fails three times, the example term shall lock the account for 15 minutes.
3. While the account is locked, the example term shall reject new sign-in attempts.
4. If the audit store is unreachable, then the example term shall queue the record.
5. Where single sign-on is enabled, the example term shall redirect the user to the identity provider.
