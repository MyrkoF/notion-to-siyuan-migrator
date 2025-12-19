# 🎯 PLAN D'ACTION - Migration PARA Notion → SiYuan

## 📋 Vue d'ensemble

**Objectif** : Migrer seulement PARA (pas Equalium) vers la structure SiYuan existante

**Durée estimée** : 3-4 heures total

---

## ✅ TÂCHE 0 : Configuration et extraction ciblée

### 0.1 - Identifier l'ID de la page PARA dans Notion

**TOI** :
```bash
# Ouvrir Notion
# Page PARA → Clic droit → Copier le lien
# Le lien ressemble à : https://notion.so/PARA-1e468cf76fd48091b8efdac7dd1f9301
# L'ID est : 1e468cf76fd48091b8efdac7dd1f9301
```

### 0.2 - Extraire seulement les databases PARA

**SCRIPT** :
```bash
cd ~/GIT/notion-to-siyuan-migrator
source venv/bin/activate
source ~/.notion_siyuan_migrator.env

# Définir le filtre PARA
export FILTER_PARENT_PAGE_ID=1e468cf76fd48091b8efdac7dd1f9301  # Remplacer par ton ID

# Lancer l'extraction améliorée
python3 extract_para_databases.py
```

**Résultat** :
- ✅ `para_migration_plan.json` - Seulement les DBs sous PARA
- ✅ `para_creation_guide.txt` - Guide avec les VRAIS types

**Durée** : 5 minutes

---

## ✅ TÂCHE 1 : Vérification et ajustements

### 1.1 - Vérifier le plan extrait

**TOI** :
```bash
cat migration_output/para_migration_plan.json | less
```

Vérifier :
- [ ] Seulement les DBs de PARA (pas Equalium)
- [ ] Types corrects (Status = select, etc.)
- [ ] Rollups détectés avec leur config

### 1.2 - Ajuster le guide si nécessaire

Si tu vois des erreurs de type, note-les et on ajuste le script.

**Durée** : 10 minutes

---

## ✅ TÂCHE 2 : Création des Attribute Views ajustée

### 2.1 - Identifier les pages de destination dans SiYuan

D'après tes screenshots, tu as déjà :
```
PARA/
├── Home
├── Inbox
├── Projects  ← Créer AV "Projects" ICI
├── Areas     ← Créer AV "Area" ICI
├── Resources ← Créer AV "Resources" ICI
├── Tasks     ← Créer AV "Tasks" ICI
├── Events
├── Objectives ← Créer AV "Objectives" ICI
├── Key Results
└── Progress Update
```

### 2.2 - Créer les AVs principales (5-10)

**TOI** - Dans SiYuan :

Pour chaque database principale :

1. **Ouvrir la page correspondante** (ex: PARA/Projects)
2. **Créer une Attribute View** dedans
3. **Nommer exactement comme Notion** (ex: "Projects")
4. **Ajouter les colonnes** selon `para_creation_guide.txt`

**Ordre recommandé** :
1. Objectives (pas de relations)
2. Area (pas de relations)
3. Events (pas de relations)
4. Key Results (relation vers Objectives)
5. Resources (relations vers Area, Tasks, Projects)
6. Tasks (relations vers Projects, Resources, Area)
7. Projects (relations vers tout)

### 2.3 - Attention aux types spéciaux

D'après tes remarques sur Projects :

```
Status → SELECT (pas text) ✅
Cover Image → ASSET (pas text) ✅
Completed Tasks → ROLLUP
  - Relation: Tasks
  - Property: Status
  - Function: Count values

All Tasks → ROLLUP  
  - Relation: Tasks
  - Property: (any)
  - Function: Count all

Days Left → FORMULA (à ignorer pour l'instant)
Project Status → Ignorer (doublon)
```

**Durée** : 30-60 minutes

---

## ✅ TÂCHE 3 : Mapper les AVs créées

### 3.1 - Récupérer les IDs des pages SiYuan

**SCRIPT** :
```bash
# Lister l'arbre PARA
curl -X POST http://192.168.1.11:6806/api/filetree/listDocTree \
  -H "Authorization: token y0k8ssy0g716id3e" \
  -H "Content-Type: application/json" \
  -d '{"notebook": "TON-NOTEBOOK-ID", "path": "/PARA"}'
```

Copier les IDs des pages (Projects, Tasks, etc.)

### 3.2 - Créer un fichier de mapping

**TOI** :
```bash
cat > migration_output/siyuan_structure_mapping.json << 'EOF'
{
  "notebook_id": "20251213161124-9q2afk3",
  "structure": {
    "Projects": {
      "page_id": "id-de-la-page-projects",
      "av_id": "id-de-lav-projects"
    },
    "Tasks": {
      "page_id": "id-de-la-page-tasks",
      "av_id": null
    },
    "Resources": {
      "page_id": "id-de-la-page-resources",
      "av_id": null
    }
  }
}
EOF
```

**Durée** : 10 minutes

---

## ✅ TÂCHE 4 : Adapter le script d'import

### 4.1 - Modifier destination

Au lieu de créer dans "Notion Migration 20251218...", importer dans la structure PARA existante.

**JE vais coder** :
- Lire `siyuan_structure_mapping.json`
- Créer les documents sous les bonnes pages
- Utiliser les AVs existantes

### 4.2 - Test avec 1 database

**SCRIPT** :
```bash
export TARGET_NOTEBOOK_ID=20251213161124-9q2afk3  # Notebook PARA
export DRY_RUN=true
export TEST_LIMIT=3
python3 import_para_data.py  # Nouveau script
```

**Durée** : 20 minutes (moi) + 5 minutes (toi pour tester)

---

## ✅ TÂCHE 5 : Import complet

### 5.1 - Import réel

```bash
export DRY_RUN=false
export TEST_LIMIT=0
python3 import_para_data.py
```

### 5.2 - Vérification

**TOI** - Dans SiYuan :
- [ ] Documents créés sous les bonnes pages
- [ ] Attributes présents
- [ ] Hiérarchie préservée

**Durée** : 1-2 heures (selon volume)

---

## 🎯 RÉCAPITULATIF DES FICHIERS

```
migration_output/
├── para_migration_plan.json           # Databases PARA uniquement
├── para_creation_guide.txt            # Guide avec vrais types
├── siyuan_structure_mapping.json     # Mapping structure SiYuan
└── import_mapping.json                # Mapping après import
```

---

## 🚦 STATUT ACTUEL

- [x] Tâche 0.1 - Identifier PARA ID (TOI - à faire)
- [ ] Tâche 0.2 - Extraction ciblée (SCRIPT - prêt)
- [ ] Tâche 1 - Vérification
- [ ] Tâche 2 - Création AVs (TOI)
- [ ] Tâche 3 - Mapping structure
- [ ] Tâche 4 - Adapter import (MOI)
- [ ] Tâche 5 - Import final

---

## 💬 QUESTIONS OUVERTES

1. **Rollups** : Les créer manuellement dans SiYuan ou les ignorer ?
   - Mon avis : Les ignorer pour l'instant (trop complexe)

2. **Formules** : Pareil, ignorer ?
   - Mon avis : Oui, les formules Notion ≠ SiYuan

3. **Assets** : Comment gérer Cover Image et Files ?
   - Mon avis : Importer les URLs en texte, télécharger manuellement

---

## 🎯 PROCHAINE ACTION IMMÉDIATE

**TOI maintenant** :
1. Trouve l'ID de la page PARA dans Notion
2. Lance `python3 extract_para_databases.py` avec le filtre
3. Montre-moi `para_migration_plan.json`

**MOI ensuite** :
- Je vérifie que les types sont corrects
- Je code le script d'import adapté à ta structure

**On y va ?** 🚀
