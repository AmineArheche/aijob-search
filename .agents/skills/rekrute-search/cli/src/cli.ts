#!/usr/bin/env bun
import { runSearch, type SearchOpts } from "./commands/search.js"
import { runDetail, type DetailOpts } from "./commands/detail.js"

interface Flags {
  _: string[]
  [k: string]: string | boolean | string[]
}

function parseFlags(argv: string[]): Flags {
  const flags: Flags = { _: [] }
  const alias: Record<string, string> = { q: "query", l: "location", n: "limit" }
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i]
    if (a.startsWith("--") || a.startsWith("-")) {
      const key = alias[a.replace(/^-+/, "")] ?? a.replace(/^-+/, "")
      const next = argv[i + 1]
      if (next === undefined || next.startsWith("-")) {
        flags[key] = true
      } else {
        flags[key] = next
        i++
      }
    } else {
      ;(flags._ as string[]).push(a)
    }
  }
  return flags
}

const HELP = `rekrute-cli — search jobs on ReKrute Morocco

USAGE
  bun run src/cli.ts search [flags]
  bun run src/cli.ts detail <id|url> [--format json|plain]

SEARCH FLAGS
  --query, -q <text>      Keywords (title, skill, role).
  --location, -l <text>   Moroccan city (e.g. Fes, Casablanca, Rabat).
  --page <n>              1-indexed page (default 1).
  --limit, -n <n>         Cap results emitted.
  --format <fmt>          json (default) | table | plain.
`

async function main(): Promise<number> {
  const flags = parseFlags(process.argv.slice(2))
  const cmd = flags._[0]

  if (flags.help || cmd === "help" || !cmd) {
    process.stdout.write(HELP)
    return 0
  }

  if (cmd === "search") {
    const parseIntFlag = (name: string, raw: string | boolean | string[]): number | null => {
      const val = typeof raw === "string" ? Number(raw.trim()) : NaN
      if (!Number.isInteger(val) || val < 1) {
        process.stderr.write(
          JSON.stringify({ error: `--${name} must be a whole number of at least 1, got "${raw}"`, code: "BAD_ARG" }) + "\n",
        )
        return null
      }
      return val
    }

    let page = 1
    if (flags.page !== undefined) {
      const p = parseIntFlag("page", flags.page)
      if (p === null) return 1
      page = p
    }

    let limit: number | undefined
    if (flags.limit !== undefined) {
      const l = parseIntFlag("limit", flags.limit)
      if (l === null) return 1
      limit = l
    }

    const format = (flags.format as string) || "json"
    if (!["json", "table", "plain"].includes(format)) {
      process.stderr.write(
        JSON.stringify({ error: `--format must be json, table, or plain, got "${format}"`, code: "BAD_ARG" }) + "\n",
      )
      return 1
    }

    const opts: SearchOpts = {
      query: typeof flags.query === "string" ? flags.query : undefined,
      location: typeof flags.location === "string" ? flags.location : undefined,
      page,
      limit,
      format: format as "json" | "table" | "plain",
    }
    return runSearch(opts)
  }

  if (cmd === "detail") {
    const idOrUrl = flags._[1]
    if (!idOrUrl) {
      process.stderr.write(
        JSON.stringify({ error: "detail requires an id or url", code: "MISSING_ARG" }) + "\n",
      )
      return 1
    }
    const format = (flags.format as string) || "json"
    const opts: DetailOpts = {
      idOrUrl,
      format: format as "json" | "plain",
    }
    return runDetail(opts)
  }

  process.stderr.write(
    JSON.stringify({ error: `Unknown command "${cmd}". Run with --help for usage.`, code: "UNKNOWN_COMMAND" }) + "\n",
  )
  return 1
}

main().then((code) => process.exit(code))
