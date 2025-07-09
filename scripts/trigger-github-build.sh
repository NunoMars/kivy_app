#!/bin/bash
# Script pour déclencher et monitorer un build GitHub Actions depuis WSL2/Ubuntu
# Usage: ./trigger-github-build.sh [apk|aab|both]

set -e

# Configuration
REPO_OWNER="NunoMars"  # Remplacez par votre nom d'utilisateur GitHub
REPO_NAME="kivy_app"   # Remplacez par le nom de votre repo
WORKFLOW_FILE="build-android.yml"
BRANCH="main"          # ou "master" selon votre branche principale

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction d'aide
show_help() {
    echo "Usage: $0 [OPTIONS] [BUILD_TYPE]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Afficher cette aide"
    echo "  -t, --token    Spécifier le token GitHub (ou utiliser GITHUB_TOKEN)"
    echo "  -r, --repo     Spécifier le repo (format: owner/repo)"
    echo "  -b, --branch   Spécifier la branche (défaut: main)"
    echo "  -w, --watch    Surveiller le build en temps réel"
    echo "  -s, --status   Vérifier seulement le statut des builds en cours"
    echo ""
    echo "Build Types:"
    echo "  apk           Build APK seulement"
    echo "  aab           Build AAB seulement"
    echo "  both          Build APK et AAB (défaut)"
    echo ""
    echo "Examples:"
    echo "  $0                    # Déclenche build APK + AAB"
    echo "  $0 apk                # Déclenche build APK seulement"
    echo "  $0 --watch aab        # Déclenche build AAB et surveille"
    echo "  $0 --status           # Vérifie le statut des builds"
    echo ""
    echo "Setup:"
    echo "  1. Créer un token GitHub: https://github.com/settings/tokens"
    echo "  2. Permissions requises: repo, actions"
    echo "  3. Exporter le token: export GITHUB_TOKEN=your_token"
    echo "  4. Ou passer avec -t: $0 -t your_token"
}

# Fonction pour afficher les messages avec couleur
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier les dépendances
check_dependencies() {
    log_info "Vérification des dépendances..."
    
    # Vérifier curl
    if ! command -v curl &> /dev/null; then
        log_error "curl n'est pas installé. Installation..."
        sudo apt-get update -qq
        sudo apt-get install -y curl
    fi
    
    # Vérifier jq
    if ! command -v jq &> /dev/null; then
        log_error "jq n'est pas installé. Installation..."
        sudo apt-get update -qq
        sudo apt-get install -y jq
    fi
    
    # Vérifier git
    if ! command -v git &> /dev/null; then
        log_error "git n'est pas installé. Installation..."
        sudo apt-get update -qq
        sudo apt-get install -y git
    fi
    
    log_success "Toutes les dépendances sont installées"
}

# Vérifier le token GitHub
check_github_token() {
    if [ -z "$GITHUB_TOKEN" ]; then
        log_error "Token GitHub non trouvé!"
        echo ""
        echo "Pour obtenir un token GitHub:"
        echo "1. Allez sur: https://github.com/settings/tokens"
        echo "2. Cliquez 'Generate new token (classic)'"
        echo "3. Sélectionnez les permissions: repo, actions"
        echo "4. Copiez le token généré"
        echo ""
        echo "Puis utilisez une de ces méthodes:"
        echo "  export GITHUB_TOKEN=your_token_here"
        echo "  ./$(basename $0) -t your_token_here"
        echo ""
        exit 1
    fi
    
    # Tester le token
    log_info "Vérification du token GitHub..."
    response=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
                   -H "Accept: application/vnd.github.v3+json" \
                   "https://api.github.com/user")
    
    if echo "$response" | jq -e '.login' > /dev/null 2>&1; then
        username=$(echo "$response" | jq -r '.login')
        log_success "Token valide pour l'utilisateur: $username"
    else
        log_error "Token GitHub invalide ou expiré"
        exit 1
    fi
}

# Vérifier l'accès au repo
check_repo_access() {
    log_info "Vérification de l'accès au repo $REPO_OWNER/$REPO_NAME..."
    
    response=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
                   -H "Accept: application/vnd.github.v3+json" \
                   "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME")
    
    if echo "$response" | jq -e '.name' > /dev/null 2>&1; then
        log_success "Accès au repo confirmé"
    else
        log_error "Impossible d'accéder au repo $REPO_OWNER/$REPO_NAME"
        echo "Vérifiez:"
        echo "  - Le nom du repo est correct"
        echo "  - Vous avez accès au repo"
        echo "  - Le token a les permissions 'repo'"
        exit 1
    fi
}

# Déclencher le workflow
trigger_workflow() {
    log_info "Déclenchement du workflow $WORKFLOW_FILE sur la branche $BRANCH..."
    
    response=$(curl -s -X POST \
                   -H "Authorization: token $GITHUB_TOKEN" \
                   -H "Accept: application/vnd.github.v3+json" \
                   "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/actions/workflows/$WORKFLOW_FILE/dispatches" \
                   -d "{\"ref\":\"$BRANCH\"}")
    
    # GitHub Actions API retourne 204 en cas de succès
    if [ $? -eq 0 ]; then
        log_success "Workflow déclenché avec succès!"
        log_info "Le build devrait commencer dans quelques secondes..."
        return 0
    else
        log_error "Échec du déclenchement du workflow"
        echo "Response: $response"
        return 1
    fi
}

# Obtenir les runs récents
get_recent_runs() {
    curl -s -H "Authorization: token $GITHUB_TOKEN" \
            -H "Accept: application/vnd.github.v3+json" \
            "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/actions/runs?per_page=5" | \
        jq -r '.workflow_runs[] | select(.name == "Build Android APK & AAB (Optimized)") | "\(.id)|\(.status)|\(.conclusion)|\(.created_at)|\(.html_url)"'
}

# Afficher le statut des builds
show_build_status() {
    log_info "Statut des builds récents:"
    echo ""
    
    printf "%-12s %-15s %-15s %-20s %s\n" "ID" "Status" "Conclusion" "Created" "URL"
    printf "%-12s %-15s %-15s %-20s %s\n" "----" "------" "----------" "-------" "---"
    
    get_recent_runs | while IFS='|' read -r id status conclusion created_at url; do
        # Formater la date
        created_formatted=$(date -d "$created_at" '+%m/%d %H:%M' 2>/dev/null || echo "$created_at")
        
        # Couleur selon le statut
        case "$status" in
            "completed")
                if [ "$conclusion" = "success" ]; then
                    status_color="${GREEN}✅ $status${NC}"
                    conclusion_color="${GREEN}$conclusion${NC}"
                elif [ "$conclusion" = "failure" ]; then
                    status_color="${RED}❌ $status${NC}"
                    conclusion_color="${RED}$conclusion${NC}"
                else
                    status_color="${YELLOW}⚠️  $status${NC}"
                    conclusion_color="${YELLOW}$conclusion${NC}"
                fi
                ;;
            "in_progress")
                status_color="${BLUE}🔄 $status${NC}"
                conclusion_color="${BLUE}running${NC}"
                ;;
            "queued")
                status_color="${YELLOW}⏳ $status${NC}"
                conclusion_color="${YELLOW}pending${NC}"
                ;;
            *)
                status_color="$status"
                conclusion_color="$conclusion"
                ;;
        esac
        
        printf "%-12s %-25s %-25s %-20s %s\n" "$id" "$status_color" "$conclusion_color" "$created_formatted" "$url"
    done
    
    echo ""
}

# Surveiller un build en temps réel
watch_build() {
    log_info "Surveillance du build en cours..."
    log_info "Appuyez sur Ctrl+C pour arrêter la surveillance"
    
    while true; do
        clear
        echo "=== Surveillance des builds GitHub Actions ==="
        echo "Repo: $REPO_OWNER/$REPO_NAME"
        echo "Mis à jour: $(date)"
        echo ""
        
        show_build_status
        
        # Vérifier s'il y a des builds en cours
        running_builds=$(get_recent_runs | grep -E "(in_progress|queued)" | wc -l)
        
        if [ "$running_builds" -eq 0 ]; then
            log_info "Aucun build en cours. Arrêt de la surveillance."
            break
        fi
        
        sleep 30
    done
}

# Parser les arguments
WATCH_MODE=false
STATUS_ONLY=false
BUILD_TYPE="both"

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -t|--token)
            GITHUB_TOKEN="$2"
            shift 2
            ;;
        -r|--repo)
            if [[ "$2" =~ ^([^/]+)/([^/]+)$ ]]; then
                REPO_OWNER="${BASH_REMATCH[1]}"
                REPO_NAME="${BASH_REMATCH[2]}"
            else
                log_error "Format de repo invalide. Utilisez: owner/repo"
                exit 1
            fi
            shift 2
            ;;
        -b|--branch)
            BRANCH="$2"
            shift 2
            ;;
        -w|--watch)
            WATCH_MODE=true
            shift
            ;;
        -s|--status)
            STATUS_ONLY=true
            shift
            ;;
        apk|aab|both)
            BUILD_TYPE="$1"
            shift
            ;;
        *)
            log_error "Option inconnue: $1"
            show_help
            exit 1
            ;;
    esac
done

# Main
main() {
    echo "=== Script de déclenchement GitHub Actions ==="
    echo "Repo: $REPO_OWNER/$REPO_NAME"
    echo "Branche: $BRANCH"
    echo "Build Type: $BUILD_TYPE"
    echo ""
    
    # Vérifications
    check_dependencies
    check_github_token
    check_repo_access
    
    # Mode status seulement
    if [ "$STATUS_ONLY" = true ]; then
        show_build_status
        exit 0
    fi
    
    # Déclencher le workflow
    if trigger_workflow; then
        echo ""
        log_info "Build déclenché! Voici les liens utiles:"
        echo ""
        echo "📱 Actions: https://github.com/$REPO_OWNER/$REPO_NAME/actions"
        echo "📋 Workflow: https://github.com/$REPO_OWNER/$REPO_NAME/actions/workflows/$WORKFLOW_FILE"
        echo ""
        
        # Attendre un peu puis afficher le statut
        log_info "Attente de 10 secondes puis affichage du statut..."
        sleep 10
        show_build_status
        
        # Mode surveillance
        if [ "$WATCH_MODE" = true ]; then
            echo ""
            watch_build
        else
            echo ""
            log_info "Utilisez --watch pour surveiller le build en temps réel"
            log_info "Ou --status pour vérifier le statut plus tard"
        fi
    else
        exit 1
    fi
}

# Exporter les variables si elles sont définies
if [ ! -z "$GITHUB_TOKEN" ]; then
    export GITHUB_TOKEN
fi

# Lancer le script principal
main "$@"
