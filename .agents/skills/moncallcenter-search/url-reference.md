# MonCallCenter Portal URL & Schema Reference

## Base URLs
- Public portal: `https://www.moncallcenter.ma`
- Search page: `https://www.moncallcenter.ma/offres-emploi?keyword={query}&ville={location}&page={page}`
- Detail page: `https://www.moncallcenter.ma/offre-emploi/...-{id}`

## Query Parameters
- `keyword` : Search keywords (e.g. `support`, `technique`, `bilingue`)
- `ville` : City filter (e.g. `fes`, `rabat`, `casablanca`)
- `page` : 1-indexed pagination page number

## Card Selectors & Anchors
- Job URL: `<a href="/offre-emploi/...-{id}" class="offreUrl">`
- Title: Inner text of `<h2><a ... class="offreUrl">{title}</a></h2>`
- Company Name: Extracted from `<img alt="{Company}" .../>` or URL prefix
- Date: `<span><b>{dd-mm-yyyy}</b>`
- Location: `<b style="...">{City}</b>`
- Job ID: Trailing digits in the slug (e.g. `140802`)
