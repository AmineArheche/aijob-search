#!/usr/bin/env python3
"""Push Notification Dispatcher for High-Matching Job Alerts.

Supports:
1. ntfy.sh (100% free, zero login required, instant push to Android/iOS/Desktop)
2. Telegram Bot (via Bot API sendMessage)

Features:
- Filters by minimum score threshold (default 70/100)
- Applies location veto (only Fès or 100% Remote)
- Deduplicates using job_scraper/notified_jobs.json
- Includes direct click-through link to apply
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / ".env"
SEEN_JOBS_PATH = ROOT_DIR / "job_scraper" / "seen_jobs.json"
NOTIFIED_JOBS_PATH = ROOT_DIR / "job_scraper" / "notified_jobs.json"


def load_config() -> Dict[str, Any]:
    config = {
        "channel": os.environ.get("NOTIFICATION_CHANNEL", "ntfy").strip().lower(),
        "ntfy_topic": os.environ.get("NTFY_TOPIC", "amine_jobs_alert_private_channel").strip(),
        "telegram_token": os.environ.get("TELEGRAM_BOT_TOKEN", "").strip(),
        "telegram_chat_id": os.environ.get("TELEGRAM_CHAT_ID", "").strip(),
        "min_score": int(os.environ.get("MIN_MATCH_SCORE", "70")),
    }

    if ENV_PATH.is_file():
        try:
            content = ENV_PATH.read_text(encoding="utf-8")
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k == "NOTIFICATION_CHANNEL" and v:
                    config["channel"] = v.lower()
                elif k == "NTFY_TOPIC" and v:
                    config["ntfy_topic"] = v
                elif k == "TELEGRAM_BOT_TOKEN" and v:
                    config["telegram_token"] = v
                elif k == "TELEGRAM_CHAT_ID" and v:
                    config["telegram_chat_id"] = v
                elif k == "MIN_MATCH_SCORE" and v.isdigit():
                    config["min_score"] = int(v)
        except Exception:
            pass

    return config


def send_ntfy_notification(
    topic: str,
    title: str,
    message: str,
    url: Optional[str] = None,
    priority: str = "high",
    tags: str = "briefcase,star",
    timeout: int = 15,
) -> Tuple[bool, str]:
    """Send an instant push notification via ntfy.sh."""
    if not topic:
        return False, "ntfy topic is empty"

    endpoint = f"https://ntfy.sh/{urllib.parse.quote(topic)}"
    headers = {
        "Title": title.encode("utf-8").decode("latin-1", errors="replace"),
        "Priority": priority,
        "Tags": tags,
    }
    if url:
        headers["Click"] = url
        headers["Actions"] = f"view, Voir l'offre, {url}"

    try:
        req = urllib.request.Request(
            endpoint,
            data=message.encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                return True, "Notification sent via ntfy.sh"
            return False, f"ntfy status {resp.status}"
    except Exception as exc:
        return False, f"ntfy request error: {exc}"


def send_telegram_notification(
    bot_token: str,
    chat_id: str,
    text: str,
    timeout: int = 15,
) -> Tuple[bool, str]:
    """Send an instant push notification via Telegram Bot API."""
    if not bot_token or not chat_id:
        return False, "Telegram token or chat_id not configured"

    endpoint = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            endpoint,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                return True, "Notification sent via Telegram"
            return False, f"Telegram status {resp.status}"
    except Exception as exc:
        return False, f"Telegram request error: {exc}"


def format_job_message(job: Dict[str, Any]) -> Tuple[str, str]:
    """Format title and body for notification."""
    title = f"🎯 [{job.get('rank_score')}/100 - {job.get('rank_verdict')}] {job.get('company')}"
    lines = [
        f"Poste: {job.get('title')}",
        f"Entreprise: {job.get('company')}",
        f"Lieu: {job.get('location')} (Éligible Fès/Remote)",
        f"Score de matching: {job.get('rank_score')}/100",
        "",
        "Points forts :",
    ]
    for s in job.get("strengths", []):
        lines.append(f"  • {s}")

    gaps = job.get("gaps", [])
    if gaps:
        lines.append("")
        lines.append("Points d'attention :")
        for g in gaps:
            lines.append(f"  ⚠ {g}")

    if job.get("url"):
        lines.append("")
        lines.append(f"Lien : {job.get('url')}")

    return title, "\n".join(lines)


def load_notified_keys() -> set[str]:
    if NOTIFIED_JOBS_PATH.is_file():
        try:
            data = json.loads(NOTIFIED_JOBS_PATH.read_text(encoding="utf-8"))
            return set(data.get("notified_keys", []))
        except Exception:
            pass
    return set()


def save_notified_key(key: str) -> None:
    notified = load_notified_keys()
    notified.add(key)
    NOTIFIED_JOBS_PATH.parent.mkdir(parents=True, exist_ok=True)
    NOTIFIED_JOBS_PATH.write_text(
        json.dumps({"notified_keys": sorted(list(notified))}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def dispatch_job_notification(job: Dict[str, Any], config: Optional[Dict[str, Any]] = None, dry_run: bool = False) -> Dict[str, Any]:
    if config is None:
        config = load_config()

    title, body = format_job_message(job)
    url = job.get("url")

    result = {
        "job_url": url,
        "company": job.get("company"),
        "role": job.get("title"),
        "score": job.get("rank_score"),
        "channel": config["channel"],
        "dry_run": dry_run,
        "success": False,
        "message": "",
    }

    if dry_run:
        result["success"] = True
        result["message"] = f"[DRY RUN] Prepared {config['channel']} alert: {title}"
        return result

    if config["channel"] == "ntfy":
        ok, msg = send_ntfy_notification(
            topic=config["ntfy_topic"],
            title=title,
            message=body,
            url=url,
        )
        result["success"] = ok
        result["message"] = msg
    elif config["channel"] == "telegram":
        ok, msg = send_telegram_notification(
            bot_token=config["telegram_token"],
            chat_id=config["telegram_chat_id"],
            text=f"<b>{title}</b>\n\n{body}",
        )
        result["success"] = ok
        result["message"] = msg
    else:
        result["message"] = f"Unsupported channel: {config['channel']}"

    return result


def scan_and_notify_shortlist(min_score: Optional[int] = None, dry_run: bool = False) -> List[Dict[str, Any]]:
    config = load_config()
    threshold = min_score if min_score is not None else config["min_score"]

    if not SEEN_JOBS_PATH.is_file():
        print("seen_jobs.json not found")
        return []

    doc = json.loads(SEEN_JOBS_PATH.read_text(encoding="utf-8"))
    seen = doc.get("seen", {})

    already_notified = load_notified_keys()
    dispatched = []

    for key, job in seen.items():
        if job.get("status") != "ranked":
            continue
        if job.get("location_verdict") != "PASS":
            continue
        score = job.get("rank_score", 0)
        if score < threshold:
            continue
        if key in already_notified and not dry_run:
            continue

        res = dispatch_job_notification(job, config, dry_run=dry_run)
        dispatched.append(res)

        if res["success"] and not dry_run:
            save_notified_key(key)

    return dispatched


def main():
    parser = argparse.ArgumentParser(description="Dispatch push notifications for top matching jobs")
    parser.add_argument("--dry-run", action="store_true", help="Format and print alerts without sending HTTP requests")
    parser.add_argument("--test-channel", action="store_true", help="Send a test notification immediately")
    parser.add_argument("--min-score", type=int, default=70, help="Minimum score threshold (default: 70)")
    args = parser.parse_args()

    config = load_config()
    print("=" * 65)
    print("🔔 PUSH NOTIFICATION DISPATCHER")
    print(f"   Canal actif : {config['channel'].upper()}")
    if config["channel"] == "ntfy":
        print(f"   Topic ntfy  : https://ntfy.sh/{config['ntfy_topic']}")
    print(f"   Seuil score : ≥ {args.min_score}/100 (Fès ou 100% Remote uniquement)")
    print("=" * 65)

    if args.test_channel:
        sample_job = {
            "title": "Développeur Python IA",
            "company": "ALTEN MAROC",
            "location": "Fes (Maroc)",
            "rank_score": 87,
            "rank_verdict": "Strong Fit",
            "url": "https://www.rekrute.com/offre-emploi-developpeur-python-ia-recrutement-alten-maroc-fes-187569.html",
            "strengths": [
                "Excellente adéquation avec les compétences Python et développement web",
                "Localisation optimale à Fès chez un leader de l'ingénierie",
            ],
            "gaps": ["Compétences Azure et MLOps à consolider en phase d'onboarding"],
        }
        print("\nEnvoi d'une notification test...")
        res = dispatch_job_notification(sample_job, config, dry_run=args.dry_run)
        print(f"Résultat : {'✓ SUCCÈS' if res['success'] else '✗ ÉCHEC'} - {res['message']}")
        return

    results = scan_and_notify_shortlist(min_score=args.min_score, dry_run=args.dry_run)
    print(f"\nOffres scannées et traitées : {len(results)}")
    for r in results:
        status = "✓ ENVOYÉ" if r["success"] else "✗ ERREUR"
        print(f"  [{status}] {r['company']} - {r['role']} (Score: {r['score']}) -> {r['message']}")


if __name__ == "__main__":
    main()
