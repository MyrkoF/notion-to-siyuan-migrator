#!/usr/bin/env python3
"""
Analyse rapide des databases Notion
Lance ce script pour voir la structure de tes databases
"""

import requests
import os
import json

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_API_URL = "https://api.notion.com/v1"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# Search for databases
response = requests.post(
    f"{NOTION_API_URL}/search",
    headers=headers,
    json={
        "filter": {"property": "object", "value": "database"},
        "page_size": 100
    }
)

data = response.json()
databases = data.get("results", [])

print(f"\n🗄️  DATABASES TROUVÉES: {len(databases)}\n")
print("="*80)

relations_map = []

for idx, db in enumerate(databases, 1):
    db_id = db.get("id")
    title_list = db.get("title", [])
    title = "".join([t.get("plain_text", "") for t in title_list]) or "Sans titre"
    
    print(f"\n{idx}. 📊 {title}")
    print(f"   ID: {db_id}")
    print(f"   URL: {db.get('url', 'N/A')}")
    
    # Get properties
    properties = db.get("properties", {})
    print(f"   Propriétés ({len(properties)}):")
    
    for prop_name, prop_data in properties.items():
        prop_type = prop_data.get("type")
        
        if prop_type == "relation":
            relation_db_id = prop_data.get("relation", {}).get("database_id")
            print(f"      - {prop_name}: {prop_type} → {relation_db_id}")
            relations_map.append({
                "from_db": title,
                "from_db_id": db_id,
                "property": prop_name,
                "to_db_id": relation_db_id
            })
        else:
            print(f"      - {prop_name}: {prop_type}")

print("\n" + "="*80)
print(f"\n🔗 RELATIONS TROUVÉES: {len(relations_map)}\n")

if relations_map:
    for rel in relations_map:
        print(f"   {rel['from_db']} --[{rel['property']}]--> {rel['to_db_id']}")

# Sauvegarder l'analyse
output = {
    "databases": databases,
    "relations": relations_map,
    "total_databases": len(databases),
    "total_relations": len(relations_map)
}

with open("notion_databases_analysis.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"\n💾 Analyse sauvegardée dans: notion_databases_analysis.json")
print("\n" + "="*80)
