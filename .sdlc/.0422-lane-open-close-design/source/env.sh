# shared by lane-open.sh and lane-close.sh
export PATH=/opt/homebrew/opt/gh/bin:$PATH
ROOT=${LANE_ROOT:-$HOME/Projects/adia/ui-kit}
BARE=$ROOT/.bare
LANES=$ROOT/lanes
ARCHIVE=$ROOT/../ui-kit-archive
REPO=${LANE_REPO:-kimgranlund/gen-ui-kit}
# the repo needs Node 22 (default node here is 24); pin it for bootstrap and gates
export PATH="/Users/kimgranlund/.npm/_npx/52027bd8fc0022aa/node_modules/node/bin:$PATH"
