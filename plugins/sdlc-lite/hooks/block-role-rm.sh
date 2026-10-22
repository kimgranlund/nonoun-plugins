#!/usr/bin/env bash
# PreToolUse(Bash): a read-only role (hooks/_role.sh resolves the role: SDLC_ROLE, else the
# sub-agent's agent_type; the set is SDLC_READONLY_ROLES) may remove files only under its throwaway
# prefix, the one its brief names ("remove them, and any scratch output you wrote under that prefix").
# T-0538: the brief told a verifier to clean up there and a host permission prompt refused it, so the
# hook now says the rule in both directions. For rm (also behind sudo, command, env, a path such as
# /bin/rm) and unlink, rmdir:
#   every path operand strictly under the prefix, and the command holds only rm, cd and && ; | joins:
#     allowed explicitly (permissionDecision allow on stdout, exit 0);
#   every path operand under the prefix but the command holds anything else: no decision (exit 0);
#   any path operand outside the prefix, relative after a cd to an unknown place, holding an
#   expansion the hook cannot read (a variable other than $SDLC_TMP_WORKTREES, or that one when it is unset or empty
#   in the hook's environment, since the shell then expands it to an empty string, T-0708), or a .. segment:
#     denied (exit 2).
# The prefix is $SDLC_TMP_WORKTREES when set, else `wtroot.py root --cwd <hook cwd>` plus /tmp, the parent of every
# dispatch tmp prefix (as block-stray-worktree.sh: the sibling <main checkout>.worktrees/tmp, never a lane, T-0563, or
# under a worktree_root: line or a bare clone's <bare parent>/lanes, T-0561), plus the dispatch scratch root
# ${TMPDIR:-/tmp}/sdlc-lite (scripts/wtroot.py). With no prefix every rm is denied.
# The builder, solo, the conductor, any other agent, and a session with no role pass untouched.
# Fails open when python3 is missing or the command cannot be tokenized (an unterminated quote).
# shellcheck source=_role.sh
. "$(dirname "${BASH_SOURCE[0]}")/_role.sh"
input=$(cat)
role=$(sdlc_role "$input")
[[ -n "$role" && "$SDLC_READONLY_ROLES" == *" $role "* ]] || exit 0
[[ "$(jq -r '.tool_name // ""' <<<"$input" 2>/dev/null)" == Bash ]] || exit 0
cmd=$(jq -r '.tool_input.command // ""' <<<"$input" 2>/dev/null)
# Cheap exit: no rm, unlink, or rmdir word even with quotes and backslashes removed.
pf=$(tr -d "\\\\'\"" <<<"$cmd")
re='(^|[^[:alnum:]_-])(rm|unlink|rmdir)([^[:alnum:]_-]|$)'
[[ $pf =~ $re ]] || exit 0

cwd=$(jq -r '.cwd // ""' <<<"$input" 2>/dev/null)
[[ -n $cwd ]] || cwd=$PWD
prefix=${SDLC_TMP_WORKTREES:-}
if [[ -z $prefix && -z "${SDLC_ROLE:-}" ]]; then
  # the worktree root from wtroot.py, as block-stray-worktree.sh (T-0561)
  top=$(python3 "$(dirname "${BASH_SOURCE[0]}")/../scripts/wtroot.py" root --cwd "$cwd" 2>/dev/null) || top=""
  scratch="${TMPDIR:-/tmp}"
  [[ -n $top ]] && prefix="$top/tmp"$'\n'"${scratch%/}/sdlc-lite"
fi

read -r -d '' checker <<'PY' || true
import posixpath, shlex, sys

cmd, prefix, cwd, varset = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] == '1'
prefixes = [p.rstrip('/') for p in prefix.split('\n') if p.strip('/')]
prefix = prefixes[0] if prefixes else ''
try:
    lex = shlex.shlex(cmd, posix=True, punctuation_chars=';&|()')
    lex.whitespace_split = True
    lex.commenters = ''
    toks = list(lex)
except ValueError:
    print('open')
    sys.exit(0)
SEP = {';', '&', '&&', '|', '||', '(', ')'}
WRAP = {'sudo', 'command', 'env', 'nohup', 'exec', 'time', 'nice'}
RM = {'rm', 'unlink', 'rmdir'}
cmds, cur = [], []
for t in toks:
    if t and set(t) <= set(';&|()'):
        if cur:
            cmds.append(cur)
        cur = []
    else:
        cur.append(t)
if cur:
    cmds.append(cur)
reasons, only_rm_cd, cwd_known = [], True, True
for words in cmds:
    while words and (words[0] in WRAP or ('=' in words[0] and not words[0].startswith(('/', '.', '-')))):
        words = words[1:]
    if not words:
        continue
    name = posixpath.basename(words[0])
    if name == 'cd' and len(words) == 2 and words[1].startswith('/') and '$' not in words[1]:
        cwd = posixpath.normpath(words[1])
        continue
    if name == 'cd':
        cwd_known = False
        continue
    if name not in RM:
        only_rm_cd = False
        continue
    paths, end = [], False
    for w in words[1:]:
        if not end and w == '--':
            end = True
        elif end or not w.startswith('-'):
            paths.append(w)
    for p in paths:
        # the shell expands the variable from its own environment: substitute only when it is set here too
        q = p.replace('${SDLC_TMP_WORKTREES}', prefix).replace('$SDLC_TMP_WORKTREES', prefix) if varset else p
        if not varset and '$SDLC_TMP_WORKTREES' in p.replace('${SDLC_TMP_WORKTREES}', '$SDLC_TMP_WORKTREES'):
            reasons.append(f'{p} ($SDLC_TMP_WORKTREES is unset where the shell runs it and expands to an empty string; write the literal prefix from the brief)')
        elif not prefix:
            reasons.append(f'{p} (no throwaway prefix is known)')
        elif '$' in q or q.startswith('~') or '`' in q:
            reasons.append(f'{p} (the hook cannot read the expansion)')
        elif '..' in q.split('/'):
            reasons.append(f'{p} (a .. segment)')
        elif not q.startswith('/') and not cwd_known:
            reasons.append(f'{p} (relative after a cd to a place the hook cannot read)')
        else:
            full = posixpath.normpath(q if q.startswith('/') else posixpath.join(cwd, q))
            if not any((full + '/').startswith(x + '/') and full != x for x in prefixes):
                reasons.append(f'{p} (outside the prefix)')
print('deny ' + '; '.join(reasons) if reasons else ('allow' if only_rm_cd else 'open'))
PY
if ! command -v python3 >/dev/null 2>&1; then exit 0; fi
verdict=$(python3 -c "$checker" "$cmd" "$prefix" "$cwd" "${SDLC_TMP_WORKTREES:+1}" 2>/dev/null) || exit 0
case "$verdict" in
  deny*)
    shown=${prefix//$'\n'/ or the scratch dir }
    echo "Blocked for sdlc role '$role': rm of ${verdict#deny }. A read-only role removes only scratch it wrote under its throwaway prefix (${shown:-unset}); give the full path under it, or \$SDLC_TMP_WORKTREES/<name>, with no variable, ~, or .. in it." >&2
    exit 2
    ;;
  allow)
    printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow","permissionDecisionReason":"rm under the role throwaway prefix"}}'
    exit 0
    ;;
esac
exit 0
