#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Python pour exécuter les tests unitaires
"""
import subprocess
import sys
from pathlib import Path


def run_tests():
    """Exécute les tests unitaires"""
    print("=== Exécution des tests unitaires ===")

    # Vérifier si on est dans le bon répertoire
    if not Path("tests").exists():
        print("❌ Dossier 'tests' non trouvé. Êtes-vous dans le répertoire racine du projet ?")
        return False

    # Installer les dépendances de développement si nécessaire
    if not Path("requirements-dev.txt").exists():
        print("❌ Fichier requirements-dev.txt non trouvé")
        return False

    try:
        # Installer pytest si nécessaire
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-q", "-r", "requirements-dev.txt"
        ], check=True)

        # Créer le répertoire pour les rapports
        Path("htmlcov").mkdir(exist_ok=True)

        # Exécuter les tests
        print("🧪 Lancement des tests...")
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/",
            "-v",
            "--tb=short",
            "--cov=.",
            "--cov-report=html",
            "--cov-report=term-missing"
        ], capture_output=True, text=True)

        # Afficher la sortie
        print(result.stdout)
        if result.stderr:
            print("Erreurs:", result.stderr)

        # Vérifier le résultat
        if result.returncode == 0:
            print("✅ Tous les tests sont passés !")
            return True
        else:
            print(f"❌ {result.returncode} test(s) ont échoué")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'exécution des tests: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False


def show_coverage_report():
    """Affiche un résumé du rapport de couverture"""
    coverage_file = Path("htmlcov/coverage.json")

    if not coverage_file.exists():
        print("❌ Rapport de couverture non trouvé")
        return

    try:
        import json
        with open(coverage_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        total_coverage = data.get('totals', {}).get('percent_covered', 0)
        print(f"Couverture totale: {total_coverage:.1f}%")
        if total_coverage >= 80:
            print("✅ Couverture suffisante (>= 80%)")
        else:
            print("⚠️  Couverture insuffisante (< 80%)")

        print("📊 Rapport HTML: htmlcov/index.html")

    except Exception as e:
        print(f"❌ Erreur lors de la lecture du rapport: {e}")


if __name__ == "__main__":
    success = run_tests()

    if success:
        print("\n=== Rapport de couverture ===")
        show_coverage_report()

    sys.exit(0 if success else 1)