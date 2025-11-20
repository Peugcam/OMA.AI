# 🔧 Code Quality Tools - README

> **Suite completa de ferramentas profissionais de qualidade de código**

[![Quality Tools](https://img.shields.io/badge/quality-21%20tools-brightgreen)](./TOOLS_SUMMARY.md)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 14+](https://img.shields.io/badge/node-14+-green.svg)](https://nodejs.org/)

---

## ⚡ Quick Start

```bash
# 1. Setup (uma vez)
npm run setup

# 2. Run (diário)
npm run check:all

# 3. Fix (quando necessário)
npm run check:all:fix
```

**Pronto!** 🎉

---

## 🎯 O Que Faz?

Esta suite de ferramentas analisa seu código Python automaticamente e fornece:

✅ **Formatação automática** - Black + isort
✅ **Detecção de bugs** - Flake8 + 6 plugins
✅ **Análise de qualidade** - Pylint customizado
✅ **Type checking** - MyPy
✅ **Código duplicado** - jscpd
✅ **Vulnerabilidades** - Bandit
✅ **Complexidade** - Radon
✅ **Código morto** - Vulture
✅ **CI/CD pronto** - GitHub Actions

---

## 📊 Ferramentas Incluídas

### 🎨 Formatação (3)
- **Black** - Formatação automática
- **isort** - Organização de imports
- **EditorConfig** - Consistência de editores

### 🔍 Linting (8)
- **Pylint** - Linting customizado
- **Flake8** - Style guide
- **flake8-bugbear** - Bugs e design
- **flake8-comprehensions** - Comprehensions
- **flake8-simplify** - Simplificações
- **flake8-docstrings** - Docstrings
- **flake8-annotations** - Type hints
- **pep8-naming** - Nomenclatura

### 🔐 Segurança & Qualidade (7)
- **Bandit** - Segurança
- **MyPy** - Type checking
- **jscpd** - Duplicação
- **Radon** - Complexidade
- **Vulture** - Código morto
- **Pre-commit** - Hooks
- **pytest** - Testes

---

## 📚 Documentação

| Documento | Para Quem | Quando Usar |
|-----------|-----------|-------------|
| [**QUICK_QUALITY_REFERENCE.md**](./QUICK_QUALITY_REFERENCE.md) | Todos | Comandos diários |
| [**INSTALLATION_GUIDE.md**](./INSTALLATION_GUIDE.md) | Novos usuários | Primeira vez |
| [**QUALITY_TOOLS_GUIDE.md**](./QUALITY_TOOLS_GUIDE.md) | Desenvolvedores | Referência completa |
| [**TOOLS_SUMMARY.md**](./TOOLS_SUMMARY.md) | Gerentes/Leads | Visão geral |
| [**IMPLEMENTATION_SUMMARY.md**](./IMPLEMENTATION_SUMMARY.md) | DevOps | O que foi feito |

---

## 🚀 Comandos Mais Usados

### Análise Completa
```bash
npm run check:all           # Verificar tudo
npm run check:all:fix       # Verificar + corrigir
npm run check:all:verbose   # Modo detalhado
```

### Por Categoria
```bash
npm run check:format        # Formatação
npm run check:lint:flake8   # Linting
npm run check:types         # Type checking
npm run check:duplicates    # Duplicação
npm run check:security      # Segurança
npm run check:complexity    # Complexidade
```

### Utilidades
```bash
npm run setup               # Setup inicial
npm run clean               # Limpar cache
npm run reports             # Gerar relatórios
npm test                    # Rodar testes
```

### Windows
```batch
RUN_QUALITY_CHECKS.bat           # Rodar tudo
RUN_QUALITY_CHECKS.bat --fix     # Rodar + corrigir
setup_quality_tools.bat          # Setup inicial
```

### Make (Unix/Linux/Mac)
```bash
make setup                  # Setup inicial
make check                  # Verificar tudo
make check-fix              # Verificar + corrigir
make all                    # Formatar + verificar + testar
```

---

## 📈 Métricas de Qualidade

### Targets Recomendados

| Métrica | Target | Ferramenta |
|---------|--------|------------|
| **Duplicação** | < 10% | jscpd |
| **Complexity** | A ou B | Radon CC |
| **Maintainability** | A ou B | Radon MI |
| **Coverage** | > 80% | pytest-cov |
| **Security** | 0 issues | Bandit |

### Como Verificar

```bash
# Duplicação
npm run check:duplicates

# Complexity
npm run check:complexity

# Maintainability
npm run check:maintainability

# Coverage
npm run report:coverage

# Security
npm run check:security
```

---

## 🔄 Workflow Recomendado

### Durante Desenvolvimento
```bash
# Antes de começar a trabalhar
git pull
npm run check:all:fix

# Durante o desenvolvimento
# (pre-commit hooks rodam automaticamente)

# Antes de commit
npm run check:all
git add .
git commit -m "feat: nova funcionalidade"  # Hooks rodarão

# Antes de push
npm test
git push
```

### CI/CD Automático
O workflow `.github/workflows/code-quality.yml` roda automaticamente:
- ✅ Em cada push
- ✅ Em cada pull request
- ✅ Matrix testing (Python 3.10, 3.11, 3.12)

---

## 🎓 Melhores Práticas

### 1. Formatação Primeiro
```bash
black . && isort .
```
Sempre corrija formatação antes de outras análises.

### 2. Use Pre-commit Hooks
```bash
pre-commit install
```
Previne commits com problemas.

### 3. Monitore Complexity
```bash
npm run check:complexity
```
Refatore funções com complexity C ou pior.

### 4. Elimine Duplicação
```bash
npm run check:duplicates
```
Refatore quando > 10%.

### 5. Rode Tudo Antes de PR
```bash
npm run check:all
npm test
```

---

## 🐛 Problemas Comuns

### "Tool not found"
```bash
npm run setup
```

### Muitos erros
```bash
npm run check:all:fix  # Auto-fix o que for possível
```

### Pre-commit lento
```bash
# Pule temporariamente (NÃO RECOMENDADO)
git commit --no-verify
```

### Windows - scripts não funcionam
```batch
# Use os .bat
RUN_QUALITY_CHECKS.bat
setup_quality_tools.bat
```

**Mais soluções:** [INSTALLATION_GUIDE.md#troubleshooting](./INSTALLATION_GUIDE.md#troubleshooting)

---

## 📊 Relatórios

### Gerar Relatórios
```bash
npm run reports
```

### Ver Relatórios
- **Duplicação:** `reports/jscpd/html/index.html`
- **Coverage:** `reports/coverage/index.html`

### Abrir Automaticamente
```bash
npm run report:duplicates   # Abre jscpd
npm run report:coverage     # Abre coverage
```

---

## 🔧 Configuração

### Arquivos de Config

| Arquivo | O Que Controla |
|---------|----------------|
| `pyproject.toml` | Black, isort, MyPy, pytest, Radon, Vulture |
| `.flake8` | Flake8 + plugins |
| `.pylintrc` | Pylint |
| `.jscpd.json` | jscpd |
| `.bandit.yaml` | Bandit |
| `.pre-commit-config.yaml` | Pre-commit hooks |
| `.editorconfig` | Editor settings |

### Customizar

**Exemplo: Ajustar line length**
```toml
# pyproject.toml
[tool.black]
line-length = 120  # Default: 100
```

**Exemplo: Ignorar erros específicos**
```ini
# .flake8
[flake8]
ignore = E203, W503
```

---

## 🆘 Suporte

### Documentação
1. [Quick Reference](./QUICK_QUALITY_REFERENCE.md) - Comandos rápidos
2. [Installation Guide](./INSTALLATION_GUIDE.md) - Setup
3. [Tools Guide](./QUALITY_TOOLS_GUIDE.md) - Guia completo
4. [Troubleshooting](./QUALITY_TOOLS_GUIDE.md#troubleshooting) - Problemas

### Links Úteis
- [Black Docs](https://black.readthedocs.io/)
- [Flake8 Docs](https://flake8.pycqa.org/)
- [MyPy Docs](https://mypy.readthedocs.io/)
- [Pre-commit Docs](https://pre-commit.com/)

---

## 📝 Licença

MIT License - Use livremente!

---

## 🎉 Pronto para Começar?

```bash
# 1. Setup
npm run setup

# 2. Primeira análise
npm run check:all:verbose

# 3. Auto-fix
npm run check:all:fix

# 4. Commit!
git add .
git commit -m "chore: apply code quality tools"
```

**Boa qualidade de código!** 🚀

---

**Versão:** 2.0.0 | **Data:** 2025-11-20 | **Status:** ✅ Pronto para uso
