#!/usr/bin/env python3
"""
Notion to SiYuan Complete Migrator
Gère correctement les Attribute Views (databases)
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
    
    # Options
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "20"))
    DELAY_BETWEEN_CALLS = float(os.getenv("DELAY_BETWEEN_CALLS", "0.5"))
    DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
    CREATE_SNAPSHOTS = os.getenv("CREATE_SNAPSHOTS", "true").lower() == "true"
    
    # Notebook cible dans SiYuan
    TARGET_NOTEBOOK_ID = os.getenv("TARGET_NOTEBOOK_ID", None)  # À définir
    
    # Dossier de sortie
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
    
    def search_databases(self) -> List[Dict]:
        """Récupère toutes les databases Notion"""
        print("🔍 Extraction des databases Notion...")
        
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
                print(response.text)
                break
            
            data = response.json()
            databases.extend(data.get("results", []))
            
            has_more = data.get("has_more", False)
            start_cursor = data.get("next_cursor")
            
            time.sleep(Config.DELAY_BETWEEN_CALLS)
        
        print(f"✅ {len(databases)} databases trouvées")
        return databases
    
    def query_database(self, database_id: str, page_size: int = 100) -> List[Dict]:
        """Récupère les entrées d'une database"""
        entries = []
        has_more = True
        start_cursor = None
        
        while has_more:
            payload = {"page_size": page_size}
            if start_cursor:
                payload["start_cursor"] = start_cursor
            
            response = requests.post(
                f"{self.base_url}/databases/{database_id}/query",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code != 200:
                print(f"❌ Erreur query database {database_id}: {response.status_code}")
                break
            
            data = response.json()
            entries.extend(data.get("results", []))
            
            has_more = data.get("has_more", False)
            start_cursor = data.get("next_cursor")
            
            time.sleep(Config.DELAY_BETWEEN_CALLS)
        
        return entries


class SiYuanClient:
    """Client pour l'API SiYuan"""
    
    def __init__(self, url: str, token: str):
        self.url = url
        self.token = token
        self.headers = {
            "Authorization": f"token {token}",
            "Content-Type": "application/json"
        }
    
    def _call_api(self, endpoint: str, data: Dict = None) -> Dict:
        """Appel générique à l'API SiYuan"""
        response = requests.post(
            f"{self.url}/api{endpoint}",
            headers=self.headers,
            json=data or {}
        )
        
        if response.status_code != 200:
            print(f"❌ Erreur SiYuan API {endpoint}: {response.status_code}")
            print(response.text)
            return {"code": -1, "msg": "Error", "data": None}
        
        return response.json()
    
    def list_notebooks(self) -> List[Dict]:
        """Liste tous les notebooks"""
        result = self._call_api("/notebook/lsNotebooks")
        return result.get("data", {}).get("notebooks", [])
    
    def create_notebook(self, name: str) -> Optional[str]:
        """Crée un nouveau notebook"""
        result = self._call_api("/notebook/createNotebook", {"name": name})
        if result.get("code") == 0:
            return result.get("data", {}).get("notebook", {}).get("id")
        return None
    
    def create_attribute_view(self, notebook_id: str, name: str, schema: Dict) -> Optional[str]:
        """
        Crée une Attribute View (database) dans SiYuan
        
        IMPORTANT: Cette API n'est PAS documentée officiellement dans l'API SiYuan.
        On se base sur le plugin siyuan-database-properties-panel qui utilise /api/av/
        
        Si cette API ne fonctionne pas, on devra créer les Attribute Views manuellement
        ou via un plugin.
        """
        print(f"⚠️  ATTENTION: Création d'Attribute View - API non officiellement documentée")
        print(f"   Si échec, création manuelle nécessaire: {name}")
        
        # Tentative avec l'API supposée (à ajuster selon tests)
        payload = {
            "notebook": notebook_id,
            "name": name,
            "schema": schema
        }
        
        result = self._call_api("/av/createAttributeView", payload)
        
        if result.get("code") == 0:
            av_id = result.get("data", {}).get("id")
            print(f"✅ Attribute View créée: {name} (ID: {av_id})")
            return av_id
        else:
            print(f"❌ Échec création Attribute View: {name}")
            print(f"   Message: {result.get('msg')}")
            return None
    
    def create_document(self, notebook_id: str, path: str, markdown: str) -> Optional[str]:
        """Crée un document dans SiYuan"""
        result = self._call_api("/filetree/createDocWithMd", {
            "notebook": notebook_id,
            "path": path,
            "markdown": markdown
        })
        
        if result.get("code") == 0:
            return result.get("data")
        return None
    
    def create_snapshot(self, memo: str = "Notion migration snapshot") -> bool:
        """Crée un snapshot avant migration"""
        result = self._call_api("/system/createSnapshot", {"memo": memo})
        return result.get("code") == 0


# =============================================================================
# CONVERSION ET MAPPING
# =============================================================================

class NotionToSiYuanConverter:
    """Convertit les structures Notion en SiYuan"""
    
    @staticmethod
    def convert_property_type(notion_type: str) -> str:
        """
        Convertit un type de propriété Notion vers SiYuan
        
        Mapping basé sur les types supportés par SiYuan Attribute Views:
        - text
        - number  
        - date
        - select
        - multi-select
        - checkbox
        - url
        - email
        - phone
        - relation
        """
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
            "rollup": "text",  # Rollups → texte (calcul perdu)
            "formula": "text",  # Formules → texte (calcul perdu)
            "people": "text",   # People → texte
            "files": "text",    # Files → texte (URLs)
            "created_time": "date",
            "created_by": "text",
            "last_edited_time": "date",
            "last_edited_by": "text"
        }
        
        return mapping.get(notion_type, "text")
    
    @staticmethod
    def convert_database_schema(notion_db: Dict) -> Dict:
        """Convertit le schéma d'une database Notion vers SiYuan"""
        properties = notion_db.get("properties", {})
        
        siyuan_schema = {
            "columns": []
        }
        
        for prop_name, prop_data in properties.items():
            prop_type = prop_data.get("type")
            siyuan_type = NotionToSiYuanConverter.convert_property_type(prop_type)
            
            column = {
                "name": prop_name,
                "type": siyuan_type
            }
            
            # Ajouter les options pour select/multi-select
            if prop_type in ["select", "multi_select"]:
                options = prop_data.get(prop_type, {}).get("options", [])
                column["options"] = [opt["name"] for opt in options]
            
            # Pour les relations, sauvegarder l'ID de la DB cible
            if prop_type == "relation":
                column["relation_db_id"] = prop_data.get("relation", {}).get("database_id")
            
            siyuan_schema["columns"].append(column)
        
        return siyuan_schema


# =============================================================================
# ORCHESTRATEUR PRINCIPAL
# =============================================================================

class MigrationOrchestrator:
    """Orchestre la migration complète"""
    
    def __init__(self):
        self.notion_client = NotionClient(Config.NOTION_TOKEN)
        self.siyuan_client = SiYuanClient(Config.SIYUAN_URL, Config.SIYUAN_TOKEN)
        self.converter = NotionToSiYuanConverter()
        
        # Mappings
        self.db_mapping = {}  # Notion DB ID → SiYuan AV ID
        self.page_mapping = {}  # Notion Page ID → SiYuan Doc ID
        
        # Statistiques
        self.stats = {
            "databases_found": 0,
            "databases_migrated": 0,
            "entries_migrated": 0,
            "errors": []
        }
    
    def run(self):
        """Point d'entrée principal de la migration"""
        print("\n" + "="*80)
        print("🚀 NOTION TO SIYUAN - MIGRATION COMPLÈTE")
        print("="*80 + "\n")
        
        print(f"Mode: {'🧪 DRY RUN (test)' if Config.DRY_RUN else '⚡ MIGRATION RÉELLE'}")
        print(f"URL SiYuan: {Config.SIYUAN_URL}")
        print(f"Batch size: {Config.BATCH_SIZE}")
        print()
        
        # Étape 0: Créer le dossier de sortie
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
        
        # Étape 1: Créer snapshot SiYuan
        if Config.CREATE_SNAPSHOTS and not Config.DRY_RUN:
            print("📸 Création d'un snapshot SiYuan...")
            if self.siyuan_client.create_snapshot():
                print("✅ Snapshot créé\n")
            else:
                print("⚠️  Échec création snapshot (continuer quand même)\n")
        
        # Étape 2: Identifier/créer le notebook cible
        target_notebook = self._setup_target_notebook()
        if not target_notebook:
            print("❌ Impossible de configurer le notebook cible")
            return
        
        # Étape 3: Extraire les databases Notion
        notion_databases = self.notion_client.search_databases()
        
        # 🧪 TEST: Limiter à 1 database pour le test
        if os.getenv("TEST_SINGLE_DB", "false").lower() == "true":
            print("🧪 MODE TEST: Limitation à 1 database")
            notion_databases = notion_databases[:1]
        
        self.stats["databases_found"] = len(notion_databases)
        
        if not notion_databases:
            print("⚠️  Aucune database trouvée dans Notion")
            return
        
        # Étape 4: Analyser et afficher le plan
        self._display_migration_plan(notion_databases)
        
        if Config.DRY_RUN:
            print("\n🧪 MODE DRY RUN - Analyse terminée sans import")
            self._save_analysis(notion_databases)
            return
        
        # Étape 5: Créer les Attribute Views dans SiYuan
        print("\n" + "="*80)
        print("📊 PHASE 1: Création des Attribute Views")
        print("="*80 + "\n")
        
        for db in notion_databases:
            self._migrate_database(db, target_notebook)
        
        # Étape 6: Importer les entrées (TODO: Phase 2)
        print("\n" + "="*80)
        print("📝 PHASE 2: Import des entrées (À IMPLÉMENTER)")
        print("="*80 + "\n")
        print("⚠️  Import des entrées non implémenté dans cette version")
        print("   Les Attribute Views sont créées, mais vides")
        print("   Prochaine étape: peupler les Attribute Views\n")
        
        # Étape 7: Rapport final
        self._display_final_report()
    
    def _setup_target_notebook(self) -> Optional[str]:
        """Configure le notebook cible pour la migration"""
        print("📓 Configuration du notebook cible...")
        
        notebooks = self.siyuan_client.list_notebooks()
        
        if Config.TARGET_NOTEBOOK_ID:
            # Vérifier que le notebook existe
            if any(nb["id"] == Config.TARGET_NOTEBOOK_ID for nb in notebooks):
                print(f"✅ Notebook cible: {Config.TARGET_NOTEBOOK_ID}\n")
                return Config.TARGET_NOTEBOOK_ID
            else:
                print(f"❌ Notebook {Config.TARGET_NOTEBOOK_ID} introuvable\n")
                return None
        
        # Créer un nouveau notebook pour la migration
        notebook_name = f"Notion Migration {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"📝 Création du notebook: {notebook_name}")
        
        notebook_id = self.siyuan_client.create_notebook(notebook_name)
        
        if notebook_id:
            print(f"✅ Notebook créé: {notebook_id}\n")
            return notebook_id
        else:
            print("❌ Échec création notebook\n")
            return None
    
    def _display_migration_plan(self, databases: List[Dict]):
        """Affiche le plan de migration"""
        print("\n" + "="*80)
        print("📋 PLAN DE MIGRATION")
        print("="*80 + "\n")
        
        # Analyser les relations
        relations_map = {}
        for db in databases:
            db_id = db["id"]
            title = "".join([t.get("plain_text", "") for t in db.get("title", [])]) or "Sans titre"
            
            props = db.get("properties", {})
            relations = [
                (name, prop.get("relation", {}).get("database_id"))
                for name, prop in props.items()
                if prop.get("type") == "relation"
            ]
            
            if relations:
                relations_map[db_id] = {
                    "title": title,
                    "relations": relations
                }
        
        print(f"✅ {len(databases)} databases à migrer")
        print(f"🔗 {len(relations_map)} databases avec relations\n")
        
        print("📊 Top 10 databases:")
        for idx, db in enumerate(databases[:10], 1):
            title = "".join([t.get("plain_text", "") for t in db.get("title", [])]) or "Sans titre"
            props_count = len(db.get("properties", {}))
            print(f"   {idx}. {title} ({props_count} propriétés)")
        
        if len(databases) > 10:
            print(f"   ... et {len(databases) - 10} autres\n")
    
    def _migrate_database(self, notion_db: Dict, notebook_id: str):
        """Migre une database Notion vers SiYuan Attribute View"""
        db_id = notion_db["id"]
        title = "".join([t.get("plain_text", "") for t in notion_db.get("title", [])]) or "Sans titre"
        
        print(f"📊 Migration: {title}")
        
        # Convertir le schéma
        schema = self.converter.convert_database_schema(notion_db)
        print(f"   → {len(schema['columns'])} colonnes")
        
        # Créer l'Attribute View dans SiYuan
        av_id = self.siyuan_client.create_attribute_view(notebook_id, title, schema)
        
        if av_id:
            self.db_mapping[db_id] = av_id
            self.stats["databases_migrated"] += 1
            print(f"   ✅ Créée (ID: {av_id})\n")
        else:
            self.stats["errors"].append(f"Échec création: {title}")
            print(f"   ❌ Échec\n")
    
    def _save_analysis(self, databases: List[Dict]):
        """Sauvegarde l'analyse en mode DRY_RUN"""
        output_file = os.path.join(Config.OUTPUT_DIR, "migration_plan.json")
        
        plan = {
            "timestamp": datetime.now().isoformat(),
            "mode": "DRY_RUN",
            "databases_count": len(databases),
            "databases": []
        }
        
        for db in databases:
            title = "".join([t.get("plain_text", "") for t in db.get("title", [])]) or "Sans titre"
            props = db.get("properties", {})
            
            db_info = {
                "id": db["id"],
                "title": title,
                "properties_count": len(props),
                "properties": []
            }
            
            for prop_name, prop_data in props.items():
                prop_info = {
                    "name": prop_name,
                    "notion_type": prop_data.get("type"),
                    "siyuan_type": self.converter.convert_property_type(prop_data.get("type"))
                }
                
                if prop_data.get("type") == "relation":
                    prop_info["relation_to"] = prop_data.get("relation", {}).get("database_id")
                
                db_info["properties"].append(prop_info)
            
            plan["databases"].append(db_info)
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Plan sauvegardé: {output_file}")
    
    def _display_final_report(self):
        """Affiche le rapport final"""
        print("\n" + "="*80)
        print("📊 RAPPORT FINAL")
        print("="*80 + "\n")
        
        print(f"✅ Databases trouvées: {self.stats['databases_found']}")
        print(f"✅ Databases migrées: {self.stats['databases_migrated']}")
        print(f"✅ Entrées migrées: {self.stats['entries_migrated']}")
        
        if self.stats["errors"]:
            print(f"\n❌ Erreurs ({len(self.stats['errors'])}):")
            for error in self.stats["errors"][:10]:
                print(f"   - {error}")
        
        # Sauvegarder le mapping
        mapping_file = os.path.join(Config.OUTPUT_DIR, "id_mapping.json")
        with open(mapping_file, "w") as f:
            json.dump({
                "database_mapping": self.db_mapping,
                "page_mapping": self.page_mapping
            }, f, indent=2)
        
        print(f"\n💾 Mapping sauvegardé: {mapping_file}")
        print("\n" + "="*80 + "\n")


# =============================================================================
# POINT D'ENTRÉE
# =============================================================================

def main():
    """Point d'entrée du script"""
    
    # Vérifier la configuration
    if not Config.NOTION_TOKEN:
        print("❌ NOTION_TOKEN non défini")
        print("   export NOTION_TOKEN=your_token")
        return
    
    if not Config.SIYUAN_TOKEN:
        print("❌ SIYUAN_TOKEN non défini")
        print("   export SIYUAN_TOKEN=your_token")
        return
    
    # Lancer la migration
    orchestrator = MigrationOrchestrator()
    orchestrator.run()


if __name__ == "__main__":
    main()
