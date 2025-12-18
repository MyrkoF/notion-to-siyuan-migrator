#!/bin/bash
# Setup script pour Notion to SiYuan Migrator
# Configure automatiquement l'environnement

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Notion → SiYuan Migrator - Configuration Setup           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fichier de configuration
CONFIG_FILE="$HOME/.notion_siyuan_migrator.env"

# =============================================================================
# VÉRIFICATIONS PRÉALABLES
# =============================================================================

echo -e "${BLUE}[1/5] Vérification des prérequis...${NC}"

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 n'est pas installé${NC}"
    echo "   Installer avec: sudo apt install python3 python3-pip"
    exit 1
fi
echo -e "${GREEN}✅ Python 3 trouvé: $(python3 --version)${NC}"

# Vérifier pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip3 n'est pas installé${NC}"
    echo "   Installer avec: sudo apt install python3-pip"
    exit 1
fi
echo -e "${GREEN}✅ pip3 trouvé${NC}"

# Installer les dépendances
echo ""
echo -e "${BLUE}[2/5] Installation des dépendances Python...${NC}"
pip3 install --user requests pyyaml --quiet
echo -e "${GREEN}✅ Dépendances installées${NC}"

# =============================================================================
# CONFIGURATION NOTION
# =============================================================================

echo ""
echo -e "${BLUE}[3/5] Configuration Notion API${NC}"
echo ""
echo "Pour obtenir votre token Notion:"
echo "  1. Aller sur https://www.notion.so/my-integrations"
echo "  2. Cliquer 'New integration'"
echo "  3. Donner un nom (ex: 'SiYuan Migration')"
echo "  4. Copier le 'Internal Integration Token'"
echo "  5. IMPORTANT: Partager vos pages avec cette intégration"
echo ""

# Lire le token existant si disponible
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
fi

read -p "Notion Integration Token [${NOTION_TOKEN:0:20}...]: " notion_token_input
if [ -n "$notion_token_input" ]; then
    NOTION_TOKEN="$notion_token_input"
fi

if [ -z "$NOTION_TOKEN" ]; then
    echo -e "${RED}❌ Token Notion requis${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Token Notion configuré${NC}"

# =============================================================================
# CONFIGURATION SIYUAN
# =============================================================================

echo ""
echo -e "${BLUE}[4/5] Configuration SiYuan API${NC}"
echo ""
echo "Pour obtenir votre token SiYuan:"
echo "  1. Ouvrir SiYuan"
echo "  2. Aller dans Paramètres → À propos"
echo "  3. Copier le 'Token API'"
echo ""

read -p "URL SiYuan [${SIYUAN_URL:-http://192.168.1.11:6806}]: " siyuan_url_input
SIYUAN_URL="${siyuan_url_input:-${SIYUAN_URL:-http://192.168.1.11:6806}}"

read -p "Token SiYuan [${SIYUAN_TOKEN:0:20}...]: " siyuan_token_input
if [ -n "$siyuan_token_input" ]; then
    SIYUAN_TOKEN="$siyuan_token_input"
fi

if [ -z "$SIYUAN_TOKEN" ]; then
    echo -e "${RED}❌ Token SiYuan requis${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Token SiYuan configuré${NC}"

# =============================================================================
# TESTER LES CONNEXIONS
# =============================================================================

echo ""
echo -e "${BLUE}[5/5] Test des connexions API...${NC}"

# Test Notion
echo -n "  Testing Notion API... "
NOTION_TEST=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $NOTION_TOKEN" \
  -H "Notion-Version: 2022-06-28" \
  https://api.notion.com/v1/users/me)

if [ "$NOTION_TEST" = "200" ]; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ Échec (HTTP $NOTION_TEST)${NC}"
    echo "   Vérifier que le token est valide et que les pages sont partagées"
    exit 1
fi

# Test SiYuan
echo -n "  Testing SiYuan API... "
SIYUAN_TEST=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST \
  "$SIYUAN_URL/api/notebook/lsNotebooks" \
  -d '{}')

if [ "$SIYUAN_TEST" = "200" ]; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ Échec (HTTP $SIYUAN_TEST)${NC}"
    echo "   Vérifier que SiYuan est lancé et que l'URL/token sont corrects"
    exit 1
fi

# =============================================================================
# SAUVEGARDER LA CONFIGURATION
# =============================================================================

echo ""
echo "💾 Sauvegarde de la configuration dans $CONFIG_FILE..."

cat > "$CONFIG_FILE" << EOF
# Configuration Notion to SiYuan Migrator
# Généré le $(date)

export NOTION_TOKEN="$NOTION_TOKEN"
export SIYUAN_URL="$SIYUAN_URL"
export SIYUAN_TOKEN="$SIYUAN_TOKEN"

# Options de migration (optionnel - modifier si besoin)
export BATCH_SIZE=50
export DELAY_BETWEEN_CALLS=0.5
export DRY_RUN=false
EOF

chmod 600 "$CONFIG_FILE"  # Sécuriser le fichier
echo -e "${GREEN}✅ Configuration sauvegardée${NC}"

# =============================================================================
# AJOUTER AU .bashrc
# =============================================================================

if ! grep -q "notion_siyuan_migrator.env" "$HOME/.bashrc"; then
    echo "" >> "$HOME/.bashrc"
    echo "# Notion to SiYuan Migrator" >> "$HOME/.bashrc"
    echo "[ -f $CONFIG_FILE ] && source $CONFIG_FILE" >> "$HOME/.bashrc"
    echo -e "${GREEN}✅ Configuration ajoutée à .bashrc${NC}"
else
    echo -e "${YELLOW}⚠️  Configuration déjà présente dans .bashrc${NC}"
fi

# =============================================================================
# INSTRUCTIONS FINALES
# =============================================================================

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                   ✅ SETUP TERMINÉ !                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📝 Prochaines étapes:"
echo ""
echo "1. Recharger la configuration:"
echo "   ${GREEN}source $CONFIG_FILE${NC}"
echo ""
echo "2. Tester avec mode DRY_RUN:"
echo "   ${GREEN}export DRY_RUN=true${NC}"
echo "   ${GREEN}python3 notion_to_siyuan_migrator.py${NC}"
echo ""
echo "3. Lancer la migration complète:"
echo "   ${GREEN}export DRY_RUN=false${NC}"
echo "   ${GREEN}python3 notion_to_siyuan_migrator.py${NC}"
echo ""
echo "📊 Les résultats seront dans: ./migration_output/"
echo ""
echo "💡 Tips:"
echo "   - Commencer avec DRY_RUN=true pour tester"
echo "   - SiYuan créera un snapshot automatique avant import"
echo "   - Consulter README_MIGRATION.md pour plus d'infos"
echo ""

# Créer le dossier de sortie
mkdir -p migration_output
echo -e "${GREEN}✅ Dossier migration_output créé${NC}"

echo ""
echo "🚀 Tout est prêt ! Bonne migration !"
echo ""
