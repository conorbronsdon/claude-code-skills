#!/usr/bin/env bash
# install.sh — manage skills from this collection in a target project.
#
#   ./install.sh install  <skill> <target-project-dir>
#   ./install.sh update   <skill> <target-project-dir>   # same as install, but requires existing copy
#   ./install.sh diff     <skill> <target-project-dir>   # show drift between collection and installed copy
#   ./install.sh uninstall <skill> <target-project-dir>
#   ./install.sh list
#
# Run from a clone of this repo. Copies the whole skill directory (SKILL.md +
# patterns/ + examples/) into <target>/.claude/skills/<skill>. No network, no
# dependencies beyond bash + coreutils. Pass TARGET_SCOPE=user to install into
# ~/.claude/skills instead of a project.

set -euo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
SKILLS=$(cd "$HERE" && for d in */SKILL.md; do dirname "$d"; done)

usage() { sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; exit 2; }

cmd=${1:-}; skill=${2:-}; target=${3:-}

dest_root() {
  if [ "${TARGET_SCOPE:-project}" = "user" ]; then echo "$HOME/.claude/skills"
  else echo "$target/.claude/skills"; fi
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
