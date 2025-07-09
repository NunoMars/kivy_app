#!/bin/bash
# Script d'installation et configuration pour WSL2/Ubuntu
# À exécuter dans WSL2 pour configurer l'environnement GitHub Actions

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

echo "=== Configuration WSL2 pour GitHub Actions ==="
echo ""

# Mettre à jour le système
log_info "Mise à jour du système..."
sudo apt-get update -qq
sudo apt-get upgrade -y

# Installer les outils nécessaires
log_info "Installation des outils requis..."
sudo apt-get install -y \
    curl \
    jq \
    git \
    wget \
    unzip \
    build-essential \
    ca-certificates \
    gnupg \
    lsb-release

# Installer GitHub CLI (optionnel mais utile)
log_info "Installation de GitHub CLI..."
type -p curl >/dev/null || sudo apt install curl -y
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
&& sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
&& sudo apt update \
&& sudo apt install gh -y

# Configurer Git si nécessaire
log_info "Configuration Git..."
if [ -z "$(git config --global user.name)" ]; then
    echo -n "Nom d'utilisateur Git: "
    read git_name
    git config --global user.name "$git_name"
fi

if [ -z "$(git config --global user.email)" ]; then
    echo -n "Email Git: "
    read git_email
    git config --global user.email "$git_email"
fi

log_success "Git configuré avec:"
echo "  Nom: $(git config --global user.name)"
echo "  Email: $(git config --global user.email)"

# Créer le répertoire des scripts
SCRIPT_DIR="$HOME/kivy_app_scripts"
mkdir -p "$SCRIPT_DIR"

# Copier les scripts dans le répertoire home
log_info "Installation des scripts dans $SCRIPT_DIR..."

# Si on est dans le repo, copier les scripts
if [ -f "scripts/trigger-github-build.sh" ]; then
    cp scripts/trigger-github-build.sh "$SCRIPT_DIR/"
    chmod +x "$SCRIPT_DIR/trigger-github-build.sh"
    log_success "Script trigger-github-build.sh installé"
fi

# Créer un script de configuration du token
cat > "$SCRIPT_DIR/setup-github-token.sh" << 'EOF'
#!/bin/bash
echo "=== Configuration du token GitHub ==="
echo ""
echo "1. Allez sur: https://github.com/settings/tokens"
echo "2. Cliquez 'Generate new token (classic)'"
echo "3. Sélectionnez les permissions suivantes:"
echo "   - repo (Full control of private repositories)"
echo "   - workflow (Update GitHub Action workflows)"
echo "4. Copiez le token généré"
echo ""
echo -n "Collez votre token GitHub: "
read -s github_token
echo ""

# Ajouter au .bashrc
if ! grep -q "GITHUB_TOKEN" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# GitHub Token for Actions" >> ~/.bashrc
    echo "export GITHUB_TOKEN=\"$github_token\"" >> ~/.bashrc
    echo "✅ Token ajouté à ~/.bashrc"
else
    # Remplacer le token existant
    sed -i "s/export GITHUB_TOKEN=.*/export GITHUB_TOKEN=\"$github_token\"/" ~/.bashrc
    echo "✅ Token mis à jour dans ~/.bashrc"
fi

# Exporter pour la session actuelle
export GITHUB_TOKEN="$github_token"

echo ""
echo "Token configuré! Rechargez votre terminal ou tapez:"
echo "  source ~/.bashrc"
EOF

chmod +x "$SCRIPT_DIR/setup-github-token.sh"

# Créer un script de raccourcis
cat > "$SCRIPT_DIR/kivy-build.sh" << 'EOF'
#!/bin/bash
# Script de raccourcis pour les builds Kivy

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

case "$1" in
    "apk")
        echo "🚀 Lancement du build APK..."
        "$SCRIPT_DIR/trigger-github-build.sh" --watch apk
        ;;
    "aab")
        echo "🚀 Lancement du build AAB..."
        "$SCRIPT_DIR/trigger-github-build.sh" --watch aab
        ;;
    "both"|"")
        echo "🚀 Lancement des builds APK + AAB..."
        "$SCRIPT_DIR/trigger-github-build.sh" --watch both
        ;;
    "status")
        echo "📊 Vérification du statut..."
        "$SCRIPT_DIR/trigger-github-build.sh" --status
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [apk|aab|both|status|help]"
        echo ""
        echo "Commandes:"
        echo "  apk     - Build APK seulement"
        echo "  aab     - Build AAB seulement"
        echo "  both    - Build APK + AAB (défaut)"
        echo "  status  - Vérifier le statut des builds"
        echo "  help    - Afficher cette aide"
        ;;
    *)
        echo "❌ Commande inconnue: $1"
        echo "Utilisez: $0 help"
        exit 1
        ;;
esac
EOF

chmod +x "$SCRIPT_DIR/kivy-build.sh"

# Ajouter les scripts au PATH
if ! grep -q "$SCRIPT_DIR" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# Kivy App Scripts" >> ~/.bashrc
    echo "export PATH=\"$SCRIPT_DIR:\$PATH\"" >> ~/.bashrc
    log_success "Scripts ajoutés au PATH"
fi

# Créer des alias pratiques
if ! grep -q "alias kivy-build" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# Kivy App Aliases" >> ~/.bashrc
    echo "alias kivy-build='$SCRIPT_DIR/kivy-build.sh'" >> ~/.bashrc
    echo "alias kivy-status='$SCRIPT_DIR/trigger-github-build.sh --status'" >> ~/.bashrc
    echo "alias kivy-apk='$SCRIPT_DIR/kivy-build.sh apk'" >> ~/.bashrc
    echo "alias kivy-aab='$SCRIPT_DIR/kivy-build.sh aab'" >> ~/.bashrc
    log_success "Alias ajoutés"
fi

# Instructions finales
echo ""
log_success "Installation terminée!"
echo ""
echo "🔧 Configuration requise:"
echo "  1. Configurez votre token GitHub:"
echo "     $SCRIPT_DIR/setup-github-token.sh"
echo ""
echo "  2. Rechargez votre terminal:"
echo "     source ~/.bashrc"
echo ""
echo "📱 Utilisation:"
echo "  kivy-build          # Build APK + AAB avec surveillance"
echo "  kivy-build apk      # Build APK seulement"
echo "  kivy-build aab      # Build AAB seulement"
echo "  kivy-status         # Vérifier le statut des builds"
echo ""
echo "📋 Scripts disponibles dans $SCRIPT_DIR:"
echo "  - trigger-github-build.sh  # Script principal"
echo "  - setup-github-token.sh    # Configuration du token"
echo "  - kivy-build.sh            # Raccourcis de build"
echo ""
echo "🌐 URLs utiles:"
echo "  - Actions: https://github.com/NunoMars/kivy_app/actions"
echo "  - Tokens: https://github.com/settings/tokens"
echo ""
log_warning "N'oubliez pas de configurer votre token GitHub!"
