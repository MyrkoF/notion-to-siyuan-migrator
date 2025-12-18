#!/bin/bash
# Script pour créer et pousser le repo vers GitHub
# Usage: ./push_to_github.sh

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Notion to SiYuan Migrator - GitHub Setup              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Vérifier si on est dans le bon dossier
if [ ! -f "notion_to_siyuan_migrator.py" ]; then
    echo -e "${RED}❌ Erreur: Ce script doit être exécuté depuis le dossier du projet${NC}"
    exit 1
fi

echo -e "${BLUE}Ce script va:${NC}"
echo "  1. Créer un nouveau repo GitHub PRIVÉ"
echo "  2. Pousser tout le code sur la branche 'main'"
echo ""

# Demander le nom du repo
read -p "Nom du repo GitHub [notion-to-siyuan-migrator]: " repo_name
repo_name=${repo_name:-notion-to-siyuan-migrator}

# Demander le username GitHub
read -p "Votre username GitHub: " github_user

if [ -z "$github_user" ]; then
    echo -e "${RED}❌ Username GitHub requis${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}⚠️  Pour créer le repo, vous avez besoin d'un Personal Access Token GitHub${NC}"
echo "   Obtenir un token sur: https://github.com/settings/tokens"
echo "   Permissions requises: repo (full control)"
echo ""

read -sp "GitHub Personal Access Token: " github_token
echo ""

if [ -z "$github_token" ]; then
    echo -e "${RED}❌ Token GitHub requis${NC}"
    exit 1
fi

# =============================================================================
# CRÉER LE REPO GITHUB
# =============================================================================

echo ""
echo -e "${BLUE}[1/3] Création du repo GitHub privé...${NC}"

response=$(curl -s -w "\n%{http_code}" \
  -X POST \
  -H "Authorization: token $github_token" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d "{
    \"name\": \"$repo_name\",
    \"description\": \"Complete migration toolkit to transfer Notion workspace to SiYuan\",
    \"private\": true,
    \"auto_init\": false
  }")

http_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | head -n -1)

if [ "$http_code" = "201" ]; then
    echo -e "${GREEN}✅ Repo créé avec succès!${NC}"
    repo_url=$(echo "$body" | grep -o '"html_url": "[^"]*' | sed 's/"html_url": "//')
    echo -e "   ${BLUE}$repo_url${NC}"
elif [ "$http_code" = "422" ]; then
    echo -e "${YELLOW}⚠️  Le repo existe déjà, on continue...${NC}"
    repo_url="https://github.com/$github_user/$repo_name"
else
    echo -e "${RED}❌ Erreur lors de la création du repo (HTTP $http_code)${NC}"
    echo "$body"
    exit 1
fi

# =============================================================================
# CONFIGURER LE REMOTE
# =============================================================================

echo ""
echo -e "${BLUE}[2/3] Configuration du remote Git...${NC}"

# Retirer l'ancien remote s'il existe
git remote remove origin 2>/dev/null || true

# Ajouter le nouveau remote avec le token
git remote add origin "https://$github_token@github.com/$github_user/$repo_name.git"

echo -e "${GREEN}✅ Remote configuré${NC}"

# =============================================================================
# POUSSER VERS GITHUB
# =============================================================================

echo ""
echo -e "${BLUE}[3/3] Push vers GitHub...${NC}"

git push -u origin main

echo -e "${GREEN}✅ Code poussé vers GitHub!${NC}"

# =============================================================================
# NETTOYER LE TOKEN DU REMOTE
# =============================================================================

echo ""
echo -e "${BLUE}Sécurisation du remote (retrait du token)...${NC}"

git remote set-url origin "https://github.com/$github_user/$repo_name.git"

echo -e "${GREEN}✅ Token retiré du remote${NC}"

# =============================================================================
# RÉSUMÉ
# =============================================================================

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                 ✅ REPO CRÉÉ AVEC SUCCÈS !                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}🎉 Votre repo est prêt:${NC}"
echo -e "   ${BLUE}$repo_url${NC}"
echo ""
echo "📝 Prochaines étapes:"
echo ""
echo "1. Visitez le repo:"
echo "   ${GREEN}$repo_url${NC}"
echo ""
echo "2. (Optionnel) Ajoutez une description et topics:"
echo "   - Topics suggérés: notion, siyuan, migration, python"
echo ""
echo "3. (Optionnel) Activez GitHub Pages pour la doc:"
echo "   Settings → Pages → Source: main branch → /docs"
echo ""
echo "4. Clonez sur d'autres machines avec:"
echo "   ${GREEN}git clone https://github.com/$github_user/$repo_name.git${NC}"
echo ""
echo "💡 Pour pousser des futures modifications:"
echo "   ${GREEN}git add .${NC}"
echo "   ${GREEN}git commit -m \"Description du changement\"${NC}"
echo "   ${GREEN}git push${NC}"
echo ""

# Sauvegarder l'URL du repo pour référence
echo "https://github.com/$github_user/$repo_name.git" > .git/GITHUB_URL

echo -e "${GREEN}✅ Setup terminé !${NC}"
echo ""
