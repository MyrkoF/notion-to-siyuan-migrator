# 🔄 Notion to SiYuan Migrator

**Migration automatisée des databases Notion vers SiYuan avec préservation de la structure et des relations**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## 📋 Vue d'ensemble

Ce projet permet de migrer des databases Notion complexes vers SiYuan en préservant :
- ✅ Structure des databases → Attribute Views
- ✅ Types de propriétés (select, date, checkbox, etc.)
- ✅ Relations entre databases
- ✅ Contenu des pages
- ⚠️ Rollups/Formules (recréation manuelle recommandée)

### Approche hybride

**Phase automatique** : Extraction Notion + Import des données  
**Phase manuelle** : Création des Attribute Views dans SiYuan (30-60 min)

**Pourquoi ?** Les APIs SiYuan ne permettent pas la création programmatique d'AVs, mais cette approche garantit :
- Stabilité à long terme (APIs officielles)
- Zéro maintenance
- Contrôle total sur la structure

---

## 🚀 Quick Start

### 1. Installation

```bash
# Cloner le repo
git clone https://github.com/MyrkoF/notion-to-siyuan-migrator.git
cd notion-to-siyuan-migrator

# Setup automatique
chmod +x setup_migrator.sh
./setup_migrator.sh
```

### 2. Configuration

```bash
# Éditer .env avec tes credentials
cp .env.example .env
nano .env
```

**Variables requises** :
```bash
NOTION_TOKEN=secret_xxxxxxxxxxxxx
SIYUAN_URL=http://192.168.1.11:6806
SIYUAN_TOKEN=your_siyuan_token
TARGET_NOTEBOOK_ID=xxx  # À définir plus tard
```

### 3. Extraction des databases

```bash
# Activer l'environnement
source activate_migrator.sh

# Extraire toutes les databases Notion
python3 extract_by_workspace.py
```

**Output** :
- `migration_output/migration_plan.json` - Analyse des 15 databases
- `migration_output/migration_guide.txt` - Guide de création des AVs

### 4. Créer les Attribute Views dans SiYuan

Utilise `migration_guide.txt` comme checklist pour créer manuellement les AVs dans SiYuan.

**Temps estimé** : 30-60 minutes

### 5. Import des données

```bash
# Test (recommandé)
export DRY_RUN=true
export TEST_LIMIT=5
python3 import_data_to_siyuan.py

# Import réel
export DRY_RUN=false
export TEST_LIMIT=0
python3 import_data_to_siyuan.py
```

---

## 📂 Structure du projet

```
notion-to-siyuan-migrator/
│
├── 📄 README.md                    # Ce fichier
├── 📄 PROJECT_PLAN.md              # Checklist détaillée du projet
├── 📄 TROUBLESHOOTING.md           # Erreurs connues et solutions
├── 📄 QUICK_START.md               # Guide rapide de démarrage
│
├── 🔧 extract_by_workspace.py      # Script d'extraction Notion
├── 🔧 import_data_to_siyuan.py     # Script d'import SiYuan
│
├── 🛠️ setup_migrator.sh             # Setup automatique (venv + deps)
├── 🛠️ activate_migrator.sh          # Activation environnement
├── 🛠️ cleanup_repo.sh               # Nettoyage fichiers obsolètes
│
├── 📁 migration_output/            # Données générées
│   ├── migration_plan.json         # Analyse complète des databases
│   ├── migration_guide.txt         # Guide de création des AVs
│   └── import_mapping.json         # Mapping Notion ↔ SiYuan (après import)
│
├── 📁 old_trash/                   # Fichiers obsolètes archivés
│
├── ⚙️ .env                          # Configuration (gitignored)
├── ⚙️ .env.example                  # Template de configuration
└── 🐍 venv/                         # Environnement Python virtuel
```

---

## 🎯 Workflow complet

### Phase 0 : Setup (5 min)
1. Clone le repo
2. Lance `./setup_migrator.sh`
3. Configure `.env`

### Phase 1 : Extraction (5 min)
1. `python3 extract_by_workspace.py`
2. Vérifie `migration_plan.json`
3. Consulte `migration_guide.txt`

### Phase 2 : Création AVs (30-60 min)
1. Ouvre SiYuan
2. Crée les Attribute Views manuellement
3. Utilise le guide comme checklist

**Priorité** : Commence par les 5 databases principales :
- DB-Projects
- DB-Tasks
- DB-Resources
- DB-Area
- DB-Objectives

### Phase 3 : Import (1-2h selon volume)
1. Test : `export DRY_RUN=true && python3 import_data_to_siyuan.py`
2. Vérifie les résultats
3. Import réel : `export DRY_RUN=false && python3 import_data_to_siyuan.py`

### Phase 4 : Rollups manuels (15 min)
Recrée manuellement les rollups dans SiYuan (voir `PROJECT_PLAN.md`)

### Phase 5 : Vérification (15 min)
- Nombre de documents
- Propriétés
- Relations
- Contenu

---

## 🔧 Scripts détaillés

### extract_by_workspace.py

**Fonction** : Extrait les databases Notion et analyse leur structure

**Features** :
- Détection automatique des types (Status → select, Files → asset, etc.)
- Identification des rollups avec leur configuration
- Mapping des relations entre databases
- Extraction des options select/multi-select
- Génération du guide de création

**Usage** :
```bash
python3 extract_by_workspace.py
```

**Output** :
- `migration_plan.json` - Données structurées pour l'import
- `migration_guide.txt` - Guide humain-readable

### import_data_to_siyuan.py

**Fonction** : Importe les données Notion dans les Attribute Views SiYuan

**Features** :
- Import des titres et contenu des pages
- Conversion des propriétés en attributes SiYuan
- Sauvegarde des relations (pour reconnexion Phase 4)
- **Skip automatique des rollups/formules** ✅
- Mode DRY_RUN pour tests
- Limitation du nombre d'entrées (TEST_LIMIT)

**Usage** :
```bash
# Test
export DRY_RUN=true
export TEST_LIMIT=5
python3 import_data_to_siyuan.py

# Production
export DRY_RUN=false
export TEST_LIMIT=0
python3 import_data_to_siyuan.py
```

**Variables d'environnement** :
- `TARGET_NOTEBOOK_ID` - ID du notebook SiYuan cible
- `DRY_RUN` - `true` = simulation, `false` = import réel
- `TEST_LIMIT` - Nombre d'entrées max par database (0 = toutes)
- `DELAY_BETWEEN_CALLS` - Délai entre appels API (défaut: 0.3s)

---

## ⚙️ Configuration

### Obtenir le token Notion

1. Va sur https://www.notion.so/my-integrations
2. Crée une nouvelle intégration
3. Copie le "Internal Integration Token"
4. **Important** : Partage tes databases avec l'intégration
   - Ouvre chaque database dans Notion
   - Clic "..." → "Add connections" → Choisis ton intégration

### Obtenir le token SiYuan

1. Ouvre SiYuan
2. Settings → About → Copy API Token
3. Note aussi l'URL (ex: `http://192.168.1.11:6806`)

### Identifier le notebook cible

```bash
# Liste les notebooks
curl -X POST http://192.168.1.11:6806/api/notebook/lsNotebooks \
  -H "Authorization: token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

Copie l'ID du notebook où tu veux importer (ex: `20251218154447-lxfdepg`)

---

## 🎨 Détection des types

Le script détecte automatiquement les bons types :

| Notion Type | SiYuan Type | Notes |
|------------|-------------|-------|
| `title` | `text` | Titre de la page |
| `rich_text` | `text` | Texte enrichi |
| `number` | `number` | Nombre |
| `select` | `select` | Options simples |
| `multi_select` | `multi-select` | Options multiples |
| `status` | `select` | ⚠️ Status Notion → select |
| `date` | `date` | Date simple ou plage |
| `checkbox` | `checkbox` | Booléen |
| `url` | `url` | Lien |
| `email` | `email` | Email |
| `phone_number` | `phone` | Téléphone |
| `relation` | `relation` | Relation vers autre DB |
| `files` | `asset` / `text` | Asset si "cover"/"image" |
| `rollup` | **SKIP** | À recréer manuellement |
| `formula` | **SKIP** | À recréer manuellement |

---

## ⚠️ Limitations et décisions de design

### Rollups et Formules

**Décision** : Les rollups et formules ne sont **pas importés** automatiquement.

**Raisons** :
1. Complexité du mapping Notion ↔ SiYuan
2. Risque d'erreurs et de conflits
3. Différences de syntaxe entre plateformes
4. Meilleure qualité en création manuelle

**Solution** : Liste fournie dans `PROJECT_PLAN.md` Phase 5

### Création manuelle des AVs

**Pourquoi pas automatique ?**

L'API SiYuan n'expose pas `/api/av/createAttributeView` de manière stable. Alternatives évaluées :
- **Option A** : Reverse-engineer les plugins → Risque élevé, maintenance cauchemar
- **Option B** : Approche hybride → Stable, rapide, maintenable ✅

**ROI** : 3-4h total (setup + création AVs + import) vs 8h+ (dev + risque + maintenance)

### Relations

Les relations sont sauvegardées dans `import_mapping.json` mais **pas encore reconnectées**. Cela nécessite un script supplémentaire (Phase 4 - à venir).

---

## 🐛 Troubleshooting

Voir `TROUBLESHOOTING.md` pour :
- Erreurs communes et solutions
- Problèmes d'authentification
- Erreurs d'API
- Conflits de types

---

## 📊 Statistiques du projet

**Databases migrées** : 15  
**Propriétés totales** : ~150  
**Relations mappées** : 25+  
**Temps de migration** : 3-4 heures total

**Databases principales** :
1. DB-Projects (14 propriétés, 5 relations)
2. DB-Tasks (16 propriétés, 4 relations)
3. DB-Resources (15 propriétés, 4 relations)
4. DB-Area (10 propriétés, 2 relations)
5. DB-Objectives (8 propriétés, 1 relation)

---

## 🤝 Contributing

Voir `CONTRIBUTING.md` pour les guidelines de contribution.

---

## 📄 License

MIT License - Voir `LICENSE` pour détails

---

## 🙏 Remerciements

- [Notion API](https://developers.notion.com/)
- [SiYuan](https://github.com/siyuan-note/siyuan)
- Communauté open-source

---

## 📞 Support

- 📄 Consulte `TROUBLESHOOTING.md`
- 📋 Vérifie `PROJECT_PLAN.md` pour la progression
- 🐛 Ouvre une issue sur GitHub

---

**✨ Happy migrating! ✨**
