# 🐛 TROUBLESHOOTING - Notion to SiYuan Migrator

**Guide de résolution des problèmes courants**

---

## 📋 Table des matières

1. [Problèmes d'authentification](#problèmes-dauthentification)
2. [Erreurs d'extraction Notion](#erreurs-dextraction-notion)
3. [Erreurs d'import SiYuan](#erreurs-dimport-siyuan)
4. [Problèmes de types](#problèmes-de-types)
5. [Erreurs de connexion](#erreurs-de-connexion)
6. [Bonnes pratiques](#bonnes-pratiques)

---

## 🔐 Problèmes d'authentification

### ❌ "NOTION_TOKEN non défini"

**Cause** : Variable d'environnement manquante

**Solution** :
```bash
# Vérifie que le .env existe
cat .env

# Active l'environnement
source activate_migrator.sh

# Ou définis manuellement
export NOTION_TOKEN=secret_xxxxxxxxxxxxx
```

### ❌ "0 databases trouvées" avec intégration valide

**Cause** : L'intégration n'a pas accès aux databases

**Solution** :
1. Ouvre chaque database dans Notion
2. Clic sur "..." en haut à droite
3. "Add connections" → Choisis ton intégration
4. Répète pour CHAQUE database

**Vérification** :
```bash
python3 debug_notion_permissions.py
```

Tu devrais voir :
```
✅ X databases trouvées
   1. Projects
   2. Tasks
   ...
```

### ❌ Erreur 401 Unauthorized

**Cause** : Token invalide ou expiré

**Solution** :
1. Va sur https://www.notion.so/my-integrations
2. Régénère le token
3. Mets à jour `.env`
4. Relance `source activate_migrator.sh`

---

## 📥 Erreurs d'extraction Notion

### ❌ "Erreur Notion API: 429"

**Cause** : Rate limit dépassé

**Solution** :
```bash
# Augmente le délai entre appels
export DELAY_BETWEEN_CALLS=1.0
python3 extract_by_workspace.py
```

### ❌ Filtrage par workspace ne fonctionne pas

**Erreur typique** :
```
📌 Filtrage workspace: Equalium
✅ 0 databases trouvées
```

**Cause** : Le filtre par workspace est trop restrictif (bug connu)

**Solution** : Extraire **TOUTES** les databases puis filtrer manuellement
```bash
unset FILTER_WORKSPACE
python3 extract_by_workspace.py
```

Ensuite édite `migration_plan.json` pour supprimer les databases non désirées.

### ❌ Filtrage par page parente ne fonctionne pas

**Erreur typique** :
```
📌 Filtrage sous la page: PARA-xxx
✅ 0 databases trouvées
```

**Cause** : Les databases sont plusieurs niveaux en dessous, pas directement enfants

**Solution** : Utilise l'extraction sans filtre (recommandé)

### ❌ Types détectés incorrects

**Exemple** : Status détecté comme "text" au lieu de "select"

**Cause** : Ancien script (obsolète)

**Solution** : Utilise `extract_by_workspace.py` qui détecte correctement :
- Status → select ✅
- Files (avec "cover"/"image") → asset ✅
- Rollups → détectés avec config ✅

---

## 📤 Erreurs d'import SiYuan

### ❌ "TARGET_NOTEBOOK_ID non défini"

**Solution** :
```bash
# Liste les notebooks
curl -X POST http://192.168.1.11:6806/api/notebook/lsNotebooks \
  -H "Authorization: token YOUR_SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'

# Définis le notebook cible
export TARGET_NOTEBOOK_ID=20251218154447-lxfdepg
```

### ❌ "Erreur SiYuan API /api/av/createAttributeView: 404"

**Cause** : L'API de création d'AVs n'est pas publique

**Ce n'est PAS une erreur !** C'est pourquoi on utilise l'approche hybride :
1. TOI : Créer les AVs manuellement (30-60 min)
2. SCRIPT : Import automatique des données

**Solution** : Suis le workflow du `PROJECT_PLAN.md`

### ❌ Erreur lors de l'import : "Attribute View non trouvée"

**Cause** : L'AV n'a pas été créée manuellement dans SiYuan

**Solution** :
1. Vérifie que tu as créé l'AV dans SiYuan
2. Vérifie que le nom correspond exactement
3. Relance l'import

### ❌ "Rollup property conflict"

**Cause** : Tentative d'import d'un rollup (non supporté)

**Solution** : C'est normal ! Les rollups sont **automatiquement skippés**.

Vérifie dans le code :
```python
# Les rollups sont ignorés à l'import
if prop_type == "rollup":
    continue  # Skip
```

Tu devras les recréer manuellement (voir Phase 5 du `PROJECT_PLAN.md`)

---

## 🎨 Problèmes de types

### ❌ Propriété "Status" importée comme texte

**Cause** : Mauvaise détection du type

**Vérification** :
```bash
# Vérifie le migration_plan.json
grep -A 3 '"Status"' migration_output/migration_plan.json
```

Tu devrais voir :
```json
{
  "name": "Status",
  "notion_type": "status",
  "siyuan_type": "select"  ← Doit être "select" !
}
```

**Solution si incorrect** : Utilise `extract_by_workspace.py` (pas les anciens scripts)

### ❌ Cover Image importée comme texte

**Vérification** :
```json
{
  "name": "Cover Image",
  "notion_type": "files",
  "siyuan_type": "asset"  ← Doit être "asset" !
}
```

**Solution** : Même chose, utilise le script à jour

### ❌ Relations non détectées

**Vérification** :
```json
{
  "name": "Tasks",
  "notion_type": "relation",
  "siyuan_type": "relation",
  "relation_to": "1e468cf7-..."  ← Doit avoir un relation_to
}
```

---

## 🌐 Erreurs de connexion

### ❌ "Connection refused" SiYuan

**Causes possibles** :
1. SiYuan n'est pas lancé
2. URL incorrecte
3. Firewall bloque

**Solutions** :
```bash
# 1. Vérifie que SiYuan est lancé
ps aux | grep siyuan

# 2. Teste la connexion
curl http://192.168.1.11:6806/api/system/version \
  -H "Authorization: token YOUR_TOKEN"

# 3. Vérifie l'URL dans .env
cat .env | grep SIYUAN_URL
```

### ❌ "Connection timeout"

**Solution** : Augmente le timeout ou vérifie le réseau
```bash
# Dans le script, ajoute un timeout
requests.post(..., timeout=30)
```

---

## ✅ Bonnes pratiques

### 1. Toujours tester en DRY_RUN d'abord

```bash
export DRY_RUN=true
export TEST_LIMIT=3
python3 import_data_to_siyuan.py
```

### 2. Créer un snapshot SiYuan avant import

Dans SiYuan :
1. Settings → Backup → Create snapshot
2. Note le nom du snapshot
3. En cas de problème : Restore

### 3. Commencer par 1 database

Au lieu d'importer les 15 databases d'un coup :
1. Édite `migration_plan.json`
2. Garde seulement 1 database (ex: Projects)
3. Teste l'import
4. Vérifie le résultat
5. Si OK, importe le reste

### 4. Vérifier les logs

Le script affiche des logs détaillés :
```
📊 DATABASE 1/15: Projects
📥 Extraction des entrées de Notion...
✅ 23 entrées trouvées
⚡ Import des 23 entrées...
   Progression: 10/23...
   Progression: 20/23...
✅ Import terminé: 23 entrées
```

Si erreur, note la ligne exacte et le message.

### 5. Garder une copie de migration_plan.json

```bash
cp migration_output/migration_plan.json migration_output/migration_plan_backup_$(date +%Y%m%d).json
```

---

## 🔄 Workflow de débogage

Si tu as un problème :

1. **Identifie la phase**
   - Extraction Notion ?
   - Import SiYuan ?
   - Création AVs ?

2. **Vérifie les prerequisites**
   - `.env` correct ?
   - Tokens valides ?
   - AVs créées manuellement ?

3. **Teste isolément**
   - `python3 debug_notion_permissions.py`
   - Test 1 database avec `TEST_LIMIT=1`

4. **Consulte les logs**
   - Messages d'erreur exacts
   - Code HTTP (401, 404, 429, etc.)

5. **Cherche dans ce fichier**
   - Erreur similaire documentée ?
   - Solution proposée ?

6. **Fallback**
   - Restore snapshot SiYuan
   - Réinitialise l'environnement
   - Recommence depuis Phase 1

---

## 📝 Erreurs documentées mais résolues

### ✅ "RESOLU : Lambda not allowed in Odoo Online"

**Contexte** : Version initiale du migrator

**Solution** : Réécriture sans lambda, utilisation de boucles classiques

### ✅ "RESOLU : APIs SiYuan createAttributeView non disponibles"

**Contexte** : Tentative de création programmatique des AVs

**Solution** : Approche hybride (création manuelle + import automatique)

### ✅ "RESOLU : Filtrage par page parente récursif trop lent"

**Contexte** : Script `extract_para_databases.py`

**Solution** : Extraction sans filtre + mapping manuel si nécessaire

---

## 🆘 Cas d'urgence

### Import raté, données corrompues

```bash
# 1. Restore snapshot SiYuan immédiatement
# 2. Supprime import_mapping.json
rm migration_output/import_mapping.json

# 3. Recommence l'import
export DRY_RUN=true
python3 import_data_to_siyuan.py
```

### Migration_plan.json corrompu

```bash
# Réextraire depuis Notion
python3 extract_by_workspace.py

# Vérifier le JSON
python3 -m json.tool migration_output/migration_plan.json
```

### Tout est cassé, recommencer from scratch

```bash
# 1. Nettoyer
rm -rf migration_output/*
rm -rf venv/

# 2. Réinstaller
./setup_migrator.sh

# 3. Reconfigurer
cp .env.example .env
nano .env

# 4. Recommencer Phase 1
source activate_migrator.sh
python3 extract_by_workspace.py
```

---

## 💡 Tips avancés

### Débugger l'extraction Notion

```python
# Ajoute des prints dans extract_by_workspace.py
print(f"DEBUG: Database {db_id} - Properties: {len(properties)}")
print(f"DEBUG: Property {prop_name} - Type: {prop_type}")
```

### Vérifier les attributes importés dans SiYuan

```bash
# Via API
curl -X POST http://192.168.1.11:6806/api/attr/getBlockAttrs \
  -H "Authorization: token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id": "BLOCK_ID"}'
```

### Tester la conversion de types

```python
# Dans un script Python
from import_data_to_siyuan import PropertyConverter

converter = PropertyConverter()
result = converter.convert_property_value("select", {"name": "In Progress"})
print(result)  # Doit afficher: "In Progress"
```

---

**✨ Si ton problème n'est pas listé ici, documente-le après l'avoir résolu ! ✨**
