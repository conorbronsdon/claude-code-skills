#!/usr/bin/env bash
# install.sh — manage skills from this collection in a target project.
#
#   ./install.sh install  <skill> <target-project-dir>
#   ./install.sh update   <skill> <target-project-dir>   # same as install, but requires existing copy
#   ./install.sh diff     <skill> <target-project-dir>   # show drift between collection and installed copy
#   ./install.sh uninstall <skill> <target-project-dir>
#   ./install.sh list
#   ./install.sh agents                                  # list supported agents
#
# Run from a clone of this repo. Copies the whole skill directory (SKILL.md +
# patterns/ + examples/) into the skills directory your agent reads. No network,
# no dependencies beyond bash + coreutils.
#
#   AGENT=claude    (default)  <target>/.claude/skills   ~/.claude/skills
#   AGENT=codex                <target>/.agents/skills   ~/.codex/skills
#   AGENT=cursor               <target>/.cursor/skills   ~/.cursor/skills
#   AGENT=opencode             <target>/.opencode/skills ~/.opencode/skills
#   AGENT=generic              <target>/.agents/skills   ~/.agents/skills
#
# Pass TARGET_SCOPE=user to install into the home directory instead of a project.

set -euo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
SKILLS=$(cd "$HERE" && for d in */SKILL.md; do dirname "$d"; done)

usage() { sed -n '2,21p' "$0" | sed 's/^# \{0,1\}//'; exit 2; }

cmd=${1:-}; skill=${2:-}; target=${3:-}

AGENT=${AGENT:-claude}

# Each agent reads skills from its own directory. Project-scoped path first,
# user-scoped second. Adding an agent means adding one row here.
agent_dirs() {
  case "$1" in
    claude)   echo ".claude/skills $HOME/.claude/skills" ;;
    codex)    echo ".agents/skills $HOME/.codex/skills" ;;
    cursor)   echo ".cursor/skills $HOME/.cursor/skills" ;;
    opencode) echo ".opencode/skills $HOME/.opencode/skills" ;;
    generic)  echo ".agents/skills $HOME/.agents/skills" ;;
    *) return 1 ;;
  esac
}

dest_root() {
  local dirs project user
  dirs=$(agent_dirs "$AGENT") || {
    echo "unknown AGENT: $AGENT" >&2
    echo "supported: claude codex cursor opencode generic" >&2
    exit 1
  }
  project=${dirs%% *}; user=${dirs##* }
  if [ "${TARGET_SCOPE:-project}" = "user" ]; then echo "$user"
  else echo "$target/$project"; fi
}

require_skill() {
  [ -n "$skill" ] || usage
  [ -f "$HERE/$skill/SKILL.md" ] || { echo "unknown skill: $skill"; echo "available:"; echo "$SKILLS" | sed 's/^/  /'; exit 1; }
}
require_target() {
  if [ "${TARGET_SCOPE:-project}" != "user" ]; then
    [ -n "$target" ] && [ -d "$target" ] || { echo "target project dir required (or TARGET_SCOPE=user)"; exit 1; }
  fi
}

case "$cmd" in
  list)
    echo "$SKILLS" ;;
  agents)
    for a in claude codex cursor opencode generic; do
      dirs=$(agent_dirs "$a")
      printf '%-10s project: %-18s user: %s\n' "$a" "${dirs%% *}" "${dirs##* }"
    done ;;
  install|update)
    require_skill; require_target
    dest="$(dest_root)/$skill"
    if [ "$cmd" = "update" ] && [ ! -d "$dest" ]; then
      echo "$skill is not installed at $dest — use install"; exit 1
    fi
    if [ "$cmd" = "install" ] && [ -d "$dest" ]; then
      echo "$skill already installed at $dest — use update (or diff first)"; exit 1
    fi
    mkdir -p "$(dest_root)"
    rm -rf "$dest"
    cp -r "$HERE/$skill" "$dest"
    echo "$cmd complete: $dest"
    echo "collection version: $(git -C "$HERE" rev-parse --short HEAD 2>/dev/null || echo unknown)" ;;
  diff)
    require_skill; require_target
    dest="$(dest_root)/$skill"
    [ -d "$dest" ] || { echo "$skill is not installed at $dest"; exit 1; }
    if diff -ru "$dest" "$HERE/$skill"; then
      echo "in sync"
    else
      echo
      echo "(left = installed copy, right = collection)"
    fi ;;
  uninstall)
    require_skill; require_target
    dest="$(dest_root)/$skill"
    [ -d "$dest" ] || { echo "$skill is not installed at $dest"; exit 0; }
    echo "about to remove: $dest"
    read -r -p "confirm [y/N] " ans
    [ "$ans" = "y" ] || { echo "aborted"; exit 1; }
    rm -rf "$dest"
    echo "removed $dest" ;;
  *) usage ;;
esac
