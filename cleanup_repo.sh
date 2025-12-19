#!/bin/bash
# Script de nettoyage du repo - Déplace les fichiers obsolètes vers old_trash/

cd "$(dirname "$0")"

echo "🧹 Nettoyage du repo notion-to-siyuan-migrator"
echo ""

# Créer old_trash si nécessaire
mkdir -p old_trash

# Fichiers Python obsolètes
echo "📦 Déplacement des scripts obsolètes..."
mv -v notion_to_siyuan_complete.py old_trash/ 2>/dev/null
mv -v extract_para_databases.py old_trash/ 2>/dev/null
mv -v generate_creation_guide.py old_trash/ 2>/dev/null
mv -v test_siyuan_apis.py old_trash/ 2>/dev/null
mv -v debug_notion_permissions.py old_trash/ 2>/dev/null
mv -v analyze_notion_databases.py old_trash/ 2>/dev/null
mv -v notion_to_siyuan_migrator.py old_trash/ 2>/dev/null
mv -v post_migration_processor.py old_trash/ 2>/dev/null

# Fichiers shell de debug
mv -v test_siyuan_connection.sh old_trash/ 2>/dev/null
mv -v push_to_myrkof_repo.sh old_trash/ 2>/dev/null

# Anciennes docs
echo ""
echo "📚 Déplacement des docs obsolètes..."
mv -v GUIDE_MIGRATION_COMPLETE.md old_trash/ 2>/dev/null
mv -v GUIDE_VRAI_MIGRATOR.md old_trash/ 2>/dev/null
mv -v PLAN_ACTION_PARA.md old_trash/ 2>/dev/null
mv -v README_MIGRATION.md old_trash/ 2>/dev/null

# Ancien JSON
mv -v notion_databases_analysis.json old_trash/ 2>/dev/null

echo ""
echo "✅ Nettoyage terminé !"
echo ""
echo "📂 Structure après nettoyage:"
echo ""
ls -lh | grep -E "\.py$|\.md$|\.sh$"
echo ""
echo "📦 Fichiers déplacés dans old_trash/:"
ls -1 old_trash/
