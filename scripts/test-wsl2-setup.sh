#!/bin/bash
# Script de test pour vérifier la configuration WSL2/GitHub Actions

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "=== Test de la configuration WSL2/GitHub Actions ==="
echo ""

# Test 1: Vérifier WSL2
log_info "Test 1: Vérification de l'environnement WSL2..."
if grep -q Microsoft /proc/version; then
    log_success "Environnement WSL2 détecté"
else
    log_warning "Pas dans WSL2, mais le script devrait fonctionner sous Linux"
fi

# Test 2: Vérifier les dépendances
log_info "Test 2: Vérification des dépendances..."
deps=("curl" "jq" "git")
missing_deps=()

for dep in "${deps[@]}"; do
    if command -v "$dep" &> /dev/null; then
        echo "  ✅ $dep installé"
    else
        echo "  ❌ $dep manquant"
        missing_deps+=("$dep")
    fi
done

if [ ${#missing_deps[@]} -eq 0 ]; then
    log_success "Toutes les dépendances sont installées"
else
    log_error "Dépendances manquantes: ${missing_deps[*]}"
    echo "Exécutez: sudo apt-get install ${missing_deps[*]}"
    exit 1
fi

# Test 3: Vérifier les scripts
log_info "Test 3: Vérification des scripts..."
script_dir="$HOME/kivy_app_scripts"

if [ -d "$script_dir" ]; then
    log_success "Répertoire des scripts trouvé: $script_dir"
else
    log_warning "Répertoire des scripts non trouvé. Exécutez setup-wsl2.sh"
fi

scripts=("trigger-github-build.sh" "setup-github-token.sh" "kivy-build.sh")
for script in "${scripts[@]}"; do
    if [ -f "$script_dir/$script" ]; then
        echo "  ✅ $script"
        if [ -x "$script_dir/$script" ]; then
            echo "    📋 Exécutable"
        else
            echo "    ⚠️  Non exécutable"
        fi
    else
        echo "  ❌ $script manquant"
    fi
done

# Test 4: Vérifier le PATH
log_info "Test 4: Vérification du PATH..."
if echo "$PATH" | grep -q "$script_dir"; then
    log_success "Scripts dans le PATH"
else
    log_warning "Scripts pas dans le PATH. Rechargez avec: source ~/.bashrc"
fi

# Test 5: Vérifier les alias
log_info "Test 5: Vérification des alias..."
aliases=("kivy-build" "kivy-status" "kivy-apk" "kivy-aab")
for alias_name in "${aliases[@]}"; do
    if alias "$alias_name" &> /dev/null; then
        echo "  ✅ $alias_name"
    else
        echo "  ❌ $alias_name manquant"
    fi
done

# Test 6: Vérifier le token GitHub
log_info "Test 6: Vérification du token GitHub..."
if [ -n "$GITHUB_TOKEN" ]; then
    log_success "Token GitHub configuré"
    
    # Tester le token
    log_info "Test de validation du token..."
    response=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
                   -H "Accept: application/vnd.github.v3+json" \
                   "https://api.github.com/user" 2>/dev/null)
    
    if echo "$response" | jq -e '.login' > /dev/null 2>&1; then
        username=$(echo "$response" | jq -r '.login')
        log_success "Token valide pour: $username"
    else
        log_error "Token invalide ou problème de connexion"
        echo "Reconfigurez avec: ~/kivy_app_scripts/setup-github-token.sh"
    fi
else
    log_warning "Token GitHub non configuré"
    echo "Configurez avec: ~/kivy_app_scripts/setup-github-token.sh"
fi

# Test 7: Vérifier l'accès au repo
log_info "Test 7: Vérification de l'accès au repo..."
if [ -n "$GITHUB_TOKEN" ]; then
    response=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
                   -H "Accept: application/vnd.github.v3+json" \
                   "https://api.github.com/repos/NunoMars/kivy_app" 2>/dev/null)
    
    if echo "$response" | jq -e '.name' > /dev/null 2>&1; then
        log_success "Accès au repo confirmé"
    else
        log_error "Impossible d'accéder au repo NunoMars/kivy_app"
    fi
else
    log_warning "Impossible de tester l'accès au repo sans token"
fi

# Test 8: Test des commandes
log_info "Test 8: Test des commandes principales..."

# Test trigger-github-build.sh --help
if [ -x "$script_dir/trigger-github-build.sh" ]; then
    if "$script_dir/trigger-github-build.sh" --help > /dev/null 2>&1; then
        log_success "trigger-github-build.sh --help fonctionne"
    else
        log_error "trigger-github-build.sh --help échoue"
    fi
fi

# Test kivy-build help (si disponible)
if command -v kivy-build &> /dev/null; then
    if kivy-build help > /dev/null 2>&1; then
        log_success "kivy-build help fonctionne"
    else
        log_warning "kivy-build help échoue (normal si pas dans PATH)"
    fi
fi

# Résumé final
echo ""
log_info "=== Résumé ==="

# Compter les tests réussis
tests_passed=0
total_tests=8

# Incrémenter selon les résultats (logique simplifiée)
if grep -q Microsoft /proc/version; then ((tests_passed++)); fi
if [ ${#missing_deps[@]} -eq 0 ]; then ((tests_passed++)); fi
if [ -d "$script_dir" ]; then ((tests_passed++)); fi
if echo "$PATH" | grep -q "$script_dir"; then ((tests_passed++)); fi
if alias kivy-build &> /dev/null; then ((tests_passed++)); fi
if [ -n "$GITHUB_TOKEN" ]; then ((tests_passed++)); fi
if [ -n "$GITHUB_TOKEN" ] && echo "$response" | jq -e '.name' > /dev/null 2>&1; then ((tests_passed++)); fi
if [ -x "$script_dir/trigger-github-build.sh" ]; then ((tests_passed++)); fi

echo "Tests réussis: $tests_passed/$total_tests"

if [ $tests_passed -eq $total_tests ]; then
    log_success "Configuration complète et fonctionnelle! 🎉"
    echo ""
    echo "🚀 Vous pouvez maintenant utiliser:"
    echo "  kivy-build      # Build complet avec surveillance"
    echo "  kivy-apk        # Build APK seulement"
    echo "  kivy-aab        # Build AAB seulement"
    echo "  kivy-status     # Vérifier le statut"
elif [ $tests_passed -ge 6 ]; then
    log_warning "Configuration presque complète ($tests_passed/$total_tests)"
    echo ""
    echo "Actions recommandées:"
    if [ -z "$GITHUB_TOKEN" ]; then
        echo "  - Configurer le token GitHub: ~/kivy_app_scripts/setup-github-token.sh"
    fi
    if ! echo "$PATH" | grep -q "$script_dir"; then
        echo "  - Recharger le terminal: source ~/.bashrc"
    fi
else
    log_error "Configuration incomplète ($tests_passed/$total_tests)"
    echo ""
    echo "Actions requises:"
    echo "  1. Réexécuter l'installation: ./scripts/setup-wsl2.sh"
    echo "  2. Configurer le token: ~/kivy_app_scripts/setup-github-token.sh"
    echo "  3. Recharger le terminal: source ~/.bashrc"
fi

echo ""
echo "📚 Documentation complète: docs/WSL2_GITHUB_ACTIONS.md"
