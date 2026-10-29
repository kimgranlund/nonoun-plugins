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
open1 catshards T-0254 0254-catalog-entry-shards L2 "size L2, generator change"
