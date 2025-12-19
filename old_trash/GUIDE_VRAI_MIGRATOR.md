# 🎯 VRAI MIGRATOR - Guide d'utilisation

## ✅ Ce que fait ce nouveau script

**ENFIN un vrai migrator qui gère les databases !**

### Phase 1 : Analyse (DRY_RUN)
1. ✅ Extrait toutes les databases Notion (39 dans ton cas)
2. ✅ Analyse leurs schémas (propriétés, types, relations)
3. ✅ Génère un plan de migration détaillé
4. ✅ Sauvegarde l'analyse en JSON

### Phase 2 : Migration réelle
1. ✅ Crée un snapshot SiYuan (sécurité)
2. ✅ Crée un notebook dédié "Notion Migration YYYYMMDD"
3. ✅ **Crée les Attribute Views dans SiYuan** (via API /api/av/)
4. ✅ Mappe Notion DB → SiYuan Attribute View
5. ⚠️  Import des entrées (Phase 3, à implémenter)

## 🚀 Utilisation

### Test avec 1 seule database (recommandé)

```bash
cd ~/GIT/notion-to-siyuan-migrator
source venv/bin/activate
source ~/.notion_siyuan_migrator.env

# Mode test
export DRY_RUN=true
python3 notion_to_siyuan_complete.py
```

Ça va créer `migration_output/migration_plan.json` avec toute l'analyse.

### Migration réelle

⚠️ **AVANT de lancer** :

1. **Vérifie que l'API SiYuan /api/av/ fonctionne**
   
   Le script utilise `/api/av/createAttributeView` qui **n'est PAS documenté officiellement**.
   
   Cette API est utilisée par le plugin `siyuan-database-properties-panel`.
   
   Si elle ne fonctionne pas, on devra :
   - Créer les Attribute Views manuellement
   - Ou trouver un autre moyen (via plugin)

2. **Lance la migration**

```bash
export DRY_RUN=false
python3 notion_to_siyuan_complete.py
```

## 📊 Ce qui est créé

```
migration_output/
├── migration_plan.json       # Plan détaillé (mode DRY_RUN)
└── id_mapping.json            # Notion DB → SiYuan AV mapping
```

## ⚠️ Limitations actuelles

### ✅ Implémenté
- Extraction databases Notion
- Conversion schémas
- Création Attribute Views SiYuan
- Mapping des IDs

### ⚠️ En cours (Phase 3)
- **Import des entrées** dans les Attribute Views
- Reconnexion des relations entre databases
- Import du contenu des pages

### ❌ Perdus (besoin recréation manuelle)
- Vues de databases (Kanban, Calendar, etc.)
- Formules et Rollups (calculés)
- Filtres et sorts

## 🔧 Variables d'environnement

```bash
# Requis
export NOTION_TOKEN="ton_token"
export SIYUAN_TOKEN="ton_token"
export SIYUAN_URL="http://192.168.1.11:6806"

# Optionnels
export TARGET_NOTEBOOK_ID="notebook-id"  # Sinon crée un nouveau
export BATCH_SIZE=20
export DRY_RUN=true
export CREATE_SNAPSHOTS=true
```

## 🎯 Workflow recommandé

### Étape 1 : Test analyse
```bash
export DRY_RUN=true
python3 notion_to_siyuan_complete.py
```

Vérifie `migration_output/migration_plan.json`

### Étape 2 : Test 1 database
Modifie le script pour limiter à 1 database :
```python
# Ligne ~220, dans run()
notion_databases = notion_databases[:1]  # Prendre seulement la première
```

Puis :
```bash
export DRY_RUN=false
python3 notion_to_siyuan_complete.py
```

Vérifie dans SiYuan si l'Attribute View est créée correctement.

### Étape 3 : Migration complète
Si tout marche :
```bash
# Retirer la limitation
python3 notion_to_siyuan_complete.py
```

## 🆘 Si l'API /api/av/ ne marche pas

**Plan B : Création manuelle**

1. Le script génère `migration_plan.json`
2. Pour chaque database :
   - Créer manuellement l'Attribute View dans SiYuan
   - Copier les propriétés depuis le plan
3. Utiliser un script d'import pour peupler les données

**Plan C : Via plugin**

Installer `siyuan-database-properties-panel` et voir si on peut scripter via lui.

## 🔍 Debug

Le script affiche beaucoup d'infos :
- ✅ Succès en vert
- ❌ Erreurs en rouge
- ⚠️  Warnings en jaune

Si échec création Attribute View, le message indique si c'est un problème d'API.

## 💡 Prochaines étapes

Une fois les Attribute Views créées, il faudra :

1. **Importer les entrées**
   - Extraire de Notion
   - Convertir en format SiYuan
   - Insérer via API

2. **Reconnecter les relations**
   - Utiliser `id_mapping.json`
   - Recréer les liens entre databases

3. **Importer le contenu texte**
   - Pages Notion → Documents SiYuan
   - Préserver la hiérarchie

---

**Lance le test maintenant** :
```bash
export DRY_RUN=true
python3 notion_to_siyuan_complete.py
```

Et montre-moi `migration_output/migration_plan.json` ! 🚀
