export const BASE_URL = "https://www.rekrute.com"
export const SEARCH_URL = "https://www.rekrute.com/offres.html"

export function writeError(error: string, code: string): void {
  process.stderr.write(JSON.stringify({ error, code }) + "\n")
}

const UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

export async function htmlFetch(url: string): Promise<string> {
  const maxRetries = 4
  let delay = 500
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(url, {
        headers: {
          "User-Agent": UA,
          Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
          "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        },
        redirect: "follow",
        signal: AbortSignal.timeout(15000),
      })
      if (response.status === 429 || response.status >= 500) {
        if (attempt === maxRetries) {
          throw new Error(`Request failed: ${response.status} ${response.statusText}`)
        }
        await new Promise((r) => setTimeout(r, delay))
        delay = Math.min(delay * 2, 4000)
        continue
      }
      if (response.status === 404) return ""
      if (!response.ok) {
        throw new Error(`Request failed: ${response.status} ${response.statusText}`)
      }
      return await response.text()
    } catch (e) {
      if (attempt === maxRetries) throw e
      await new Promise((r) => setTimeout(r, delay))
      delay = Math.min(delay * 2, 4000)
    }
  }
  throw new Error("Request failed after max retries")
}

export interface JobCard {
  id: string
  title: string
  company: string | null
  location: string | null
  date: string | null
  url: string
}

export function parseJobCards(html: string): JobCard[] {
  const cards: JobCard[] = []
  
  // Find all titreJob links
  const regex = /<a[^>]*class=['"]titreJob['"][^>]*href=['"]([^'"]*)['"][^>]*>([\s\S]*?)<\/a>/gi
  let match: RegExpExecArray | null
  
  while ((match = regex.exec(html)) !== null) {
    const rawHref = match[1].trim()
    const rawTitleLoc = match[2].replace(/<[^>]+>/g, "").trim().replace(/\s+/g, " ")
    
    // Extract ID from URL (e.g. /offre-emploi-...-187569.html -> 187569)
    const idMatch = rawHref.match(/-(\d+)\.html/i)
    const id = idMatch ? idMatch[1] : `rekrute-${cards.length + 1}`
    
    const fullUrl = rawHref.startsWith("http") ? rawHref : `${BASE_URL}${rawHref}`
    
    // Split title and location if separated by '|'
    let title = rawTitleLoc
    let location: string | null = "Maroc"
    if (rawTitleLoc.includes("|")) {
      const parts = rawTitleLoc.split("|")
      title = parts[0].trim()
      location = parts.slice(1).join(" ").trim()
    }
    
    // Look ahead in surrounding HTML for company and date
    const surrounding = html.slice(match.index, match.index + 2500)
    
    let date: string | null = null
    const dateMatch = surrounding.match(/Publication\s*:\s*du\s*<span>(\d{2}\/\d{2}\/\d{4})<\/span>/i)
    if (dateMatch) {
      const [d, m, y] = dateMatch[1].split("/")
      date = `${y}-${m}-${d}`
    }
    
    let company: string | null = null
    const companyMatch = surrounding.match(/([A-Z0-9\s-]{3,30})\s+recherche\b/i)
    if (companyMatch) {
      company = companyMatch[1].trim()
    } else {
      const compLink = surrounding.match(/href="\/([a-z0-9-]+)-emploi-recrutement-[0-9]+\.html"/i)
      if (compLink) {
        company = compLink[1].replace(/-/g, " ").toUpperCase()
      }
    }
    
    cards.push({
      id,
      title,
      company: company || "ReKrute Employer",
      location,
      date,
      url: fullUrl,
    })
  }
  
  return cards
}
