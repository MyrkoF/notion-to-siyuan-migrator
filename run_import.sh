#!/bin/bash
# Script de lancement de l'import

cd "$(dirname "$0")"

# Charger les variables d'environnement
if [ -f ~/.notion_siyuan_migrator.env ]; then
    source ~/.notion_siyuan_migrator.env
elif [ -f .env ]; then
    set -a
    source .env
    set +a
else
    echo "❌ Fichier .env introuvable"
    exit 1
fi

# Vérifier les variables essentielles
if [ -z "$NOTION_TOKEN" ]; then
    echo "❌ NOTION_TOKEN non défini dans .env"
    exit 1
fi

if [ -z "$SIYUAN_TOKEN" ]; then
    echo "❌ SIYUAN_TOKEN non défini dans .env"
    exit 1
fi

echo "✅ Variables chargées"
echo "   NOTION_TOKEN: ${NOTION_TOKEN:0:10}..."
echo "   SIYUAN_TOKEN: ${SIYUAN_TOKEN:0:10}..."
echo "   SIYUAN_URL: $SIYUAN_URL"
echo ""

# Activer le venv
source venv/bin/activate

# Lancer le script d'import
python3 import_data_to_siyuan.py
