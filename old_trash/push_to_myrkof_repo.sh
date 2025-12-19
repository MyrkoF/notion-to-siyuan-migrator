#!/bin/bash
# Push rapide vers ton repo GitHub MyrkoF/notion-to-siyuan-migrator

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Push vers GitHub - notion-to-siyuan-migrator          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}Repo cible:${NC} https://github.com/MyrkoF/notion-to-siyuan-migrator"
echo ""

# Vérifier qu'on est dans le bon dossier
if [ ! -f "notion_to_siyuan_migrator.py" ]; then
    echo "❌ Erreur: Ce script doit être exécuté depuis /home/claude/"
    exit 1
fi

# Afficher l'état actuel
echo -e "${BLUE}[1/3] État du repo local:${NC}"
git status --short
echo ""

# Afficher les commits à pousser
echo -e "${BLUE}[2/3] Commits à pousser:${NC}"
git log --oneline origin/main..HEAD 2>/dev/null || git log --oneline
echo ""

# Demander confirmation
echo -e "${YELLOW}Prêt à pousser vers GitHub ?${NC}"
read -p "Continuer ? (y/N): " confirm

if [ "$confirm" != "y" ]; then
    echo "❌ Annulé"
    exit 0
fi

# Push
echo ""
echo -e "${BLUE}[3/3] Push en cours...${NC}"

if git push -u origin main 2>&1; then
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                 ✅ PUSH RÉUSSI !                           ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo -e "${GREEN}🎉 Ton code est maintenant sur GitHub :${NC}"
    echo -e "   ${BLUE}https://github.com/MyrkoF/notion-to-siyuan-migrator${NC}"
    echo ""
    echo "📝 Prochaines étapes:"
    echo ""
    echo "1. Vérifie que le repo est PRIVÉ 🔒"
    echo "   https://github.com/MyrkoF/notion-to-siyuan-migrator/settings"
    echo ""
    echo "2. Ajoute une description et des topics:"
    echo "   - Description: Complete migration toolkit for Notion to SiYuan"
    echo "   - Topics: notion, siyuan, migration, python, note-taking"
    echo ""
    echo "3. (Optionnel) Crée une Release v1.0.0"
    echo ""
else
    echo ""
    echo "❌ Erreur lors du push"
    echo ""
    echo "💡 Solutions possibles:"
    echo ""
    echo "1. Authentification requise:"
    echo "   git push utilise HTTPS, tu as besoin de t'authentifier"
    echo ""
    echo "   Option A - Personal Access Token (recommandé):"
    echo "   git remote set-url origin https://TOKEN@github.com/MyrkoF/notion-to-siyuan-migrator.git"
    echo "   git push -u origin main"
    echo ""
    echo "   Option B - SSH (si configuré):"
    echo "   git remote set-url origin git@github.com:MyrkoF/notion-to-siyuan-migrator.git"
    echo "   git push -u origin main"
    echo ""
    echo "   Option C - Credential helper:"
    echo "   git config --global credential.helper store"
    echo "   git push -u origin main  # Te demandera user/password une fois"
    echo ""
    exit 1
fi
