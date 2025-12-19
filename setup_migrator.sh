#!/bin/bash
# Setup script pour Notion to SiYuan Migrator
# Configure automatiquement l'environnement avec virtual environment

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
VENV_DIR="./venv"

# =============================================================================
# VÉRIFICATIONS PRÉALABLES
# =============================================================================

echo -e "${BLUE}[1/6] Vérification des prérequis...${NC}"

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 n'est pas installé${NC}"
    echo "   Installer avec: sudo apt install python3 python3-venv"
    exit 1
fi
echo -e "${GREEN}✅ Python 3 trouvé: $(python3 --version)${NC}"

# Vérifier python3-venv
if ! python3 -m venv --help &> /dev/null; then
    echo -e "${RED}❌ python3-venv n'est pas installé${NC}"
    echo "   Installer avec: sudo apt install python3-venv"
    exit 1
fi
echo -e "${GREEN}✅ python3-venv disponible${NC}"

# =============================================================================
# CRÉATION ET ACTIVATION DU VIRTUAL ENVIRONMENT
# =============================================================================

echo ""
echo -e "${BLUE}[2/6] Configuration de l'environnement virtuel Python...${NC}"

if [ -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}⚠️  Environnement virtuel existant détecté${NC}"
    read -p "Voulez-vous le recréer ? (y/N): " recreate
    if [ "$recreate" = "y" ]; then
        rm -rf "$VENV_DIR"
        echo "   Suppression de l'ancien venv..."
    fi
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "   Création du virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}✅ Virtual environment créé${NC}"
else
    echo -e "${GREEN}✅ Virtual environment déjà présent${NC}"
fi

# Activer le venv
source "$VENV_DIR/bin/activate"
echo -e "${GREEN}✅ Virtual environment activé${NC}"

# =============================================================================
# INSTALLATION DES DÉPENDANCES
# =============================================================================

echo ""
echo -e "${BLUE}[3/6] Installation des dépendances Python...${NC}"

# Upgrade pip silencieusement
pip install --upgrade pip --quiet 2>/dev/null || true

# Installer les dépendances
pip install requests pyyaml --quiet
echo -e "${GREEN}✅ Dépendances installées (requests, pyyaml)${NC}"

# Vérifier les installations
echo "   Packages installés:"
pip list | grep -E "requests|PyYAML" | sed 's/^/     - /'

# =============================================================================
# CONFIGURATION NOTION
# =============================================================================

echo ""
echo -e "${BLUE}[4/6] Configuration Notion API${NC}"
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
echo -e "${BLUE}[5/6] Configuration SiYuan API${NC}"
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
echo -e "${BLUE}[6/6] Test des connexions API...${NC}"

# Test Notion
echo -n "  Testing Notion API... "
NOTION_TEST=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $NOTION_TOKEN" \
  -H "Notion-Version: 2022-06-28" \
  https://api.notion.com/v1/users/me 2>/dev/null || echo "000")

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
  -d '{}' 2>/dev/null || echo "000")

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
# CRÉER UN SCRIPT D'ACTIVATION
# =============================================================================

echo ""
echo "📝 Création d'un script d'activation rapide..."

cat > "./activate_migrator.sh" << 'ACTIVATESCRIPT'
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
ACTIVATESCRIPT

chmod +x "./activate_migrator.sh"
echo -e "${GREEN}✅ Script d'activation créé: ./activate_migrator.sh${NC}"

# =============================================================================
# AJOUTER AU .bashrc
# =============================================================================

if ! grep -q "notion_siyuan_migrator.env" "$HOME/.bashrc" 2>/dev/null; then
    echo "" >> "$HOME/.bashrc"
    echo "# Notion to SiYuan Migrator (optionnel - commenter si non désiré)" >> "$HOME/.bashrc"
    echo "# [ -f $CONFIG_FILE ] && source $CONFIG_FILE" >> "$HOME/.bashrc"
    echo -e "${GREEN}✅ Configuration ajoutée à .bashrc (commentée)${NC}"
else
    echo -e "${YELLOW}⚠️  Configuration déjà présente dans .bashrc${NC}"
fi

# =============================================================================
# CRÉER LE DOSSIER DE SORTIE
# =============================================================================

mkdir -p migration_output
echo -e "${GREEN}✅ Dossier migration_output créé${NC}"

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
echo "1. L'environnement est DÉJÀ ACTIVÉ dans ce terminal !"
echo "   (Vous voyez '(venv)' au début de votre prompt)"
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
echo "💡 Pour les prochaines sessions:"
echo "   ${GREEN}cd $(pwd)${NC}"
echo "   ${GREEN}source ./activate_migrator.sh${NC}"
echo "   ${GREEN}python3 notion_to_siyuan_migrator.py${NC}"
echo ""
echo "🔧 Pour quitter le virtual environment:"
echo "   ${GREEN}deactivate${NC}"
echo ""
echo "🚀 Tout est prêt ! Lancez directement:"
echo "   ${GREEN}python3 notion_to_siyuan_migrator.py${NC}"
echo ""
