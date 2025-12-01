#!/usr/bin/env bash

# Rehearsal - Script de lancement pour l'outil de révision interactive
# Ce script démarre un serveur HTTP local et ouvre le navigateur

set -e

# Couleurs pour l'affichage
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Déterminer le répertoire du script (en suivant les liens symboliques)
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  SCRIPT_DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$SCRIPT_DIR/$SOURCE"
done
SCRIPT_DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"

# Port par défaut
PORT=${REHEARSAL_PORT:-8080}

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  Rehearsal - Révision Interactive${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Vérifier si le port est déjà utilisé
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠ Le port $PORT est déjà utilisé. Tentative avec un port alternatif...${NC}"
    PORT=$((PORT + 1))
fi

echo -e "${GREEN}✓${NC} Démarrage du serveur sur le port ${GREEN}$PORT${NC}"
echo -e "${GREEN}✓${NC} Répertoire: ${BLUE}$SCRIPT_DIR${NC}"
echo ""
echo -e "${YELLOW}➜${NC} Ouverture du navigateur: ${BLUE}http://localhost:$PORT${NC}"
echo ""
echo -e "${YELLOW}Appuyez sur Ctrl+C pour arrêter le serveur${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Fonction pour ouvrir le navigateur selon l'OS
open_browser() {
    local url=$1

    # Petit délai pour laisser le serveur démarrer
    sleep 1

    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        open "$url" 2>/dev/null
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v xdg-open &> /dev/null; then
            xdg-open "$url" 2>/dev/null
        elif command -v gnome-open &> /dev/null; then
            gnome-open "$url" 2>/dev/null
        elif command -v firefox &> /dev/null; then
            firefox "$url" 2>/dev/null &
        elif command -v chromium-browser &> /dev/null; then
            chromium-browser "$url" 2>/dev/null &
        elif command -v google-chrome &> /dev/null; then
            google-chrome "$url" 2>/dev/null &
        else
            echo -e "${YELLOW}⚠ Impossible d'ouvrir automatiquement le navigateur${NC}"
            echo -e "Ouvrez manuellement: ${BLUE}$url${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ Système d'exploitation non reconnu${NC}"
        echo -e "Ouvrez manuellement: ${BLUE}$url${NC}"
    fi
}

# Démarrer le serveur HTTP et ouvrir le navigateur en arrière-plan
cd "$SCRIPT_DIR"

# Vérifier que index.html existe
if [ ! -f "index.html" ]; then
    echo -e "${RED}✗ Erreur: index.html non trouvé dans $SCRIPT_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Fichiers trouvés: index.html, questions.json"
echo ""

# Ouvrir le navigateur en arrière-plan avec index.html
open_browser "http://localhost:$PORT/index.html" &

# Vérifier si Python 3 est disponible
if command -v python3 &> /dev/null; then
    python3 -m http.server $PORT
elif command -v python &> /dev/null; then
    python -m http.server $PORT
else
    echo -e "${YELLOW}⚠ Python n'est pas installé. Installation de Python requise.${NC}"
    exit 1
fi
