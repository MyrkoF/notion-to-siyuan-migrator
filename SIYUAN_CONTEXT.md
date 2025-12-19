# 📚 SiYuan Context & Resources

> Comprehensive reference for SiYuan architecture, APIs, and plugin ecosystem for the Notion to SiYuan migration project.

## 📖 Table of Contents

- [Official Documentation](#-official-documentation)
- [SiYuan Architecture](#-siyuan-architecture)
- [API Reference](#-api-reference)
- [Plugin Ecosystem](#-plugin-ecosystem)
- [Development Resources](#-development-resources)
- [Migration Considerations](#-migration-considerations)

---

## 🌐 Official Documentation

### Core Resources

| Resource | URL | Purpose |
|----------|-----|---------|
| **SiYuan Homepage** | https://b3log.org/siyuan/en/ | Official website and downloads |
| **Download Page** | https://b3log.org/siyuan/en/download.html | Latest releases |
| **Community Docs** | https://docs.siyuan-note.club/en/ | Developer documentation |
| **API Documentation** | https://github.com/siyuan-note/siyuan/blob/master/API.md | Complete API reference |
| **Community Forum** | https://liuyun.io | User discussions and support |

### Local Sync Server

- **URL**: `http://192.168.1.11:9101/browser/siyuan-sync/repo%2F`
- **Purpose**: Local synchronization repository browser

---

## 🏗️ SiYuan Architecture

### Core Concepts

#### 1. **Block-Based System**
- Everything in SiYuan is a block (paragraphs, headings, lists, etc.)
- Each block has a unique ID (e.g., `20210808180320-fqgskfj`)
- Blocks can be referenced and linked across documents

#### 2. **Notebooks**
- Top-level organizational units
- Each notebook has a unique ID
- Can be opened/closed independently
- Support custom configurations

#### 3. **Documents**
- Stored as `.sy` files
- Contain hierarchical blocks
- Support Markdown with extensions
- Include metadata and properties

#### 4. **Attributes**
- Custom properties attached to blocks
- Key-value pairs for metadata
- Support for database-like views

---

## 🔌 API Reference

### Authentication

```bash
# API Endpoint
http://127.0.0.1:6806

# Authorization Header
Authorization: Token <your-api-token>

# Content-Type
Content-Type: application/json
```

### Response Format

```json
{
  "code": 0,        // 0 = success, non-zero = error
  "msg": "",        // Error message if any
  "data": {}        // Response data
}
```

### Key Endpoints for Migration

#### Notebooks

```bash
# List all notebooks
POST /api/notebook/lsNotebooks

# Create notebook
POST /api/notebook/createNotebook
{
  "name": "Notebook name"
}

# Open/Close notebook
POST /api/notebook/openNotebook
POST /api/notebook/closeNotebook
{
  "notebook": "20210831090520-7dvbdv0"
}
```

#### Documents

```bash
# Create document with Markdown
POST /api/filetree/createDocWithMd
{
  "notebook": "20210817205410-2kvfpfn",
  "path": "/foo/bar",
  "markdown": "# Content here"
}

# Rename document
POST /api/filetree/renameDoc
{
  "notebook": "20210831090520-7dvbdv0",
  "path": "/20210902210113-0avi12f.sy",
  "title": "New title"
}

# Move documents
POST /api/filetree/moveDocs
{
  "fromPaths": ["/20210917220056-yxtyl7i.sy"],
  "toNotebook": "20210817205410-2kvfpfn",
  "toPath": "/"
}
```

#### Blocks

```bash
# Insert blocks
POST /api/block/insertBlock
{
  "dataType": "markdown",
  "data": "Block content",
  "parentID": "parent-block-id"
}

# Update block
POST /api/block/updateBlock
{
  "id": "block-id",
  "dataType": "markdown",
  "data": "Updated content"
}

# Get block children
POST /api/block/getChildBlocks
{
  "id": "parent-block-id"
}
```

#### Attributes

```bash
# Set block attributes
POST /api/attr/setBlockAttrs
{
  "id": "block-id",
  "attrs": {
    "custom-key": "custom-value",
    "tags": "tag1,tag2"
  }
}

# Get block attributes
POST /api/attr/getBlockAttrs
{
  "id": "block-id"
}
```

#### SQL Queries

```bash
# Execute SQL query
POST /api/query/sql
{
  "stmt": "SELECT * FROM blocks WHERE content LIKE '%search%' LIMIT 10"
}
```

#### Assets

```bash
# Upload assets (images, files)
POST /api/asset/upload
# Multipart form data with file
```

---

## 🔧 Plugin Ecosystem

### Recommended Plugins for Migration

#### 1. **Task Note Management**
- **Repository**: https://github.com/Achuan-2/siyuan-plugin-task-note-management
- **Purpose**: Task management with Bullet Journal method
- **Features**:
  - Document and block reminders
  - Calendar view for scheduling
  - Pomodoro timer
  - Habit tracking
  - Project kanban boards
- **Relevance**: Useful for migrating Notion task databases

#### 2. **KMind Plugin**
- **Repository**: https://github.com/suka233/siyuan-kmind-plugin
- **Purpose**: Mind mapping integration
- **Features**:
  - Document tree to mind map conversion
  - Multiple layout and theme support
  - Node mirroring
  - PDF annotation linking
  - Global search integration
- **Relevance**: Visualizing migrated hierarchical content

#### 3. **Database Properties Panel**
- **Repository**: https://github.com/Macavity/siyuan-database-properties-panel
- **Purpose**: Enhanced property management
- **Features**:
  - Visual property panel
  - Database-like views
  - Property editing interface
- **Relevance**: **CRITICAL** for recreating Notion databases as Attribute Views

#### 4. **Templater**
- **Repository**: https://github.com/hogmoff/siyuan-plugin-templater
- **Purpose**: Advanced template management
- **Features**:
  - Path-dependent templates
  - Sprig template engine
  - Hotkey support
  - Extended functions
- **Relevance**: Creating templates for migrated content types

---

## 💻 Development Resources

### Plugin Development

```bash
# Community Developer Docs
https://docs.siyuan-note.club/en/guide/plugin/

# Plugin Development Guide
https://docs.siyuan-note.club/en/guide/

# Reference Documentation
https://docs.siyuan-note.club/en/reference/
```

### Theme Development

```bash
# Theme Development Guide
https://docs.siyuan-note.club/en/guide/theme/
```

### Widget Development

```bash
# Widget Development Guide
https://docs.siyuan-note.club/en/guide/widget/
```

---

## 🔄 Migration Considerations

### 1. **Notion Properties → SiYuan Attributes**

**Current Approach** (in `notion_to_siyuan_migrator.py`):
```python
# Properties stored in YAML frontmatter
def to_markdown(self):
    frontmatter = {
        'notion_id': self.id,
        'title': self.title,
        'properties': self.properties,
        'tags': self.tags
    }
    return f"---\n{yaml.dump(frontmatter)}---\n\n{content}"
```

**Recommended Enhancement**:
```python
# Use SiYuan Attributes API after document creation
def set_document_attributes(siyuan_client, doc_id, properties):
    attrs = {}
    for key, value in properties.items():
        # Convert Notion property types to SiYuan attributes
        if isinstance(value, list):
            attrs[key] = ','.join(str(v) for v in value)
        else:
            attrs[key] = str(value)
    
    siyuan_client._request('/api/attr/setBlockAttrs', {
        'id': doc_id,
        'attrs': attrs
    })
```

### 2. **Notion Databases → SiYuan Attribute Views**

**Challenge**: Notion databases cannot be directly migrated.

**Solution Strategy**:

1. **Detect databases** (already implemented in `analyze_notion_databases.py`)
2. **Export schema** to JSON
3. **Create Attribute View** in SiYuan using Database Properties Panel plugin
4. **Recreate structure** manually or via API
5. **Import data** using SQL API or batch attribute setting

**Example Database Recreation**:
```python
def recreate_database_as_attribute_view(database_schema, entries):
    """
    Recreate Notion database as SiYuan Attribute View
    """
    # 1. Create parent document for the database
    parent_doc_id = siyuan_client.create_document(
        notebook_id=target_notebook,
        path=f"/databases/{database_schema['name']}",
        markdown=f"# {database_schema['name']}\n\nDatabase view"
    )
    
    # 2. Create child documents for each entry
    for entry in entries:
        doc_id = siyuan_client.create_document(
            notebook_id=target_notebook,
            path=f"/databases/{database_schema['name']}/{entry['title']}",
            markdown=convert_entry_to_markdown(entry)
        )
        
        # 3. Set attributes for database properties
        attrs = convert_properties_to_attrs(entry['properties'])
        siyuan_client._request('/api/attr/setBlockAttrs', {
            'id': doc_id,
            'attrs': attrs
        })
```

### 3. **Internal Links Conversion**

**Current Approach** (in `post_migration_processor.py`):
- Maintains `id_mapping.json` (Notion ID → SiYuan ID)
- Post-processes documents to convert links

**Enhancement with SiYuan Block References**:
```python
def convert_notion_link_to_siyuan_ref(notion_link, id_mapping):
    """
    Convert Notion link to SiYuan block reference
    """
    notion_id = extract_id_from_link(notion_link)
    siyuan_id = id_mapping.get(notion_id)
    
    if siyuan_id:
        # SiYuan block reference format
        return f"(('{siyuan_id}' '{link_text}'))"
    else:
        return notion_link  # Keep original if not found
```

### 4. **Hierarchical Structure Preservation**

**SiYuan Path Format**:
```
/parent-folder/child-folder/document-name
```

**Mapping Notion Hierarchy**:
```python
def build_siyuan_path(notion_page, parent_map):
    """
    Build SiYuan path from Notion page hierarchy
    """
    path_parts = []
    current_id = notion_page.parent_id
    
    while current_id:
        parent = parent_map.get(current_id)
        if parent:
            path_parts.insert(0, sanitize_filename(parent.title))
            current_id = parent.parent_id
        else:
            break
    
    path_parts.append(sanitize_filename(notion_page.title))
    return '/' + '/'.join(path_parts)
```

### 5. **Tags Migration**

**Notion Tags** → **SiYuan Tags**:
```python
def migrate_tags(notion_tags):
    """
    Convert Notion tags to SiYuan format
    """
    # SiYuan tags use # prefix
    siyuan_tags = [f"#{tag.replace(' ', '-')}" for tag in notion_tags]
    
    # Can be stored as:
    # 1. In document content: #tag1 #tag2
    # 2. As block attribute: tags="tag1,tag2"
    
    return siyuan_tags
```

---

## 🚀 Next Steps for Migration Enhancement

### Phase 1: Current Implementation ✅
- [x] Extract Notion content
- [x] Convert to Markdown with YAML frontmatter
- [x] Create documents in SiYuan
- [x] Maintain ID mapping
- [x] Detect databases

### Phase 2: Enhanced Integration 🔄
- [ ] Use SiYuan Attributes API instead of YAML frontmatter
- [ ] Implement block-level migration (not just documents)
- [ ] Convert internal links to SiYuan block references
- [ ] Migrate tags as SiYuan tags (not just metadata)

### Phase 3: Database Recreation 📊
- [ ] Install Database Properties Panel plugin
- [ ] Create Attribute Views for each Notion database
- [ ] Batch import database entries with attributes
- [ ] Recreate relations using ID mapping

### Phase 4: Advanced Features 🎯
- [ ] Integrate with KMind for mind map views
- [ ] Use Templater for content templates
- [ ] Implement incremental sync (not one-shot migration)
- [ ] Create custom plugin for automated database recreation

---

## 📝 Code Examples

### Complete Migration Flow with Attributes

```python
class EnhancedSiYuanMigrator:
    """
    Enhanced migrator using SiYuan Attributes API
    """
    
    def migrate_page_with_attributes(self, notion_page: NotionPage):
        # 1. Create document
        doc_id = self.siyuan_client.create_document(
            notebook_id=self.target_notebook,
            path=self.build_path(notion_page),
            markdown=notion_page.to_markdown()
        )
        
        # 2. Set attributes (properties)
        if notion_page.properties:
            attrs = self.convert_properties_to_attrs(notion_page.properties)
            self.siyuan_client._request('/api/attr/setBlockAttrs', {
                'id': doc_id,
                'attrs': attrs
            })
        
        # 3. Set tags
        if notion_page.tags:
            tag_attr = ','.join(notion_page.tags)
            self.siyuan_client._request('/api/attr/setBlockAttrs', {
                'id': doc_id,
                'attrs': {'tags': tag_attr}
            })
        
        # 4. Store mapping
        self.id_mapping[notion_page.id] = doc_id
        
        return doc_id
    
    def convert_properties_to_attrs(self, properties: Dict) -> Dict:
        """
        Convert Notion properties to SiYuan attributes
        """
        attrs = {}
        
        for key, value in properties.items():
            if isinstance(value, dict):
                # Handle Notion property types
                prop_type = value.get('type')
                
                if prop_type == 'select':
                    attrs[key] = value['select']['name']
                elif prop_type == 'multi_select':
                    attrs[key] = ','.join([s['name'] for s in value['multi_select']])
                elif prop_type == 'date':
                    attrs[key] = value['date']['start']
                elif prop_type == 'number':
                    attrs[key] = str(value['number'])
                elif prop_type == 'checkbox':
                    attrs[key] = 'true' if value['checkbox'] else 'false'
                # Add more type conversions as needed
            else:
                attrs[key] = str(value)
        
        return attrs
```

---

## 🔗 Quick Reference Links

### Documentation
- [SiYuan API](https://github.com/siyuan-note/siyuan/blob/master/API.md)
- [Developer Docs](https://docs.siyuan-note.club/en/)
- [Community Forum](https://liuyun.io)

### Plugins
- [Task Management](https://github.com/Achuan-2/siyuan-plugin-task-note-management)
- [KMind](https://github.com/suka233/siyuan-kmind-plugin)
- [Database Properties](https://github.com/Macavity/siyuan-database-properties-panel)
- [Templater](https://github.com/hogmoff/siyuan-plugin-templater)

### Local Resources
- Sync Server: `http://192.168.1.11:9101/browser/siyuan-sync/repo%2F`
- SiYuan API: `http://192.168.1.11:6806`

---

**Last Updated**: 2024-12-18  
**Project**: Notion to SiYuan Migrator  
**Maintainer**: MyrkoF
