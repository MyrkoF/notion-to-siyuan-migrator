# 🚀 Notion to SiYuan Migration - Guide de démarrage rapide

## 📦 Fichiers inclus

```
notion-to-siyuan-migration/
├── notion_to_siyuan_migrator.py    # Script principal de migration
├── post_migration_processor.py     # Post-traitement (databases, liens)
├── setup_migrator.sh               # Configuration automatique
├── README_MIGRATION.md             # Documentation complète
└── QUICK_START.md                  # Ce fichier
```

## ⚡ Démarrage en 3 étapes

### 1️⃣ Configuration (5 min)

```bash
# Lancer le setup interactif
./setup_migrator.sh
```

Le script va :
- ✅ Vérifier Python et dépendances
- ✅ Demander vos tokens Notion et SiYuan
- ✅ Tester les connexions API
- ✅ Sauvegarder la config dans `~/.notion_siyuan_migrator.env`

**Tokens requis:**
- **Notion:** https://www.notion.so/my-integrations (créer intégration)
- **SiYuan:** Paramètres → À propos → Token API

### 2️⃣ Migration (temps variable selon taille)

```bash
# Charger la configuration
source ~/.notion_siyuan_migrator.env

# OPTION A: Test sans import réel (recommandé)
export DRY_RUN=true
python3 notion_to_siyuan_migrator.py

# OPTION B: Migration complète
export DRY_RUN=false
python3 notion_to_siyuan_migrator.py
```

**Que se passe-t-il ?**
1. 📥 Extraction de toutes vos pages Notion
2. 🔄 Conversion en Markdown + frontmatter YAML
3. 📤 Import dans SiYuan (avec snapshot automatique)
4. 📊 Génération du rapport

**Résultats:**
```
migration_output/
├── migration_report.json    # Rapport complet
├── id_mapping.json          # Notion ID → SiYuan ID
└── (logs si erreurs)
```

### 3️⃣ Post-traitement (optionnel, ~10 min)

```bash
# Traiter les databases et liens
python3 post_migration_processor.py
```

**Que fait-il ?**
- 🔍 Analyse les databases Notion détectées
- 📝 Génère des instructions de recréation
- 🔗 Convertit les liens internes (Notion ID → SiYuan ID)
- 📊 Génère un rapport de conversion

## 🎯 Workflow complet recommandé

### Première fois

```bash
# 1. Setup
./setup_migrator.sh

# 2. Test en dry-run
source ~/.notion_siyuan_migrator.env
export DRY_RUN=true
python3 notion_to_siyuan_migrator.py

# 3. Vérifier les fichiers dans migration_output/
ls -lh migration_output/

# 4. Si tout est OK, migration réelle
export DRY_RUN=false
python3 notion_to_siyuan_migrator.py

# 5. Post-traitement
python3 post_migration_processor.py
```

### Migrations suivantes (sync)

```bash
# Charger la config
source ~/.notion_siyuan_migrator.env

# Relancer la migration
python3 notion_to_siyuan_migrator.py
```

## 📊 Vérifications post-migration

### 1. Compter les documents

```bash
# Dans SiYuan, ouvrir le notebook et compter
# Ou via terminal:
ls -R ~/SiYuan/data/*/migration-notion/ | wc -l
```

### 2. Tester la recherche

- Ouvrir SiYuan
- Rechercher des mots-clés connus
- Vérifier que les résultats apparaissent

### 3. Vérifier les propriétés

- Ouvrir un document migré
- Vérifier le frontmatter YAML en haut
- Les propriétés Notion doivent être là

### 4. Consulter les rapports

```bash
# Rapport principal
cat migration_output/migration_report.json

# Instructions pour databases
cat migration_output/databases_instructions.md

# Rapport de conversion des liens
cat migration_output/links_conversion_report.md
```

## ⚠️ Points d'attention

### Ce qui EST migré automatiquement ✅

- ✅ Tout le contenu textuel
- ✅ Structure hiérarchique
- ✅ Formatage (gras, italique, code, etc.)
- ✅ Propriétés (dans frontmatter YAML)
- ✅ Tags
- ✅ Blocs de code avec syntax highlighting

### Ce qui nécessite post-traitement ⚠️

- ⚠️ **Databases Notion** → Recréer comme Attribute Views
  - Exporter en CSV depuis Notion
  - Recréer manuellement dans SiYuan
  - Suivre les instructions générées

- ⚠️ **Relations entre pages** → Reconnecter manuellement
  - Utiliser `id_mapping.json`
  - Convertir les liens via post-processor
  - Vérifier les relations importantes

- ⚠️ **Embeds tiers** → Non migrables
  - YouTube, Figma, etc. ne peuvent pas être migrés
  - Remplacer par des liens directs

## 🔄 Rollback si problème

### Via SiYuan (recommandé)

```
Menu → Historique des données → Snapshots
→ Sélectionner "Avant migration Notion"
→ Restaurer
```

### Via ligne de commande

```bash
# Supprimer uniquement le dossier migration
rm -rf ~/SiYuan/data/*/migration-notion/
```

## 💡 Astuces pro

### 1. Migration par lots

Si vous avez un énorme workspace Notion:

```python
# Dans notion_to_siyuan_migrator.py
Config.BATCH_SIZE = 20  # Réduire la taille des batches
```

### 2. Mode debug

Activer les logs détaillés:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 3. Filtrer les pages à migrer

Modifier `_extract_notion()` pour filtrer:

```python
# Exemple: ne migrer que les pages avec un tag spécifique
if "migration" not in notion_page.tags:
    continue
```

### 4. Backup avant tout

```bash
# Backup SiYuan
cp -r ~/SiYuan/data ~/SiYuan/data.backup

# Ou via SiYuan: Menu → Export → Exporter données
```

## 🆘 Problèmes courants

### "Notion API error 401"
**Solution:** Vérifier que vos pages sont **partagées avec l'intégration**

### "No notebooks available"
**Solution:** Créer au moins un notebook dans SiYuan

### "Connection refused to SiYuan"
**Solution:** Vérifier que SiYuan est lancé et que l'URL est correcte

### Liens non convertis
**Solution:** Exécuter `post_migration_processor.py` et consulter le rapport

## 📚 Ressources

- **Documentation complète:** `README_MIGRATION.md`
- **API Notion:** https://developers.notion.com/
- **API SiYuan:** https://github.com/siyuan-note/siyuan/blob/master/API.md
- **SiYuan Docs:** https://docs.siyuan-note.club/en/

## 🤝 Support

Si vous rencontrez des problèmes:

1. Consulter `migration_output/migration_report.json`
2. Vérifier les logs
3. Lire la documentation complète
4. Créer une issue avec les logs d'erreur

## 🎉 Après la migration

Une fois la migration terminée et validée:

1. ✅ Créer un snapshot "post-migration"
2. ✅ Documenter les databases recréées
3. ✅ Partager le retour d'expérience
4. ✅ Profiter de SiYuan ! 🚀

---

**Version:** 1.0.0
**Auteur:** Myrko (via Claude/JARVIS)
**License:** MIT
