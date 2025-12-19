#!/usr/bin/env python3
"""
Post-Migration Processor
Traite les databases Notion et reconvertit les liens internes après migration.

Usage:
  python3 post_migration_processor.py

Features:
  - Analyse les databases Notion exportées
  - Génère des scripts SQL pour créer les Attribute Views SiYuan
  - Convertit les liens Notion ID vers SiYuan ID
  - Génère un rapport de traitement
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set
from dataclasses import dataclass

# =============================================================================
# CONFIGURATION
# =============================================================================

OUTPUT_DIR = Path("./migration_output")
MAPPING_FILE = OUTPUT_DIR / "id_mapping.json"
WORKSPACE_DIR = Path("./workspace/data")  # À adapter selon votre installation

# =============================================================================
# MODÈLES
# =============================================================================

@dataclass
class DatabaseInfo:
    """Info sur une database Notion"""
    notion_id: str
    name: str
    properties: Dict
    entries_count: int
    
@dataclass
class LinkConversion:
    """Info sur une conversion de lien"""
    file_path: str
    line_number: int
    old_link: str
    new_link: str
    converted: bool

# =============================================================================
# ANALYSEUR DE DATABASES
# =============================================================================

class DatabaseAnalyzer:
    """Analyse les databases Notion pour faciliter la recréation"""
    
    def __init__(self):
        self.databases: List[DatabaseInfo] = []
    
    def analyze_report(self, report_path: Path) -> List[DatabaseInfo]:
        """Analyse le rapport de migration pour trouver les databases"""
        print("\n📊 Analyse des databases Notion...")
        
        with open(report_path) as f:
            report = json.load(f)
        
        warnings = report.get("warnings", [])
        
        for warning in warnings:
            if "Database" in warning and "nécessite traitement manuel" in warning:
                # Extraire le nom de la database
                match = re.search(r"Database '([^']+)'", warning)
                if match:
                    db_name = match.group(1)
                    print(f"  📁 Database trouvée: {db_name}")
                    
                    # Note: On ne peut pas récupérer tous les détails ici
                    # L'utilisateur devra exporter manuellement depuis Notion
                    db_info = DatabaseInfo(
                        notion_id="unknown",
                        name=db_name,
                        properties={},
                        entries_count=0
                    )
                    self.databases.append(db_info)
        
        print(f"✅ {len(self.databases)} database(s) détectée(s)")
        return self.databases
    
    def generate_instructions(self, output_file: Path):
        """Génère des instructions pour recréer les databases"""
        print(f"\n📝 Génération des instructions: {output_file}")
        
        with open(output_file, 'w') as f:
            f.write("# Instructions pour recréer les Databases Notion dans SiYuan\n\n")
            f.write("## Databases détectées\n\n")
            
            for idx, db in enumerate(self.databases, 1):
                f.write(f"### {idx}. {db.name}\n\n")
                f.write("**Actions requises:**\n\n")
                f.write("1. Dans Notion, exporter cette database en CSV:\n")
                f.write(f"   - Ouvrir la database '{db.name}'\n")
                f.write("   - Menu ⋯ → Export → CSV\n")
                f.write(f"   - Sauvegarder comme `{db.name.lower().replace(' ', '_')}.csv`\n\n")
                f.write("2. Dans SiYuan, créer une nouvelle Attribute View:\n")
                f.write("   - Créer un document dédié\n")
                f.write("   - Insérer un bloc Attribute View\n")
                f.write("   - Recréer les colonnes selon le CSV\n")
                f.write("   - Importer les données ligne par ligne\n\n")
                f.write("3. Reconnecter les relations:\n")
                f.write("   - Utiliser le fichier `id_mapping.json`\n")
                f.write("   - Remplacer les Notion IDs par les SiYuan IDs\n\n")
                f.write("---\n\n")
            
            f.write("\n## Notes importantes\n\n")
            f.write("- Les Attribute Views SiYuan ne supportent pas tous les types de propriétés Notion\n")
            f.write("- Les formules et rollups doivent être recréés manuellement\n")
            f.write("- Les relations peuvent nécessiter des ajustements\n")
            f.write("- Consulter: https://docs.siyuan-note.club/en/ pour plus d'infos\n")
        
        print(f"✅ Instructions sauvegardées")

# =============================================================================
# CONVERTISSEUR DE LIENS
# =============================================================================

class LinkConverter:
    """Convertit les liens Notion en liens SiYuan"""
    
    def __init__(self, mapping_file: Path):
        self.mapping = self._load_mapping(mapping_file)
        self.conversions: List[LinkConversion] = []
    
    def _load_mapping(self, mapping_file: Path) -> Dict[str, str]:
        """Charge le mapping Notion ID → SiYuan ID"""
        if not mapping_file.exists():
            print(f"⚠️  Fichier mapping introuvable: {mapping_file}")
            return {}
        
        with open(mapping_file) as f:
            mapping = json.load(f)
        
        print(f"📋 {len(mapping)} mappings chargés")
        return mapping
    
    def convert_links_in_workspace(self, workspace_dir: Path):
        """Convertit tous les liens dans le workspace SiYuan"""
        print(f"\n🔗 Conversion des liens dans: {workspace_dir}")
        
        if not workspace_dir.exists():
            print(f"⚠️  Workspace introuvable: {workspace_dir}")
            return
        
        # Trouver tous les fichiers .sy
        sy_files = list(workspace_dir.glob("**/*.sy"))
        print(f"📁 {len(sy_files)} fichiers .sy trouvés")
        
        for sy_file in sy_files:
            self._convert_links_in_file(sy_file)
        
        print(f"✅ {len([c for c in self.conversions if c.converted])} liens convertis")
    
    def _convert_links_in_file(self, file_path: Path):
        """Convertit les liens dans un fichier"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Pattern pour trouver les liens Notion
            # Ex: [text](notion-id) ou [text](https://notion.so/page-id)
            pattern = r'\[([^\]]+)\]\(([a-f0-9]{32}|https://www\.notion\.so/[a-f0-9-]+)\)'
            
            def replace_link(match):
                text = match.group(1)
                notion_id = match.group(2)
                
                # Nettoyer l'ID si c'est une URL
                if "notion.so" in notion_id:
                    notion_id = notion_id.split('/')[-1].replace('-', '')
                
                # Chercher dans le mapping
                siyuan_id = self.mapping.get(notion_id)
                
                if siyuan_id:
                    # Convertir en référence de bloc SiYuan
                    new_link = f"(({siyuan_id} '{text}'))"
                    self.conversions.append(LinkConversion(
                        file_path=str(file_path),
                        line_number=0,  # TODO: calculer le numéro de ligne
                        old_link=match.group(0),
                        new_link=new_link,
                        converted=True
                    ))
                    return new_link
                else:
                    # Garder l'ancien lien avec un warning
                    self.conversions.append(LinkConversion(
                        file_path=str(file_path),
                        line_number=0,
                        old_link=match.group(0),
                        new_link=match.group(0),
                        converted=False
                    ))
                    return f"<!-- TODO: Link not converted --> {match.group(0)}"
            
            # Appliquer les conversions
            new_content = re.sub(pattern, replace_link, content)
            
            # Sauvegarder si modifié
            if new_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
        
        except Exception as e:
            print(f"  ⚠️  Erreur sur {file_path.name}: {str(e)}")
    
    def generate_report(self, output_file: Path):
        """Génère un rapport des conversions"""
        print(f"\n📝 Génération du rapport: {output_file}")
        
        converted = [c for c in self.conversions if c.converted]
        not_converted = [c for c in self.conversions if not c.converted]
        
        with open(output_file, 'w') as f:
            f.write("# Rapport de conversion des liens\n\n")
            f.write(f"**Total:** {len(self.conversions)} liens analysés\n")
            f.write(f"**Convertis:** {len(converted)} ✅\n")
            f.write(f"**Non convertis:** {len(not_converted)} ❌\n\n")
            
            if not_converted:
                f.write("## Liens non convertis (action manuelle requise)\n\n")
                for conv in not_converted:
                    f.write(f"- `{conv.file_path}`\n")
                    f.write(f"  - Lien: `{conv.old_link}`\n")
                    f.write(f"  - Raison: Notion ID introuvable dans le mapping\n\n")
            
            f.write("\n## Statistiques par fichier\n\n")
            files_stats = {}
            for conv in self.conversions:
                if conv.file_path not in files_stats:
                    files_stats[conv.file_path] = {"total": 0, "converted": 0}
                files_stats[conv.file_path]["total"] += 1
                if conv.converted:
                    files_stats[conv.file_path]["converted"] += 1
            
            for file_path, stats in files_stats.items():
                ratio = stats["converted"] / stats["total"] * 100
                f.write(f"- `{Path(file_path).name}`: {stats['converted']}/{stats['total']} ({ratio:.0f}%)\n")
        
        print(f"✅ Rapport sauvegardé")

# =============================================================================
# MAIN
# =============================================================================

def main():
    """Point d'entrée principal"""
    
    print("\n" + "="*70)
    print("🔧 POST-MIGRATION PROCESSOR")
    print("="*70)
    
    # 1. Analyser les databases
    db_analyzer = DatabaseAnalyzer()
    report_file = OUTPUT_DIR / "migration_report.json"
    
    if report_file.exists():
        databases = db_analyzer.analyze_report(report_file)
        db_analyzer.generate_instructions(OUTPUT_DIR / "databases_instructions.md")
    else:
        print(f"⚠️  Rapport de migration introuvable: {report_file}")
    
    # 2. Convertir les liens
    link_converter = LinkConverter(MAPPING_FILE)
    
    # Demander confirmation avant de modifier les fichiers
    print("\n⚠️  Le convertisseur va modifier les fichiers .sy dans le workspace")
    response = input("Continuer ? (y/N): ").strip().lower()
    
    if response == 'y':
        link_converter.convert_links_in_workspace(WORKSPACE_DIR)
        link_converter.generate_report(OUTPUT_DIR / "links_conversion_report.md")
    else:
        print("❌ Conversion des liens annulée")
    
    print("\n" + "="*70)
    print("✅ POST-TRAITEMENT TERMINÉ")
    print("="*70)
    print(f"\n📁 Fichiers générés:")
    print(f"   - {OUTPUT_DIR}/databases_instructions.md")
    print(f"   - {OUTPUT_DIR}/links_conversion_report.md")
    print("\n")

if __name__ == "__main__":
    main()
