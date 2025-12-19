#!/usr/bin/env python3
"""
Notion to SiYuan - Import des données dans les Attribute Views
ÉTAPE 2 : Après création manuelle des AVs

⚠️ IMPORTANT : Les rollups et formules sont SKIPPÉS automatiquement
Ils doivent être recréés manuellement dans SiYuan (voir PROJECT_PLAN.md Phase 5)
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
    
    # Notebook cible
    TARGET_NOTEBOOK_ID = os.getenv("TARGET_NOTEBOOK_ID")
    
    # Options
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "10"))
    DELAY_BETWEEN_CALLS = float(os.getenv("DELAY_BETWEEN_CALLS", "0.3"))
    DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
    
    # Test limité
    TEST_LIMIT = int(os.getenv("TEST_LIMIT", "0"))  # 0 = tous, N = limiter à N entrées
    
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
    
    def get_database(self, database_id: str) -> Dict:
        """Récupère les infos d'une database"""
        response = requests.get(
            f"{self.base_url}/databases/{database_id}",
            headers=self.headers
        )
        return response.json() if response.status_code == 200 else {}
    
    def query_database(self, database_id: str, limit: int = 0) -> List[Dict]:
        """Récupère les entrées d'une database"""
        entries = []
        has_more = True
        start_cursor = None
        
        while has_more:
            payload = {"page_size": 100}
            if start_cursor:
                payload["start_cursor"] = start_cursor
            
            response = requests.post(
                f"{self.base_url}/databases/{database_id}/query",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code != 200:
                print(f"❌ Erreur query database: {response.status_code}")
                break
            
            data = response.json()
            batch = data.get("results", [])
            entries.extend(batch)
            
            # Limiter si demandé
            if limit > 0 and len(entries) >= limit:
                entries = entries[:limit]
                break
            
            has_more = data.get("has_more", False)
            start_cursor = data.get("next_cursor")
            
            time.sleep(Config.DELAY_BETWEEN_CALLS)
        
        return entries
    
    def get_page_content(self, page_id: str) -> str:
        """Récupère le contenu Markdown d'une page"""
        # Récupérer les blocs
        response = requests.get(
            f"{self.base_url}/blocks/{page_id}/children",
            headers=self.headers,
            params={"page_size": 100}
        )
        
        if response.status_code != 200:
            return ""
        
        blocks = response.json().get("results", [])
        
        # Conversion simplifiée en Markdown
        markdown_lines = []
        for block in blocks:
            block_type = block.get("type")
            if block_type == "paragraph":
                text = self._extract_rich_text(block.get("paragraph", {}).get("rich_text", []))
                if text:
                    markdown_lines.append(text)
            elif block_type == "heading_1":
                text = self._extract_rich_text(block.get("heading_1", {}).get("rich_text", []))
                if text:
                    markdown_lines.append(f"# {text}")
            elif block_type == "heading_2":
                text = self._extract_rich_text(block.get("heading_2", {}).get("rich_text", []))
                if text:
                    markdown_lines.append(f"## {text}")
            elif block_type == "heading_3":
                text = self._extract_rich_text(block.get("heading_3", {}).get("rich_text", []))
                if text:
                    markdown_lines.append(f"### {text}")
            elif block_type == "bulleted_list_item":
                text = self._extract_rich_text(block.get("bulleted_list_item", {}).get("rich_text", []))
                if text:
                    markdown_lines.append(f"- {text}")
            elif block_type == "numbered_list_item":
                text = self._extract_rich_text(block.get("numbered_list_item", {}).get("rich_text", []))
                if text:
                    markdown_lines.append(f"1. {text}")
        
        return "\n\n".join(markdown_lines)
    
    def _extract_rich_text(self, rich_text: List[Dict]) -> str:
        """Extrait le texte d'un tableau de rich_text"""
        return "".join([t.get("plain_text", "") for t in rich_text])


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
            return {"code": -1, "msg": "Error", "data": None}
        
        return response.json()
    
    def list_attribute_views(self, notebook_id: str) -> List[Dict]:
        """Liste toutes les Attribute Views d'un notebook"""
        # Lister tous les documents
        result = self._call_api("/filetree/listDocTree", {"notebook": notebook_id})
        
        if result.get("code") != 0:
            return []
        
        # TODO: Filtrer pour ne garder que les AVs
        # Pour l'instant on retourne tous les docs
        return result.get("data", [])
    
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
    
    def set_block_attrs(self, block_id: str, attrs: Dict[str, str]) -> bool:
        """Définit les attributes d'un bloc"""
        result = self._call_api("/attr/setBlockAttrs", {
            "id": block_id,
            "attrs": attrs
        })
        
        return result.get("code") == 0
    
    def get_block_attrs(self, block_id: str) -> Dict:
        """Récupère les attributes d'un bloc"""
        result = self._call_api("/attr/getBlockAttrs", {
            "id": block_id
        })
        
        if result.get("code") == 0:
            return result.get("data", {})
        return {}


# =============================================================================
# CONVERTISSEUR DE PROPRIÉTÉS
# =============================================================================

class PropertyConverter:
    """Convertit les propriétés Notion en attributes SiYuan"""
    
    @staticmethod
    def convert_property_value(prop_type: str, prop_value: Any) -> Optional[str]:
        """Convertit une valeur de propriété Notion en string pour SiYuan"""
        
        if not prop_value:
            return None
        
        # Title
        if prop_type == "title":
            if isinstance(prop_value, list):
                return "".join([t.get("plain_text", "") for t in prop_value])
        
        # Rich text
        elif prop_type == "rich_text":
            if isinstance(prop_value, list):
                return "".join([t.get("plain_text", "") for t in prop_value])
        
        # Number
        elif prop_type == "number":
            return str(prop_value) if prop_value is not None else None
        
        # Select
        elif prop_type == "select":
            if isinstance(prop_value, dict):
                return prop_value.get("name")
        
        # Multi-select
        elif prop_type == "multi_select":
            if isinstance(prop_value, list):
                return ", ".join([opt.get("name", "") for opt in prop_value])
        
        # Date
        elif prop_type == "date":
            if isinstance(prop_value, dict):
                start = prop_value.get("start", "")
                end = prop_value.get("end")
                if end:
                    return f"{start} → {end}"
                return start
        
        # Checkbox
        elif prop_type == "checkbox":
            return "true" if prop_value else "false"
        
        # URL
        elif prop_type == "url":
            return prop_value if isinstance(prop_value, str) else None
        
        # Email
        elif prop_type == "email":
            return prop_value if isinstance(prop_value, str) else None
        
        # Phone
        elif prop_type == "phone_number":
            return prop_value if isinstance(prop_value, str) else None
        
        # Relation (on stocke les IDs pour reconnexion plus tard)
        elif prop_type == "relation":
            if isinstance(prop_value, list):
                ids = [rel.get("id") for rel in prop_value]
                return ",".join(ids) if ids else None
        
        # Rollup et Formula → SKIP (à recréer manuellement)
        elif prop_type in ["rollup", "formula"]:
            # ⚠️ SKIP : Ces propriétés ne sont PAS importées
            # Raison : Risque d'erreurs, complexité du mapping
            # Action : Recréer manuellement dans SiYuan après import
            return None  # Retourne None pour ignorer
        
        # Files
        elif prop_type == "files":
            if isinstance(prop_value, list):
                urls = [f.get("file", {}).get("url", "") or f.get("external", {}).get("url", "") 
                       for f in prop_value]
                return ", ".join([u for u in urls if u])
        
        # People
        elif prop_type == "people":
            if isinstance(prop_value, list):
                names = [p.get("name", "") for p in prop_value]
                return ", ".join([n for n in names if n])
        
        # Created time, Last edited time
        elif prop_type in ["created_time", "last_edited_time"]:
            return prop_value if isinstance(prop_value, str) else None
        
        # Created by, Last edited by
        elif prop_type in ["created_by", "last_edited_by"]:
            if isinstance(prop_value, dict):
                return prop_value.get("name", "")
        
        return None


# =============================================================================
# ORCHESTRATEUR D'IMPORT
# =============================================================================

class DataImporter:
    """Importe les données Notion dans les Attribute Views SiYuan"""
    
    def __init__(self):
        self.notion_client = NotionClient(Config.NOTION_TOKEN)
        self.siyuan_client = SiYuanClient(Config.SIYUAN_URL, Config.SIYUAN_TOKEN)
        self.converter = PropertyConverter()
        
        # Mappings
        self.notion_to_siyuan_ids = {}  # Notion page ID → SiYuan block ID
        
        # Stats
        self.stats = {
            "databases_processed": 0,
            "entries_imported": 0,
            "rollups_skipped": 0,
            "formulas_skipped": 0,
            "errors": []
        }
    
    def run(self):
        """Point d'entrée principal"""
        print("\n" + "="*80)
        print("📥 IMPORT DES DONNÉES NOTION → SIYUAN")
        print("="*80 + "\n")
        
        print(f"Mode: {'🧪 DRY RUN' if Config.DRY_RUN else '⚡ IMPORT RÉEL'}")
        print(f"URL SiYuan: {Config.SIYUAN_URL}")
        
        if Config.TEST_LIMIT > 0:
            print(f"🧪 TEST MODE: Limité à {Config.TEST_LIMIT} entrées par database")
        print()
        
        # Charger le plan de migration
        plan_file = os.path.join(Config.OUTPUT_DIR, "migration_plan.json")
        if not os.path.exists(plan_file):
            print(f"❌ Fichier {plan_file} introuvable")
            print("   Lance d'abord: python3 notion_to_siyuan_complete.py avec DRY_RUN=true")
            return
        
        with open(plan_file) as f:
            plan = json.load(f)
        
        databases = plan["databases"]
        print(f"📊 {len(databases)} databases à traiter\n")
        
        # Vérifier le notebook cible
        if not Config.TARGET_NOTEBOOK_ID:
            print("❌ TARGET_NOTEBOOK_ID non défini")
            print("   export TARGET_NOTEBOOK_ID=your-notebook-id")
            return
        
        # Traiter chaque database
        for idx, db_info in enumerate(databases, 1):
            print(f"\n{'='*80}")
            print(f"📊 DATABASE {idx}/{len(databases)}: {db_info['title']}")
            print(f"{'='*80}\n")
            
            self._process_database(db_info)
            self.stats["databases_processed"] += 1
        
        # Rapport final
        self._display_report()
    
    def _process_database(self, db_info: Dict):
        """Traite une database"""
        db_id = db_info["id"]
        db_title = db_info["title"]
        
        # Compter les rollups/formules dans cette DB
        rollups_in_db = sum(1 for p in db_info["properties"] if p.get("notion_type") == "rollup")
        formulas_in_db = sum(1 for p in db_info["properties"] if p.get("notion_type") == "formula")
        
        if rollups_in_db > 0 or formulas_in_db > 0:
            print(f"⚠️  {rollups_in_db} rollups et {formulas_in_db} formules seront SKIPPÉS")
            self.stats["rollups_skipped"] += rollups_in_db
            self.stats["formulas_skipped"] += formulas_in_db
        
        # Extraire les entrées de Notion
        print(f"📥 Extraction des entrées de Notion...")
        entries = self.notion_client.query_database(db_id, limit=Config.TEST_LIMIT)
        
        if not entries:
            print(f"⚠️  Aucune entrée trouvée")
            return
        
        print(f"✅ {len(entries)} entrées trouvées\n")
        
        if Config.DRY_RUN:
            print("🧪 DRY RUN - Affichage des 3 premières entrées:")
            for entry in entries[:3]:
                self._display_entry(entry, db_info)
            return
        
        # Import réel
        print(f"⚡ Import des {len(entries)} entrées...")
        
        for idx, entry in enumerate(entries, 1):
            if idx % 10 == 0:
                print(f"   Progression: {idx}/{len(entries)}...")
            
            success = self._import_entry(entry, db_info)
            if success:
                self.stats["entries_imported"] += 1
            else:
                self.stats["errors"].append(f"{db_title}: Entrée {idx}")
            
            time.sleep(Config.DELAY_BETWEEN_CALLS)
        
        print(f"✅ Import terminé: {self.stats['entries_imported']} entrées\n")
    
    def _display_entry(self, entry: Dict, db_info: Dict):
        """Affiche une entrée (mode DRY_RUN)"""
        # Extraire le titre
        title_prop = next((p for p in db_info["properties"] if p["notion_type"] == "title"), None)
        if title_prop:
            title_value = entry.get("properties", {}).get(title_prop["name"], {})
            title = self.converter.convert_property_value("title", title_value.get("title", []))
        else:
            title = "Sans titre"
        
        print(f"\n📄 {title}")
        print(f"   ID Notion: {entry['id']}")
        
        # Afficher quelques propriétés
        props = entry.get("properties", {})
        for prop_name, prop_data in list(props.items())[:5]:
            prop_type = prop_data.get("type")
            prop_value = prop_data.get(prop_type)
            converted = self.converter.convert_property_value(prop_type, prop_value)
            if converted:
                print(f"   - {prop_name}: {converted[:50]}...")
    
    def _import_entry(self, entry: Dict, db_info: Dict) -> bool:
        """Importe une entrée"""
        try:
            # 1. Extraire le titre
            title_prop = next((p for p in db_info["properties"] if p["notion_type"] == "title"), None)
            if title_prop:
                title_value = entry.get("properties", {}).get(title_prop["name"], {})
                title = self.converter.convert_property_value("title", title_value.get("title", []))
            else:
                title = "Sans titre"
            
            # 2. Extraire le contenu de la page
            content = self.notion_client.get_page_content(entry["id"])
            
            # 3. Créer le document dans SiYuan
            path = f"/{db_info['title']}/{title}"
            markdown = f"# {title}\n\n{content}" if content else f"# {title}"
            
            block_id = self.siyuan_client.create_document(
                Config.TARGET_NOTEBOOK_ID,
                path,
                markdown
            )
            
            if not block_id:
                return False
            
            # Sauvegarder le mapping
            self.notion_to_siyuan_ids[entry["id"]] = block_id
            
            # 4. Définir les attributes
            attrs = {}
            props = entry.get("properties", {})
            
            rollups_skipped = []
            formulas_skipped = []
            
            for prop_name, prop_data in props.items():
                prop_type = prop_data.get("type")
                prop_value = prop_data.get(prop_type)
                
                # Tracker les rollups/formules skippés
                if prop_type == "rollup":
                    rollups_skipped.append(prop_name)
                elif prop_type == "formula":
                    formulas_skipped.append(prop_name)
                
                # Convertir la valeur
                converted = self.converter.convert_property_value(prop_type, prop_value)
                
                if converted:
                    # Normaliser le nom de l'attribute (custom-XXX)
                    attr_name = f"custom-{prop_name.lower().replace(' ', '-')}"
                    attrs[attr_name] = converted
            
            # Ajouter des metadata
            attrs["custom-notion-id"] = entry["id"]
            attrs["custom-notion-db"] = db_info["title"]
            
            # Définir les attributes
            if attrs:
                self.siyuan_client.set_block_attrs(block_id, attrs)
            
            # Info sur les propriétés skippées
            if rollups_skipped or formulas_skipped:
                skipped_info = []
                if rollups_skipped:
                    skipped_info.append(f"Rollups: {', '.join(rollups_skipped)}")
                if formulas_skipped:
                    skipped_info.append(f"Formules: {', '.join(formulas_skipped)}")
                # Log silencieux (pas de print pour ne pas polluer)
                # L'utilisateur sera informé dans le rapport final
            
            return True
        
        except Exception as e:
            print(f"❌ Erreur import: {e}")
            return False
    
    def _display_report(self):
        """Affiche le rapport final"""
        print("\n" + "="*80)
        print("📊 RAPPORT FINAL")
        print("="*80 + "\n")
        
        print(f"✅ Databases traitées: {self.stats['databases_processed']}")
        print(f"✅ Entrées importées: {self.stats['entries_imported']}")
        
        if self.stats["rollups_skipped"] > 0 or self.stats["formulas_skipped"] > 0:
            print(f"\n⚠️  Propriétés skippées (recréer manuellement):")
            if self.stats["rollups_skipped"] > 0:
                print(f"   - {self.stats['rollups_skipped']} rollups au total")
            if self.stats["formulas_skipped"] > 0:
                print(f"   - {self.stats['formulas_skipped']} formules au total")
            print(f"   📖 Voir PROJECT_PLAN.md Phase 5 pour la liste complète")
        
        if self.stats["errors"]:
            print(f"\n❌ Erreurs ({len(self.stats['errors'])}):")
            for error in self.stats["errors"][:10]:
                print(f"   - {error}")
        
        # Sauvegarder le mapping
        mapping_file = os.path.join(Config.OUTPUT_DIR, "import_mapping.json")
        with open(mapping_file, "w") as f:
            json.dump({
                "notion_to_siyuan": self.notion_to_siyuan_ids,
                "stats": self.stats
            }, f, indent=2)
        
        print(f"\n💾 Mapping sauvegardé: {mapping_file}")
        print("\n" + "="*80 + "\n")


# =============================================================================
# POINT D'ENTRÉE
# =============================================================================

def main():
    """Point d'entrée"""
    
    # Vérifier config
    if not Config.NOTION_TOKEN:
        print("❌ NOTION_TOKEN non défini")
        return
    
    if not Config.SIYUAN_TOKEN:
        print("❌ SIYUAN_TOKEN non défini")
        return
    
    if not Config.TARGET_NOTEBOOK_ID:
        print("❌ TARGET_NOTEBOOK_ID non défini")
        print("   Définis le notebook où importer:")
        print("   export TARGET_NOTEBOOK_ID=20251218154447-lxfdepg")
        return
    
    # Lancer l'import
    importer = DataImporter()
    importer.run()


if __name__ == "__main__":
    main()
