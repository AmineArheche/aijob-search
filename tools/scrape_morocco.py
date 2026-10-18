#!/usr/bin/env python3
"""Scrape jobs from Moroccan portals (ReKrute, MonCallCenter) and store in seen_jobs.json."""

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from job_key import make_key  # noqa: E402

SEEN_FILE = ROOT / "job_scraper" / "seen_jobs.json"


def run_node_cli(cli_path: Path, args: list[str]) -> list[dict]:
    cmd = ["npx", "tsx", str(cli_path)] + args
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=30, shell=True)
        if proc.returncode == 0 and proc.stdout.strip():
            data = json.loads(proc.stdout)
            return data.get("results", [])
        else:
            print(f"Error in {cli_path.name}: {proc.stderr}", file=sys.stderr)
    except Exception as e:
        print(f"Error running {cli_path.name}: {e}", file=sys.stderr)
    return []


def main():
    today = date.today().isoformat()
    seen_doc = {"seen": {}}
    if SEEN_FILE.is_file():
        try:
            seen_doc = json.loads(SEEN_FILE.read_text(encoding="utf-8"))
            if "seen" not in seen_doc or not isinstance(seen_doc["seen"], dict):
                seen_doc = {"seen": {}}
        except Exception:
            seen_doc = {"seen": {}}

    seen = seen_doc["seen"]
    existing_urls = {entry.get("url", "").rstrip("/") for entry in seen.values()}

    collected = []

    # 1. ReKrute search
    rekrute_cli = ROOT / ".agents" / "skills" / "rekrute-search" / "cli" / "src" / "cli.ts"
    queries_rekrute = ["developpeur", "python", "support"]
    for q in queries_rekrute:
        print(f"Scraping ReKrute for '{q}'...")
        results = run_node_cli(rekrute_cli, ["search", "-q", q, "--limit", "5"])
        for r in results:
            r["portal"] = "rekrute-search"
            collected.append(r)

    # 2. MonCallCenter search
    mcc_cli = ROOT / ".agents" / "skills" / "moncallcenter-search" / "cli" / "src" / "cli.ts"
    print("Scraping MonCallCenter...")
    results_mcc = run_node_cli(mcc_cli, ["search", "--limit", "5"])
    for r in results_mcc:
        r["portal"] = "moncallcenter-search"
        collected.append(r)

    added = 0
    skipped = 0

    for item in collected:
        url = (item.get("url") or "").rstrip("/")
        if not url or url in existing_urls:
            skipped += 1
            continue

        company = item.get("company") or "Recruiter"
        title = item.get("title") or "Position"
        key = make_key(company, title, url)

        if key in seen:
            skipped += 1
            continue

        seen[key] = {
            "title": title,
            "company": company,
            "location": item.get("location") or "Maroc",
            "url": url,
            "first_seen": today,
            "posted_date": item.get("date") or today,
            "deadline": None,
            "fit": "medium",
            "status": "new",
            "portal": item.get("portal", "cli"),
            "source": "cli"
        }
        existing_urls.add(url)
        added += 1

    SEEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    SEEN_FILE.write_text(json.dumps(seen_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nDone: {len(collected)} fetched, {added} new added to {SEEN_FILE}, {skipped} duplicates skipped.")


if __name__ == "__main__":
    main()
