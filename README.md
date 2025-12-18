# 🚀 Notion to SiYuan Migrator

> Complete migration toolkit to transfer your entire Notion workspace to SiYuan, preserving properties, tags, and structure.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

## 📋 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [What Gets Migrated](#-what-gets-migrated)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Usage](#-usage)
- [Configuration](#-configuration)
- [Post-Migration](#-post-migration)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

- **🔄 Complete Extraction**: Pulls all pages, properties, and content from Notion
- **📝 Smart Conversion**: Converts to Markdown with YAML frontmatter for properties
- **🏗️ Structure Preservation**: Maintains hierarchical organization
- **🏷️ Properties & Tags**: Preserves metadata in SiYuan-compatible format
- **📊 Detailed Reports**: ID mapping, error logs, migration statistics
- **🔒 Safe Migration**: Automatic snapshots before import
- **🧪 Dry Run Mode**: Test migration without actual import
- **⚡ Batch Processing**: Handles large workspaces efficiently

## ⚡ Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/notion-to-siyuan-migrator.git
cd notion-to-siyuan-migrator

# 2. Run setup
./setup_migrator.sh

# 3. Test migration (dry run)
source ~/.notion_siyuan_migrator.env
export DRY_RUN=true
python3 notion_to_siyuan_migrator.py

# 4. Run actual migration
export DRY_RUN=false
python3 notion_to_siyuan_migrator.py
```

**See [QUICK_START.md](QUICK_START.md) for detailed walkthrough.**

## ✅ What Gets Migrated

### Automatically Migrated ✅

| Content Type | Status | Notes |
|--------------|--------|-------|
| Text content | ✅ Full support | All formatting preserved |
| Headings (h1-h6) | ✅ Full support | Converted to Markdown |
| Lists (ordered/unordered) | ✅ Full support | Nested lists supported |
| Code blocks | ✅ Full support | Syntax highlighting preserved |
| Tables | ✅ Full support | Markdown tables |
| Quotes & Callouts | ✅ Full support | Converted to blockquotes |
| Properties | ✅ Full support | Stored in YAML frontmatter |
| Tags | ✅ Full support | Preserved as SiYuan tags |
| Hierarchical structure | ✅ Full support | Document tree maintained |

### Requires Post-Processing ⚠️

| Content Type | Status | Solution |
|--------------|--------|----------|
| Notion Databases | ⚠️ Detected | Manual recreation as Attribute Views |
| Internal links | ⚠️ Mapped | Auto-conversion via post-processor |
| Relations | ⚠️ Mapped | ID mapping saved for reconnection |
| Embedded content | ❌ Not supported | Replace with direct links |

## 🔧 Prerequisites

- **Python 3.8+** with `pip`
- **Notion Integration Token** ([Get one here](https://www.notion.so/my-integrations))
- **SiYuan** installed and running ([Download](https://github.com/siyuan-note/siyuan))
- **SiYuan API Token** (Settings → About → API Token)

## 📦 Installation

### Option 1: Automatic Setup (Recommended)

```bash
chmod +x setup_migrator.sh
./setup_migrator.sh
```

The setup script will:
- ✅ Check Python and dependencies
- ✅ Install required packages (`requests`, `pyyaml`)
- ✅ Request your API tokens
- ✅ Test API connections
- ✅ Save configuration securely

### Option 2: Manual Setup

```bash
# Install dependencies
pip3 install requests pyyaml

# Copy and configure environment
cp .env.example .env
nano .env  # Edit with your tokens

# Export configuration
export $(cat .env | xargs)
```

## 🚀 Usage

### Basic Migration

```bash
# Load configuration
source ~/.notion_siyuan_migrator.env

# Run migration
python3 notion_to_siyuan_migrator.py
```

### Advanced Options

```bash
# Dry run (no actual import)
export DRY_RUN=true
python3 notion_to_siyuan_migrator.py

# Custom batch size
export BATCH_SIZE=20
python3 notion_to_siyuan_migrator.py

# Disable snapshots
export CREATE_SNAPSHOTS=false
python3 notion_to_siyuan_migrator.py
```

### Post-Migration Processing

```bash
# Convert internal links and analyze databases
python3 post_migration_processor.py
```

## ⚙️ Configuration

Edit `.env` or set environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `NOTION_TOKEN` | Notion Integration Token | **Required** |
| `SIYUAN_URL` | SiYuan API endpoint | `http://localhost:6806` |
| `SIYUAN_TOKEN` | SiYuan API Token | **Required** |
| `BATCH_SIZE` | Pages per batch | `50` |
| `DELAY_BETWEEN_CALLS` | API call delay (seconds) | `0.5` |
| `DRY_RUN` | Test mode without import | `false` |
| `CREATE_SNAPSHOTS` | Auto-snapshot before import | `true` |

See [`.env.example`](.env.example) for complete configuration template.

## 📊 Output Files

After migration, check `migration_output/`:

```
migration_output/
├── migration_report.json         # Complete migration report
├── id_mapping.json                # Notion ID → SiYuan ID mapping
├── databases_instructions.md      # How to recreate databases
└── links_conversion_report.md     # Link conversion report
```

### Understanding the Report

```json
{
  "start_time": "2024-01-15T10:30:00",
  "end_time": "2024-01-15T10:32:22",
  "total_pages": 156,
  "pages_migrated": 156,
  "databases_found": 5,
  "errors": [],
  "warnings": ["Database 'CRM' needs manual recreation"],
  "mapping": {
    "notion-page-id": "siyuan-doc-id",
    ...
  }
}
```

## 🔄 Post-Migration

### 1. Verify Migration

```bash
# Check document count in SiYuan
# Settings → About → Statistics

# Test search functionality
# Search for known keywords

# Inspect frontmatter in documents
# Properties should be in YAML header
```

### 2. Recreate Databases

Follow instructions in `migration_output/databases_instructions.md`:

1. Export Notion database as CSV
2. Create Attribute View in SiYuan
3. Import data manually or via script
4. Reconnect relations using `id_mapping.json`

### 3. Convert Internal Links

```bash
# Run post-processor to convert links
python3 post_migration_processor.py

# Review conversion report
cat migration_output/links_conversion_report.md
```

## 🐛 Troubleshooting

### Common Issues

<details>
<summary><b>Error: "Notion API error 401"</b></summary>

**Cause**: Invalid token or pages not shared with integration.

**Solution**:
1. Verify token is correct
2. In Notion, share pages with your integration
3. Ensure integration has appropriate permissions
</details>

<details>
<summary><b>Error: "SiYuan API error 401"</b></summary>

**Cause**: Invalid SiYuan API token.

**Solution**:
1. Regenerate token in SiYuan (Settings → About)
2. Update `.env` with new token
3. Verify SiYuan is running
</details>

<details>
<summary><b>Warning: "Database XXX needs manual recreation"</b></summary>

**Cause**: Notion databases cannot be auto-migrated.

**Solution**:
1. Export database as CSV from Notion
2. Follow instructions in `databases_instructions.md`
3. Recreate as Attribute View in SiYuan
</details>

<details>
<summary><b>Links not working after migration</b></summary>

**Cause**: Links still use Notion IDs.

**Solution**:
```bash
python3 post_migration_processor.py
```
This converts links using the ID mapping.
</details>

See [README_MIGRATION.md](README_MIGRATION.md) for comprehensive troubleshooting.

## 🛡️ Rollback

If migration goes wrong:

### Via SiYuan UI
```
Menu → Data History → Snapshots
→ Select "Before Notion Migration"
→ Restore
```

### Via Command Line
```bash
# Remove migration folder only
rm -rf ~/SiYuan/data/*/migration-notion/
```

## 📚 Documentation

- **[QUICK_START.md](QUICK_START.md)** - Get started in 3 steps
- **[README_MIGRATION.md](README_MIGRATION.md)** - Complete technical documentation
- **[API Reference](https://github.com/siyuan-note/siyuan/blob/master/API.md)** - SiYuan API docs
- **[Notion API](https://developers.notion.com/)** - Notion API documentation

## 🧪 Testing

```bash
# Run with dry run to test extraction/conversion
export DRY_RUN=true
python3 notion_to_siyuan_migrator.py

# Check output in migration_output/
ls -lh migration_output/

# Verify markdown conversion
cat migration_output/sample_converted.md
```

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/notion-to-siyuan-migrator.git

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/
```

## 🗺️ Roadmap

- [ ] Support for Attribute Views via raw SiYuan API
- [ ] Automatic internal link conversion
- [ ] Incremental sync (instead of one-shot migration)
- [ ] GUI interface for easier configuration
- [ ] Docker container for portable execution
- [ ] CI/CD integration for automated migrations

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [SiYuan](https://github.com/siyuan-note/siyuan) - Amazing block-based note-taking app
- [Notion](https://www.notion.so) - Source platform with excellent API
- Community contributors and testers

## 📧 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/notion-to-siyuan-migrator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/notion-to-siyuan-migrator/discussions)

## ⭐ Star History

If this project helped you, please consider giving it a star! ⭐

---

**Made with ❤️ for the SiYuan community**

*Migrating knowledge, preserving structure, empowering workflows.*
