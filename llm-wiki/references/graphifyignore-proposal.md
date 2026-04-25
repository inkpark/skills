# `.graphifyignore` proposal

Prefer graphing explicit paths (`wiki/` or `raw/`) rather than the knowledge repository root. If a future root graph is explicitly approved, validate an ignore policy equivalent to this before running Graphify.

```gitignore
# VCS, agent runtime, and editor state
.git/
.omx/
.obsidian/
.codex/
.claude/

# Secrets and local environment
.env
.env.*
*.pem
*.key
*.p12
*.pfx

# Generated graph output and caches
graphify-out/
**/.cache/
**/__pycache__/
*.pyc

# Immutable raw source notes (root graphs should default to wiki-only content)
raw/

# Dependency/build outputs
node_modules/
dist/
build/
.venv/
venv/
```

Generated files such as manifests, cost reports, caches, and intermediate extraction artifacts should remain outside canonical wiki content. Keep `graphify-out/wiki/GRAPH_REPORT.md` only as navigation aid, not as source evidence. Excluding `raw/` protects immutable source notes during any explicitly approved root graph; use the separate raw-audit workflow when raw source graphing is intentionally requested.
