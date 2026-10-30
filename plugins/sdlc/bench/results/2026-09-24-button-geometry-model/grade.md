hidden_check: pass
exit_code: 0

```
[2m$ tsc -p packages/gen-ui/tsconfig.json --noEmit && tsc -p apps/host/tsconfig.json --noEmit[22m
[2m$ vitest run[22m

[1m[30m[46m RUN [49m[39m[22m [36mv5.0.1 [39m[90m/private/var/folders/0b/jf4lh4jd4sd9y2q7x271c9jm0000gn/T/tmp.cWIyFyPzkS[39m


[2m Test Files [22m [1m[32m11 passed[39m[22m[90m (11)[39m
[2m      Tests [22m [1m[32m37 passed[39m[22m[90m (37)[39m
[2m   Start at [22m 12:18:39
[2m   Duration [22m 2.78s[2m (environment 37%, import 34%, transform 20%, tests 8%, worker 1%)[22m

[2m$ node --import ./scripts/ts-resolve.mjs packages/gen-ui/src/registry/check.ts[22m
gen:check: 4 generated files match their sources
[2m$ node --import ./scripts/ts-resolve.mjs packages/gen-ui/src/geometry/check.ts[22m
gen:geometry:check: geometry.generated.ts matches component-geometry.csv
```
