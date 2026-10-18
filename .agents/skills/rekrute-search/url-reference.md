# ReKrute Portal URL & Schema Reference

## Base URLs
- Public portal: `https://www.rekrute.com`
- Search page: `https://www.rekrute.com/offres.html?s=3&p={page}&customSearch=true&keyword={query}`
- Detail page: `https://www.rekrute.com/offre-emploi-...-{id}.html`

## Query Parameters
- `s=3` : Sort by date (most recent first)
- `p={n}` : Page number (1-indexed)
- `customSearch=true` : Enables faceted search
- `keyword={query}` : Keyword search term

## Card Selectors & Anchors
- Job URL & Title: `<a class='titreJob' href="/offre-emploi-...-{id}.html">{title} | {location}</a>`
- Company Name: Found in description or logo/link `<a ... href="/...-recrutement-...html">`
- Location: Extracted from title pipe (`| Fes (Maroc)`) or job info
- Dates: `<em class="date">Publication : du <span>{start_date}</span> au <span>{deadline}</span></em>`
- Job ID: Trailing integer in the URL, e.g. `-187569.html` -> `187569`
