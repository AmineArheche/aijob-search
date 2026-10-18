import { BASE_URL, htmlFetch, writeError } from "../helpers.js"

export interface DetailOpts {
  idOrUrl: string
  format: "json" | "plain"
}

function resolveUrl(idOrUrl: string): string {
  if (idOrUrl.startsWith("http://") || idOrUrl.startsWith("https://")) {
    return idOrUrl
  }
  return `${BASE_URL}/offre-emploi/${idOrUrl}`
}

export async function runDetail(opts: DetailOpts): Promise<number> {
  try {
    const url = resolveUrl(opts.idOrUrl)
    const html = await htmlFetch(url)
    if (!html) {
      writeError(`Posting not found: ${opts.idOrUrl}`, "NOT_FOUND")
      return 1
    }

    const titleMatch = html.match(/<h1[^>]*>([\s\S]*?)<\/h1>/i) ||
                       html.match(/<meta[^>]*property="og:title"[^>]*content="([^"]*)"/i) ||
                       html.match(/<title>([^<]*)<\/title>/i)
    const title = titleMatch ? titleMatch[1].replace(/<[^>]+>/g, "").trim() : "Job Posting"

    const descMatch = html.match(/<div[^>]*class=['"][^'"]*desc_offre[^'"]*['"][^>]*>([\s\S]*?)<\/div>/i) ||
                       html.match(/<meta[^>]*property="og:description"[^>]*content="([^"]*)"/i)
    const description = descMatch ? descMatch[1].replace(/<[^>]+>/g, "").trim() : ""

    const detail = {
      id: opts.idOrUrl,
      title,
      url,
      description,
    }

    if (opts.format === "plain") {
      process.stdout.write(`${title}\n${url}\n\n${description}\n`)
    } else {
      process.stdout.write(JSON.stringify(detail, null, 2) + "\n")
    }
    return 0
  } catch (e) {
    writeError(e instanceof Error ? e.message : String(e), "DETAIL_FAILED")
    return 1
  }
}
