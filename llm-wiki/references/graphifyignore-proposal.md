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

# Immutable raw source notes (root graphs should not include raw implicitly)
raw/

# Dependency/build outputs
node_modules/
dist/
build/
.venv/
venv/
```

Generated files such as manifests, cost reports, caches, and intermediate extraction artifacts should remain outside canonical wiki content. Keep `graphify-out/raw-map/GRAPH_REPORT.md` and `graphify-out/wiki/GRAPH_REPORT.md` only as navigation aids, not as source evidence. Excluding `raw/` protects against accidental mixed/root graphing; when raw graphing is intended for wiki generation, run the separate raw-map workflow directly on `raw/` with isolated output.
