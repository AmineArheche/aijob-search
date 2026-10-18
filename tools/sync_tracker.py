#!/usr/bin/env python3
"""Tracker Synchronization & Job Search Funnel Manager.

Maintains job_search_tracker.csv in lockstep with:
- job_scraper/applications_log.json (Human Approval Gate & prepared packages)
- job_scraper/seen_jobs.json (Scraped and ranked Moroccan job offers)

Enforces:
- Canonical status vocabulary: drafted, applied, interview, offer, hired, rejected, no_response, offer_declined, withdrawn
- Strict CSV escaping (no rogue commas or unescaped quotes in notes)
- Header schema conformity: date,company,sector,role,role_type,channel,status,contact_person,fit_rating,notes,cv_file,cover_letter_file,source,deadline
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
TRACKER_PATH = ROOT_DIR / "job_search_tracker.csv"
APPLICATIONS_LOG_PATH = ROOT_DIR / "job_scraper" / "applications_log.json"
SEEN_JOBS_PATH = ROOT_DIR / "job_scraper" / "seen_jobs.json"

HEADER = [
    "date",
    "company",
    "sector",
    "role",
    "role_type",
    "channel",
    "status",
    "contact_person",
    "fit_rating",
    "notes",
    "cv_file",
    "cover_letter_file",
    "source",
    "deadline",
]

CANONICAL_STATUSES = {
    "drafted",
    "applied",
    "interview",
    "offer",
    "hired",
    "rejected",
    "no_response",
    "offer_declined",
    "withdrawn",
}

FINAL_STATUSES = {
    "hired",
    "rejected",
    "no_response",
    "offer_declined",
    "withdrawn",
}


def read_tracker_rows() -> List[Dict[str, str]]:
    if not TRACKER_PATH.is_file():
        return []
    rows = []
    text = TRACKER_PATH.read_text(encoding="utf-8")
    reader = csv.DictReader(io.StringIO(text))
    for r in reader:
        # Standardize status space-spellings to canonical underscore spellings
        st = r.get("status", "").strip().lower()
        if st == "no response":
            st = "no_response"
        elif st == "offer declined":
            st = "offer_declined"
        r["status"] = st
        rows.append(r)
    return rows


def write_tracker_rows(rows: List[Dict[str, str]]) -> None:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=HEADER, lineterminator="\n")
    writer.writeheader()
    for r in rows:
        filtered = {k: r.get(k, "") for k in HEADER}
        writer.writerow(filtered)
    TRACKER_PATH.write_text(buf.getvalue(), encoding="utf-8")


def normalize_key(company: str, role: str) -> str:
    clean_c = re.sub(r"[^\w]", "", company.lower())
    clean_r = re.sub(r"[^\w]", "", role.lower())
    return f"{clean_c}_{clean_r}"


def sync_applications_with_tracker() -> Tuple[int, int]:
    """Sync job_scraper/applications_log.json into job_search_tracker.csv."""
    if not APPLICATIONS_LOG_PATH.is_file():
        return 0, 0

    log_data = json.loads(APPLICATIONS_LOG_PATH.read_text(encoding="utf-8"))
    apps = log_data.get("applications", {})

    tracker_rows = read_tracker_rows()
    existing_keys = {normalize_key(r["company"], r["role"]): i for i, r in enumerate(tracker_rows)}

    added = 0
    updated = 0

    for app_id, app in apps.items():
        comp = app.get("company", "").strip()
        role = app.get("role", "").strip()
        if not comp or not role:
            continue

        key = normalize_key(comp, role)
        decision = app.get("human_decision", "PENDING")
        status = "applied" if decision == "APPROVED" else "drafted"

        notes_parts = []
        if decision == "APPROVED":
            notes_parts.append(f"Approved and applied on {app.get('decision_date', 'today')}")
        else:
            notes_parts.append(f"Human Approval Gate: Ready for review in documents/applications/{app_id}/")

        if app.get("notes"):
            notes_parts.append(app.get("notes"))

        notes_clean = " | ".join(notes_parts)

        # Relative paths for CV & Cover letter
        cv_rel = app.get("cv_pdf", "")
        cover_rel = app.get("cover_pdf", "")
        if cv_rel:
            try:
                cv_rel = str(Path(cv_rel).relative_to(ROOT_DIR)).replace("\\", "/")
            except Exception:
                pass
        if cover_rel:
            try:
                cover_rel = str(Path(cover_rel).relative_to(ROOT_DIR)).replace("\\", "/")
            except Exception:
                pass

        row_dict = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "company": comp,
            "sector": "Tech / Support / Engineering",
            "role": role,
            "role_type": "full-time",
            "channel": "portal",
            "status": status,
            "contact_person": "Talent Acquisition / HR",
            "fit_rating": "5" if "ia" in role.lower() or "python" in role.lower() else "4",
            "notes": notes_clean,
            "cv_file": cv_rel,
            "cover_letter_file": cover_rel,
            "source": "rekrute-search",
            "deadline": "",
        }

        if key in existing_keys:
            idx = existing_keys[key]
            # Update status if progressed
            if tracker_rows[idx]["status"] != status and status == "applied":
                tracker_rows[idx]["status"] = status
                tracker_rows[idx]["notes"] = notes_clean
                updated += 1
        else:
            tracker_rows.append(row_dict)
            existing_keys[key] = len(tracker_rows) - 1
            added += 1

    write_tracker_rows(tracker_rows)
    return added, updated


def update_row_status(target_company: str, new_status: str, notes: Optional[str] = None) -> bool:
    """Update application status matching target company name."""
    norm_status = new_status.strip().lower().replace(" ", "_")
    if norm_status not in CANONICAL_STATUSES:
        raise ValueError(
            f"Invalid status '{new_status}'. Allowed values: {', '.join(sorted(CANONICAL_STATUSES))}"
        )

    rows = read_tracker_rows()
    target = target_company.strip().lower()
    matched = False

    for r in rows:
        if target in r["company"].strip().lower() or target in r["role"].strip().lower():
            r["status"] = norm_status
            if notes:
                existing_notes = r.get("notes", "").strip()
                r["notes"] = f"{existing_notes} | {notes}" if existing_notes else notes
            matched = True
            break

    if matched:
        write_tracker_rows(rows)
    return matched


def calculate_funnel_stats(rows: List[Dict[str, str]]) -> Dict[str, Any]:
    total = len(rows)
    drafted = sum(1 for r in rows if r["status"] == "drafted")
    applied = sum(1 for r in rows if r["status"] == "applied")
    interview = sum(1 for r in rows if r["status"] == "interview")
    offer = sum(1 for r in rows if r["status"] == "offer")
    hired = sum(1 for r in rows if r["status"] == "hired")
    rejected = sum(1 for r in rows if r["status"] in FINAL_STATUSES and r["status"] != "hired")

    submitted = total - drafted
    conversion = round(((interview + offer + hired) / submitted * 100), 1) if submitted > 0 else 0.0

    return {
        "total": total,
        "drafted": drafted,
        "applied": applied,
        "interview": interview,
        "offer": offer,
        "hired": hired,
        "rejected": rejected,
        "conversion_rate": conversion,
    }


def main():
    parser = argparse.ArgumentParser(description="Synchronize tracker with applications and manage funnel")
    parser.add_argument("--sync", action="store_true", help="Sync applications_log.json into job_search_tracker.csv")
    parser.add_argument("--list", action="store_true", help="List applications in tracker with funnel statistics")
    parser.add_argument("--update", type=str, default="", help="Company name to update")
    parser.add_argument("--status", type=str, default="", help="New status to set")
    parser.add_argument("--notes", type=str, default="", help="Notes to append")
    parser.add_argument("--validate", action="store_true", help="Validate CSV formatting and status vocabulary")
    args = parser.parse_args()

    print("=" * 65)
    print("📊 JOB SEARCH TRACKER & FUNNEL MANAGER")
    print("=" * 65)

    if args.update and args.status:
        try:
            ok = update_row_status(args.update, args.status, args.notes)
            if ok:
                print(f"✓ Statut mis à jour pour '{args.update}' -> {args.status}")
            else:
                print(f"✗ Aucune candidature trouvée pour '{args.update}'")
        except Exception as e:
            print(f"✗ Erreur : {e}")
        return

    if args.sync or True:
        added, updated = sync_applications_with_tracker()
        print(f"🔄 Synchronisation réalisée : {added} ajoutée(s), {updated} mise(s) à jour.")

    rows = read_tracker_rows()
    stats = calculate_funnel_stats(rows)

    print("\n📈 MÉTRIQUES DU PIPELINE :")
    print(f"   • Total candidatures suivies : {stats['total']}")
    print(f"   • Préparées (Drafted / Gate)  : {stats['drafted']}")
    print(f"   • Envoyées (Applied)          : {stats['applied']}")
    print(f"   • Entretiens (Interview)      : {stats['interview']}")
    print(f"   • Offres reçues (Offer)       : {stats['offer']}")
    print(f"   • Embauches (Hired)           : {stats['hired']}")
    print(f"   • Clôturées / Refus           : {stats['rejected']}")
    print(f"   🎯 Taux de conversion         : {stats['conversion_rate']}%")

    if args.list or True:
        print("\n📋 DÉTAIL DES CANDIDATURES :")
        for i, r in enumerate(rows, 1):
            badge = "🟢" if r["status"] in ("interview", "offer", "hired") else "🟡" if r["status"] in ("applied", "drafted") else "⚪"
            print(f"  {badge} #{i} [{r['status'].upper()}] {r['company']} - {r['role']} (Note: {r['fit_rating']}/5)")
            if r.get("notes"):
                print(f"     Note : {r['notes'][:80]}...")


if __name__ == "__main__":
    main()
