#!/bin/bash
# Script pour exécuter les tests unitaires

set -e

echo "=== Exécution des tests unitaires ==="

# Vérifier si pytest est installé
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest n'est pas installé. Installation..."
    pip install -r requirements-dev.txt
fi

# Créer le répertoire pour les rapports de couverture
mkdir -p htmlcov

# Exécuter les tests avec couverture
echo "🧪 Exécution des tests..."
pytest tests/ -v --tb=short --cov=. --cov-report=html --cov-report=term-missing

# Afficher un résumé
echo ""
echo "=== Résumé des tests ==="
echo "📊 Rapport HTML généré dans: htmlcov/index.html"
echo "📈 Pour voir la couverture détaillée: open htmlcov/index.html"

# Vérifier la couverture minimale
echo ""
echo "=== Vérification de la couverture ==="
COVERAGE=$(python -c "
import json
try:
    with open('htmlcov/coverage.json', 'r') as f:
        data = json.load(f)
        total = data.get('totals', {}).get('percent_covered', 0)
        print(f'Couverture totale: {total:.1f}%')
        if total >= 80:
            print('✅ Couverture suffisante (>= 80%)')
        else:
            print('⚠️  Couverture insuffisante (< 80%)')
except:
    print('❌ Impossible de lire le rapport de couverture')
")