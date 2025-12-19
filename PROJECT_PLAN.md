# 📋 PROJECT PLAN - Notion to SiYuan Migration

**Dernière mise à jour** : 2024-12-18  
**Status** : Phase 2 - Import des données

---

## 🎯 Objectif du projet

Migrer les databases Notion (workspace PARA) vers SiYuan en préservant :
- ✅ Structure des databases
- ✅ Propriétés et types
- ✅ Relations entre databases
- ✅ Contenu des pages
- ⚠️ Rollups/Formules (à recréer manuellement)

---

## 📊 PHASE 0 : Setup et Configuration ✅

- [x] Créer l'intégration Notion
- [x] Obtenir le token API Notion
- [x] Configurer SiYuan API (token + URL)
- [x] Setup environnement Python (venv)
- [x] Installer dépendances
- [x] Tester connexions API
- [x] Créer structure du repo Git

**Durée** : 30 min  
**Fichiers** : `.env`, `setup_migrator.sh`, `activate_migrator.sh`

---

## 📊 PHASE 1 : Extraction et Analyse ✅

### 1.1 Extraction des databases Notion ✅

- [x] Script d'extraction fonctionnel
- [x] Détection correcte des types (Status → select, etc.)
- [x] Identification des rollups et formules
- [x] Extraction des options select/multi-select
- [x] Mapping des relations entre databases
- [x] **15 databases extraites avec succès**

**Script** : `extract_by_workspace.py`  
**Output** : `migration_output/migration_plan.json`

### 1.2 Génération du guide de création ✅

- [x] Guide formaté par database
- [x] Liste des propriétés avec types corrects
- [x] Indication des relations
- [x] Options des select/multi-select

**Output** : `migration_output/migration_guide.txt`

**Durée Phase 1** : 10 min  
**Status** : ✅ TERMINÉ

---

## 📊 PHASE 2 : Création manuelle des Attribute Views ⏳

### 2.1 Databases principales (prioritaires)

- [ ] **DB-Projects** (14 propriétés, 5 relations)
- [ ] **DB-Tasks** (16 propriétés, 4 relations)
- [ ] **DB-Resources** (15 propriétés, 4 relations)
- [ ] **DB-Area** (10 propriétés, 2 relations)
- [ ] **DB-Objectives** (8 propriétés, 1 relation)

### 2.2 Databases secondaires

- [ ] DB-Inbox (15 propriétés)
- [ ] DB-Comptes Bancaires (12 propriétés)
- [ ] DB-Serials numbers (5 propriétés)
- [ ] DB-Polices Ass Privé (5 propriétés)
- [ ] DB-Expenses Privée (6 propriétés)

### 2.3 Databases techniques (optionnelles)

- [ ] DB-3DPrint Layers
- [ ] DB-3DPrint filaments
- [ ] DB-3DPrint-Motifs
- [ ] DB-MetaFB ID
- [ ] DB-Onde de Forme

### ⚠️ IMPORTANT - Rollups et Formules

**Décision** : Les rollups et formules ne sont **PAS importés** automatiquement.

**Pourquoi ?**
- Risque d'erreurs de mapping
- Complexité des formules Notion ≠ SiYuan
- Meilleure qualité en création manuelle

**À faire manuellement après import** :
- `DB-Projects.Completed Tasks` (rollup)
- `DB-Projects.All Tasks` (rollup)
- `DB-Area.Earliest Deadline` (rollup)
- `DB-Area.Progress` (rollup)
- `DB-Onde de Forme.montant a verser` (formula)

**Durée Phase 2** : 30-60 min (utilisateur)  
**Status** : ⏳ EN COURS

---

## 📊 PHASE 3 : Import automatique des données ⏸️

### 3.1 Configuration ⏳

- [ ] Identifier le notebook SiYuan cible
- [ ] Mapper les AVs créées manuellement
- [ ] Configurer les variables d'environnement

**Variables requises** :
```bash
export TARGET_NOTEBOOK_ID=xxx
export DRY_RUN=false
```

### 3.2 Import des données 🔜

- [ ] Test en DRY_RUN (1 database, 5 entrées)
- [ ] Vérification des propriétés importées
- [ ] Import réel de toutes les databases
- [ ] Vérification post-import

**Script** : `import_data_to_siyuan.py` (à finaliser)

### 3.3 Gestion des données

Pour chaque entrée Notion :
- [x] Import du titre → Nom du document
- [x] Import du contenu → Corps du document
- [x] Import des propriétés simples → Attributes
- [x] Sauvegarde des IDs relations (pour Phase 4)
- [x] **Skip des rollups/formules** ✅
- [ ] Metadata : `custom-notion-id`, `custom-notion-db`

**Durée Phase 3** : 1-2h (selon volume)  
**Status** : 🔜 À DÉMARRER

---

## 📊 PHASE 4 : Reconnexion des relations 🔜

### 4.1 Mapping Notion ↔ SiYuan

- [ ] Charger `import_mapping.json`
- [ ] Pour chaque relation, mapper Notion ID → SiYuan ID
- [ ] Mettre à jour les attributes des documents

### 4.2 Vérification

- [ ] Toutes les relations sont connectées
- [ ] Les relations bidirectionnelles fonctionnent
- [ ] Pas de relations cassées

**Script** : À créer - `reconnect_relations.py`

**Durée Phase 4** : 30 min  
**Status** : 🔜 À DÉMARRER

---

## 📊 PHASE 5 : Rollups manuels 🔜

### 5.1 Recréer les rollups dans SiYuan

**Utilisateur** - Créer manuellement les rollups suivants :

#### DB-Projects
- `Completed Tasks` : Count values (relation Tasks, propriété Archive = checked)
- `All Tasks` : Count all (relation Tasks)

#### DB-Area
- `Earliest Deadline` : Earliest date (relation Tasks, propriété Due Date)
- `Progress` : Percent per group
- `Quantity of Resources` : Count (relation Resources)
- `Quantity of Projects` : Count (relation Projects)

#### DB-Onde de Forme
- `montant a verser` : Formula à recréer

**Durée Phase 5** : 15-20 min  
**Status** : 🔜 À FAIRE APRÈS IMPORT

---

## 📊 PHASE 6 : Vérification et tests ✅

### 6.1 Checklist de vérification

- [ ] Toutes les databases créées dans SiYuan
- [ ] Nombre de documents correspond à Notion
- [ ] Properties correctement définies
- [ ] Relations fonctionnelles
- [ ] Rollups recréés et fonctionnels
- [ ] Contenu des pages préservé

### 6.2 Tests de navigation

- [ ] Naviguer dans Projects → Tasks
- [ ] Naviguer dans Area → Resources
- [ ] Vérifier les filtres et vues
- [ ] Tester les recherches

**Durée Phase 6** : 30 min  
**Status** : 🔜 À FAIRE

---

## 📈 PROGRESSION GLOBALE

```
Phase 0 : Setup               ████████████████████ 100% ✅
Phase 1 : Extraction          ████████████████████ 100% ✅
Phase 2 : Création AVs        ████░░░░░░░░░░░░░░░░  20% ⏳
Phase 3 : Import données      ░░░░░░░░░░░░░░░░░░░░   0% 🔜
Phase 4 : Reconnexion         ░░░░░░░░░░░░░░░░░░░░   0% 🔜
Phase 5 : Rollups manuels     ░░░░░░░░░░░░░░░░░░░░   0% 🔜
Phase 6 : Vérification        ░░░░░░░░░░░░░░░░░░░░   0% 🔜

TOTAL : ████░░░░░░░░░░░░░░░░░░ 25%
```

---

## 🎯 PROCHAINES ACTIONS IMMÉDIATES

### Pour l'utilisateur (TOI)
1. ✅ Exécuter `./cleanup_repo.sh` (nettoyer le repo)
2. ⏳ Créer les 5 AVs principales dans SiYuan
3. 🔜 Noter les IDs des pages/AVs créées

### Pour le script (MOI)
1. ✅ Finaliser `import_data_to_siyuan.py` (skip rollups)
2. 🔜 Créer `reconnect_relations.py`
3. 🔜 Tester l'import sur 1 database

---

## 📂 STRUCTURE DU REPO

```
notion-to-siyuan-migrator/
├── 📄 README.md                    # Documentation principale
├── 📄 PROJECT_PLAN.md              # Ce fichier (checklist)
├── 📄 TROUBLESHOOTING.md           # Erreurs connues et solutions
├── 📄 QUICK_START.md               # Guide rapide
│
├── 🔧 extract_by_workspace.py      # Script extraction Notion
├── 🔧 import_data_to_siyuan.py     # Script import SiYuan
│
├── 📁 migration_output/            # Données de migration
│   ├── migration_plan.json         # 15 databases analysées
│   └── migration_guide.txt         # Guide de création AVs
│
├── 📁 old_trash/                   # Fichiers obsolètes
│
├── ⚙️ .env                          # Config (gitignored)
├── ⚙️ setup_migrator.sh            # Setup initial
└── ⚙️ activate_migrator.sh         # Activation env
```

---

## 📞 SUPPORT

En cas de problème :
1. Consulter `TROUBLESHOOTING.md`
2. Vérifier les logs du script
3. Tester en mode `DRY_RUN=true`
4. Créer un snapshot SiYuan avant import

---

**✨ Ce fichier est la source de vérité du projet. Garde-le à jour ! ✨**
