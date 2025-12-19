# 🔑 Guide Authentification GitHub - Push rapide

## 🎯 Objectif
Pousser le code de `/home/claude` vers ton repo GitHub : 
**https://github.com/MyrkoF/notion-to-siyuan-migrator**

## ⚡ Méthode la plus simple (Personal Access Token)

### Étape 1 : Créer un token GitHub

1. Va sur : **https://github.com/settings/tokens**
2. Clique **"Generate new token" → "Generate new token (classic)"**
3. Configuration :
   - Name: `Notion Migrator Push`
   - Expiration: `90 days` (ou `No expiration`)
   - Permissions: Coche ✅ **`repo`** (full control)
4. Clique **"Generate token"**
5. **⚠️ COPIE LE TOKEN IMMÉDIATEMENT** (tu ne pourras plus le voir)

### Étape 2 : Configurer Git avec le token

```bash
cd /home/claude

# Option A: URL avec token (pour un seul push)
git remote set-url origin https://TON_TOKEN@github.com/MyrkoF/notion-to-siyuan-migrator.git

# Puis push
git push -u origin main

# Ensuite, retire le token de l'URL (sécurité)
git remote set-url origin https://github.com/MyrkoF/notion-to-siyuan-migrator.git
```

### Étape 3 : Push automatique avec le script

```bash
cd /home/claude
./push_to_myrkof_repo.sh
```

## 🔐 Alternative : Credential Helper (stockage sécurisé)

Si tu ne veux pas mettre le token dans l'URL :

```bash
cd /home/claude

# Activer le credential helper
git config --global credential.helper store

# Première fois, Git te demandera user + token
git push -u origin main
# Username: MyrkoF
# Password: [COLLE TON TOKEN ICI]

# Les fois suivantes, ce sera automatique !
```

Le token sera stocké dans `~/.git-credentials` (fichier texte, donc à protéger).

## 🔑 Alternative : SSH (si déjà configuré)

Si tu as déjà des clés SSH configurées sur GitHub :

```bash
cd /home/claude

# Changer l'URL vers SSH
git remote set-url origin git@github.com:MyrkoF/notion-to-siyuan-migrator.git

# Push
git push -u origin main
```

## ✅ Vérification après push

Une fois le push réussi, vérifie sur GitHub :

1. **Repo accessible** : https://github.com/MyrkoF/notion-to-siyuan-migrator
2. **Les fichiers sont là** (11 fichiers)
3. **2 commits visibles** :
   - `🎉 Initial commit: Complete Notion to SiYuan migration toolkit`
   - `docs: Add contribution guidelines and GitHub push script`
4. **README.md s'affiche bien** en page d'accueil

## 🔒 Sécurité

### ✅ Vérifier que le repo est PRIVÉ

```
https://github.com/MyrkoF/notion-to-siyuan-migrator/settings
→ Danger Zone → Change visibility
→ Doit être sur "Private" 🔒
```

### ✅ Vérifier qu'aucun fichier sensible n'est présent

Sur GitHub, vérifie que tu vois :
- ✅ `.env.example` (template vide)
- ❌ PAS de `.env` (avec tes vrais tokens)
- ❌ PAS de `migration_output/`
- ❌ PAS de fichiers de config perso

## 🆘 Dépannage

### Erreur : "Authentication failed"

**Solution :**
```bash
# Vérifier que le token a les bonnes permissions (repo)
# Regénérer un nouveau token si besoin
# Réessayer avec la méthode "URL avec token"
```

### Erreur : "remote: Repository not found"

**Causes possibles :**
1. Le repo n'existe pas encore → Va le créer sur GitHub
2. Mauvais nom de repo → Vérifie l'URL
3. Token sans permissions → Vérifie les permissions du token

**Solution :**
```bash
# Vérifier l'URL du remote
git remote -v

# Si besoin, la corriger
git remote set-url origin https://github.com/MyrkoF/notion-to-siyuan-migrator.git
```

### Erreur : "refusing to merge unrelated histories"

**Cause :** Le repo GitHub a été initialisé avec des fichiers (README, .gitignore)

**Solution :**
```bash
# Forcer le push (attention, écrase ce qui est sur GitHub)
git push -u origin main --force

# Ou fusionner les historiques
git pull origin main --allow-unrelated-histories
git push -u origin main
```

## 📞 Support

Si ça ne marche toujours pas :
1. Copie l'erreur exacte
2. Vérifie que le repo existe sur GitHub
3. Vérifie que le token a les bonnes permissions

## 🎯 TL;DR - Version Express

```bash
# 1. Créer token sur https://github.com/settings/tokens (permission: repo)

# 2. Push avec le token
cd /home/claude
git remote set-url origin https://TON_TOKEN@github.com/MyrkoF/notion-to-siyuan-migrator.git
git push -u origin main

# 3. Nettoyer
git remote set-url origin https://github.com/MyrkoF/notion-to-siyuan-migrator.git

# 4. Vérifier sur GitHub
# https://github.com/MyrkoF/notion-to-siyuan-migrator
```

C'est tout ! 🚀
