# Notion to SiYuan Migrator 🚀

Script complet pour migrer tout le contenu de Notion vers SiYuan en préservant les propriétés et relations.

## ✨ Fonctionnalités

✅ **Extraction complète de Notion**
- Toutes les pages et sous-pages
- Détection et export des databases
- Préservation des propriétés et tags
- Extraction récursive des blocs

✅ **Conversion intelligente**
- Markdown avec frontmatter YAML
- Conversion des blocs Notion vers syntaxe Markdown
- Préservation du formatage (gras, italique, code, etc.)
- Gestion des callouts, quotes, listes, etc.

✅ **Import structuré dans SiYuan**
- Création automatique de l'arborescence
- Snapshots avant/après migration
- Batch processing pour grandes quantités
- Mode dry-run pour tester

✅ **Rapport détaillé**
- Mapping Notion ID → SiYuan ID
- Liste des erreurs et warnings
- Statistiques de migration
- Sauvegarde JSON complète

## 🔧 Prérequis

1. **Python 3.8+** avec modules:
   ```bash
   pip install requests pyyaml
   ```

2. **Notion Integration Token**
   - Aller dans https://www.notion.so/my-integrations
   - Créer une nouvelle intégration
   - Copier le "Internal Integration Token"
   - Partager vos pages Notion avec cette intégration

3. **SiYuan API Token**
   - Dans SiYuan: Paramètres → À propos → Token API
   - Copier le token affiché

## 🚀 Installation rapide

```bash
# 1. Cloner ou télécharger le script
wget https://your-repo/notion_to_siyuan_migrator.py

# 2. Rendre exécutable
chmod +x notion_to_siyuan_migrator.py

# 3. Configurer les tokens
export NOTION_TOKEN="secret_xxxxxxxxxxxxxxxxxxxx"
export SIYUAN_TOKEN="votre-token-siyuan"
export SIYUAN_URL="http://192.168.1.11:6806"  # Votre URL SiYuan

# 4. Lancer la migration
./notion_to_siyuan_migrator.py
```

## ⚙️ Configuration avancée

Éditer les variables dans la classe `Config`:

```python
class Config:
    # Notion
    NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")
    
    # SiYuan
    SIYUAN_URL = os.getenv("SIYUAN_URL", "http://localhost:6806")
    SIYUAN_TOKEN = os.getenv("SIYUAN_TOKEN", "")
    
    # Migration
    BATCH_SIZE = 50              # Taille des batches
    DELAY_BETWEEN_CALLS = 0.5    # Délai entre appels API
    OUTPUT_DIR = Path("./migration_output")
    
    # Options
    PRESERVE_PROPERTIES = True
    PRESERVE_RELATIONS = True
    CREATE_SNAPSHOTS = True
    DRY_RUN = False              # Mode simulation
```

## 📋 Workflow de migration

### Phase 1: Extraction Notion
```
📥 Extraction de Notion...
  [1/45] Extraction: 12a4b5c6...
  [2/45] Extraction: 78e9f0a1...
  ...
✅ 45 pages extraites
```

**Ce qui est extrait:**
- Contenu de toutes les pages
- Blocs et sous-blocs
- Propriétés (texte, nombre, select, date, etc.)
- Tags et metadata
- Relations entre pages (sauvegardées pour mapping)

### Phase 2: Conversion
```
🔄 Conversion et mapping...
  [1/45] Conversion: Mon document important...
  [2/45] Conversion: Notes de réunion...
  ...
✅ 45 documents convertis
```

**Conversion appliquée:**
- Structure Markdown standard
- Frontmatter YAML avec propriétés
- Syntaxe compatible SiYuan
- Sanitization des noms de fichiers

### Phase 3: Import SiYuan
```
📤 Import dans SiYuan...
📸 Création d'un snapshot avant import...
  [1/45] Import: /migration-notion/Mon-document...
  [2/45] Import: /migration-notion/Notes-de-reunion...
  ...
✅ 45 documents importés
```

**Organisation dans SiYuan:**
```
📓 Votre Notebook
  └── 📁 migration-notion/
      ├── 📄 Document-1.md
      ├── 📄 Document-2.md
      └── ...
```

### Phase 4: Rapport
```
📊 Génération du rapport...
  💾 Mapping sauvegardé: ./migration_output/id_mapping.json

✅ MIGRATION TERMINÉE en 142.3s
   Pages migrées: 45/45
   Databases: 3
   Erreurs: 0
   Rapport: ./migration_output/migration_report.json
```

## 📊 Fichiers générés

```
migration_output/
├── migration_report.json    # Rapport complet
├── id_mapping.json          # Notion ID → SiYuan ID
└── (autres logs si erreurs)
```

### Format du rapport

```json
{
  "start_time": "2024-01-15T10:30:00",
  "end_time": "2024-01-15T10:32:22",
  "total_pages": 45,
  "pages_migrated": 45,
  "databases_found": 3,
  "errors": [],
  "warnings": [
    "Database 'CRM' nécessite traitement manuel"
  ],
  "mapping": {
    "notion-id-1": "siyuan-id-1",
    "notion-id-2": "siyuan-id-2"
  }
}
```

## 🔍 Vérification post-migration

1. **Compter les documents**
   ```bash
   # Dans SiYuan, vérifier le nombre de docs importés
   ls -R workspace/data/*/migration-notion/ | wc -l
   ```

2. **Tester la recherche**
   - Rechercher des mots-clés connus
   - Vérifier les résultats

3. **Vérifier les liens**
   - Ouvrir quelques documents
   - Vérifier que les liens internes fonctionnent

4. **Contrôler les propriétés**
   - Ouvrir le frontmatter YAML
   - Vérifier que les propriétés sont préservées

## ⚠️ Limitations connues

### Ce qui EST migré:
✅ Contenu textuel complet
✅ Structure hiérarchique
✅ Formatage basique (gras, italique, code)
✅ Listes, tableaux, quotes
✅ Propriétés dans frontmatter YAML
✅ Tags
✅ Code blocks avec syntaxe
✅ Images (chemins préservés)

### Ce qui NÉCESSITE post-traitement:

❌ **Databases Notion** → Doivent être recréées manuellement comme Attribute Views
- Le script détecte les databases
- Les exporte en JSON pour référence
- Mais ne peut pas créer automatiquement les Attribute Views

⚠️ **Relations entre pages** → Mapping sauvegardé, à reconnecter manuellement
- Le fichier `id_mapping.json` contient toutes les correspondances
- Les liens `[page](notion-id)` doivent être convertis en `((siyuan-id))`

⚠️ **Blocs synchronisés Notion** → Ne peuvent pas être reproduits

⚠️ **Embeds tiers** → Perdus (YouTube, Figma, etc.)

## 🛠️ Mode DRY_RUN

Pour tester la migration sans rien importer:

```python
Config.DRY_RUN = True  # Dans le script
```

Ou via variable d'environnement:

```bash
export DRY_RUN=true
./notion_to_siyuan_migrator.py
```

Le script va:
- Extraire tout depuis Notion
- Convertir en Markdown
- Sauvegarder dans `migration_output/`
- **SANS** importer dans SiYuan

Permet de vérifier le contenu converti avant l'import réel.

## 🔄 Rollback si problème

Si la migration ne se passe pas comme prévu:

1. **Depuis SiYuan**
   ```
   Menu → Historique des données → Snapshots
   → Sélectionner "Avant migration Notion"
   → Restaurer
   ```

2. **Ou supprimer manuellement**
   ```bash
   # Supprimer le dossier migration-notion
   rm -rf workspace/data/*/migration-notion/
   ```

## 🐛 Troubleshooting

### Erreur: "Notion API error 401"
**Cause:** Token invalide ou non autorisé
**Solution:** 
- Vérifier que le token est correct
- Partager vos pages avec l'intégration Notion

### Erreur: "SiYuan API error 401"
**Cause:** Token SiYuan invalide
**Solution:**
- Regénérer le token dans SiYuan
- Vérifier que l'URL est correcte

### Erreur: "No notebooks available"
**Cause:** Aucun notebook dans SiYuan
**Solution:**
- Créer au moins un notebook dans SiYuan

### Warning: "Database XXX nécessite traitement manuel"
**Cause:** Les databases Notion ne peuvent pas être migrées automatiquement
**Solution:**
- Exporter la database en CSV depuis Notion
- Recréer comme Attribute View dans SiYuan
- Utiliser le mapping pour reconnecter les liens

## 💡 Best Practices

1. **Avant migration:**
   - ✅ Faire un backup complet de SiYuan
   - ✅ Tester avec DRY_RUN d'abord
   - ✅ Migrer par petits lots si workspace énorme

2. **Pendant migration:**
   - ✅ Ne pas toucher à SiYuan pendant l'import
   - ✅ Surveiller les logs en temps réel
   - ✅ Noter les warnings pour post-traitement

3. **Après migration:**
   - ✅ Vérifier le comptage des documents
   - ✅ Tester la recherche globale
   - ✅ Vérifier quelques documents clés
   - ✅ Créer un nouveau snapshot "post-migration"

## 🚀 Améliorations futures

- [ ] Support des Attribute Views via API raw SiYuan
- [ ] Conversion automatique des liens internes
- [ ] Migration incrémentale (sync plutôt que one-shot)
- [ ] GUI pour sélectionner quoi migrer
- [ ] Support des images hébergées sur Notion

## 📞 Support

En cas de problème:
1. Vérifier les logs dans `migration_output/`
2. Activer le mode debug (voir section Debug)
3. Consulter la documentation API Notion et SiYuan

## 📝 License

MIT License - Libre d'utilisation et modification

---

**Made with ❤️ by Myrko (via Claude/JARVIS)**
