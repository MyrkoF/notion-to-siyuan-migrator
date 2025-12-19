#!/usr/bin/env python3
"""
Génère les instructions de création manuelle des Attribute Views
Basé sur migration_plan.json
"""

import json

with open("migration_output/migration_plan.json") as f:
    plan = json.load(f)

print("\n" + "="*80)
print("📋 GUIDE DE CRÉATION MANUELLE DES ATTRIBUTE VIEWS")
print("="*80 + "\n")

print("Total databases à créer : {}\n".format(plan["databases_count"]))

for idx, db in enumerate(plan["databases"], 1):
    print(f"\n{'='*80}")
    print(f"DATABASE {idx}/{plan['databases_count']}: {db['title']}")
    print(f"{'='*80}\n")
    
    print(f"📊 Nombre de colonnes : {db['properties_count']}\n")
    
    # Grouper par type
    by_type = {}
    relations = []
    
    for prop in db["properties"]:
        prop_type = prop["siyuan_type"]
        if prop_type not in by_type:
            by_type[prop_type] = []
        by_type[prop_type].append(prop)
        
        if prop_type == "relation":
            relations.append(prop)
    
    # Afficher par type
    for prop_type, props in sorted(by_type.items()):
        print(f"\n📌 Type: {prop_type.upper()} ({len(props)} colonnes)")
        print("-" * 40)
        
        for prop in props:
            if prop_type == "relation":
                rel_db_id = prop.get("relation_to", "???")
                # Trouver le nom de la DB cible
                target_db = next((d for d in plan["databases"] if d["id"] == rel_db_id), None)
                target_name = target_db["title"] if target_db else "???"
                print(f"   - {prop['name']} → Relation vers '{target_name}'")
            else:
                print(f"   - {prop['name']}")
    
    # Instructions spéciales pour les relations
    if relations:
        print(f"\n🔗 RELATIONS À CRÉER ({len(relations)}):")
        print("-" * 40)
        for rel in relations:
            rel_db_id = rel.get("relation_to", "???")
            target_db = next((d for d in plan["databases"] if d["id"] == rel_db_id), None)
            target_name = target_db["title"] if target_db else "???"
            print(f"   '{rel['name']}' → '{target_name}' (créer cette AV d'abord !)")
    
    # Checklist
    print(f"\n✅ CHECKLIST:")
    print("-" * 40)
    print("   [ ] Créer l'Attribute View avec le nom ci-dessus")
    print(f"   [ ] Ajouter les {db['properties_count']} colonnes")
    print("   [ ] Définir les types corrects pour chaque colonne")
    if relations:
        print(f"   [ ] Configurer les {len(relations)} relation(s)")
    print()

print("\n" + "="*80)
print("💡 ORDRE DE CRÉATION RECOMMANDÉ")
print("="*80 + "\n")

# Analyser l'ordre optimal (databases sans dépendances d'abord)
no_deps = []
with_deps = []

for db in plan["databases"]:
    has_relation = any(p["siyuan_type"] == "relation" for p in db["properties"])
    if has_relation:
        with_deps.append(db["title"])
    else:
        no_deps.append(db["title"])

print("1️⃣ CRÉER D'ABORD (sans relations) :")
for name in no_deps[:10]:
    print(f"   - {name}")
if len(no_deps) > 10:
    print(f"   ... et {len(no_deps) - 10} autres")

print("\n2️⃣ PUIS CRÉER (avec relations) :")
for name in with_deps[:10]:
    print(f"   - {name}")
if len(with_deps) > 10:
    print(f"   ... et {len(with_deps) - 10} autres")

print("\n" + "="*80 + "\n")

print("💾 Instructions complètes sauvegardées dans :")
print("   → migration_output/manual_creation_guide.txt\n")

# Sauvegarder aussi en fichier texte
with open("migration_output/manual_creation_guide.txt", "w", encoding="utf-8") as f:
    f.write("="*80 + "\n")
    f.write("GUIDE DE CRÉATION MANUELLE DES ATTRIBUTE VIEWS\n")
    f.write("="*80 + "\n\n")
    
    for idx, db in enumerate(plan["databases"], 1):
        f.write(f"\n{'='*80}\n")
        f.write(f"DATABASE {idx}/{plan['databases_count']}: {db['title']}\n")
        f.write(f"{'='*80}\n\n")
        
        for prop in db["properties"]:
            if prop["siyuan_type"] == "relation":
                rel_db_id = prop.get("relation_to", "???")
                target_db = next((d for d in plan["databases"] if d["id"] == rel_db_id), None)
                target_name = target_db["title"] if target_db else "???"
                f.write(f"[ ] {prop['name']} ({prop['siyuan_type']}) → {target_name}\n")
            else:
                f.write(f"[ ] {prop['name']} ({prop['siyuan_type']})\n")
        
        f.write(f"\n")

print("✅ Terminé !\n")
