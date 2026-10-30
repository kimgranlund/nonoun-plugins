# shellcheck shell=bash
# Sourced library: the records-dir rule of scripts/order.py (records_dir) for bash.
# No top-level side effects. Usage:
#   . scripts/records.sh
#   records_dir <dir>        print the records dir for a task or step dir (no create)
#   records_dir_make <dir>   same, and for a runtime result mkdir -p it and write
#                            <base>/runtime/.gitignore ('*') when missing
# Rules, first match wins (<base> is the nearest ancestor named .sdlc, else <A>/.sdlc for the
# nearest ancestor A whose .sdlc/config sets a work_root holding the dir, else the parent: the
# roots.py state_of rule; <key> is the folder name without leading dots):
#   1. a path already inside <base>/runtime/tasks/ is itself;
#   2. a step-<n> dir (or step-<n>.superseded-<k>) is records_dir(parent)/<name>;
#   3. an existing <base>/runtime/tasks/<key>;
#   4. legacy: the dir holds runs.jsonl, a *.attempt.json, a role result, or a step-<n> dir
#      that holds one of those; records stay in place (skips.md is no marker);
#   5. else <base>/runtime/tasks/<key>.
# A relative input is prefixed with $PWD/. Symlinks are not resolved.

_records_base() {
  local q=${1%/*} up
  [[ -n $q ]] || q=/
  while :; do
    if [[ ${q##*/} == .sdlc ]]; then printf '%s\n' "$q"; return 0; fi
    up=${q%/*}
    [[ -n $up ]] || up=/
    if [[ $up == "$q" ]]; then break; fi
    q=$up
  done
  q=${1%/*}
  q=${q:-/}
  # rule 2: the nearest ancestor A (q itself included) whose A/.sdlc/config sets a work_root W holding q
  local a=$q w
  while :; do
    w=$(_records_work_root "${a%/}/.sdlc/config")
    if [[ -n $w ]]; then
      case $q in
        "${a%/}/$w"|"${a%/}/$w"/*) printf '%s\n' "${a%/}/.sdlc"; return 0 ;;
      esac
    fi
    [[ $a == / ]] && break
    a=${a%/*}
    a=${a:-/}
  done
  printf '%s\n' "$q"
}

# The work_root value of a config file (roots.py rules), normalized with no ./ or trailing /; nothing when the file
# is absent or sets no work_root, or the value is one roots.py refuses (empty, ., absolute, .., under .sdlc, two
# different values, beside ticket_root).
_records_work_root() {
  local cfg=$1 vals v
  [[ -f $cfg ]] || return 0
  vals=$(sed -n -E 's/^[[:space:]]*work_root[[:space:]]*:[[:space:]]*([^#]*[^#[:space:]])?[[:space:]]*(#.*)?$/=\1/p' "$cfg" | sort -u)
  [[ -n $vals && $vals != *$'\n'* ]] || return 0
  grep -Eq '^[[:space:]]*ticket_root[[:space:]]*:' "$cfg" && return 0
  v=${vals#=}
  while [[ $v == ./* ]]; do v=${v#./}; done
  while [[ $v == */ ]]; do v=${v%/}; done
  case $v in
    ''|.|/*|..|../*|*/..|*/../*|.sdlc|.sdlc/*) return 0 ;;
  esac
  printf '%s\n' "$v"
}

# find in a here-doc, not a glob (a glob with no match aborts under zsh) and not <(...)
# (refused by sh): this file may be sourced from bash, sh or zsh.
_records_holds() {
  local d=$1 n
  [[ -e $d/runs.jsonl ]] && return 0
  while IFS= read -r n; do
    n=${n##*/}
    [[ $n == *.attempt.json ]] && return 0
    [[ $n =~ ^[a-z][a-z-]*-L[0-9]+.*\.md$ ]] && return 0
  done <<EOF
$(find "$d" -mindepth 1 -maxdepth 1 -type f 2>/dev/null)
EOF
  return 1
}

_records_legacy() {
  local d=$1 s
  _records_holds "$d" && return 0
  while IFS= read -r s; do
    [[ ${s##*/} =~ ^step-[0-9]+(\.superseded-[0-9]+)?$ ]] || continue
    _records_holds "$s" && return 0
  done <<EOF
$(find "$d" -mindepth 1 -maxdepth 1 -type d -name 'step-*' 2>/dev/null)
EOF
  return 1
}

# Sets _records_path and _records_runtime_base (empty for a legacy, in-place result).
_records_resolve() {
  local p=$1 name base tasks key
  name=${p##*/}
  base=$(_records_base "$p")
  tasks=$base/runtime/tasks
  case $p in
    "$tasks"/*) _records_path=$p; _records_runtime_base=$base; return 0 ;;
  esac
  if [[ $name =~ ^step-[0-9]+(\.superseded-[0-9]+)?$ ]]; then
    _records_resolve "${p%/*}"
    _records_path=$_records_path/$name
    return 0
  fi
  key=$name
  while [[ $key == .* ]]; do key=${key#.}; done
  if [[ -d $tasks/$key ]]; then
    _records_path=$tasks/$key; _records_runtime_base=$base; return 0
  fi
  if _records_legacy "$p"; then
    _records_path=$p; _records_runtime_base=; return 0
  fi
  _records_path=$tasks/$key; _records_runtime_base=$base
}

_records_abs() {
  local p=$1
  [[ $p == /* ]] || p=$PWD/$p
  while [[ $p == */ && $p != / ]]; do p=${p%/}; done
  printf '%s\n' "$p"
}

records_dir() {
  [[ $# -eq 1 && -n $1 ]] || { echo "usage: records_dir <dir>" >&2; return 2; }
  _records_resolve "$(_records_abs "$1")"
  printf '%s\n' "$_records_path"
}

records_dir_make() {
  [[ $# -eq 1 && -n $1 ]] || { echo "usage: records_dir_make <dir>" >&2; return 2; }
  _records_resolve "$(_records_abs "$1")"
  if [[ -n $_records_runtime_base ]]; then
    mkdir -p "$_records_path" || return 1
    [[ -e $_records_runtime_base/runtime/.gitignore ]] \
      || printf '*\n' > "$_records_runtime_base/runtime/.gitignore" || return 1
  fi
  printf '%s\n' "$_records_path"
}
