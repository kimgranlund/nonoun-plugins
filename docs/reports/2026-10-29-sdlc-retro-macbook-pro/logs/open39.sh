#!/bin/bash
P=/Users/kimba/.claude/plugins/cache/sdlc-lite/sdlc-lite/0.40.0/scripts
S=/private/tmp/claude-501/-Users-kimba-Projects-ultimate-tokens-color-science/b8497289-311c-4bb2-84f3-2d7d26944ccf/scratchpad
W=/Users/kimba/Projects/ultimate-tokens-color-science.worktrees/fanout
R=/Users/kimba/Projects/ultimate-tokens-color-science
open1(){ lane=$1 t=$2 slug=$3 tier=$4 why=$5
 cd $R; python3 $P/lanes.py open $lane --kind fanout --ticket $t --base $(git rev-parse fanout/2026-10-21) --into fanout/2026-10-21 --path $W/$lane --branch fanout/2026-10-21-$lane --no-claim </dev/null 2>&1 | tail -1
 cd $W/$lane; TD=$W/$lane/docs/tickets/$slug
 python3 $P/steps.py lane $TD 2>&1 | head -1
 echo "- Lane: solo because $why" >> $TD/skips.md
 python3 $P/solo_run.py run --task-dir $TD --tier $tier --brief "Deliver the ticket per the handoff; show each new check red then green." --cwd $W/$lane > $S/solo-$lane.json 2>$S/solo-$lane.err; echo "$lane rc=$?"
}
open1 focusfix T-0264 0264-keyboard-focus-after-actions L2 "size L2, three focus fixes"
open1 cbcontrast T-0265 0265-checkbox-unchecked-contrast L1 "size L1, one CSS fix"
open1 jigrange T-0267 0267-jig-out-of-range-feedback L2 "size L2, input validation"
open1 nexpempty T-0268 0268-native-export-empty-state L2 "size L2, export dialog state"
open1 unkroute T-0269 0269-unknown-theme-route L1 "size L1, one route fix"
