#!/bin/bash

# Script de diagnostic réseau pour le build Android
# Utilise par le workflow GitHub Actions

set -e

echo "🌐 === DIAGNOSTIC RESEAU COMPLET ==="
echo "Timestamp: $(date)"
echo ""

# Test de connectivité de base
echo "� 1. TEST DE CONNECTIVITE DE BASE"
echo "------------------------------------"

# Test des serveurs DNS
DNS_SERVERS=("8.8.8.8" "1.1.1.1" "208.67.222.222")
echo "Testing DNS servers..."
for server in "${DNS_SERVERS[@]}"; do
    if ping -c 2 -W 5 "$server" >/dev/null 2>&1; then
        echo "✅ DNS $server: OK"
    else
        echo "❌ DNS $server: FAIL"
    fi
done

echo ""

# Test de résolution DNS
echo "🔍 2. TEST DE RESOLUTION DNS"
echo "-----------------------------"

DOMAINS=("github.com" "download.savannah.gnu.org" "sourceforge.net" "openssl.org")
echo "Testing domain resolution..."
for domain in "${DOMAINS[@]}"; do
    if nslookup "$domain" >/dev/null 2>&1; then
        echo "✅ DNS resolve $domain: OK"
    else
        echo "❌ DNS resolve $domain: FAIL"
    fi
done

echo ""

# Test de connectivité HTTP/HTTPS
echo "🔍 3. TEST DE CONNECTIVITE HTTP/HTTPS"
echo "-------------------------------------"

URLS=(
    "https://github.com"
    "https://download.savannah.gnu.org"
    "https://sourceforge.net"
    "https://www.openssl.org"
)

echo "Testing HTTP/HTTPS connectivity..."
for url in "${URLS[@]}"; do
    if curl -L --connect-timeout 10 --max-time 20 -s "$url" >/dev/null 2>&1; then
        echo "✅ HTTP $url: OK"
    else
        echo "❌ HTTP $url: FAIL"
    fi
done

echo ""

# Test spécifique des URLs de téléchargement
echo "🔍 4. TEST DES URLS DE DEPENDANCES"
echo "----------------------------------"

DEPENDENCY_URLS=(
    "https://download.savannah.gnu.org/releases/freetype/freetype-2.10.1.tar.gz"
    "https://github.com/libffi/libffi/archive/v3.4.2.tar.gz"
    "https://www.openssl.org/source/openssl-1.1.1w.tar.gz"
    "https://sourceforge.net/projects/libpng/files/libpng16/1.6.37/libpng-1.6.37.tar.xz"
)

echo "Testing dependency download URLs..."
for url in "${DEPENDENCY_URLS[@]}"; do
    echo "  Testing: $url"
    
    # Test avec curl
    if curl -L --connect-timeout 10 --max-time 20 -I "$url" 2>/dev/null | grep -q "200 OK"; then
        echo "  ✅ CURL: OK"
    else
        echo "  ❌ CURL: FAIL"
    fi
    
    # Test avec wget
    if wget -q --timeout=10 --tries=1 --spider "$url" 2>/dev/null; then
        echo "  ✅ WGET: OK"
    else
        echo "  ❌ WGET: FAIL"
    fi
    
    echo ""
done

# Test des certificats SSL
echo "🔍 5. TEST DES CERTIFICATS SSL"
echo "------------------------------"

SSL_HOSTS=("github.com" "download.savannah.gnu.org" "sourceforge.net" "openssl.org")
echo "Testing SSL certificates..."
for host in "${SSL_HOSTS[@]}"; do
    if echo | openssl s_client -connect "$host:443" -servername "$host" 2>/dev/null | grep -q "Verify return code: 0"; then
        echo "✅ SSL $host: OK"
    else
        echo "❌ SSL $host: FAIL"
    fi
done

echo ""

# Informations système
echo "🔍 6. INFORMATIONS SYSTEME"
echo "--------------------------"

echo "System info:"
echo "  OS: $(uname -s)"
echo "  Kernel: $(uname -r)"
echo "  Architecture: $(uname -m)"
echo "  Hostname: $(hostname)"
echo "  User: $(whoami)"

echo ""

echo "Network configuration:"
echo "  Default route: $(ip route show default 2>/dev/null || route -n get default 2>/dev/null || echo 'Unknown')"
echo "  DNS servers: $(cat /etc/resolv.conf 2>/dev/null | grep nameserver || echo 'Unknown')"
echo "  Network interfaces:"
ip addr show 2>/dev/null | grep -E "(inet|UP|DOWN)" | head -10 || ifconfig 2>/dev/null | grep -E "(inet|UP|DOWN)" | head -10 || echo "Cannot determine network interfaces"

echo ""

# Test de variables d'environnement
echo "🔍 7. VARIABLES D'ENVIRONNEMENT"
echo "-------------------------------"

ENV_VARS=(
    "HTTP_PROXY"
    "HTTPS_PROXY"
    "NO_PROXY"
    "PYTHONHTTPSVERIFY"
    "REQUESTS_CA_BUNDLE"
    "CURL_CA_BUNDLE"
)

echo "Environment variables:"
for var in "${ENV_VARS[@]}"; do
    value="${!var}"
    if [ -n "$value" ]; then
        echo "  $var=$value"
    else
        echo "  $var=<not set>"
    fi
done

echo ""

# Test des outils de téléchargement
echo "🔍 8. OUTILS DE TELECHARGEMENT"
echo "------------------------------"

echo "Available tools:"
echo "  curl: $(which curl 2>/dev/null || echo 'Not found')"
echo "  wget: $(which wget 2>/dev/null || echo 'Not found')"
echo "  python: $(which python 2>/dev/null || echo 'Not found')"
echo "  pip: $(which pip 2>/dev/null || echo 'Not found')"

if command -v curl >/dev/null 2>&1; then
    echo "  curl version: $(curl --version | head -1)"
fi

if command -v wget >/dev/null 2>&1; then
    echo "  wget version: $(wget --version | head -1)"
fi

echo ""

# Test du cache buildozer
echo "🔍 9. CACHE BUILDOZER"
echo "--------------------"

echo "Cache directories:"
echo "  ~/.buildozer: $(ls -la ~/.buildozer 2>/dev/null | wc -l) items"
echo "  ~/.cache/python-for-android: $(ls -la ~/.cache/python-for-android 2>/dev/null | wc -l) items"
echo "  ~/.buildozer/android/packages: $(ls -la ~/.buildozer/android/packages 2>/dev/null | wc -l) items"

echo ""

echo "Cache sizes:"
echo "  ~/.buildozer: $(du -sh ~/.buildozer 2>/dev/null || echo '0B')"
echo "  ~/.cache/python-for-android: $(du -sh ~/.cache/python-for-android 2>/dev/null || echo '0B')"
echo "  ~/.buildozer/android/packages: $(du -sh ~/.buildozer/android/packages 2>/dev/null || echo '0B')"

echo ""

# Fin du diagnostic
echo "🏁 === FIN DU DIAGNOSTIC ==="
echo "Timestamp: $(date)"

# 3. Test de téléchargement
echo ""
echo "📥 Test de téléchargement"
echo "------------------------"

# URLs critiques pour buildozer
DOWNLOAD_URLS=(
    "https://download.savannah.gnu.org/releases/freetype/freetype-2.10.1.tar.gz"
    "https://pypi.org/simple/"
    "https://github.com/kivy/python-for-android/archive/master.zip"
)

for url in "${DOWNLOAD_URLS[@]}"; do
    echo "  Testing: $(basename "$url")"
    
    # Test avec curl
    if curl -s --connect-timeout 10 --max-time 30 -I "$url" >/dev/null 2>&1; then
        echo "    ✅ Curl: OK"
    else
        echo "    ❌ Curl: Échec"
    fi
    
    # Test avec wget
    if wget -q --timeout=10 --tries=1 --spider "$url" 2>/dev/null; then
        echo "    ✅ Wget: OK"
    else
        echo "    ❌ Wget: Échec"
    fi
done

# 4. Variables d'environnement réseau
echo ""
echo "🔧 Variables d'environnement réseau"
echo "-----------------------------------"

ENV_VARS=(
    "http_proxy"
    "https_proxy"
    "HTTP_PROXY"
    "HTTPS_PROXY"
    "no_proxy"
    "NO_PROXY"
    "REQUESTS_CA_BUNDLE"
    "CURL_CA_BUNDLE"
    "PYTHONHTTPSVERIFY"
)

for var in "${ENV_VARS[@]}"; do
    value="${!var}"
    if [ -n "$value" ]; then
        echo "  $var=$value"
    else
        echo "  $var: Non défini"
    fi
done

# 5. Configuration système
echo ""
echo "⚙️ Configuration système"
echo "------------------------"

echo "  OS: $(uname -a)"
echo "  Python: $(python --version 2>&1)"
echo "  Curl: $(curl --version 2>&1 | head -1)"
echo "  Wget: $(wget --version 2>&1 | head -1)"

# Vérifier les certificats SSL
if [ -d "/etc/ssl/certs" ]; then
    cert_count=$(ls /etc/ssl/certs/*.pem 2>/dev/null | wc -l)
    echo "  Certificats SSL: $cert_count trouvés"
else
    echo "  Certificats SSL: Répertoire non trouvé"
fi

# 6. Solutions recommandées
echo ""
echo "💡 Solutions recommandées"
echo "========================="

echo "1. Variables d'environnement pour contourner SSL:"
echo "   export PYTHONHTTPSVERIFY=0"
echo "   export REQUESTS_CA_BUNDLE=''"
echo "   export CURL_CA_BUNDLE=''"

echo ""
echo "2. Configuration wget (~/.wgetrc):"
echo "   check_certificate = off"
echo "   timeout = 30"
echo "   tries = 3"

echo ""
echo "3. Configuration curl (~/.curlrc):"
echo "   --insecure"
echo "   --connect-timeout 30"
echo "   --max-time 300"

echo ""
echo "4. Retry avec délais:"
echo "   for i in {1..3}; do"
echo "     buildozer android debug && break"
echo "     sleep \$((i * 30))"
echo "   done"

# 7. Test de buildozer spécifique
echo ""
echo "🏗️ Test spécifique buildozer"
echo "----------------------------"

if command -v buildozer >/dev/null 2>&1; then
    echo "  Buildozer: $(buildozer --version 2>&1)"
    
    if [ -f "buildozer.spec" ]; then
        echo "  buildozer.spec: Trouvé"
        
        # Vérifier les requirements
        requirements=$(grep "^requirements" buildozer.spec | cut -d'=' -f2)
        echo "  Requirements: $requirements"
    else
        echo "  buildozer.spec: Non trouvé"
    fi
else
    echo "  Buildozer: Non installé"
fi

# 8. Statistiques réseau
echo ""
echo "📊 Statistiques réseau"
echo "======================

# Afficher les interfaces réseau
echo "Interfaces réseau:"
ip addr show 2>/dev/null || ifconfig 2>/dev/null || echo "Impossible d'afficher les interfaces"

echo ""
echo "Routes:"
ip route show 2>/dev/null || route -n 2>/dev/null || echo "Impossible d'afficher les routes"

# 9. Recommandations finales
echo ""
echo "🎯 Recommandations finales"
echo "=========================="

# Compter les succès
success_count=0
total_tests=0

for server in "${SERVERS[@]}"; do
    total_tests=$((total_tests + 1))
    if ping -c 1 -W 2 "$server" >/dev/null 2>&1; then
        success_count=$((success_count + 1))
    fi
done

success_rate=$((success_count * 100 / total_tests))

echo "Taux de succès de connectivité: $success_rate% ($success_count/$total_tests)"

if [ $success_rate -lt 50 ]; then
    echo "❌ Connectivité très dégradée - Build probable d'échouer"
    echo "💡 Suggestions:"
    echo "  - Réessayer plus tard"
    echo "  - Utiliser un cache complet"
    echo "  - Configurer un proxy si disponible"
elif [ $success_rate -lt 80 ]; then
    echo "⚠️ Connectivité dégradée - Utiliser les retry et timeouts"
    echo "💡 Suggestions:"
    echo "  - Augmenter les timeouts"
    echo "  - Utiliser les mécanismes de retry"
    echo "  - Pré-télécharger les dépendances si possible"
else
    echo "✅ Connectivité correcte - Build devrait fonctionner"
fi

echo ""
echo "✅ Diagnostic terminé"
