hidden_check: fail
exit_code: 1

```

Expected: "FOOTER"
Received: "DIV"

 ❯ packages/agent-ui/components/src/controls/command-modal/command-modal.test.ts:144:28
    142|     const { el, modal } = makePalette([option('a', 'Alpha')])
    143|     const footer = el.querySelector<HTMLElement>('[data-part="footer"]…
    144|     expect(footer.tagName).toBe('FOOTER')
       |                            ^
    145|     expect(footer.closest('ui-modal')).toBe(modal) // rode the same de…
    146|     const hints = footer.querySelectorAll<HTMLElement>('[data-hint]')

⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯[1/1]⎯


 Test Files  1 failed | 1 passed (2)
      Tests  1 failed | 61 passed (62)
   Start at  11:26:55
   Duration  1.95s (transform 324ms, setup 0ms, import 420ms, tests 173ms, environment 2.17s)

```
