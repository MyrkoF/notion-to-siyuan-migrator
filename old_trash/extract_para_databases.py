#!/usr/bin/env python3
"""
Notion to SiYuan - Extraction ciblée PARA uniquement
avec détection améliorée des types
"""

import requests
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# =============================================================================
# CONFIGURATION
# =============================================================================

class Config:
    NOTION_TOKEN = os.getenv("NOTION_TOKEN")
    SIYUAN_URL = os.getenv("SIYUAN_URL", "http://192.168.1.11:6806")
    SIYUAN_TOKEN = os.getenv("SIYUAN_TOKEN")
    
    # 🎯 NOUVEAU : Filtrer par page parente
    FILTER_PARENT_PAGE_ID = os.getenv("FILTER_PARENT_PAGE_ID", None)  # ID de la page PARA
    
    # Notebook cible dans SiYuan (PARA existant)
    TARGET_NOTEBOOK_ID = os.getenv("TARGET_NOTEBOOK_ID", None)
    
    # Options
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "20"))
    DELAY_BETWEEN_CALLS = float(os.getenv("DELAY_BETWEEN_CALLS", "0.5"))
    DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
    
    OUTPUT_DIR = "migration_output"

# =============================================================================
# CLIENTS API
# =============================================================================

class NotionClient:
    """Client pour l'API Notion"""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
    
    def get_page(self, page_id: str) -> Dict:
        """Récupère une page"""
        response = requests.get(
            f"{self.base_url}/pages/{page_id}",
            headers=self.headers
        )
        return response.json() if response.status_code == 200 else {}
    
    def search_databases(self, parent_page_id: Optional[str] = None) -> List[Dict]:
        """Récupère toutes les databases, optionnellement filtrées par parent"""
        print("🔍 Extraction des databases Notion...")
        
        if parent_page_id:
            print(f"📌 Filtrage sous la page: {parent_page_id}")
        
        databases = []
        has_more = True
        start_cursor = None
        
        while has_more:
            payload = {
                "filter": {"property": "object", "value": "database"},
                "page_size": 100
            }
            if start_cursor:
                payload["start_cursor"] = start_cursor
            
            response = requests.post(
                f"{self.base_url}/search",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code != 200:
                print(f"❌ Erreur Notion API: {response.status_code}")
                break
            
            data = response.json()
            batch = data.get("results", [])
            
            # Filtrer par parent si demandé
            if parent_page_id:
                batch = [db for db in batch if self._is_child_of(db, parent_page_id)]
            
            databases.extend(batch)
            
            has_more = data.get("has_more", False)
            start_cursor = data.get("next_cursor")
            
            time.sleep(Config.DELAY_BETWEEN_CALLS)
        
        print(f"✅ {len(databases)} databases trouvées")
        return databases
    
    def _is_child_of(self, item: Dict, parent_id: str) -> bool:
        """Vérifie si un item est enfant d'une page"""
        parent = item.get("parent", {})
        
        # Direct parent
        if parent.get("type") == "page_id" and parent.get("page_id") == parent_id:
            return True
        
        # Récursif : vérifier le parent du parent
        if parent.get("type") == "page_id":
            parent_page_id = parent.get("page_id")
            parent_page = self.get_page(parent_page_id)
            if parent_page:
                return self._is_child_of(parent_page, parent_id)
        
        return False


class TypeDetector:
    """Détecte les vrais types des propriétés Notion"""
    
    @staticmethod
    def detect_property_type(prop_name: str, prop_data: Dict) -> str:
        """
        Détecte le vrai type d'une propriété
        
        Améliorations :
        - Status Notion → select (pas text)
        - Rollups → détection + config
        - Files → asset
        """
        notion_type = prop_data.get("type")
        
        # Status Notion (type spécial)
        if notion_type == "status":
            return "select"  # Dans SiYuan = select
        
        # Rollup - détecter la config
        if notion_type == "rollup":
            rollup_config = prop_data.get("rollup", {})
            return {
                "type": "rollup",
                "relation_property": rollup_config.get("relation_property_name") or rollup_config.get("relation_property_id"),
                "rollup_property": rollup_config.get("rollup_property_name") or rollup_config.get("rollup_property_id"),
                "function": rollup_config.get("function", "count")
            }
        
        # Formula
        if notion_type == "formula":
            formula_config = prop_data.get("formula", {})
            return {
                "type": "formula",
                "expression": formula_config.get("expression", "")
            }
        
        # Files → asset dans SiYuan
        if notion_type == "files":
            # Vérifier le nom pour détecter si c'est une cover image
            if "cover" in prop_name.lower() or "image" in prop_name.lower():
                return "asset"  # Type spécial SiYuan pour médias
            return "text"  # URLs en texte
        
        # Mapping standard
        mapping = {
            "title": "text",
            "rich_text": "text",
            "number": "number",
            "select": "select",
            "multi_select": "multi-select",
            "date": "date",
            "checkbox": "checkbox",
            "url": "url",
            "email": "email",
            "phone_number": "phone",
            "relation": "relation",
            "people": "text",
            "created_time": "date",
            "created_by": "text",
            "last_edited_time": "date",
            "last_edited_by": "text"
        }
        
        return mapping.get(notion_type, "text")


class MigrationAnalyzer:
    """Analyse et prépare le plan de migration"""
    
    def __init__(self):
        self.notion_client = NotionClient(Config.NOTION_TOKEN)
        self.type_detector = TypeDetector()
    
    def analyze(self) -> Dict:
        """Analyse complète"""
        print("\n" + "="*80)
        print("📊 ANALYSE DES DATABASES NOTION")
        print("="*80 + "\n")
        
        # Extraire les databases
        databases = self.notion_client.search_databases(
            parent_page_id=Config.FILTER_PARENT_PAGE_ID
        )
        
        if not databases:
            print("⚠️  Aucune database trouvée")
            return {"databases": [], "databases_count": 0}
        
        # Analyser chaque database
        analyzed = []
        
        for db in databases:
            db_id = db["id"]
            title = "".join([t.get("plain_text", "") for t in db.get("title", [])]) or "Sans titre"
            
            print(f"📊 Analyse: {title}")
            
            properties = db.get("properties", {})
            analyzed_props = []
            
            for prop_name, prop_data in properties.items():
                detected_type = self.type_detector.detect_property_type(prop_name, prop_data)
                
                prop_info = {
                    "name": prop_name,
                    "notion_type": prop_data.get("type"),
                    "siyuan_type": detected_type if isinstance(detected_type, str) else detected_type["type"]
                }
                
                # Ajouter config pour rollup/formula
                if isinstance(detected_type, dict):
                    prop_info.update(detected_type)
                
                # Ajouter relation target
                if prop_data.get("type") == "relation":
                    prop_info["relation_to"] = prop_data.get("relation", {}).get("database_id")
                
                # Ajouter select options
                if prop_data.get("type") in ["select", "multi_select", "status"]:
                    options_key = "status" if prop_data.get("type") == "status" else prop_data.get("type")
                    options = prop_data.get(options_key, {}).get("options", [])
                    prop_info["options"] = [{"name": opt["name"], "color": opt.get("color")} for opt in options]
                
                analyzed_props.append(prop_info)
            
            analyzed.append({
                "id": db_id,
                "title": title,
                "parent": db.get("parent", {}),
                "properties_count": len(analyzed_props),
                "properties": analyzed_props
            })
        
        return {
            "timestamp": datetime.now().isoformat(),
            "mode": "ANALYSIS",
            "filter_parent": Config.FILTER_PARENT_PAGE_ID,
            "databases_count": len(analyzed),
            "databases": analyzed
        }
    
    def save_analysis(self, analysis: Dict):
        """Sauvegarde l'analyse"""
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
        
        output_file = os.path.join(Config.OUTPUT_DIR, "para_migration_plan.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Analyse sauvegardée: {output_file}")
        
        # Générer aussi le guide de création
        self._generate_creation_guide(analysis)
    
    def _generate_creation_guide(self, analysis: Dict):
        """Génère le guide de création amélioré"""
        guide_file = os.path.join(Config.OUTPUT_DIR, "para_creation_guide.txt")
        
        with open(guide_file, "w", encoding="utf-8") as f:
            f.write("="*80 + "\n")
            f.write("GUIDE DE CRÉATION - DATABASES PARA\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"📊 Databases à créer: {analysis['databases_count']}\n")
            if analysis.get('filter_parent'):
                f.write(f"📌 Scope: Seulement sous PARA\n")
            f.write("\n")
            
            for idx, db in enumerate(analysis["databases"], 1):
                f.write(f"\n{'='*80}\n")
                f.write(f"DATABASE {idx}/{analysis['databases_count']}: {db['title']}\n")
                f.write(f"{'='*80}\n\n")
                
                # Grouper par type
                by_type = {}
                for prop in db["properties"]:
                    ptype = prop["siyuan_type"]
                    if ptype not in by_type:
                        by_type[ptype] = []
                    by_type[ptype].append(prop)
                
                # Afficher par type avec détails
                for ptype, props in sorted(by_type.items()):
                    f.write(f"\n📌 {ptype.upper()}\n")
                    f.write("-" * 40 + "\n")
                    
                    for prop in props:
                        line = f"[ ] {prop['name']}"
                        
                        # Détails spéciaux
                        if ptype == "select" and prop.get("options"):
                            opts = [o["name"] for o in prop["options"][:3]]
                            line += f" (options: {', '.join(opts)}...)"
                        elif ptype == "relation":
                            target = prop.get("relation_to", "???")
                            target_db = next((d for d in analysis["databases"] if d["id"] == target), None)
                            target_name = target_db["title"] if target_db else "???"
                            line += f" → {target_name}"
                        elif ptype == "rollup":
                            line += f" (rollup: {prop.get('function', 'count')})"
                        elif ptype == "formula":
                            line += " (formula - calculé)"
                        elif ptype == "asset":
                            line += " (fichier/image)"
                        
                        f.write(line + "\n")
                
                f.write("\n")
        
        print(f"💾 Guide de création: {guide_file}")


# =============================================================================
# POINT D'ENTRÉE
# =============================================================================

def main():
    """Point d'entrée"""
    
    if not Config.NOTION_TOKEN:
        print("❌ NOTION_TOKEN non défini")
        return
    
    if not Config.SIYUAN_TOKEN:
        print("❌ SIYUAN_TOKEN non défini")
        return
    
    if not Config.FILTER_PARENT_PAGE_ID:
        print("⚠️  FILTER_PARENT_PAGE_ID non défini")
        print("   On va extraire TOUTES les databases")
        print("   Pour filtrer seulement PARA:")
        print("   export FILTER_PARENT_PAGE_ID=id-de-la-page-para")
        print()
    
    # Lancer l'analyse
    analyzer = MigrationAnalyzer()
    analysis = analyzer.analyze()
    analyzer.save_analysis(analysis)
    
    print("\n" + "="*80)
    print("✅ ANALYSE TERMINÉE")
    print("="*80 + "\n")
    
    print("📋 Prochaines étapes:")
    print("1. Vérifier para_migration_plan.json")
    print("2. Créer les Attribute Views dans SiYuan/PARA")
    print("3. Lancer l'import des données\n")


if __name__ == "__main__":
    main()
