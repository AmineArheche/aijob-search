#!/usr/bin/env python3
"""Human Approval Gate & Application Package Assembler.

Enforces strict Human-in-the-Loop approval before any job application is dispatched.
Assembles:
1. Validated tailored CV (PDF + LaTeX source)
2. Validated tailored Cover Letter (PDF + LaTeX source)
3. Ready-to-paste Application Form text snippets (pitch, motivation, project details, salary, availability)
4. Human Approval Gate confirmation logging
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
DOSSIERS_DIR = ROOT_DIR / "documents" / "applications"
SEEN_JOBS_PATH = ROOT_DIR / "job_scraper" / "seen_jobs.json"
APPLICATIONS_LOG_PATH = ROOT_DIR / "job_scraper" / "applications_log.json"


def sanitize_token(text: str) -> str:
    import re
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "_", text)
    return text.strip("_")


def load_applications_log() -> Dict[str, Any]:
    if APPLICATIONS_LOG_PATH.is_file():
        try:
            return json.loads(APPLICATIONS_LOG_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"applications": {}}


def save_applications_log(data: Dict[str, Any]) -> None:
    APPLICATIONS_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    APPLICATIONS_LOG_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def generate_form_fields_text(role: str, company: str, location: str) -> str:
    """Generate structured form responses conforming to 08-application-forms.md."""
    role_lower = role.lower()

    if "ia" in role_lower or "python" in role_lower:
        self_intro = (
            "Développeur Full-stack diplômé de l'ISTA Ifrane (DTS en Développement Digital) et certifié CISCO Python Essentials. "
            "J'ai développé des architectures web complètes en freelance et sur des projets de plateformes e-commerce. "
            f"Je souhaite mettre à profit mes bases solides en algorithmique Python et conception d'APIs au service d'{company} à Fès."
        )
        motivation = (
            f"L'envergure d'{company} dans l'ingénierie technologique et le positionnement innovant de ce poste sur Python et l'IA à Fès "
            "correspondent exactement à mes compétences logicielles et à ma volonté de contribuer à des projets industriels d'excellence."
        )
        project_desc = (
            "Projet Plateforme E-commerce Énergie Solaire (Stage - 2025) : Conception et implémentation du catalogue interactif, "
            "interfaçage de base de données relationnelle et sécurisation du parcours d'achat. "
            "Difficulté technique : Optimisation des requêtes de filtres multi-critères. Résultat : plateforme fonctionnelle et réactive."
        )
    elif "support" in role_lower or "n2" in role_lower or "réseau" in role_lower:
        self_intro = (
            "Professionnel du support technique fort d'une expérience concrète chez Concentrix et d'une formation en Développement Digital (ISTA Ifrane). "
            "Trilingue (Français B2, Anglais B2, Arabe natif), j'assure un diagnostic rigoureux des incidents N1/N2 et le respect strict des SLA. "
            f"Je souhaite intégrer {company} pour garantir une haute disponibilité de service et la satisfaction des utilisateurs."
        )
        motivation = (
            f"Rejoindre {company} me permet de mobiliser ma double expertise : aisance relationnelle en support client et rigueur technique d'analyse "
            "pour résoudre efficacement les pannes et pérenniser la documentation opérationnelle."
        )
        project_desc = (
            "Gestion des Incidents Techniques Concentrix (2025-2026) : Prise en charge quotidienne des requêtes utilisateurs sous engagements contractuels. "
            "Résolution méthodique d'anomalies, qualification des dysfonctionnements complexes et transmission coordonnée au niveau supérieur avec score CSAT élevé."
        )
    elif "comptabilité" in role_lower or "paiement" in role_lower:
        self_intro = (
            "Spécialiste de la relation client et du traitement de données techniques, combinant une pratique quotidienne chez Concentrix "
            "et une formation en développement digital. Rigoureux et autonome, j'assure le rapprochement des flux et la résolution rapide d'incidents transactionnels."
        )
        motivation = (
            f"La structure 100 % remote d'{company} valorise pleinement mon autonomie organisationnelle et ma rigueur dans le suivi des échéanciers "
            "et la réconciliation de données financières."
        )
        project_desc = (
            "Gestion Transactionnelle & Support Client (Concentrix & Projets) : Suivi des réclamations liées aux transactions, "
            "vérification des dossiers clients et maintien de la cohérence des données sur outils de gestion et tableurs avancés."
        )
    else:
        self_intro = (
            "Développeur Full-stack et technicien digital diplômé de l'ISTA Ifrane, certifié CISCO Python Essentials. "
            "Expérimenté en conception d'interfaces web, architectures backend et relation client."
        )
        motivation = f"Je souhaite apporter ma motivation, ma rigueur technique et ma réactivité aux équipes d'{company}."
        project_desc = "Conception et déploiement de solutions applicatives web en environnement structuré."

    content = f"""================================================================================
FORMULAIRE DE CANDIDATURE - {company} | {role}
================================================================================
NOTE TO SELF : Textes prêts pour copier-coller dans les portails ATS / formulaires.
Aucun envoi n'est réalisé sans votre validation explicite.
================================================================================

[1. PITCH / PRÉSENTATION COURTE (100-150 mots)]
{self_intro}

[2. MOTIVATION POUR L'ENTREPRISE]
{motivation}

[3. PROJET RÉCENT / RÉALISATION MARQUANTE]
{project_desc}

[4. DISPONIBILITÉ & PRÉAVIS]
Disponibilité : Immédiate (sans préavis à effectuer).

[5. PRÉTENTIONS SALARIALES INDICATIVES]
Selon la grille de l'entreprise et la nature du poste (fourchette marché Fès / Remote).

[6. COORDONNÉES CONFIRMÉES]
Nom : Amine Arheche
Email : Aminearheche@gmail.com
Téléphone : +212 720819047
Ville : Fès, Maroc
Langues : Arabe (Natif), Français (B2 Professionnel), Anglais (B2 Professionnel)
================================================================================
"""
    return content


def assemble_application_package(role: str, company: str, job_url: str = "") -> Dict[str, Any]:
    """Assemble complete application package ready for human gate approval."""
    comp_tok = sanitize_token(company)
    role_tok = sanitize_token(role)

    dossier_folder = DOSSIERS_DIR / f"{comp_tok}_{role_tok}"
    dossier_folder.mkdir(parents=True, exist_ok=True)

    # 1. Generate CV and Cover Letter files
    from tools.gemini_drafter import draft_application

    draft_res = draft_application(role, company, output_tex=True, compile_pdf=True)

    # 2. Generate form fields text
    form_text = generate_form_fields_text(role, company, "Fès / Remote")
    form_file = dossier_folder / "form_answers.txt"
    form_file.write_text(form_text, encoding="utf-8")

    # 3. Copy/link CV and Cover letter into the dedicated application folder
    import shutil
    cv_dest = dossier_folder / f"CV_Amine_Arheche_{comp_tok}.pdf"
    cover_dest = dossier_folder / f"Lettre_Motivation_Amine_Arheche_{comp_tok}.pdf"
    shutil.copy2(draft_res["cv_pdf"], cv_dest)
    shutil.copy2(draft_res["cover_pdf"], cover_dest)

    app_id = f"{comp_tok}_{role_tok}"
    log_data = load_applications_log()
    log_data["applications"][app_id] = {
        "company": company,
        "role": role,
        "url": job_url,
        "dossier_folder": str(dossier_folder),
        "cv_pdf": str(cv_dest),
        "cover_pdf": str(cover_dest),
        "form_answers": str(form_file),
        "assembled_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "READY_FOR_HUMAN_APPROVAL",
        "human_decision": "PENDING",
    }
    save_applications_log(log_data)

    return {
        "app_id": app_id,
        "dossier_folder": str(dossier_folder),
        "cv_pdf": str(cv_dest),
        "cover_pdf": str(cover_dest),
        "form_answers": str(form_file),
        "status": "READY_FOR_HUMAN_APPROVAL",
    }


def record_human_approval(app_id: str, approved: bool, notes: str = "") -> bool:
    """Record user's explicit approval or rejection in the gate."""
    log_data = load_applications_log()
    if app_id not in log_data.get("applications", {}):
        return False

    app = log_data["applications"][app_id]
    app["human_decision"] = "APPROVED" if approved else "REJECTED"
    app["decision_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    app["status"] = "APPROVED_BY_USER" if approved else "REJECTED_BY_USER"
    app["notes"] = notes
    save_applications_log(log_data)
    return True


def main():
    parser = argparse.ArgumentParser(description="Human Approval Gate & Application Package Assembler")
    parser.add_argument("--top", type=int, default=0, help="Assemble application package for top N jobs")
    parser.add_argument("--approve", type=str, default="", help="Record approval for application ID")
    parser.add_argument("--reject", type=str, default="", help="Record rejection for application ID")
    parser.add_argument("--notes", type=str, default="", help="Optional notes on approval/rejection")
    args = parser.parse_args()

    print("=" * 65)
    print("🛡 HUMAN APPROVAL GATE - ASSISTED APPLICATION WORKFLOW")
    print("=" * 65)

    if args.approve:
        if record_human_approval(args.approve, approved=True, notes=args.notes):
            print(f"✓ Candidature '{args.approve}' validée et approuvée par l'utilisateur.")
        else:
            print(f"✗ Candidature '{args.approve}' introuvable.")
        return

    if args.reject:
        if record_human_approval(args.reject, approved=False, notes=args.notes):
            print(f"✓ Candidature '{args.reject}' marquée comme rejetée par l'utilisateur.")
        else:
            print(f"✗ Candidature '{args.reject}' introuvable.")
        return

    # Assemble for top jobs
    targets = []
    if SEEN_JOBS_PATH.is_file():
        doc = json.loads(SEEN_JOBS_PATH.read_text(encoding="utf-8"))
        ranked = [v for v in doc.get("seen", {}).values() if v.get("location_verdict") == "PASS"]
        ranked.sort(key=lambda x: x.get("rank_score", 0), reverse=True)
        count = args.top if args.top > 0 else 3
        for r in ranked[:count]:
            targets.append(r)

    print(f"\n📦 Préparation des dossiers complets ({len(targets)} offres sélectionnées) :")
    for t in targets:
        print(f"\n⚙ Traitement : {t.get('title')} chez {t.get('company')}")
        pkg = assemble_application_package(t.get("title"), t.get("company"), t.get("url", ""))
        print(f"  ✓ Dossier complet : {pkg['dossier_folder']}")
        print(f"  ✓ CV : {Path(pkg['cv_pdf']).name}")
        print(f"  ✓ Lettre : {Path(pkg['cover_pdf']).name}")
        print(f"  ✓ Formulaires : {Path(pkg['form_answers']).name}")
        print(f"  🔒 Statut : {pkg['status']} (En attente de votre feu vert)")

    print("\n" + "=" * 65)
    print("💡 RAPPEL SÉCURITÉ :")
    print("L'agent ne transmet AUCUNE candidature automatiquement.")
    print("Chaque dossier est prêt à être vérifié par vous avant envoi.")
    print("=" * 65)


if __name__ == "__main__":
    main()
