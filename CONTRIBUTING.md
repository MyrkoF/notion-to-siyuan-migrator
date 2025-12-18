# Contributing to Notion to SiYuan Migrator

First off, thank you for considering contributing to this project! 🎉

## 🤝 Ways to Contribute

- 🐛 Report bugs and issues
- 💡 Suggest new features or enhancements
- 📖 Improve documentation
- 🔧 Submit bug fixes
- ✨ Add new features
- 🧪 Write tests
- 🌐 Translate to other languages

## 🚀 Getting Started

### Development Setup

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/notion-to-siyuan-migrator.git
   cd notion-to-siyuan-migrator
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   # For development dependencies:
   pip install -r requirements-dev.txt  # If available
   ```

4. **Set up your environment**
   ```bash
   cp .env.example .env
   # Edit .env with your test credentials
   ```

## 🔧 Development Workflow

### Creating a Branch

```bash
# Create a new branch for your feature/fix
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Adding or updating tests

### Making Changes

1. **Write clear, concise code**
   - Follow PEP 8 style guidelines
   - Add comments for complex logic
   - Keep functions focused and small

2. **Test your changes**
   ```bash
   # Run with dry-run mode first
   export DRY_RUN=true
   python3 notion_to_siyuan_migrator.py
   
   # Test specific functionality
   pytest tests/  # If tests exist
   ```

3. **Update documentation**
   - Update README.md if needed
   - Add/update docstrings
   - Update CHANGELOG.md (if exists)

### Committing Changes

```bash
# Stage your changes
git add .

# Commit with a clear message
git commit -m "feat: Add support for nested callouts

- Implement nested callout parsing
- Add tests for nested structures
- Update documentation with examples"
```

**Commit message format:**
```
<type>: <subject>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Pushing and Pull Request

```bash
# Push your branch
git push origin feature/your-feature-name
```

Then on GitHub:
1. Navigate to your fork
2. Click "Pull Request"
3. Select your branch
4. Fill in the PR template
5. Submit!

## 📋 Pull Request Guidelines

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] Changes are tested (dry-run mode at minimum)
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] No merge conflicts with main branch

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
How was this tested?

## Screenshots (if applicable)

## Checklist
- [ ] Code tested with dry-run mode
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

## 🐛 Reporting Bugs

**Before creating a bug report:**
1. Check if the bug is already reported
2. Try with the latest version
3. Collect relevant information

**Bug report should include:**
- Clear, descriptive title
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs
- Environment details:
  - Python version
  - OS
  - SiYuan version
  - Notion workspace size (approx)

**Template:**
```markdown
**Describe the bug**
Clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Configure with '...'
2. Run command '...'
3. See error

**Expected behavior**
What you expected to happen.

**Error logs**
```
Paste error messages here
```

**Environment:**
- Python version: 3.x.x
- OS: Ubuntu 22.04 / Windows 11 / macOS 14
- SiYuan version: x.x.x
```

## 💡 Suggesting Features

**Feature request template:**
```markdown
**Is your feature related to a problem?**
Clear description of the problem.

**Describe the solution**
How you'd like it to work.

**Describe alternatives**
Other solutions you've considered.

**Additional context**
Screenshots, examples, etc.
```

## 🏗️ Code Style

### Python Style Guidelines

- Follow [PEP 8](https://pep8.org/)
- Maximum line length: 100 characters
- Use type hints where possible
- Document functions with docstrings

**Example:**
```python
def convert_notion_block(block: Dict[str, Any]) -> str:
    """
    Convert a Notion block to Markdown format.
    
    Args:
        block: Notion block object from API
        
    Returns:
        Markdown representation of the block
        
    Raises:
        ValueError: If block type is not supported
    """
    block_type = block.get("type")
    # Implementation...
```

### File Organization

```
notion-to-siyuan-migrator/
├── src/                    # Source code (if refactored)
│   ├── extractors/        # Notion extraction logic
│   ├── converters/        # Markdown conversion
│   └── importers/         # SiYuan import logic
├── tests/                 # Test files
├── docs/                  # Additional documentation
└── examples/              # Example configurations
```

## 🧪 Testing

### Manual Testing

```bash
# Always test with dry-run first
export DRY_RUN=true
python3 notion_to_siyuan_migrator.py

# Test with small Notion workspace
# Verify output in migration_output/

# If confident, test real migration
export DRY_RUN=false
python3 notion_to_siyuan_migrator.py
```

### Automated Tests (Future)

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_conversion.py

# Run with coverage
pytest --cov=src tests/
```

## 📖 Documentation

### README Updates

Update when:
- Adding new features
- Changing configuration options
- Modifying installation process
- Adding new dependencies

### Code Comments

```python
# Good: Explains WHY
# Use batch processing to avoid rate limits
BATCH_SIZE = 50

# Bad: Explains WHAT (obvious from code)
# Set batch size to 50
BATCH_SIZE = 50
```

### Docstrings

Required for:
- All public functions
- All classes
- Complex algorithms

## 🙏 Recognition

Contributors will be:
- Listed in README.md
- Credited in release notes
- Mentioned in commit messages

## ❓ Questions?

- Create a [Discussion](https://github.com/username/notion-to-siyuan-migrator/discussions)
- Open an [Issue](https://github.com/username/notion-to-siyuan-migrator/issues)
- Check existing documentation

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing! 🎉**
