export const BASE_URL = "https://www.moncallcenter.ma"
export const SEARCH_URL = "https://www.moncallcenter.ma/offres-emploi"

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
  
  // Find card blocks
  const cardBlocks = html.split(/<div[^>]*class=['"][^'"]*offresacc[^'"]*['"]/i)
  
  for (let i = 1; i < cardBlocks.length; i++) {
    const block = cardBlocks[i]
    
    // Extract link & title from h2 tag
    const titleMatch = block.match(/<h2>\s*<a[^>]*href=['"]([^'"]*\/offre-emploi\/[^'"]*)['"][^>]*>([\s\S]*?)<\/a>\s*<\/h2>/i)
    if (!titleMatch) continue
    
    const rawHref = titleMatch[1].trim()
    const rawTitle = titleMatch[2].replace(/<[^>]+>/g, "").trim().replace(/\s+/g, " ")
    if (!rawTitle) continue
    
    const idMatch = rawHref.match(/-(\d+)$/)
    const id = idMatch ? idMatch[1] : `mcc-${cards.length + 1}`
    const fullUrl = rawHref.startsWith("http") ? rawHref : `${BASE_URL}${rawHref}`
    
    // Extract company name from image alt or text
    let company: string | null = null
    const companyMatch = block.match(/<img[^>]*alt=['"]([^'"]+)['"]/i)
    if (companyMatch && companyMatch[1] && companyMatch[1].toLowerCase() !== "logo") {
      company = companyMatch[1].trim()
    }
    
    // Extract date
    let date: string | null = null
    const dateMatch = block.match(/<b>(\d{2}-\d{2}-\d{4})<\/b>/i)
    if (dateMatch) {
      const [d, m, y] = dateMatch[1].split("-")
      date = `${y}-${m}-${d}`
    }
    
    // Extract location
    let location: string | null = "Maroc"
    const locMatch = block.match(/<b[^>]*style=['"][^'"]*color:[^'"]*['"][^>]*>([^<]+)<\/b>/i)
    if (locMatch) {
      location = locMatch[1].trim()
    }
    
    cards.push({
      id,
      title: rawTitle,
      company: company || "MonCallCenter Recruiter",
      location,
      date,
      url: fullUrl,
    })
  }
  
  return cards
}
