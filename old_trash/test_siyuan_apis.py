#!/usr/bin/env python3
"""
Test des APIs SiYuan disponibles
"""

import requests
import os

SIYUAN_URL = os.getenv("SIYUAN_URL", "http://192.168.1.11:6806")
SIYUAN_TOKEN = os.getenv("SIYUAN_TOKEN")

headers = {
    "Authorization": f"token {SIYUAN_TOKEN}",
    "Content-Type": "application/json"
}

print("\n🔍 TEST DES APIs SIYUAN DISPONIBLES\n")
print("="*80)

# Liste d'APIs à tester
apis_to_test = [
    # Système
    ("/api/system/version", {}),
    ("/api/system/currentTime", {}),
    ("/api/system/getConf", {}),
    
    # Notebooks
    ("/api/notebook/lsNotebooks", {}),
    
    # Attribute Views (supposées)
    ("/api/av/getAttributeView", {}),
    ("/api/av/createAttributeView", {"name": "test"}),
    ("/api/av/renderAttributeView", {}),
    
    # Snapshots
    ("/api/snapshot/getSnapshot", {}),
    ("/api/system/createSnapshot", {"memo": "test"}),
    
    # Blocks/Documents
    ("/api/block/getBlockInfo", {}),
    ("/api/filetree/listDocTree", {}),
]

for endpoint, payload in apis_to_test:
    print(f"\n📍 Testing: {endpoint}")
    
    try:
        response = requests.post(
            f"{SIYUAN_URL}{endpoint}",
            headers=headers,
            json=payload,
            timeout=5
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ OK - Code: {data.get('code')}, Msg: {data.get('msg', 'N/A')}")
        elif response.status_code == 404:
            print(f"   ❌ 404 - API non disponible")
        else:
            print(f"   ⚠️  {response.status_code} - {response.text[:100]}")
    
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n" + "="*80)
print("\n💡 APIs qui fonctionnent = celles avec ✅ OK\n")
