# Graphify Reference for the LLM Wiki Skill

Use this reference when the user asks to generate, refresh, inspect, or troubleshoot the LLM Wiki graph layer.

## Role in the knowledge repository

Graphify is an optional generated graph layer over raw notes and maintained wiki pages. Its primary value is to map relationships in `raw/` so an agent can generate better `wiki/` pages:

```text
raw/            immutable source notes; normal Graphify planning input
wiki/           reviewed Markdown knowledge layer; optional refresh input after the wiki exists
graphify-out/   generated graph artifacts; reproducible, non-canonical output
```

Normal first-pass or maintenance planning graphs `raw/` only and writes to `graphify-out/raw-map/`. Treat that output as a navigation, clustering, and synthesis aid. Do not treat it as canonical evidence; canonical citations still come from maintained wiki pages and their raw provenance.

Use `wiki/` graphing only after a reviewed wiki exists and the task is to inspect wiki navigation or cross-link quality. Never mix `raw/` and `wiki/` in one root graph by default.

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

## Default graph workflow: raw-map for wiki generation

Before a real raw-map refresh:

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

6. Run raw-only graph generation using a help-confirmed output mechanism.

If current help confirms an output flag such as `--out` or equivalent:

```bash
graphify ./raw --out graphify-out/raw-map
```

If no output flag is confirmed, use a controlled staging directory instead of running from the knowledge repository root. Example pattern:

```bash
rm -rf /tmp/llm-wiki-graphify-stage
mkdir -p /tmp/llm-wiki-graphify-stage/raw
cp -R raw/. /tmp/llm-wiki-graphify-stage/raw/
(
  cd /tmp/llm-wiki-graphify-stage
  graphify ./raw
)
# Move only verified generated artifacts into graphify-out/raw-map after inspection.
```

After a successful run, expected review targets are:

```text
graphify-out/raw-map/graph.html
graphify-out/raw-map/graph.json
graphify-out/raw-map/GRAPH_REPORT.md
```

Use `GRAPH_REPORT.md` to identify clusters, missing source-page candidates, concept candidates, and cross-source relationships before drafting `wiki/` pages. Append a graph refresh entry to `wiki/log.md` if wiki logging is in scope for the user request.

## Wiki-refresh mode

Use wiki-refresh mode only after reviewed wiki pages exist and the task is to inspect wiki navigation, cross-links, or concept coverage.

Rules:

- Input is `wiki/` only.
- Output is isolated under `graphify-out/wiki/`.
- Do not use wiki graph output to replace raw provenance.

Help-confirmed output example:

```bash
graphify ./wiki --out graphify-out/wiki
```

## Raw-audit mode

Raw-audit mode is for source coverage, extraction sanity checks, or cost/exposure audits beyond normal wiki generation. It remains explicit and isolated.

Rules:

- Input is `raw/` only.
- Output is isolated under `graphify-out/raw-audit/`.
- Do not mix `raw/` and `wiki/` outputs.
- Do not edit `raw/` before, during, or after audit.

Help-confirmed output example:

```bash
graphify ./raw --out graphify-out/raw-audit
```

Without a help-confirmed output flag, use a staging workflow analogous to raw-map mode.

## `.graphifyignore` proposal

When creating or reviewing a `.graphifyignore`, include patterns that keep accidental root graphs focused and reduce secret/cost exposure:

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

- Excluding `raw/` protects against accidental mixed/root graphing. For normal wiki generation, run Graphify directly on `raw/` with isolated output under `graphify-out/raw-map/` after explicit confirmation.
- If the user asks for a mixed/root graph, first validate `.graphifyignore`, inspect `graphify --help`, and ask for explicit confirmation because this materially changes scope and cost exposure.

## Helper script

The optional helper defaults to raw-map mode and accepts an explicit knowledge repository root so installed skill copies do not accidentally treat the assistant skill directory as the repo:

```bash
python ~/.codex/skills/llm-wiki/scripts/run_graphify.py --repo-root /path/to/knowledge-repo --dry-run --mode raw-map
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
