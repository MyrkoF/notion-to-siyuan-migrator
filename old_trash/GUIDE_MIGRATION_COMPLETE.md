# 🎯 MIGRATION NOTION → SIYUAN - Guide Complet

## 📋 Vue d'ensemble

**Approche hybride en 2 phases** :
1. **TOI** : Créer les Attribute Views manuellement (30-60 min)
2. **SCRIPT** : Import automatique des données

---

## PHASE 1 : Création manuelle des Attribute Views

### 📁 Fichiers de référence

Tu as **3 fichiers** pour t'aider :

1. **`migration_plan.json`** - Plan complet avec toutes les infos
2. **`manual_creation_guide.txt`** - Guide de création étape par étape
3. **`notion_databases_analysis.json`** - Analyse détaillée

### 🎯 Processus de création

Pour chaque database (39 au total, ou commence par les principales) :

#### 1️⃣ Ouvrir SiYuan et créer une nouvelle Attribute View

```
1. Clic droit dans le notebook
2. "Nouveau" → "Base de données" (Attribute View)
3. Nommer exactement comme dans Notion (ex: "Projects")
```

#### 2️⃣ Ajouter les colonnes

Utilise `manual_creation_guide.txt` pour voir :
- Le nom exact de chaque colonne
- Son type (text, select, date, etc.)
- Les relations vers d'autres AVs

**Exemple pour "Projects"** :
```
[ ] Progress (text)
[ ] Archive (checkbox)
[ ] Difficulty Level (select)
[ ] Status (text)
[ ] Priority (select)
[ ] Start Date (date)
[ ] Description (text)
[ ] Skills Involved (multi-select)
...etc
```

#### 3️⃣ Configurer les options des select/multi-select

Pour les colonnes de type `select` ou `multi-select`, ajoute les options.

**Tu n'es PAS obligé de mettre toutes les options** - le script créera les valeurs automatiquement.

Mais si tu veux, voici les plus communes :

**Status** : Not Started, In Progress, Done, Archived
**Priority** : Low, Medium, High
**Difficulty** : Easy, Medium, Hard

#### 4️⃣ Créer les relations

Pour les colonnes avec `(relation) → Autre DB` :
- Crée d'abord la database cible
- Puis reviens créer la relation

**Ordre recommandé** (databases sans relations d'abord) :
1. Comptes
2. Serials numbers and key
3. Toutes les polices
4. Objectives
5. Area
6. Events
7. Key Results
8. Resources
9. Tasks
10. Projects
...etc

### ✅ Checklist par database

```
[ ] Attribute View créée avec le bon nom
[ ] Toutes les colonnes ajoutées
[ ] Types corrects pour chaque colonne
[ ] Options des select/multi-select configurées (optionnel)
[ ] Relations configurées vers les autres AVs
```

### 💡 Astuces

- **Commence par 5-10 databases principales** pour tester
- Les databases sans relations sont plus simples
- Tu peux faire ça en plusieurs sessions
- Pas besoin d'être parfait - le script s'adapte

---

## PHASE 2 : Import automatique des données

Une fois que tu as créé quelques AVs, lance l'import !

### 📝 Prérequis

1. **Identifier le notebook SiYuan** où tu as créé les AVs :

```bash
# Liste les notebooks
curl -X POST http://192.168.1.11:6806/api/notebook/lsNotebooks \
  -H "Authorization: token y0k8ssy0g716id3e" \
  -H "Content-Type: application/json" \
  -d '{}'
```

Copie l'ID du notebook (ex: `20251218154447-lxfdepg`)

2. **Configurer l'environnement** :

```bash
cd ~/GIT/notion-to-siyuan-migrator
source venv/bin/activate
source ~/.notion_siyuan_migrator.env

# Définir le notebook cible
export TARGET_NOTEBOOK_ID=20251218154447-lxfdepg
```

### 🧪 Test avec 1 database (recommandé)

```bash
# Mode DRY RUN pour voir ce qui sera importé
export DRY_RUN=true
export TEST_LIMIT=5  # Limiter à 5 entrées pour le test
python3 import_data_to_siyuan.py
```

Ça va afficher :
- ✅ Les entrées qui seront importées
- ✅ Les propriétés converties
- ✅ Pas d'import réel

Vérifie que tout est OK !

### ⚡ Import réel

Si le test est bon :

```bash
# Import de TOUTES les entrées
export DRY_RUN=false
export TEST_LIMIT=0  # 0 = toutes les entrées
python3 import_data_to_siyuan.py
```

Le script va :
1. ✅ Lire le `migration_plan.json`
2. ✅ Pour chaque database :
   - Extraire les entrées de Notion
   - Créer les documents dans SiYuan
   - Définir les attributes (propriétés)
3. ✅ Sauvegarder le mapping Notion ID ↔ SiYuan ID

### 📊 Ce qui est importé

Pour chaque entrée Notion :
- ✅ **Titre** → Nom du document SiYuan
- ✅ **Contenu texte** → Corps du document
- ✅ **Propriétés** → Attributes SiYuan (`custom-property-name`)
- ✅ **Relations** → IDs sauvegardés (reconnexion Phase 3)
- ✅ **Metadata** → `custom-notion-id`, `custom-notion-db`

### 🎛️ Options avancées

```bash
# Limiter à 10 entrées par database (pour tests)
export TEST_LIMIT=10

# Changer le délai entre appels (si rate limit)
export DELAY_BETWEEN_CALLS=0.5

# Changer la taille des batchs
export BATCH_SIZE=20
```

---

## PHASE 3 : Reconnexion des relations (TODO)

**Actuellement les relations sont sauvegardées mais pas reconnectées.**

Le fichier `import_mapping.json` contient :
```json
{
  "notion_to_siyuan": {
    "notion-page-id-1": "siyuan-block-id-1",
    "notion-page-id-2": "siyuan-block-id-2",
    ...
  }
}
```

**Script de reconnexion à venir** qui utilisera ce mapping.

---

## 📂 Structure des fichiers

```
migration_output/
├── migration_plan.json              # Plan complet de migration
├── manual_creation_guide.txt        # Guide création manuelle AVs
├── notion_databases_analysis.json   # Analyse des DBs Notion
└── import_mapping.json              # Mapping Notion ↔ SiYuan (après import)
```

---

## 🔧 Troubleshooting

### Erreur "TARGET_NOTEBOOK_ID non défini"
```bash
export TARGET_NOTEBOOK_ID=ton-notebook-id
```

### Erreur "migration_plan.json introuvable"
Lance d'abord :
```bash
export DRY_RUN=true
python3 notion_to_siyuan_complete.py
```

### Import trop lent
Augmente le délai :
```bash
export DELAY_BETWEEN_CALLS=1.0
```

### Tester avec moins de databases
Édite `migration_plan.json` et supprime les databases que tu ne veux pas importer.

---

## 🎯 Workflow complet recommandé

### Jour 1 : Préparation (10 min)
```bash
# Générer le plan et le guide
export DRY_RUN=true
python3 notion_to_siyuan_complete.py
python3 generate_creation_guide.py
```

### Jour 2 : Création AVs (30-60 min)
- Créer 5-10 databases principales manuellement dans SiYuan
- Utiliser `manual_creation_guide.txt` comme référence

### Jour 3 : Test import (15 min)
```bash
# Test avec 5 entrées
export DRY_RUN=true
export TEST_LIMIT=5
export TARGET_NOTEBOOK_ID=ton-notebook-id
python3 import_data_to_siyuan.py
```

### Jour 4 : Import complet (1-2h selon volume)
```bash
# Import réel
export DRY_RUN=false
export TEST_LIMIT=0
python3 import_data_to_siyuan.py
```

### Jour 5 : Vérification
- Vérifier dans SiYuan que les données sont bien importées
- Vérifier les attributes des documents
- Signaler tout problème

---

## ✅ Checklist finale

Avant de lancer l'import réel :

```
[ ] Les AVs sont créées dans SiYuan
[ ] Le TARGET_NOTEBOOK_ID est défini
[ ] Le test DRY_RUN fonctionne
[ ] Les tokens Notion/SiYuan sont valides
[ ] Snapshot SiYuan créé (sécurité)
[ ] Prêt pour l'import !
```

---

## 🆘 Support

En cas de problème :
1. Vérifie les logs du script
2. Teste en mode DRY_RUN
3. Vérifie `import_mapping.json` pour voir ce qui a été importé
4. Contacte-moi avec les erreurs

---

## 🚀 Next Steps (Améliorations futures)

- [ ] Reconnexion automatique des relations
- [ ] Import des vues (Kanban, Calendar, etc.)
- [ ] Gestion des formules/rollups
- [ ] Import incrémental (sync)
- [ ] UI web pour suivre la migration
