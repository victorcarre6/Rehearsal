#!/usr/bin/env bash

# Script d'installation pour Rehearsal
# Crée un lien symbolique pour rendre la commande 'rehearsal' accessible globalement

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="$SCRIPT_DIR/rehearsal.sh"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  Installation de Rehearsal${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Vérifier que le script existe
if [ ! -f "$SCRIPT_PATH" ]; then
    echo -e "${RED}✗ Erreur: rehearsal.sh non trouvé dans $SCRIPT_DIR${NC}"
    exit 1
fi

# Déterminer le répertoire bin de l'utilisateur
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    BIN_DIR="$HOME/.local/bin"
else
    # Linux
    BIN_DIR="$HOME/.local/bin"
fi

# Créer le répertoire bin s'il n'existe pas
mkdir -p "$BIN_DIR"

LINK_PATH="$BIN_DIR/rehearsal"

# Supprimer l'ancien lien s'il existe
if [ -L "$LINK_PATH" ]; then
    echo -e "${YELLOW}⚠ Suppression de l'ancien lien symbolique${NC}"
    rm "$LINK_PATH"
fi

# Créer le lien symbolique
ln -s "$SCRIPT_PATH" "$LINK_PATH"
chmod +x "$LINK_PATH"

echo -e "${GREEN}✓${NC} Lien symbolique créé: ${BLUE}$LINK_PATH${NC} -> ${BLUE}$SCRIPT_PATH${NC}"
echo ""

# Vérifier si le répertoire bin est dans le PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo -e "${YELLOW}⚠ Le répertoire $BIN_DIR n'est pas dans votre PATH${NC}"
    echo ""
    echo -e "Ajoutez cette ligne à votre fichier de configuration shell:"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    if [[ "$SHELL" == *"zsh"* ]]; then
        echo -e "${GREEN}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
        echo ""
        echo -e "Pour ${YELLOW}zsh${NC}, ajoutez à: ${BLUE}~/.zshrc${NC}"
        echo -e "Puis exécutez: ${YELLOW}source ~/.zshrc${NC}"
    elif [[ "$SHELL" == *"bash"* ]]; then
        echo -e "${GREEN}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
        echo ""
        if [[ "$OSTYPE" == "darwin"* ]]; then
            echo -e "Pour ${YELLOW}bash${NC} sur macOS, ajoutez à: ${BLUE}~/.bash_profile${NC} ou ${BLUE}~/.bashrc${NC}"
            echo -e "Puis exécutez: ${YELLOW}source ~/.bash_profile${NC}"
        else
            echo -e "Pour ${YELLOW}bash${NC}, ajoutez à: ${BLUE}~/.bashrc${NC}"
            echo -e "Puis exécutez: ${YELLOW}source ~/.bashrc${NC}"
        fi
    else
        echo -e "${GREEN}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
        echo ""
        echo -e "Ajoutez cette ligne à votre fichier de configuration shell et rechargez-le"
    fi

    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${YELLOW}Ou pour une installation temporaire (session actuelle uniquement):${NC}"
    echo -e "${GREEN}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
else
    echo -e "${GREEN}✓${NC} Le répertoire $BIN_DIR est déjà dans votre PATH"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Installation terminée!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "Vous pouvez maintenant lancer l'application avec la commande:"
echo -e "  ${GREEN}rehearsal${NC}"
echo ""
