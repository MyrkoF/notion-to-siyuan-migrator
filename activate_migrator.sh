#!/bin/bash
# Script pour activer rapidement l'environnement du migrator

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Activation de l'environnement Notion to SiYuan Migrator${NC}"
echo ""

# Activer le venv
if [ -d "./venv" ]; then
    source ./venv/bin/activate
    echo -e "${GREEN}✅ Virtual environment activé${NC}"
else
    echo "❌ Virtual environment introuvable. Lancez ./setup_migrator.sh d'abord"
    exit 1
fi

# Charger la config
if [ -f "$HOME/.notion_siyuan_migrator.env" ]; then
    source "$HOME/.notion_siyuan_migrator.env"
    echo -e "${GREEN}✅ Configuration chargée${NC}"
else
    echo "❌ Configuration introuvable. Lancez ./setup_migrator.sh d'abord"
    exit 1
fi

echo ""
echo "📊 Variables configurées:"
echo "   NOTION_TOKEN: ${NOTION_TOKEN:0:20}..."
echo "   SIYUAN_URL: $SIYUAN_URL"
echo "   SIYUAN_TOKEN: ${SIYUAN_TOKEN:0:20}..."
echo "   DRY_RUN: $DRY_RUN"
echo ""
echo "💡 Commandes disponibles:"
echo "   ${GREEN}python3 notion_to_siyuan_migrator.py${NC}    # Lancer la migration"
echo "   ${GREEN}python3 post_migration_processor.py${NC}     # Post-traitement"
echo "   ${GREEN}deactivate${NC}                               # Quitter le venv"
echo ""
