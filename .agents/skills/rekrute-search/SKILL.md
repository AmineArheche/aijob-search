---
name: rekrute-search
version: 1.0.0
description: >
  Use this skill to search live job postings in Morocco on ReKrute (rekrute.com),
  the premier portal for executives, IT, engineering, finance, management, and technical
  roles in Morocco. Search by keywords, Moroccan cities (Casablanca, Rabat, Fès, Tanger,
  Marrakech, etc.), sector, or remote. Trigger phrases: rekrute, rekrute.com, maroc job,
  jobs au maroc, offres d'emploi maroc, emploi fès, informatique maroc, développeur maroc,
  recrutement maroc, stage maroc, tech jobs morocco.
context: fork
enabled: true
allowed-tools: Bash(bun run .agents/skills/rekrute-search/cli/src/cli.ts *)
---

# ReKrute Search Skill

Search live job listings from ReKrute (rekrute.com), Morocco's leading recruitment portal
for executives, IT professionals, software engineers, and managers.

## ⚠️ Personal use only

This reads ReKrute's public job search pages. Keep query volume low, respect rate limits,
and do not use commercially or for bulk data collection.

## When to use this skill

- Search for open positions across Morocco (Casablanca, Rabat, Fès, Tanger, etc.) or remote
- Look up tech, software, IT, customer support, and engineering opportunities
- Retrieve full job descriptions and application requirements for specific postings

## Commands

### Search job listings

```bash
bun run .agents/skills/rekrute-search/cli/src/cli.ts search [flags]
```

Flags:
- `--query <text>` / `-q <text>` — Keywords (e.g. `"developpeur"`, `"python"`, `"support"`).
- `--location <text>` / `-l <text>` — Moroccan city (e.g. `"Fes"`, `"Casablanca"`, `"Rabat"`).
- `--page <n>` — Page number (1-indexed).
- `--limit <n>` / `-n <n>` — Maximum number of results to output.
- `--format <fmt>` — `json` (default), `table`, or `plain`.

### Fetch job details

```bash
bun run .agents/skills/rekrute-search/cli/src/cli.ts detail <id|url> [--format json|plain]
```
