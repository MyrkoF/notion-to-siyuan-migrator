#!/usr/bin/env python3
"""
Debug : Vérifier ce que l'intégration Notion peut voir
"""

import requests
import os
import json

NOTION_TOKEN = os.getenv("NOTION_TOKEN")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

print("\n🔍 DIAGNOSTIC DE L'INTÉGRATION NOTION\n")
print("="*80)

# Test 1: Search sans filtre
print("\n1️⃣ Test: Search sans filtre (tout)")
response = requests.post(
    "https://api.notion.com/v1/search",
    headers=headers,
    json={"page_size": 10}
)

if response.status_code == 200:
    data = response.json()
    results = data.get("results", [])
    print(f"   ✅ {len(results)} éléments trouvés")
    
    for item in results[:5]:
        obj_type = item.get("object")
        title = "Sans titre"
        
        if obj_type == "page":
            title_prop = item.get("properties", {}).get("title", {}).get("title", [])
            title = "".join([t.get("plain_text", "") for t in title_prop])
        elif obj_type == "database":
            title_list = item.get("title", [])
            title = "".join([t.get("plain_text", "") for t in title_list])
        
        print(f"      - [{obj_type}] {title[:50]}")
else:
    print(f"   ❌ Erreur {response.status_code}")
    print(f"      {response.text}")

# Test 2: Search databases uniquement
print("\n2️⃣ Test: Search databases uniquement")
response = requests.post(
    "https://api.notion.com/v1/search",
    headers=headers,
    json={
        "filter": {"property": "object", "value": "database"},
        "page_size": 100
    }
)

if response.status_code == 200:
    data = response.json()
    databases = data.get("results", [])
    print(f"   ✅ {len(databases)} databases trouvées")
    
    if databases:
        print("\n   📊 Liste des databases:")
        for idx, db in enumerate(databases[:10], 1):
            title = "".join([t.get("plain_text", "") for t in db.get("title", [])])
            url = db.get("url", "")
            print(f"      {idx}. {title}")
            print(f"         URL: {url}")
    else:
        print("\n   ⚠️  AUCUNE DATABASE ACCESSIBLE")
        print("   Causes possibles:")
        print("      1. L'intégration n'a pas été ajoutée aux databases")
        print("      2. Les databases sont dans un workspace différent")
        print("      3. Permissions insuffisantes")
else:
    print(f"   ❌ Erreur {response.status_code}")

# Test 3: Search pages
print("\n3️⃣ Test: Search pages")
response = requests.post(
    "https://api.notion.com/v1/search",
    headers=headers,
    json={
        "filter": {"property": "object", "value": "page"},
        "page_size": 20
    }
)

if response.status_code == 200:
    data = response.json()
    pages = data.get("results", [])
    print(f"   ✅ {len(pages)} pages trouvées")
    
    if pages:
        print("\n   📄 Premières pages:")
        for idx, page in enumerate(pages[:10], 1):
            title_prop = page.get("properties", {}).get("title", {}).get("title", [])
            title = "".join([t.get("plain_text", "") for t in title_prop])
            parent = page.get("parent", {})
            parent_type = parent.get("type", "???")
            print(f"      {idx}. {title[:50]} (parent: {parent_type})")
else:
    print(f"   ❌ Erreur {response.status_code}")

print("\n" + "="*80)
print("\n💡 SOLUTION:\n")
print("Si 0 databases mais des pages visibles:")
print("   → L'intégration voit l'espace mais pas les databases")
print("   → Il faut PARTAGER chaque database avec l'intégration\n")
print("Comment partager une database:")
print("   1. Ouvrir la database dans Notion")
print("   2. Clic sur '...' en haut à droite")
print("   3. 'Add connections' → Choisir ton intégration")
print("   4. Répéter pour chaque database\n")
print("OU utiliser l'ancien script qui fonctionnait (notion_databases_analysis.json)\n")
