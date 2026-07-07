#!/usr/bin/env bash
# install.sh — install the personal-humanizer-maker skill into a Claude Code / Codex host.
#
#   bash setup/install.sh                      # Claude Code (default) -> ~/.claude/skills
#   bash setup/install.sh --target codex       # Codex               -> ~/.codex/skills (+ ~/.agents/skills mirror)
#   bash setup/install.sh --target both
#
# Pure stdlib Python 3.9+ — no third-party deps, no venv, no network.
set -euo pipefail

TARGET="claude"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET="$2"; shift 2 ;;
    -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILL_SRC="$REPO_ROOT/skills/personal-humanizer-maker"

install_to() {
  local dest_root="$1"
  local dest="$dest_root/personal-humanizer-maker"
  mkdir -p "$dest_root"
  rm -rf "$dest"
  cp -R "$SKILL_SRC" "$dest"
  cp -R "$REPO_ROOT/schemas" "$dest/schemas"
  find "$dest" -name __pycache__ -type d -prune -exec rm -rf {} +
  echo "  installed -> $dest"
}

echo "personal-humanizer-maker installer"
command -v python3 >/dev/null || { echo "python3 is required" >&2; exit 1; }
python3 - <<'PY'
import sys
assert sys.version_info >= (3, 9), "Python 3.9+ required"
print(f"  python {sys.version.split()[0]} ok")
PY

case "$TARGET" in
  claude) install_to "$HOME/.claude/skills" ;;
  codex)  install_to "${CODEX_HOME:-$HOME/.codex}/skills" ; install_to "$HOME/.agents/skills" 2>/dev/null || true ;;
  both)   install_to "$HOME/.claude/skills" ; install_to "${CODEX_HOME:-$HOME/.codex}/skills" ; install_to "$HOME/.agents/skills" 2>/dev/null || true ;;
  *) echo "unknown target: $TARGET (use claude|codex|both)" >&2; exit 2 ;;
esac

echo "done. Trigger it inside a session:  \"내가 쓴 이 글로 개인 휴머나이저 만들어줘\""
