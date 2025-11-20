# 🚀 Installation Guide - Quality Tools

Guia passo a passo para instalar e configurar todas as ferramentas de qualidade.

## 📋 Pré-requisitos

- ✅ Python 3.10+
- ✅ Node.js 14+
- ✅ npm 6+
- ✅ Git

### Verificar Versões

```bash
python --version    # Deve ser 3.10+
node --version      # Deve ser 14+
npm --version       # Deve ser 6+
git --version       # Qualquer versão recente
```

---

## ⚡ Instalação Rápida (Recomendado)

### Opção 1: NPM Script (Mais Fácil)

```bash
npm run setup
```

Isso irá:
1. ✅ Instalar todas as dependências Python
2. ✅ Instalar todas as dependências Node.js
3. ✅ Configurar pre-commit hooks

### Opção 2: Make (Unix/Linux/Mac)

```bash
make setup
```

### Opção 3: Batch (Windows)

```batch
setup_quality_tools.bat
```

---

## 🔧 Instalação Manual

### Passo 1: Dependências Python

```bash
pip install -r requirements_analysis.txt
```

**O que será instalado:**
- Black, isort (formatação)
- Pylint, Flake8 + plugins (linting)
- MyPy (type checking)
- Bandit (segurança)
- Radon, Vulture (análise)
- Pre-commit (hooks)
- pytest + plugins (testes)

### Passo 2: Dependências Node.js

```bash
npm install
```

**O que será instalado:**
- jscpd (detecção de duplicação)
- nodemon (watch mode)

### Passo 3: Pre-commit Hooks

```bash
pre-commit install
```

**O que será configurado:**
- Hooks automáticos antes de commits
- Validação de formatação
- Verificação de linting
- Análise de segurança
- Detecção de duplicação

---

## ✅ Verificação da Instalação

### Teste Rápido

```bash
# Verificar se todas as ferramentas estão disponíveis
black --version
isort --version
flake8 --version
pylint --version
mypy --version
bandit --version
radon --version
vulture --version
pre-commit --version
jscpd --version
```

### Teste Completo

```bash
# Rodar análise completa (pode mostrar warnings, é normal)
npm run check:all
```

---

## 🎯 Configuração Pós-Instalação

### 1. Configurar Editor/IDE

#### VS Code

Instale extensões recomendadas:
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-python.isort",
    "ms-python.flake8",
    "ms-python.pylint",
    "charliermarsh.ruff",
    "EditorConfig.EditorConfig"
  ]
}
```

Configure settings.json:
```json
{
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  },
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "isort.check": true
}
```

#### PyCharm

1. Configurar Black:
   - File → Settings → Tools → Black
   - Marcar "On code reformat" e "On save"

2. Configurar isort:
   - File → Settings → Tools → External Tools
   - Adicionar isort com argumentos: `--profile black .`

3. Habilitar EditorConfig:
   - Já vem habilitado por padrão

#### Sublime Text / Atom / Outros

Consulte a documentação do seu editor para:
- Habilitar EditorConfig
- Configurar formatação automática com Black
- Habilitar linting com Pylint/Flake8

### 2. Configurar Git Hooks (Opcional)

Se `pre-commit install` não funcionou:

```bash
# Desinstalar hooks antigos
pre-commit uninstall

# Limpar cache
pre-commit clean

# Reinstalar
pre-commit install

# Testar
pre-commit run --all-files
```

### 3. Gerar Relatório Inicial

```bash
# Gerar relatórios de duplicação e cobertura
npm run reports

# Abrir relatórios no navegador
# - reports/jscpd/html/index.html
# - reports/coverage/index.html
```

---

## 🐛 Troubleshooting

### Problema: "pip: command not found"

**Solução:**
```bash
# Windows
python -m pip install --upgrade pip

# Unix/Linux/Mac
python3 -m pip install --upgrade pip
```

### Problema: "npm: command not found"

**Solução:**
Instale Node.js: https://nodejs.org/

### Problema: "Permission denied" no Linux/Mac

**Solução:**
```bash
# Dar permissão de execução aos scripts
chmod +x run_quality_checks.py
chmod +x setup_analysis.sh

# Ou usar sudo para pip
sudo pip install -r requirements_analysis.txt
```

### Problema: "Module not found" ao rodar ferramentas

**Solução:**
```bash
# Verificar se está no ambiente virtual correto
which python  # ou where python no Windows

# Reinstalar dependências
pip install --force-reinstall -r requirements_analysis.txt
```

### Problema: Pre-commit hooks muito lentos

**Solução:**
```bash
# Desabilitar checks pesados temporariamente
# Edite .pre-commit-config.yaml e comente os hooks lentos

# Ou pule hooks em commits urgentes (NÃO RECOMENDADO)
git commit --no-verify -m "mensagem"
```

### Problema: Muitos erros de formatação

**Solução:**
```bash
# Auto-fix formatação
npm run check:all:fix

# Ou manualmente
black .
isort .
```

### Problema: Windows - Scripts .sh não funcionam

**Solução:**
Use os equivalentes .bat:
```batch
RUN_QUALITY_CHECKS.bat
setup_analysis.bat
```

Ou instale Git Bash / WSL.

---

## 🔄 Atualização de Ferramentas

### Atualizar Dependências Python

```bash
pip install --upgrade -r requirements_analysis.txt
```

### Atualizar Dependências Node.js

```bash
npm update
```

### Atualizar Pre-commit Hooks

```bash
npm run pre-commit:update
```

---

## 📊 Verificação Final

Execute a lista de verificação:

- [ ] Python 3.10+ instalado
- [ ] Node.js 14+ instalado
- [ ] `pip install -r requirements_analysis.txt` sem erros
- [ ] `npm install` sem erros
- [ ] `pre-commit install` executado
- [ ] `black --version` funciona
- [ ] `flake8 --version` funciona
- [ ] `npm run check:all` executa (pode ter warnings)
- [ ] Editor configurado para formatação automática
- [ ] Git hooks funcionando

### Comando de Verificação Completa

```bash
# Este comando testa TUDO
python -c "
import sys
print('✅ Python:', sys.version)
" && \
node --version && \
npm --version && \
black --version && \
flake8 --version && \
mypy --version && \
pre-commit --version && \
echo '✅ Todas as ferramentas instaladas corretamente!'
```

---

## 🎓 Primeiros Passos Após Instalação

### 1. Formatação Inicial

```bash
# Auto-formatar todo o código
black .
isort .
```

### 2. Análise Inicial

```bash
# Ver estado atual do código
npm run check:all:verbose > quality_report.txt
```

### 3. Configurar CI/CD (Opcional)

- Copie `.github/workflows/code-quality.yml` para seu repositório
- Ajuste conforme necessário
- Commit e push

### 4. Criar Branch de Qualidade

```bash
git checkout -b quality-improvements
black . && isort .
git add .
git commit -m "chore: apply code formatting"
git push
```

---

## 📚 Próximos Passos

Após a instalação, consulte:

1. **[QUICK_QUALITY_REFERENCE.md](./QUICK_QUALITY_REFERENCE.md)** - Comandos rápidos
2. **[QUALITY_TOOLS_GUIDE.md](./QUALITY_TOOLS_GUIDE.md)** - Guia completo
3. **[TOOLS_SUMMARY.md](./TOOLS_SUMMARY.md)** - Resumo de ferramentas

---

## 🆘 Suporte

Se encontrar problemas:

1. Consulte a seção [Troubleshooting](#troubleshooting) acima
2. Verifique [QUALITY_TOOLS_GUIDE.md](./QUALITY_TOOLS_GUIDE.md#troubleshooting)
3. Abra uma issue no GitHub
4. Consulte documentação oficial das ferramentas

---

**Boa instalação!** 🎉

Se tudo funcionou, você está pronto para:
```bash
npm run check:all
```
