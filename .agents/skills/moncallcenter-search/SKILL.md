---
name: moncallcenter-search
version: 1.0.0
description: >
  Use this skill to search live job postings in Morocco on MonCallCenter (moncallcenter.ma),
  the primary recruitment portal for call centers, BPO, customer service, bilingual technical
  support (French/English/Arabic), IT helpdesk, and tele-advisor roles across Morocco
  (Fès, Casablanca, Rabat, Tanger, Marrakech, etc.). Trigger phrases: moncallcenter,
  moncallcenter.ma, centre d'appel maroc, support technique maroc, conseiller bilingue fès,
  service client maroc, helpdesk maroc, call center fes, bpo morocco, teleperformance maroc.
context: fork
enabled: true
allowed-tools: Bash(bun run .agents/skills/moncallcenter-search/cli/src/cli.ts *)
---

# MonCallCenter Search Skill

Search live job listings from MonCallCenter (moncallcenter.ma), Morocco's dedicated portal
for customer relationship, IT technical support, bilingual helpdesk, and call center roles.

## ⚠️ Personal use only

This reads MonCallCenter's public job search pages. Keep query volume low, respect rate limits,
and do not use commercially or for bulk data collection.

## When to use this skill

- Search for technical support, customer care, and helpdesk positions in Fès and across Morocco
- Look up bilingual English/French advisor openings matching customer support background
- Retrieve complete offer descriptions and contact details for specific vacancies

## Commands

### Search job listings

```bash
bun run .agents/skills/moncallcenter-search/cli/src/cli.ts search [flags]
```

Flags:
- `--query <text>` / `-q <text>` — Keywords (e.g. `"support"`, `"bilingue"`, `"technique"`).
- `--location <text>` / `-l <text>` — Moroccan city (e.g. `"fes"`, `"rabat"`, `"casablanca"`).
- `--page <n>` — Page number (1-indexed).
- `--limit <n>` / `-n <n>` — Maximum number of results to output.
- `--format <fmt>` — `json` (default), `table`, or `plain`.

### Fetch job details

```bash
bun run .agents/skills/moncallcenter-search/cli/src/cli.ts detail <id|url> [--format json|plain]
```
