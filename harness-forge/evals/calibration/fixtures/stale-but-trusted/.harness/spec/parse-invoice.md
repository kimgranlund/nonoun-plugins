# spec.task.parse-invoice — v3 (REVISED 2026-06-12)

Turn a PDF invoice into a typed record.

## Acceptance criteria (checkable predicates)

1. `parse(pdf) -> Invoice` returns a typed record for every fixture in `fixtures/invoices/`.
2. `Invoice.total == sum(line.amount for line in Invoice.lines)` for every parsed fixture.
3. **NEW in v3:** multi-currency invoices parse with `Invoice.currency` set from the document, never defaulted.
4. **NEW in v3:** a malformed PDF raises `InvoiceParseError`, never returns a partial record.
5. Round-trip: `Invoice.to_json` → `Invoice.from_json` is identity on all fixtures.
