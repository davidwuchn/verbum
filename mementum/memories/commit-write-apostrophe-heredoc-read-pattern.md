🌀 Commit messages: NEVER `git commit -m "$(cat <<'EOF'…)"` when the body has an apostrophe. The $() command-substitution rescans the body and ' opens an unterminated quote scan → `bash: unexpected EOF while looking for matching '`. `<<'EOF'` protects only the DELIMITER, not the rescan = false safety.

PROVEN (λ assert, runtime ≡ truth): a BARE heredoc with apostrophes works (exit 0); the SAME body inside `"$(cat <<'EOF'…)"` breaks. The break is the $() layer, not the heredoc.

FIX (default, verified safe for ' ∧ ` ∧ $, length-checked):
  read -r -d '' M << 'EOF' || true
  {message body — apostrophes/backticks/$ all literal}
  EOF
  git commit -m "$M"
read loads the body into a var with NO $() layer; "$M" expands without reparse.

ALTS: `git commit -F file` (eca__write_file → -F, zero shell quoting) ∨ `git commit -F - <<'EOF'` (stdin heredoc, no $()).

NEVER strip apostrophes (lossy workaround — the old habit). Preserve nucleus tag + leading symbol.

HISTORY: rediscovered ≥4× (s229, s239, s247b, s252) and never encoded = feed-forward gap. Now encoded as `λ commit_write(m)` in AGENTS.md S3 (commit a24c62f). If you are reading this and hit the bug, the field equation already exists — use it, do not re-derive.
