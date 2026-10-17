# Search Queries for Job Scraper

<!-- SETUP: Customize these queries based on your skills, target roles, and location -->

## Installed portal CLIs (primary for `/scrape`)

`/scrape` discovers every portal skill under `.agents/skills/*/SKILL.md` and runs its CLI first. Shipped country-agnostic CLIs include `linkedin-search` and `freehire-search`; Danish demos and any skill you add with `/add-portal` are included the same way. You do **not** need a matching `site:` line below for those CLIs to run.

The `site:` query templates in this file are the **WebSearch fallback** — for portals without a CLI, company career pages, or when a CLI fails.

**Language scope:** write every query category in every language listed in your CLAUDE.md Languages table (typically 1-2, sometimes more). A posting requiring a language you have *not* declared, as a job condition, is excluded before scoring; a posting requiring a *higher level* than you declared in a language you *do* work in is flagged for your own judgment, not excluded — see `04-job-evaluation.md`'s Language Gate, the single source of truth for this rule. Translate each category's keywords rather than machine-translating word-for-word (e.g. "Frontend Developer" -> "Desarrollador Frontend", not a literal word-for-word translation) if you work in more than one language.

## Search Sites

Primary (Job boards Maroc & Remote):
- **rekrute.com** - Portale d'emploi cadres et IT au Maroc
- **emploi.ma** - Portail national marocain
- **moncallcenter.ma** - Portail leader pour les centres d'appels et le support client technique au Maroc
- **marocannonces.com** - Offres d'emploi directes au Maroc
- **optioncarriere.ma** - Moteur de recherche d'emploi au Maroc
- **freehire.me** - Agrégateur international d'offres tech en télétravail (remote)
- **linkedin.com/jobs** - Filtres: Maroc / Fès / Remote

Secondary (Company career pages & Freelance platforms):
- Plateformes freelance : Upwork, Malt, ComeUp, Mostaql
- Recherche Google ciblée avec filtres `site:` pour entreprises locales et internationales

## Query Categories

### Priority 1: Développeur Web Full-Stack / Développeur Web (Maroc & Remote)
```
site:rekrute.com "Développeur Web" OR "Full Stack"
site:emploi.ma "developpeur web" OR "python"
site:linkedin.com/jobs "Full Stack Developer" Maroc OR Remote
site:freehire.me "Full Stack" OR "Web Developer"
site:optioncarriere.ma "développeur full stack" Fès OR "Télétravail"
```

### Priority 2: Conseiller Clientèle Technique & Support Informatique (Call Center / BPO)
```
site:moncallcenter.ma "support technique" OR "bilingue" Fès
site:rekrute.com "conseiller technique" OR "support client"
site:emploi.ma "support informatique" OR "helpdesk"
site:linkedin.com/jobs "Customer Support Technical" Maroc
```

### Priority 3: Développeur E-commerce & Intégrateur Web
```
site:emploi.ma "e-commerce" OR "prestashop" OR "wordpress"
site:rekrute.com "developpeur e-commerce"
site:optioncarriere.ma "intégrateur web"
```

### Priority 4: Freelance & Télétravail (Missions à distance)
```
site:linkedin.com/jobs "développeur freelance" "remote"
site:emploi.ma "freelance" OR "télétravail" informatique
site:freehire.me "python developer" remote
```

## Location Filter
- **Fès et agglomération** : Présentiel, hybride ou télétravail (idéal).
- **Tout le Maroc / International** : Télétravail / Full Remote uniquement.
- **Hors de Fès sans télétravail** : À écarter (deal-breaker de mobilité non couverte).

## Language Filter

Your working languages and levels are in CLAUDE.md's Languages table. When filtering scraped results, apply `04-job-evaluation.md`'s Language Gate: a posting requiring a language you haven't declared at all is excluded; a posting requiring a higher level than you declared in a language you do work in is not excluded, flag it clearly instead (see `job-scraper/SKILL.md`'s Step 3 "Quick Fit Assessment" for how the flag surfaces in `/scrape` output). Postings simply *written* in a language you don't work in, that don't require it on the job, are fine.

## Date Filter

Only include jobs posted within the last 14 days, or with an application deadline that has not yet passed. If a posting date cannot be determined, include it but flag as "date unknown".

## Adapting Queries

If the user specifies a focus area, select queries from the matching category and also generate 2-3 custom queries for that focus. For example:
- "/scrape [focus_area]" -> relevant category queries + custom focus-specific queries
