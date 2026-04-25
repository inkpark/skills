# Graphify Reference for the LLM Wiki Skill

Use this reference when the user asks to generate, refresh, inspect, or troubleshoot the LLM Wiki graph layer.

## Role in the knowledge repository

Graphify is an optional generated graph layer over the reviewable Markdown wiki:

```text
raw/            immutable source notes; never edit from this skill
wiki/           reviewed Markdown knowledge layer; default Graphify input
graphify-out/   generated graph artifacts; reproducible, non-canonical output
```

Normal operation graphs `wiki/` only. Treat `raw/` as source evidence and `graphify-out/` as disposable derived output. Do not use `graphify-out/` as the source of truth for citations; cite wiki pages and raw provenance instead.

## Dependency and command facts

- Package name: `graphifyy`.
- CLI command: `graphify`.
- Expected generated artifacts include `graph.html`, `graph.json`, and `GRAPH_REPORT.md`.
- Graphify may send file contents to the configured assistant/model provider for semantic extraction. Treat every real graph build as network/API/cost-sensitive unless the current Graphify help and local configuration prove otherwise.

Reference links for re-checking before real use:

- PyPI: <https://pypi.org/project/graphifyy/>
- Graphify open-source product page: <https://graphify.net/kr/>
- Hosted Graphify page, not the default for the knowledge repository: <https://graphify.homes/>

## Hard safety rules

Do not do any of the following unless the user explicitly requests that exact side effect in an execution stage:

1. Install `graphifyy`.
2. Run a real `graphify` build.
3. Run model/API-consuming extraction.
4. Graph the full knowledge repository root with `graphify .`.
5. Graph `raw/` together with `wiki/` in one mixed output.
6. Modify, move, normalize, or generate files under `raw/`.
7. Overwrite an existing `graphify-out/` directory without a backup or explicit replacement approval.

Dry-run wrappers may print commands and verify path containment, but must not execute `graphify` without an explicit non-dry-run flag and user approval.

## Install commands: documentation only

Preferred setup commands to document, not run automatically:

```bash
uv tool install graphifyy
# alternatives when uv tool is unavailable:
pipx install graphifyy
python3 -m pip install --user graphifyy
```

Assistant integration commands are version-sensitive. Before running, check `graphify --help` and the current docs. The preferred forms from current Graphify docs/releases are:

```bash
graphify codex install
graphify claude install
```

Do not blindly use legacy compatibility forms such as `graphify install --platform codex`; first verify they are still accepted by the installed CLI.

## Default graph workflow: wiki-only

Before a real graph refresh:

1. Confirm the user wants a real Graphify run now.
2. Confirm model/API/network/cost implications are acceptable.
3. Verify `graphify` exists and inspect current help:

   ```bash
   command -v graphify
   graphify --help
   ```

4. Verify the intended input and output paths are contained in the knowledge repository.
5. Snapshot raw checksums and confirm no raw writes are planned:

   ```bash
   find raw -type f -print0 | sort -z | xargs -0 sha256sum > /tmp/llm-wiki-raw.before
   ```

6. Run wiki-only graph generation using a help-confirmed output mechanism.

If current help confirms an output flag such as `--out` or equivalent:

```bash
graphify ./wiki --out graphify-out/wiki
```

If no output flag is confirmed, use a controlled staging directory instead of running from the knowledge repository root. Example pattern:

```bash
rm -rf /tmp/llm-wiki-graphify-stage
mkdir -p /tmp/llm-wiki-graphify-stage/wiki
cp -R wiki/. /tmp/llm-wiki-graphify-stage/wiki/
(
  cd /tmp/llm-wiki-graphify-stage
  graphify ./wiki
)
# Move only verified generated artifacts into graphify-out/wiki after inspection.
```

After a successful run, expected review targets are:

```text
graphify-out/wiki/graph.html
graphify-out/wiki/graph.json
graphify-out/wiki/GRAPH_REPORT.md
```

Append a graph refresh entry to `wiki/log.md` if wiki logging is in scope for the user request.

## Raw-audit mode

Raw-inclusive graphing is not normal operation. Use it only when the user explicitly asks for raw audit/source-map review.

Rules:

- Input is `raw/` only.
- Output is isolated under `graphify-out/raw-audit/`.
- Do not mix `raw/` and `wiki/` outputs.
- Do not edit `raw/` before, during, or after audit.

Help-confirmed output example:

```bash
graphify ./raw --out graphify-out/raw-audit
```

Without a help-confirmed output flag, use a staging workflow analogous to wiki-only mode.

## `.graphifyignore` proposal

When creating or reviewing a `.graphifyignore`, include patterns that keep the generated graph focused and reduce accidental secret/cost exposure:

```gitignore
.git/
.omx/
.obsidian/
.codex/
.claude/
.env
.env.*
**/.env
**/.env.*
node_modules/
.venv/
venv/
__pycache__/
.pytest_cache/
graphify-out/
raw/
```

Notes:

- Excluding `raw/` protects against accidental root graphing. In raw-audit mode, run Graphify directly on `raw/` with isolated output after explicit confirmation.
- If the user asks for a mixed/root graph, first validate `.graphifyignore`, inspect `graphify --help`, and ask for explicit confirmation because this materially changes scope and cost exposure.

## Helper script

The optional helper accepts an explicit knowledge repository root so installed skill copies do not accidentally treat the assistant skill directory as the repo:

```bash
python ~/.codex/skills/llm-wiki/scripts/run_graphify.py --repo-root /path/to/knowledge-repo --dry-run --mode wiki-only
```

If `--repo-root` is omitted, it uses `LLM_WIKI_REPO_ROOT`, then walks upward from the current working directory until it finds `wiki/` or `raw/`.

## Verification checks

Use these checks after dry-runs or real graph workflows:

```bash
# raw immutability
find raw -type f -print0 | sort -z | xargs -0 sha256sum > /tmp/llm-wiki-raw.after
diff -u /tmp/llm-wiki-raw.before /tmp/llm-wiki-raw.after

# graph outputs should exist only after an approved real run
find graphify-out -type f -print 2>/dev/null | sort || true

# no graphify process should be started by install/dry-run validation
# review terminal history/output and script logs for actual `graphify ./...` execution.
```
