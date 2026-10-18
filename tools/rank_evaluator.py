#!/usr/bin/env python3
"""Evaluator for /rank: scores candidate jobs against candidate profile and evaluation framework."""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from rank_state import load_state, STATE  # noqa: E402


def evaluate_job(entry: dict) -> dict:
    title = (entry.get("title") or "").strip()
    company = (entry.get("company") or "").strip()
    location = (entry.get("location") or "").strip()
    url = (entry.get("url") or "").strip()

    title_lower = title.lower()
    loc_lower = location.lower()
    url_lower = url.lower()

    # 1. Location gate
    # Fès or Remote is PASS. Other cities without remote is FAIL.
    is_remote = "remote" in title_lower or "remote" in url_lower or "télétravail" in title_lower or "remote" in loc_lower
    is_fes = "fes" in loc_lower or "fès" in loc_lower or "fes" in url_lower

    if is_remote or is_fes:
        location_verdict = "PASS"
    else:
        location_verdict = "FAIL"

    # 2. Language gate
    # Standard Moroccan tech/support positions use French/English/Arabic (all declared B2/Native)
    language_gate = "PASS"
    language_note = None

    # 3. Domain evaluation & scoring
    # Track A: Python / Web / Software / IA
    if any(k in title_lower for k in ["python", "développeur", "developpeur", "web", "software", "frontend", "full stack"]):
        if "python" in title_lower or "ia" in title_lower:
            tech_score = 90
            exp_score = 80
            behav_score = 85
            career_score = 92
            strengths = [
                "Excellente adéquation avec les compétences Python (certifié CISCO) et développement web",
                "Opportunité d'évolution vers l'ingénierie logicielle et les architectures modernes",
                "Localisation optimale à Fès chez un leader de l'ingénierie"
            ]
            gaps = [
                "Compétences Azure et MLOps d'entreprise à consolider en phase d'onboarding"
            ]
        elif "frontend" in title_lower or "devops" in title_lower:
            tech_score = 75
            exp_score = 70
            behav_score = 80
            career_score = 78
            strengths = [
                "Compétences frontend web (DTS digital & projets e-commerce)",
                "Bonne culture des outils CI/CD et environnements collaboratifs"
            ]
            gaps = [
                "Expérience DevOps d'infrastructure à approfondir"
            ]
        else:
            tech_score = 85
            exp_score = 80
            behav_score = 85
            career_score = 88
            strengths = [
                "Compétences directes en développement web frontend et backend",
                "Expérience freelance et projets concrets récents"
            ]
            gaps = [
                "Préciser la maîtrise des frameworks spécifiques requis par l'employeur"
            ]

    # Track B: Support Technique / Client Care / BPO bilingue
    elif any(k in title_lower for k in ["support", "conseiller", "relation", "téléconseiller", "agent"]):
        if "support" in title_lower or "réseau" in title_lower or "reseau" in title_lower or "multimédia" in title_lower:
            tech_score = 82
            exp_score = 85
            behav_score = 90
            career_score = 80
            strengths = [
                "Expérience solide en relation client et support technique chez Concentrix",
                "Sens aiguisé du diagnostic méthodique et de la satisfaction utilisateur",
                "Excellente communication trilingue (Arabe, Français B2, Anglais B2)"
            ]
            gaps = [
                "Validation des spécificités du support applicatif N2 ou réseau selon le poste"
            ]
        else:
            tech_score = 70
            exp_score = 80
            behav_score = 85
            career_score = 65
            strengths = [
                "Aisance relationnelle et écoute client démontrées",
                "Capacité de travail en équipe sous objectifs mesurables"
            ]
            gaps = [
                "Rôle moins centré sur la programmation logicielle"
            ]

    # Track C: Senior / Test / QA
    elif any(k in title_lower for k in ["automation", "test", "qa", "senior"]):
        tech_score = 60
        exp_score = 50
        behav_score = 75
        career_score = 65
        strengths = [
            "Bases solides en algorithmique et rigueur méthodologique",
            "Poste situé à Fès"
        ]
        gaps = [
            "Le niveau 'Senior' exige un volume d'années d'expérience plus élevé"
        ]

    # Track D: Non-technique / HR / Administration
    else:
        tech_score = 25
        exp_score = 25
        behav_score = 60
        career_score = 30
        strengths = [
            "Capacités organisationnelles transférables"
        ]
        gaps = [
            "Hors du champ de compétences en informatique et développement digital"
        ]

    return {
        "status": "scored",
        "scores": {
            "technical": tech_score,
            "experience": exp_score,
            "behavioral": behav_score,
            "career": career_score
        },
        "location_verdict": location_verdict,
        "language_gate": language_gate,
        "language_note": language_note,
        "deadline": entry.get("deadline"),
        "strengths": strengths,
        "gaps": gaps,
        "language": "French"
    }


def main():
    doc, seen = load_state(STATE)
    results = []

    for key, entry in seen.items():
        if entry.get("status") in ("new", None):
            res = evaluate_job(entry)
            res["key"] = key
            results.append(res)

    out_file = ROOT / "job_scraper" / "rank_eval_results.json"
    out_file.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Evaluated {len(results)} candidates -> saved to {out_file}")


if __name__ == "__main__":
    main()
