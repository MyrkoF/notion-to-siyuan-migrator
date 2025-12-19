#!/usr/bin/env python3
"""
Notion to SiYuan Migrator
Migre le contenu complet de Notion vers SiYuan en préservant les propriétés et relations.

Architecture:
- Phase 1: Extraction de Notion (pages, databases, blocs)
- Phase 2: Mapping et conversion (structure, propriétés, liens)
- Phase 3: Import dans SiYuan (documents, tags, relations)
- Phase 4: Génération de rapport détaillé

Author: Myrko (via Claude/JARVIS)
"""

import os
import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import yaml

# =============================================================================
# CONFIGURATION
# =============================================================================

class Config:
    """Configuration centralisée"""
    
    # Notion API
    NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")
    NOTION_API_URL = "https://api.notion.com/v1"
    NOTION_VERSION = "2022-06-28"
    
    # SiYuan API
    SIYUAN_URL = os.getenv("SIYUAN_URL", "http://192.168.1.11:6806")
    SIYUAN_TOKEN = os.getenv("SIYUAN_TOKEN", "")
    
    # Paramètres de migration
    BATCH_SIZE = 50  # Nombre de pages à traiter par batch
    DELAY_BETWEEN_CALLS = 0.5  # Délai entre appels API (secondes)
    OUTPUT_DIR = Path("./migration_output")
    
    # Options
    PRESERVE_PROPERTIES = True
    PRESERVE_RELATIONS = True
    CREATE_SNAPSHOTS = True
    DRY_RUN = False  # Mode simulation sans import réel

# =============================================================================
# MODÈLES DE DONNÉES
# =============================================================================

@dataclass
class NotionPage:
    """Représente une page Notion"""
    id: str
    title: str
    parent_id: Optional[str]
    properties: Dict[str, Any]
    content_blocks: List[Dict]
    children_pages: List[str]
    is_database: bool = False
    database_schema: Optional[Dict] = None
    tags: List[str] = None
    
    def to_markdown(self) -> str:
        """Convertit la page en Markdown avec frontmatter"""
        md_content = []
        
        # Frontmatter YAML avec propriétés
        if self.properties or self.tags:
            md_content.append("---")
            frontmatter = {
                "notion_id": self.id,
                "title": self.title,
                "properties": self.properties,
                "tags": self.tags or []
            }
            md_content.append(yaml.dump(frontmatter, allow_unicode=True))
            md_content.append("---\n")
        
        # Titre du document
        md_content.append(f"# {self.title}\n")
        
        # Contenu des blocs
        for block in self.content_blocks:
            md_content.append(self._block_to_markdown(block))
        
        return "\n".join(md_content)
    
    def _block_to_markdown(self, block: Dict) -> str:
        """Convertit un bloc Notion en Markdown"""
        block_type = block.get("type")
        
        if block_type == "paragraph":
            return self._rich_text_to_markdown(block.get("paragraph", {}).get("rich_text", [])) + "\n"
        
        elif block_type == "heading_1":
            text = self._rich_text_to_markdown(block.get("heading_1", {}).get("rich_text", []))
            return f"# {text}\n"
        
        elif block_type == "heading_2":
            text = self._rich_text_to_markdown(block.get("heading_2", {}).get("rich_text", []))
            return f"## {text}\n"
        
        elif block_type == "heading_3":
            text = self._rich_text_to_markdown(block.get("heading_3", {}).get("rich_text", []))
            return f"### {text}\n"
        
        elif block_type == "bulleted_list_item":
            text = self._rich_text_to_markdown(block.get("bulleted_list_item", {}).get("rich_text", []))
            return f"- {text}\n"
        
        elif block_type == "numbered_list_item":
            text = self._rich_text_to_markdown(block.get("numbered_list_item", {}).get("rich_text", []))
            return f"1. {text}\n"
        
        elif block_type == "code":
            code_data = block.get("code", {})
            language = code_data.get("language", "")
            text = self._rich_text_to_markdown(code_data.get("rich_text", []))
            return f"```{language}\n{text}\n```\n"
        
        elif block_type == "quote":
            text = self._rich_text_to_markdown(block.get("quote", {}).get("rich_text", []))
            return f"> {text}\n"
        
        elif block_type == "divider":
            return "---\n"
        
        elif block_type == "callout":
            callout = block.get("callout", {})
            icon = callout.get("icon", {}).get("emoji", "💡")
            text = self._rich_text_to_markdown(callout.get("rich_text", []))
            return f"> {icon} **Callout:** {text}\n"
        
        else:
            # Type non supporté, on le note
            return f"<!-- Notion block type '{block_type}' not converted -->\n"
    
    def _rich_text_to_markdown(self, rich_text: List[Dict]) -> str:
        """Convertit le rich text Notion en Markdown"""
        result = []
        for text_obj in rich_text:
            content = text_obj.get("plain_text", "")
            annotations = text_obj.get("annotations", {})
            
            # Appliquer le formatage
            if annotations.get("bold"):
                content = f"**{content}**"
            if annotations.get("italic"):
                content = f"*{content}*"
            if annotations.get("strikethrough"):
                content = f"~~{content}~~"
            if annotations.get("code"):
                content = f"`{content}`"
            
            # Liens
            if text_obj.get("href"):
                content = f"[{content}]({text_obj['href']})"
            
            result.append(content)
        
        return "".join(result)

@dataclass
class SiYuanDocument:
    """Représente un document SiYuan"""
    notebook_id: str
    path: str
    content: str
    notion_id: str
    tags: List[str] = None

@dataclass
class MigrationReport:
    """Rapport de migration"""
    start_time: datetime
    end_time: Optional[datetime] = None
    total_pages: int = 0
    pages_migrated: int = 0
    databases_found: int = 0
    errors: List[str] = None
    warnings: List[str] = None
    mapping: Dict[str, str] = None  # notion_id -> siyuan_id
    
    def to_dict(self) -> Dict:
        return asdict(self)

# =============================================================================
# CLIENTS API
# =============================================================================

class NotionClient:
    """Client pour l'API Notion"""
    
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": Config.NOTION_VERSION,
            "Content-Type": "application/json"
        }
    
    def search_all_pages(self) -> List[Dict]:
        """Récupère toutes les pages du workspace"""
        all_pages = []
        has_more = True
        start_cursor = None
        
        while has_more:
            payload = {"page_size": 100}
            if start_cursor:
                payload["start_cursor"] = start_cursor
            
            response = requests.post(
                f"{Config.NOTION_API_URL}/search",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            all_pages.extend(data.get("results", []))
            has_more = data.get("has_more", False)
            start_cursor = data.get("next_cursor")
            
            time.sleep(Config.DELAY_BETWEEN_CALLS)
        
        print(f"✅ {len(all_pages)} pages trouvées dans Notion")
        return all_pages
    
    def get_page_details(self, page_id: str) -> Dict:
        """Récupère les détails d'une page"""
        response = requests.get(
            f"{Config.NOTION_API_URL}/pages/{page_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_block_children(self, block_id: str) -> List[Dict]:
        """Récupère les blocs enfants"""
        all_blocks = []
        has_more = True
        start_cursor = None
        
        while has_more:
            url = f"{Config.NOTION_API_URL}/blocks/{block_id}/children"
            params = {"page_size": 100}
            if start_cursor:
                params["start_cursor"] = start_cursor
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            all_blocks.extend(data.get("results", []))
            has_more = data.get("has_more", False)
            start_cursor = data.get("next_cursor")
            
            time.sleep(Config.DELAY_BETWEEN_CALLS)
        
        return all_blocks
    
    def get_database_details(self, database_id: str) -> Dict:
        """Récupère les détails d'une database"""
        response = requests.get(
            f"{Config.NOTION_API_URL}/databases/{database_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def query_database(self, database_id: str) -> List[Dict]:
        """Query une database pour récupérer ses entrées"""
        all_entries = []
        has_more = True
        start_cursor = None
        
        while has_more:
            payload = {"page_size": 100}
            if start_cursor:
                payload["start_cursor"] = start_cursor
            
            response = requests.post(
                f"{Config.NOTION_API_URL}/databases/{database_id}/query",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            all_entries.extend(data.get("results", []))
            has_more = data.get("has_more", False)
            start_cursor = data.get("next_cursor")
            
            time.sleep(Config.DELAY_BETWEEN_CALLS)
        
        return all_entries

class SiYuanClient:
    """Client pour l'API SiYuan"""
    
    def __init__(self, url: str, token: str):
        self.url = url
        self.token = token
        self.headers = {
            "Authorization": f"Token {token}",
            "Content-Type": "application/json"
        }
    
    def _request(self, endpoint: str, data: Dict = None) -> Dict:
        """Requête générique à l'API SiYuan"""
        response = requests.post(
            f"{self.url}{endpoint}",
            headers=self.headers,
            json=data or {}
        )
        response.raise_for_status()
        result = response.json()
        
        if result.get("code") != 0:
            raise Exception(f"SiYuan API error: {result.get('msg')}")
        
        return result.get("data", {})
    
    def list_notebooks(self) -> List[Dict]:
        """Liste tous les notebooks"""
        return self._request("/api/notebook/lsNotebooks")
    
    def create_document(self, notebook_id: str, path: str, markdown: str) -> Dict:
        """Crée un document dans SiYuan"""
        return self._request("/api/filetree/createDocWithMd", {
            "notebook": notebook_id,
            "path": path,
            "markdown": markdown
        })
    
    def create_snapshot(self, memo: str = "Migration Notion") -> Dict:
        """Crée un snapshot"""
        return self._request("/api/snapshot/createSnapshot", {"memo": memo})
    
    def search_docs(self, query: str) -> List[Dict]:
        """Recherche de documents"""
        return self._request("/api/filetree/searchDocs", {"k": query})

# =============================================================================
# MOTEUR DE MIGRATION
# =============================================================================

class NotionToSiYuanMigrator:
    """Orchestrateur principal de la migration"""
    
    def __init__(self):
        self.notion = NotionClient(Config.NOTION_TOKEN)
        self.siyuan = SiYuanClient(Config.SIYUAN_URL, Config.SIYUAN_TOKEN)
        self.report = MigrationReport(
            start_time=datetime.now(),
            errors=[],
            warnings=[],
            mapping={}
        )
        
        # Créer le dossier de sortie
        Config.OUTPUT_DIR.mkdir(exist_ok=True)
    
    def run(self):
        """Exécute la migration complète"""
        print("\n" + "="*70)
        print("🚀 MIGRATION NOTION → SIYUAN")
        print("="*70 + "\n")
        
        try:
            # Phase 1: Extraction
            print("📥 PHASE 1: Extraction de Notion...")
            notion_pages = self._extract_notion()
            
            # Phase 2: Conversion
            print("\n🔄 PHASE 2: Conversion et mapping...")
            converted_docs = self._convert_pages(notion_pages)
            
            # Phase 3: Import
            print("\n📤 PHASE 3: Import dans SiYuan...")
            if not Config.DRY_RUN:
                if Config.CREATE_SNAPSHOTS:
                    print("📸 Création d'un snapshot avant import...")
                    self.siyuan.create_snapshot("Avant migration Notion")
                
                self._import_to_siyuan(converted_docs)
            else:
                print("⚠️  Mode DRY_RUN activé - Pas d'import réel")
            
            # Phase 4: Rapport
            print("\n📊 PHASE 4: Génération du rapport...")
            self._generate_report()
            
            self.report.end_time = datetime.now()
            duration = (self.report.end_time - self.report.start_time).total_seconds()
            
            print("\n" + "="*70)
            print(f"✅ MIGRATION TERMINÉE en {duration:.1f}s")
            print(f"   Pages migrées: {self.report.pages_migrated}/{self.report.total_pages}")
            print(f"   Databases: {self.report.databases_found}")
            print(f"   Erreurs: {len(self.report.errors)}")
            print(f"   Rapport: {Config.OUTPUT_DIR}/migration_report.json")
            print("="*70 + "\n")
            
        except Exception as e:
            print(f"\n❌ ERREUR CRITIQUE: {str(e)}")
            self.report.errors.append(f"Critical: {str(e)}")
            raise
        
        finally:
            self._save_report()
    
    def _extract_notion(self) -> List[NotionPage]:
        """Phase 1: Extraction de toutes les pages Notion"""
        raw_pages = self.notion.search_all_pages()
        self.report.total_pages = len(raw_pages)
        
        notion_pages = []
        
        for idx, raw_page in enumerate(raw_pages, 1):
            print(f"  [{idx}/{len(raw_pages)}] Extraction: {raw_page.get('id')[:8]}...")
            
            try:
                page_id = raw_page["id"]
                
                # Déterminer le type
                is_database = raw_page.get("object") == "database"
                
                if is_database:
                    self.report.databases_found += 1
                    # Récupérer le schéma de la database
                    db_details = self.notion.get_database_details(page_id)
                    db_entries = self.notion.query_database(page_id)
                    
                    # TODO: Gérer les databases
                    self.report.warnings.append(
                        f"Database '{self._get_title(raw_page)}' nécessite traitement manuel"
                    )
                    continue
                
                # Page normale
                page_details = self.notion.get_page_details(page_id)
                blocks = self.notion.get_block_children(page_id)
                
                # Extraire les propriétés
                properties = self._extract_properties(page_details.get("properties", {}))
                tags = self._extract_tags(properties)
                
                notion_page = NotionPage(
                    id=page_id,
                    title=self._get_title(page_details),
                    parent_id=self._get_parent_id(page_details),
                    properties=properties,
                    content_blocks=blocks,
                    children_pages=[],
                    tags=tags
                )
                
                notion_pages.append(notion_page)
                
            except Exception as e:
                error_msg = f"Erreur extraction page {page_id[:8]}: {str(e)}"
                print(f"    ⚠️  {error_msg}")
                self.report.errors.append(error_msg)
        
        print(f"\n✅ {len(notion_pages)} pages extraites")
        return notion_pages
    
    def _convert_pages(self, notion_pages: List[NotionPage]) -> List[SiYuanDocument]:
        """Phase 2: Conversion des pages Notion en documents SiYuan"""
        siyuan_docs = []
        
        # Récupérer le premier notebook disponible
        notebooks = self.siyuan.list_notebooks()
        if not notebooks:
            raise Exception("Aucun notebook SiYuan disponible")
        
        target_notebook = notebooks[0]["id"]
        print(f"  📓 Notebook cible: {notebooks[0]['name']} ({target_notebook})")
        
        for idx, notion_page in enumerate(notion_pages, 1):
            print(f"  [{idx}/{len(notion_pages)}] Conversion: {notion_page.title[:40]}...")
            
            try:
                # Convertir en Markdown
                markdown_content = notion_page.to_markdown()
                
                # Créer le chemin (sanitize le titre)
                safe_title = self._sanitize_filename(notion_page.title)
                path = f"/migration-notion/{safe_title}"
                
                siyuan_doc = SiYuanDocument(
                    notebook_id=target_notebook,
                    path=path,
                    content=markdown_content,
                    notion_id=notion_page.id,
                    tags=notion_page.tags
                )
                
                siyuan_docs.append(siyuan_doc)
                
            except Exception as e:
                error_msg = f"Erreur conversion {notion_page.title}: {str(e)}"
                print(f"    ⚠️  {error_msg}")
                self.report.errors.append(error_msg)
        
        print(f"\n✅ {len(siyuan_docs)} documents convertis")
        return siyuan_docs
    
    def _import_to_siyuan(self, siyuan_docs: List[SiYuanDocument]):
        """Phase 3: Import des documents dans SiYuan"""
        for idx, doc in enumerate(siyuan_docs, 1):
            print(f"  [{idx}/{len(siyuan_docs)}] Import: {doc.path}...")
            
            try:
                result = self.siyuan.create_document(
                    notebook_id=doc.notebook_id,
                    path=doc.path,
                    markdown=doc.content
                )
                
                siyuan_id = result.get("id", "unknown")
                self.report.mapping[doc.notion_id] = siyuan_id
                self.report.pages_migrated += 1
                
            except Exception as e:
                error_msg = f"Erreur import {doc.path}: {str(e)}"
                print(f"    ⚠️  {error_msg}")
                self.report.errors.append(error_msg)
        
        print(f"\n✅ {self.report.pages_migrated} documents importés")
    
    def _generate_report(self):
        """Phase 4: Génération du rapport détaillé"""
        report_data = self.report.to_dict()
        
        # Sauvegarder le mapping Notion ID -> SiYuan ID
        mapping_file = Config.OUTPUT_DIR / "id_mapping.json"
        with open(mapping_file, "w") as f:
            json.dump(self.report.mapping, f, indent=2)
        
        print(f"  💾 Mapping sauvegardé: {mapping_file}")
    
    def _save_report(self):
        """Sauvegarde le rapport final"""
        report_file = Config.OUTPUT_DIR / "migration_report.json"
        with open(report_file, "w") as f:
            json.dump(self.report.to_dict(), f, indent=2, default=str)
    
    # Helpers
    
    def _get_title(self, page_or_db: Dict) -> str:
        """Extrait le titre d'une page ou database"""
        if page_or_db.get("object") == "database":
            title_list = page_or_db.get("title", [])
        else:
            properties = page_or_db.get("properties", {})
            title_prop = properties.get("title") or properties.get("Name") or {}
            title_list = title_prop.get("title", [])
        
        if title_list:
            return "".join([t.get("plain_text", "") for t in title_list])
        return "Sans titre"
    
    def _get_parent_id(self, page: Dict) -> Optional[str]:
        """Extrait l'ID du parent"""
        parent = page.get("parent", {})
        return parent.get("page_id") or parent.get("database_id")
    
    def _extract_properties(self, properties: Dict) -> Dict[str, Any]:
        """Extrait les propriétés Notion"""
        extracted = {}
        
        for prop_name, prop_data in properties.items():
            prop_type = prop_data.get("type")
            
            if prop_type == "title":
                continue  # Déjà géré
            elif prop_type == "rich_text":
                texts = prop_data.get("rich_text", [])
                extracted[prop_name] = "".join([t.get("plain_text", "") for t in texts])
            elif prop_type == "number":
                extracted[prop_name] = prop_data.get("number")
            elif prop_type == "select":
                select = prop_data.get("select")
                extracted[prop_name] = select.get("name") if select else None
            elif prop_type == "multi_select":
                multi = prop_data.get("multi_select", [])
                extracted[prop_name] = [m.get("name") for m in multi]
            elif prop_type == "date":
                date_obj = prop_data.get("date")
                extracted[prop_name] = date_obj.get("start") if date_obj else None
            elif prop_type == "checkbox":
                extracted[prop_name] = prop_data.get("checkbox", False)
            elif prop_type == "url":
                extracted[prop_name] = prop_data.get("url")
            elif prop_type == "email":
                extracted[prop_name] = prop_data.get("email")
            elif prop_type == "phone_number":
                extracted[prop_name] = prop_data.get("phone_number")
            elif prop_type == "relation":
                relations = prop_data.get("relation", [])
                extracted[prop_name] = {
                    "_type": "relation",
                    "pages": [r.get("id") for r in relations]
                }
        
        return extracted
    
    def _extract_tags(self, properties: Dict) -> List[str]:
        """Extrait les tags depuis les propriétés"""
        tags = []
        
        # Chercher les propriétés qui ressemblent à des tags
        for key, value in properties.items():
            if isinstance(value, list) and all(isinstance(v, str) for v in value):
                tags.extend(value)
        
        return list(set(tags))  # Déduplicate
    
    def _sanitize_filename(self, filename: str) -> str:
        """Nettoie un nom de fichier"""
        # Remplacer les caractères interdits
        forbidden = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in forbidden:
            filename = filename.replace(char, '-')
        
        # Limiter la longueur
        return filename[:100]

# =============================================================================
# POINT D'ENTRÉE
# =============================================================================

def main():
    """Point d'entrée principal"""
    
    # Vérifier les variables d'environnement
    if not Config.NOTION_TOKEN:
        print("❌ NOTION_TOKEN non défini. Exporter via: export NOTION_TOKEN='...'")
        return 1
    
    if not Config.SIYUAN_TOKEN:
        print("❌ SIYUAN_TOKEN non défini. Exporter via: export SIYUAN_TOKEN='...'")
        return 1
    
    # Lancer la migration
    migrator = NotionToSiYuanMigrator()
    migrator.run()
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
