# 🔍 Code Analysis & Duplicate Detection - OMA Project

> **Status:** ✅ **FULLY OPERATIONAL** | **Duplication:** 3.96% ✅ (Target: <5%)

## 🎯 What This Does

This project now includes a comprehensive code analysis system that:

1. **Detects duplicate code** in real-time during development
2. **Enforces code quality patterns** with custom Python rules
3. **Scans for security vulnerabilities** automatically
4. **Prevents bad code** from being committed via pre-commit hooks

## ⚡ Quick Start

### 1. Install (One Command)

**Windows:**
```bash
setup_analysis.bat
```

**Linux/Mac:**
```bash
chmod +x setup_analysis.sh && ./setup_analysis.sh
```

### 2. Run Analysis

```bash
python run_analysis.py
```

### 3. View Results

Open `reports/jscpd/html/index.html` in your browser to see duplicate code visualization.

## 📊 Current Project Health

```
┌────────┬────────────────┬─────────────┬──────────────┬──────────────┬──────────────────┬───────────────────┐
│ Format │ Files analyzed │ Total lines │ Total tokens │ Clones found │ Duplicated lines │ Duplicated tokens │
├────────┼────────────────┼─────────────┼──────────────┼──────────────┼──────────────────┼───────────────────┤
│ python │ 22             │ 6605        │ 40405        │ 22           │ 221 (3.35%)      │ 1600 (3.96%)      │
└────────┴────────────────┴─────────────┴──────────────┴──────────────┴──────────────────┴───────────────────┘
```

**Assessment:** ✅ **HEALTHY** - Duplication is below 5% threshold!

## 🛠️ Tools Included

| Tool | Purpose | Status |
|------|---------|--------|
| **jscpd** | Copy/Paste Detector | ✅ Active |
| **Pylint + Custom Checkers** | Code pattern detection | ✅ Active |
| **Bandit** | Security scanner | ✅ Active |
| **Pre-commit Hooks** | Automatic validation | ✅ Active |
| **Black + isort** | Code formatting | ✅ Active |
| **MyPy** | Type checking | ✅ Active |

## 📋 Available Commands

### Daily Development

```bash
# Watch for duplicates (runs automatically on save)
npm run check:duplicates:watch

# Quick duplicate check
npm run check:duplicates

# Full analysis (all tools)
python run_analysis.py
```

### Before Committing

```bash
# Pre-commit runs automatically on 'git commit'
# Or run manually:
pre-commit run --all-files
```

### View Reports

```bash
# Open HTML report (Windows)
start reports/jscpd/html/index.html

# Open HTML report (Mac)
open reports/jscpd/html/index.html

# Open HTML report (Linux)
xdg-open reports/jscpd/html/index.html
```

## 🎨 Custom Rules Implemented

### 8 Custom Pylint Checkers

| ID | Rule | What It Catches |
|----|------|-----------------|
| W9001 | duplicate-try-except | Repeated error handling patterns |
| W9002 | duplicate-api-call | Repeated API call patterns |
| W9003 | hardcoded-string-constant | URLs/endpoints not in constants |
| W9004 | missing-async-error-handling | Async functions without try/except |
| W9005 | excessive-nesting | Code nested more than 3 levels |
| W9006 | too-many-locals | Functions with >15 local variables |
| W9101 | agent-missing-method | Agent classes missing required methods |
| W9103 | agent-missing-logging | Agent methods without logging |

### Examples

**❌ Bad:**
```python
async def fetch_user():
    result = await api.get("/users")  # Missing error handling!
    return result
```

**✅ Good:**
```python
async def fetch_user():
    try:
        result = await api.get("/users")
        return result
    except Exception as e:
        logger.error(f"Failed to fetch user: {e}")
        raise
```

## 📁 Project Structure

```
OMA_REFACTORED/
├── 📊 Analysis Tools
│   ├── .jscpd.json                    # Duplicate detection config
│   ├── .pylintrc                      # Pylint configuration
│   ├── .pre-commit-config.yaml        # Pre-commit hooks
│   ├── .bandit.yaml                   # Security config
│   ├── pylint_custom_checkers.py      # Custom rules (230 lines)
│   ├── run_analysis.py                # Main analyzer (280 lines)
│   └── requirements_analysis.txt      # Python dependencies
│
├── 🚀 Setup Scripts
│   ├── setup_analysis.bat             # Windows setup
│   └── setup_analysis.sh              # Linux/Mac setup
│
├── 📖 Documentation
│   ├── README_ANALYSIS.md             # This file
│   ├── CODE_ANALYSIS_GUIDE.md         # Complete guide (450 lines)
│   ├── QUICK_REFERENCE.md             # Quick reference card
│   └── ANALYSIS_SUMMARY.md            # Implementation summary
│
├── 📊 Reports (Auto-generated)
│   └── reports/
│       ├── jscpd/
│       │   ├── html/                  # Visual duplicate report
│       │   └── jscpd-report.json      # Machine-readable data
│       ├── pylint_report.json         # Linting results
│       ├── bandit_report.json         # Security scan results
│       └── analysis_summary.json      # Combined summary
│
└── 🐍 Your Code
    ├── core/                          # Core modules
    ├── agents/                        # Agent implementations
    └── ...
```

## 🔄 How It Works

### Development Workflow

```
┌─────────────────┐
│  Write Code     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Save File      │ ◄──── Watch mode detects duplicates
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Git Add        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Git Commit     │ ◄──── Pre-commit hooks run automatically
└────────┬────────┘
         │
    ┌────┴────┐
    │ Success? │
    └─┬────┬──┘
  No  │    │ Yes
      │    │
      ▼    ▼
   Fix   Push
  Issues
```

### Pre-commit Checks (Automatic)

When you run `git commit`, these checks run automatically:

1. ✅ **Black** - Formats Python code
2. ✅ **isort** - Sorts imports
3. ✅ **Pylint** - Checks custom rules
4. ✅ **jscpd** - Detects duplicates
5. ✅ **Bandit** - Scans for security issues
6. ✅ **File checks** - Trailing whitespace, file size, etc.

If any check fails, the commit is blocked until you fix it!

## 🎯 Key Features

### 1. Real-time Duplicate Detection

```bash
npm run check:duplicates:watch
```

Watches your files and shows duplicates immediately when you save.

### 2. Custom Pattern Detection

8 custom Pylint rules specifically designed for this project's patterns.

### 3. Security Scanning

Automatic detection of:
- SQL injection vulnerabilities
- XSS risks
- Hardcoded credentials
- Insecure cryptography
- And 40+ more security issues

### 4. Automated Quality Gates

Pre-commit hooks prevent bad code from entering the repository.

### 5. Comprehensive Reporting

- Visual HTML reports
- JSON data for automation
- Console summaries
- CI/CD integration ready

## 📈 Metrics & Goals

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Code Duplication | 3.96% | < 5% | ✅ Excellent |
| Critical Issues | 0 | 0 | ✅ Good |
| Security Issues | - | 0 | ⏳ Run full analysis |
| Test Coverage | - | > 80% | 📋 To track |

## 🚨 Top Duplicates Found

1. **Test Setup Code** - Similar initialization in test files
   - **Fix:** Create shared test fixtures

2. **Agent Initialization** - Duplicate setup in agent classes
   - **Fix:** Create base agent class

3. **Error Handling** - Repeated try-except patterns
   - **Fix:** Use decorators or error handling utilities

4. **API Calls** - Similar API call patterns
   - **Fix:** Create reusable API client methods

## 💡 Best Practices

### Daily Development

```bash
# Morning: Check current state
python run_analysis.py

# During work: Watch mode
npm run check:duplicates:watch

# Before commit: Auto-runs via hooks
git commit -m "Your message"
```

### Code Review

```bash
# Generate reports for PR
python run_analysis.py

# Check specific files
pylint core/ai_client.py agents/supervisor_agent.py
```

### Refactoring

```bash
# Identify areas to refactor
npm run report

# Monitor improvement
python run_analysis.py
```

## 🔧 Configuration

### Customize Duplicate Detection

Edit `.jscpd.json`:
```json
{
  "threshold": 20,    // Strictness (lower = more strict)
  "minLines": 5,      // Minimum lines to consider
  "minTokens": 50     // Minimum tokens to consider
}
```

### Add Custom Rules

Edit `pylint_custom_checkers.py` to add new pattern detection rules.

### Adjust Pre-commit

Edit `.pre-commit-config.yaml` to enable/disable specific hooks.

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **README_ANALYSIS.md** | Quick overview (this file) |
| **CODE_ANALYSIS_GUIDE.md** | Complete usage guide |
| **QUICK_REFERENCE.md** | Command reference |
| **ANALYSIS_SUMMARY.md** | Implementation details |

## 🎓 Learn More

### Understanding Reports

**jscpd HTML Report:**
- Shows exact duplicate locations
- Side-by-side comparison
- Clickable file links

**Pylint Report:**
- Issue severity levels
- Line numbers
- Fix suggestions

**Bandit Report:**
- Security severity (LOW/MEDIUM/HIGH)
- CWE references
- Code context

### Advanced Usage

See `CODE_ANALYSIS_GUIDE.md` for:
- CI/CD integration
- Custom rule development
- Team workflows
- Troubleshooting

## 🤝 Integration

### VSCode

Add to `.vscode/settings.json`:
```json
{
  "python.linting.pylintEnabled": true,
  "python.linting.pylintArgs": ["--rcfile=.pylintrc"],
  "python.formatting.provider": "black"
}
```

### GitHub Actions

```yaml
- name: Code Analysis
  run: |
    npm install
    pip install -r requirements_analysis.txt
    python run_analysis.py
```

### GitLab CI

```yaml
code_analysis:
  script:
    - npm install
    - pip install -r requirements_analysis.txt
    - python run_analysis.py
  artifacts:
    paths:
      - reports/
```

## 🆘 Troubleshooting

### "npm command not found"
Install Node.js from https://nodejs.org/

### "jscpd not found"
Run: `npm install`

### "Pylint custom checkers not loading"
Ensure you're in the project root directory

### Pre-commit hooks not running
Run: `pre-commit install`

## ✨ Benefits

- 🚀 **Faster Development** - Catch issues early
- 🛡️ **Better Security** - Automatic vulnerability detection
- 📉 **Less Technical Debt** - Prevent code duplication
- 🎯 **Higher Quality** - Enforce consistent patterns
- 👥 **Team Consistency** - Automated style enforcement
- 💰 **Lower Maintenance** - Cleaner, more maintainable code

## 🎉 You're All Set!

The analysis system is fully configured and ready to use!

**Quick Start:**
```bash
# Run full analysis now
python run_analysis.py

# Or start watch mode
npm run check:duplicates:watch
```

**View Results:**
```bash
# Open the visual report
start reports/jscpd/html/index.html   # Windows
open reports/jscpd/html/index.html    # Mac
xdg-open reports/jscpd/html/index.html # Linux
```

---

**Questions?** Check `CODE_ANALYSIS_GUIDE.md` or `QUICK_REFERENCE.md`

**Happy Coding!** 🚀
