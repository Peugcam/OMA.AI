# 📊 OMA Code Analysis & Duplicate Detection Guide

This guide covers the integrated code analysis and duplicate detection system for the OMA project.

## 🎯 Overview

The analysis system includes:

1. **jscpd** - Copy/Paste Detector for finding duplicate code
2. **Pylint with Custom Checkers** - Python linting with project-specific rules
3. **Bandit** - Security vulnerability scanner
4. **Pre-commit Hooks** - Automated checks during development

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Node.js dependencies for jscpd
npm install

# Install Python analysis tools
pip install -r requirements_analysis.txt

# Install pre-commit hooks
pre-commit install
```

### 2. Run Complete Analysis

```bash
# Run all analysis tools
python run_analysis.py

# Or run individually
npm run check:duplicates      # Duplicate detection
pylint --rcfile=.pylintrc .   # Linting
bandit -r . -c .bandit.yaml   # Security scan
```

## 📋 Available Commands

### Duplicate Detection (jscpd)

```bash
# Run duplicate detection
npm run check:duplicates

# Watch mode (runs on file changes)
npm run check:duplicates:watch

# CI mode (exits with error code if duplicates found)
npm run check:duplicates:ci

# Generate and open HTML report
npm run report
```

### Pylint Custom Checkers

```bash
# Run all pylint checks
pylint --rcfile=.pylintrc .

# Run only custom checkers
pylint --load-plugins=pylint_custom_checkers \
       --disable=all \
       --enable=duplicate-try-except,duplicate-api-call,hardcoded-string-constant .

# Run on specific files
pylint --rcfile=.pylintrc core/ai_client.py agents/supervisor_agent.py
```

### Security Analysis

```bash
# Run Bandit security scan
bandit -r . -c .bandit.yaml

# Generate JSON report
bandit -r . -c .bandit.yaml -f json -o reports/bandit_report.json
```

### Pre-commit Hooks

```bash
# Install hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files

# Run specific hook
pre-commit run pylint-custom --all-files
pre-commit run jscpd --all-files

# Update hook versions
pre-commit autoupdate
```

## 🔍 Custom Pylint Checkers

### Available Custom Rules

#### 1. **duplicate-try-except** (W9001)
Detects duplicate error handling patterns.

```python
# ❌ Bad - Duplicate pattern
async def fetch_data1():
    try:
        await client.get("/api/data")
    except HTTPError as e:
        log.error(f"HTTP Error: {e}")

async def fetch_data2():
    try:  # Same pattern!
        await client.post("/api/data")
    except HTTPError as e:
        log.error(f"HTTP Error: {e}")
```

```python
# ✅ Good - Use decorator or utility
@handle_http_errors
async def fetch_data1():
    await client.get("/api/data")

@handle_http_errors
async def fetch_data2():
    await client.post("/api/data")
```

#### 2. **duplicate-api-call** (W9002)
Detects duplicate API call patterns.

```python
# ❌ Bad - Repeated API calls
result1 = client.post("/api/endpoint", data=data1)
result2 = client.post("/api/endpoint", data=data2)

# ✅ Good - Create reusable method
def create_resource(data):
    return client.post("/api/endpoint", data=data)

result1 = create_resource(data1)
result2 = create_resource(data2)
```

#### 3. **hardcoded-string-constant** (W9003)
Detects URLs, API endpoints that should be constants.

```python
# ❌ Bad - Hardcoded
response = requests.get("https://api.example.com/v1/users")

# ✅ Good - Use constants
API_BASE_URL = "https://api.example.com/v1"
response = requests.get(f"{API_BASE_URL}/users")
```

#### 4. **missing-async-error-handling** (W9004)
Ensures async functions have error handling.

```python
# ❌ Bad - No error handling
async def process_task():
    result = await external_api.call()
    return result

# ✅ Good - Proper error handling
async def process_task():
    try:
        result = await external_api.call()
        return result
    except Exception as e:
        log.error(f"Task failed: {e}")
        raise
```

#### 5. **excessive-nesting** (W9005)
Warns when nesting depth exceeds 3 levels.

```python
# ❌ Bad - Too much nesting
def process(data):
    if data:
        for item in data:
            if item.valid:
                for sub in item.subs:
                    if sub.active:  # 4 levels deep!
                        process_sub(sub)

# ✅ Good - Refactored
def process(data):
    if not data:
        return

    valid_items = [item for item in data if item.valid]
    for item in valid_items:
        process_active_subs(item.subs)

def process_active_subs(subs):
    active_subs = [s for s in subs if s.active]
    for sub in active_subs:
        process_sub(sub)
```

#### 6. **agent-missing-method** (W9101)
Ensures agent classes implement required methods.

```python
# ❌ Bad - Missing required method
class CustomAgent:
    def __init__(self):
        self.state = {}

# ✅ Good - Implements interface
class CustomAgent:
    def __init__(self):
        self.state = {}

    def run(self, task):
        # Implementation
        pass
```

#### 7. **agent-missing-logging** (W9103)
Ensures agent methods include logging.

```python
# ❌ Bad - No logging
def process_task(self, task):
    result = self.execute(task)
    return result

# ✅ Good - Includes logging
def process_task(self, task):
    self.logger.info(f"Processing task: {task.id}")
    result = self.execute(task)
    self.logger.debug(f"Task result: {result}")
    return result
```

## 📊 Understanding jscpd Reports

### Configuration (.jscpd.json)

```json
{
  "threshold": 20,           // Minimum tokens for duplication
  "minLines": 5,            // Minimum lines to consider
  "minTokens": 50,          // Minimum tokens to consider
  "format": ["python"],     // File types to analyze
  "output": "./reports/jscpd"
}
```

### Reading Reports

After running `npm run check:duplicates`, check:

- **Console output**: Quick summary
- **reports/jscpd/html/index.html**: Visual HTML report
- **reports/jscpd/jscpd-report.json**: Machine-readable data

## 🔄 Pre-commit Workflow

When you commit code, these checks run automatically:

1. **Black** - Auto-formats Python code
2. **isort** - Sorts imports
3. **Pylint** - Custom rule checks
4. **jscpd** - Duplicate detection
5. **Bandit** - Security scan
6. **Common checks** - Trailing whitespace, file size, etc.

If any check fails, the commit is blocked until you fix the issues.

### Skipping Hooks (Use Sparingly!)

```bash
# Skip all hooks (not recommended)
git commit --no-verify

# Skip specific hook
SKIP=pylint-custom git commit -m "message"
```

## 📈 CI/CD Integration

### GitHub Actions Example

```yaml
name: Code Quality
on: [push, pull_request]

jobs:
  analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install dependencies
        run: |
          pip install -r requirements_analysis.txt
          npm install

      - name: Run analysis
        run: python run_analysis.py

      - name: Upload reports
        uses: actions/upload-artifact@v3
        with:
          name: analysis-reports
          path: reports/
```

## 🎛️ Configuration Files

### .pylintrc
Main Pylint configuration with custom checker settings.

### .jscpd.json
jscpd duplicate detection configuration.

### .bandit.yaml
Bandit security scanner configuration.

### .pre-commit-config.yaml
Pre-commit hooks configuration.

### pylint_custom_checkers.py
Custom Pylint checker implementations.

## 🐛 Troubleshooting

### jscpd not found
```bash
npm install
```

### Pylint custom checkers not loading
```bash
# Ensure you're in the project directory
cd /path/to/OMA_REFACTORED

# Run with explicit path
python -m pylint --load-plugins=pylint_custom_checkers .
```

### Pre-commit hooks not running
```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install

# Update hooks
pre-commit autoupdate
```

### Bandit false positives
Edit `.bandit.yaml` to skip specific tests:

```yaml
skips:
  - B101  # assert_used
  - B601  # paramiko_calls
```

## 📚 Best Practices

1. **Run analysis frequently** - Don't let issues accumulate
2. **Fix duplicates early** - Easier to refactor early than later
3. **Don't ignore warnings** - They often indicate design issues
4. **Use pre-commit hooks** - Catch issues before they reach CI/CD
5. **Review reports regularly** - Track quality metrics over time
6. **Customize rules** - Adapt checkers to your team's needs

## 🎯 Integration with Development Workflow

### Daily Development
```bash
# Start of day - check current state
python run_analysis.py

# During development - watch mode
npm run check:duplicates:watch

# Before commit - pre-commit handles this automatically
git add .
git commit -m "Your message"  # Hooks run automatically
```

### Code Review
```bash
# Generate reports for PR
python run_analysis.py

# Check specific changes
pylint $(git diff --name-only main...HEAD | grep '\.py$')
```

### Refactoring Sessions
```bash
# Identify duplicates
npm run report

# Fix duplicates and re-run
python run_analysis.py
```

## 📊 Metrics to Track

Monitor these over time:
- Duplication percentage (target: < 5%)
- Critical issues (target: 0)
- Code complexity (Cyclomatic complexity < 10)
- Security issues (target: 0 HIGH/CRITICAL)

## 🤝 Contributing

When adding new patterns to detect:

1. Edit `pylint_custom_checkers.py`
2. Add new message code (W90XX or W91XX)
3. Implement checker logic
4. Test on sample code
5. Update this documentation

---

**Need help?** Check the reports in `./reports/` or run `python run_analysis.py` for detailed output.
