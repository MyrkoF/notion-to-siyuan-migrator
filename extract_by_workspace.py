#!/usr/bin/env python3
"""
Notion to SiYuan - Extraction par WORKSPACE
Permet de choisir quel espace de travail Notion extraire
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
    
    # 🎯 FILTRAGE PAR WORKSPACE
    # Si vide, liste tous les workspaces disponibles
    # Si défini, extrait seulement ce workspace
    FILTER_WORKSPACE = os.getenv("FILTER_WORKSPACE", None)
    
    # Options
    DELAY_BETWEEN_CALLS = float(os.getenv("DELAY_BETWEEN_CALLS", "0.5"))
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
    
    def list_workspaces(self) -> List[Dict]:
        """Liste tous les workspaces accessibles"""
        print("🔍 Recherche des workspaces Notion...")
        
        # On va chercher toutes les pages top-level
        # Chaque workspace aura son propre parent
        all_items = []
        has_more = True
        start_cursor = None
        
        while has_more:
            payload = {
                "page_size": 100,
                "filter": {"property": "object", "value": "page"}
            }
            if start_cursor:
                payload["start_cursor"] = start_cursor
            
            response = requests.post(
                f"{self.base_url}/search",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code != 200:
                break
            
            data = response.json()
            all_items.extend(data.get("results", []))
            
            has_more = data.get("has_more", False)
            start_cursor = data.get("next_cursor")
            time.sleep(Config.DELAY_BETWEEN_CALLS)
        
        # Identifier les workspaces via les pages workspace
        workspaces = {}
        for item in all_items:
            parent = item.get("parent", {})
            if parent.get("type") == "workspace":
                workspace_id = parent.get("workspace")
                # Le workspace_id est True pour workspace racine
                # On utilise le titre de la page comme nom du workspace
                title = "".join([t.get("plain_text", "") for t in item.get("properties", {}).get("title", {}).get("title", [])])
                
                if workspace_id not in workspaces:
                    workspaces[workspace_id] = {
                        "id": workspace_id,
                        "name": title or "Workspace",
                        "pages": []
                    }
                workspaces[workspace_id]["pages"].append({
                    "id": item["id"],
                    "title": title
                })
        
        return list(workspaces.values())
    
    def search_databases(self, workspace_filter: Optional[str] = None) -> List[Dict]:
        """Récupère toutes les databases"""
        print("🔍 Extraction des databases Notion...")
        
        if workspace_filter:
            print(f"📌 Filtrage workspace: {workspace_filter}")
        
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
            
            # Filtrer par workspace si demandé
            if workspace_filter:
                batch = [db for db in batch if self._match_workspace(db, workspace_filter)]
            
            databases.extend(batch)
            
            has_more = data.get("has_more", False)
            start_cursor = data.get("next_cursor")
            
            time.sleep(Config.DELAY_BETWEEN_CALLS)
        
        print(f"✅ {len(databases)} databases trouvées")
        return databases
    
    def _match_workspace(self, db: Dict, workspace_name: str) -> bool:
        """Vérifie si une DB appartient à un workspace (match par nom)"""
        # Stratégie : on match par le nom du workspace dans le chemin
        # On récupère le parent et on remonte jusqu'à trouver une page workspace
        
        # Pour l'instant, simple match par titre contenu dans URL
        url = db.get("url", "")
        
        # Le workspace apparaît dans l'URL : notion.so/workspace-name/...
        workspace_slug = workspace_name.lower().replace(" ", "-")
        
        return workspace_slug in url.lower()


class TypeDetector:
    """Détecte les vrais types des propriétés Notion"""
    
    @staticmethod
    def detect_property_type(prop_name: str, prop_data: Dict) -> str:
        """Détecte le vrai type d'une propriété"""
        notion_type = prop_data.get("type")
        
        # Status Notion → select
        if notion_type == "status":
            return "select"
        
        # Rollup
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
        
        # Files → asset ou text
        if notion_type == "files":
            if "cover" in prop_name.lower() or "image" in prop_name.lower():
                return "asset"
            return "text"
        
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
    
    def run(self):
        """Point d'entrée principal"""
        print("\n" + "="*80)
        print("📊 NOTION TO SIYUAN - SÉLECTION WORKSPACE")
        print("="*80 + "\n")
        
        # Si pas de filtre, lister les workspaces
        if not Config.FILTER_WORKSPACE:
            print("ℹ️  Aucun workspace spécifié")
            print("   Extraction de TOUS les workspaces\n")
            print("💡 Pour filtrer un workspace spécifique:")
            print("   export FILTER_WORKSPACE='Equalium'")
            print("   export FILTER_WORKSPACE='PARA'\n")
            
            # Optionnel : Lister les workspaces disponibles
            print("📋 Détection des espaces de travail...")
            self._detect_workspaces()
            print()
        
        # Extraire les databases
        databases = self.notion_client.search_databases(
            workspace_filter=Config.FILTER_WORKSPACE
        )
        
        if not databases:
            print("\n⚠️  Aucune database trouvée")
            if Config.FILTER_WORKSPACE:
                print(f"   Avec le filtre workspace: {Config.FILTER_WORKSPACE}")
                print("   Essaie sans filtre pour voir toutes les DBs")
            return
        
        # Analyser
        analysis = self._analyze_databases(databases)
        self._save_analysis(analysis)
        
        print("\n" + "="*80)
        print("✅ ANALYSE TERMINÉE")
        print("="*80 + "\n")
    
    def _detect_workspaces(self):
        """Détecte et affiche les workspaces disponibles"""
        # Stratégie simple : regarder les URLs des databases
        all_dbs = self.notion_client.search_databases()
        
        workspaces = set()
        for db in all_dbs:
            url = db.get("url", "")
            # Extraire le workspace de l'URL
            # Format : https://www.notion.so/workspace-name/db-name-id
            parts = url.split("/")
            if len(parts) >= 4:
                workspace_part = parts[3]  # workspace-name
                if workspace_part and not workspace_part.startswith("db"):
                    workspaces.add(workspace_part)
        
        if workspaces:
            print(f"   Workspaces détectés dans les URLs : {len(workspaces)}")
            for ws in sorted(workspaces):
                print(f"      - {ws}")
        else:
            print("   Impossible de détecter les workspaces automatiquement")
    
    def _analyze_databases(self, databases: List[Dict]) -> Dict:
        """Analyse les databases"""
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
                
                # Config rollup/formula
                if isinstance(detected_type, dict):
                    prop_info.update(detected_type)
                
                # Relation target
                if prop_data.get("type") == "relation":
                    prop_info["relation_to"] = prop_data.get("relation", {}).get("database_id")
                
                # Select options
                if prop_data.get("type") in ["select", "multi_select", "status"]:
                    options_key = "status" if prop_data.get("type") == "status" else prop_data.get("type")
                    options = prop_data.get(options_key, {}).get("options", [])
                    prop_info["options"] = [{"name": opt["name"], "color": opt.get("color")} for opt in options]
                
                analyzed_props.append(prop_info)
            
            analyzed.append({
                "id": db_id,
                "title": title,
                "url": db.get("url"),
                "properties_count": len(analyzed_props),
                "properties": analyzed_props
            })
        
        return {
            "timestamp": datetime.now().isoformat(),
            "workspace_filter": Config.FILTER_WORKSPACE,
            "databases_count": len(analyzed),
            "databases": analyzed
        }
    
    def _save_analysis(self, analysis: Dict):
        """Sauvegarde l'analyse"""
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
        
        # Nom du fichier selon filtre
        if analysis.get("workspace_filter"):
            filename = f"{analysis['workspace_filter'].lower()}_migration_plan.json"
        else:
            filename = "migration_plan.json"
        
        output_file = os.path.join(Config.OUTPUT_DIR, filename)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Analyse sauvegardée: {output_file}")
        
        # Guide de création
        self._generate_creation_guide(analysis, filename.replace("_plan.json", "_guide.txt"))
    
    def _generate_creation_guide(self, analysis: Dict, guide_filename: str):
        """Génère le guide de création"""
        guide_file = os.path.join(Config.OUTPUT_DIR, guide_filename)
        
        with open(guide_file, "w", encoding="utf-8") as f:
            f.write("="*80 + "\n")
            f.write("GUIDE DE CRÉATION DES ATTRIBUTE VIEWS\n")
            f.write("="*80 + "\n\n")
            
            if analysis.get('workspace_filter'):
                f.write(f"📌 Workspace: {analysis['workspace_filter']}\n")
            f.write(f"📊 Databases: {analysis['databases_count']}\n\n")
            
            for idx, db in enumerate(analysis["databases"], 1):
                f.write(f"\n{'='*80}\n")
                f.write(f"DATABASE {idx}/{analysis['databases_count']}: {db['title']}\n")
                f.write(f"URL: {db.get('url', 'N/A')}\n")
                f.write(f"{'='*80}\n\n")
                
                for prop in db["properties"]:
                    line = f"[ ] {prop['name']} ({prop['siyuan_type']})"
                    
                    # Détails
                    if prop['siyuan_type'] == "select" and prop.get("options"):
                        opts = [o["name"] for o in prop["options"][:3]]
                        line += f" - Options: {', '.join(opts)}"
                        if len(prop["options"]) > 3:
                            line += f" +{len(prop['options'])-3} autres"
                    elif prop['siyuan_type'] == "relation":
                        line += f" → DB: {prop.get('relation_to', '???')}"
                    elif prop['siyuan_type'] == "rollup":
                        line += f" - Rollup: {prop.get('function', 'count')}"
                    
                    f.write(line + "\n")
                
                f.write("\n")
        
        print(f"💾 Guide de création: {guide_file}")


# =============================================================================
# POINT D'ENTRÉE
# =============================================================================

def main():
    if not Config.NOTION_TOKEN:
        print("❌ NOTION_TOKEN non défini")
        return
    
    analyzer = MigrationAnalyzer()
    analyzer.run()


if __name__ == "__main__":
    main()
