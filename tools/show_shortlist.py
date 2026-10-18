#!/usr/bin/env python3
import json
import sys
from pathlib import Path

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")

p = Path("job_scraper/seen_jobs.json")
if not p.is_file():
    print("seen_jobs.json not found")
    exit(0)

doc = json.loads(p.read_text(encoding="utf-8"))
ranked = [v for v in doc.get("seen", {}).values() if v.get("status") == "ranked"]
ranked.sort(key=lambda x: x.get("rank_score", 0), reverse=True)

print(f"Total ranked: {len(ranked)}")
print("\n" + "="*70)
print("🎯 TOP SHORTLIST (Eligible & Location PASS - Fès / Remote)")
print("="*70)
count = 0
for r in ranked:
    if r.get("location_verdict") == "PASS":
        count += 1
        print(f"\n#{count} [{r.get('rank_score')}/100 - {r.get('rank_verdict')}] {r.get('title')} chez {r.get('company')}")
        print(f"   Localisation: {r.get('location')} | Portail: {r.get('portal')}")
        print(f"   Lien: {r.get('url')}")
        for s in r.get("strengths", []):
            print(f"   • Force : {s}")
        for g in r.get("gaps", []):
            print(f"   ⚠ Point d'attention : {g}")

print("\n" + "="*70)
print("🚫 EXCLUS PAR VETO GÉOGRAPHIQUE (Présentiel hors Fès)")
print("="*70)
for r in ranked:
    if r.get("location_verdict") == "FAIL":
        print(f"[VETO] {r.get('title')} chez {r.get('company')} ({r.get('location')}) - Score brut: {r.get('rank_score')}/100")
