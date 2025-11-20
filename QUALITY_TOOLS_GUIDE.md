# 🔧 Guia Completo de Ferramentas de Qualidade de Código

Este guia descreve todas as ferramentas de qualidade implementadas no projeto OMA_REFACTORED.

## 📋 Índice

- [Instalação](#instalação)
- [Ferramentas Implementadas](#ferramentas-implementadas)
- [Como Usar](#como-usar)
- [Integração CI/CD](#integração-cicd)
- [Configurações](#configurações)
- [Troubleshooting](#troubleshooting)

---

## 🚀 Instalação

### Setup Completo (Recomendado)

```bash
npm run setup
```

Isso irá:
1. Instalar todas as dependências Python
2. Instalar dependências Node.js
3. Configurar pre-commit hooks

### Instalação Manual

```bash
# Dependências Python
pip install -r requirements_analysis.txt

# Dependências Node.js
npm install

# Pre-commit hooks
pre-commit install
```

---

## 🛠️ Ferramentas Implementadas

### 1. **Black** - Formatação Automática
- **O que faz:** Formata código Python automaticamente
- **Por que usar:** Elimina discussões sobre estilo de código
- **Configuração:** `pyproject.toml` (seção `[tool.black]`)

### 2. **isort** - Organização de Imports
- **O que faz:** Ordena e organiza imports Python
- **Por que usar:** Mantém imports consistentes e legíveis
- **Configuração:** `pyproject.toml` (seção `[tool.isort]`)

### 3. **Pylint** - Linting Customizado
- **O que faz:** Detecta erros, code smells e padrões duplicados
- **Por que usar:** Inclui checkers customizados para o projeto
- **Configuração:** `.pylintrc` + `pylint_custom_checkers.py`
- **Features:**
  - Detecção de try-except duplicados
  - Detecção de chamadas de API duplicadas
  - Validação de estrutura de agents
  - E muito mais!

### 4. **Flake8** - Análise Estática Avançada
- **O que faz:** Verifica style guide + bugs potenciais
- **Por que usar:** Combina múltiplos plugins para análise completa
- **Configuração:** `.flake8`
- **Plugins incluídos:**
  - `flake8-bugbear`: Detecta bugs e design problems
  - `flake8-comprehensions`: Melhora list/dict comprehensions
  - `flake8-simplify`: Sugere simplificações
  - `flake8-docstrings`: Valida docstrings
  - `flake8-annotations`: Verifica type hints
  - `pep8-naming`: Valida convenções de nomenclatura

### 5. **MyPy** - Type Checking
- **O que faz:** Verifica tipos estáticos em Python
- **Por que usar:** Previne bugs relacionados a tipos
- **Configuração:** `pyproject.toml` (seção `[tool.mypy]`)

### 6. **jscpd** - Detecção de Código Duplicado
- **O que faz:** Encontra código duplicado no projeto
- **Por que usar:** Identifica oportunidades de refatoração
- **Configuração:** `.jscpd.json`
- **Threshold:** 20 linhas (configurável)

### 7. **Bandit** - Análise de Segurança
- **O que faz:** Detecta vulnerabilidades de segurança
- **Por que usar:** Previne problemas comuns de segurança
- **Configuração:** `.bandit.yaml`

### 8. **Radon** - Análise de Complexidade
- **O que faz:** Mede complexidade ciclomática e maintainability index
- **Por que usar:** Identifica código complexo que precisa refatoração
- **Configuração:** `pyproject.toml` (seção `[tool.radon]`)
- **Métricas:**
  - **Cyclomatic Complexity (CC):** Mede quantidade de caminhos no código
  - **Maintainability Index (MI):** Score de manutenibilidade (0-100)

### 9. **Vulture** - Detecção de Código Morto
- **O que faz:** Encontra código não utilizado
- **Por que usar:** Remove código desnecessário
- **Configuração:** `pyproject.toml` (seção `[tool.vulture]`)
- **Confiança mínima:** 80%

### 10. **Pre-commit Hooks** - Validação Automática
- **O que faz:** Executa checks antes de cada commit
- **Por que usar:** Garante qualidade antes do código entrar no repo
- **Configuração:** `.pre-commit-config.yaml`

### 11. **EditorConfig** - Consistência de Editor
- **O que faz:** Padroniza configurações entre editores
- **Por que usar:** Garante formatação consistente independente do editor
- **Configuração:** `.editorconfig`

---

## 🎯 Como Usar

### Análise Completa (Recomendado)

```bash
# Rodar todas as verificações
npm run check:all

# Rodar e corrigir automaticamente o que for possível
npm run check:all:fix

# Modo verbose (mostra detalhes)
npm run check:all:verbose
```

### Verificações Individuais

#### Formatação
```bash
# Verificar formatação
npm run check:format

# Corrigir formatação
npm run check:format:fix
# ou
black .
```

#### Imports
```bash
# Verificar imports
npm run check:imports

# Corrigir imports
npm run check:imports:fix
# ou
isort .
```

#### Linting
```bash
# Pylint (custom checkers)
npm run check:lint:pylint

# Flake8 (style + bugs)
npm run check:lint:flake8
```

#### Type Checking
```bash
npm run check:types
```

#### Código Duplicado
```bash
# Análise de duplicação
npm run check:duplicates

# Abrir relatório HTML
npm run report:duplicates

# Watch mode (monitora mudanças)
npm run check:duplicates:watch
```

#### Segurança
```bash
npm run check:security
```

#### Complexidade
```bash
# Complexidade ciclomática
npm run check:complexity

# Índice de manutenibilidade
npm run check:maintainability
```

#### Código Morto
```bash
npm run check:deadcode
```

### Pre-commit Hooks

```bash
# Instalar hooks
npm run pre-commit:install

# Rodar manualmente
npm run pre-commit:run

# Atualizar versões
npm run pre-commit:update

# Pular hooks (NÃO RECOMENDADO)
git commit --no-verify
```

### Testes com Coverage

```bash
# Rodar testes
npm test

# Gerar relatório de cobertura
npm run report:coverage
```

### Limpeza

```bash
# Limpar cache e relatórios
npm run clean
```

---

## 🔄 Integração CI/CD

### GitHub Actions

```yaml
name: Code Quality

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm run setup

      - name: Run quality checks
        run: npm run check:all

      - name: Run tests with coverage
        run: npm test
```

### GitLab CI

```yaml
quality:
  stage: test
  script:
    - npm run setup
    - npm run check:all
    - npm test
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: reports/coverage.xml
```

---

## ⚙️ Configurações

### Arquivos de Configuração

| Arquivo | Ferramenta(s) | Descrição |
|---------|---------------|-----------|
| `pyproject.toml` | Black, isort, MyPy, pytest, Radon, Vulture | Configuração centralizada |
| `.flake8` | Flake8 + plugins | Style guide e análise estática |
| `.pylintrc` | Pylint | Linting customizado |
| `pylint_custom_checkers.py` | Pylint | Checkers específicos do projeto |
| `.jscpd.json` | jscpd | Detecção de duplicação |
| `.bandit.yaml` | Bandit | Análise de segurança |
| `.pre-commit-config.yaml` | Pre-commit | Hooks automáticos |
| `.editorconfig` | Editores | Consistência de formatação |

### Customização

#### Ajustar Complexidade Máxima

**Flake8** (`.flake8`):
```ini
max-complexity = 10  # Altere para o valor desejado
```

**Radon** (via scripts):
```bash
radon cc . --min B  # A, B, C, D, E, F
```

#### Ajustar Threshold de Duplicação

**jscpd** (`.jscpd.json`):
```json
{
  "threshold": 20,  # Porcentagem máxima de duplicação
  "minLines": 5,    # Mínimo de linhas para considerar duplicação
  "minTokens": 50   # Mínimo de tokens
}
```

#### Ignorar Arquivos/Diretórios

Todos os arquivos de configuração suportam exclusão. Exemplo no `pyproject.toml`:

```toml
[tool.black]
extend-exclude = '''
/(
    \.git
  | meu_diretorio_especial
)/
'''
```

---

## 🐛 Troubleshooting

### Problema: "Tool not found"

**Solução:**
```bash
# Reinstalar dependências
pip install -r requirements_analysis.txt
npm install
```

### Problema: Pre-commit falha

**Solução:**
```bash
# Reinstalar hooks
pre-commit uninstall
pre-commit install

# Limpar cache
pre-commit clean
```

### Problema: Muitos erros do Flake8/Pylint

**Solução progressiva:**

1. **Começar com formatação:**
```bash
black .
isort .
```

2. **Corrigir erros críticos primeiro:**
```bash
flake8 . | grep "E9"  # Erros de sintaxe
```

3. **Ignorar temporariamente:**

Adicione ao código:
```python
# pylint: disable=nome-do-erro
# flake8: noqa
```

Ou configure nos arquivos `.flake8` / `.pylintrc`.

### Problema: MyPy reporta muitos erros

**Solução:**

1. Começar com configuração leniente (já está assim)
2. Adicionar type hints gradualmente
3. Usar `# type: ignore` temporariamente

### Problema: Código duplicado inevitável

**Solução:**

Adicione ao `.jscpd.json`:
```json
{
  "ignore": [
    "**/caminho/para/arquivo.py"
  ]
}
```

---

## 📊 Interpretando Resultados

### Radon - Complexidade Ciclomática

- **A (1-5):** Simples, fácil de testar
- **B (6-10):** Mais complexo, ainda ok
- **C (11-20):** Complexo, considere refatorar
- **D (21-30):** Muito complexo, DEVE refatorar
- **E (31-40):** Extremamente complexo
- **F (41+):** Não testável, refatoração urgente

### Radon - Maintainability Index

- **A (100-20):** Muito bom
- **B (19-10):** Bom
- **C (9-0):** Precisa atenção

### jscpd - Duplicação

- **0-5%:** Excelente
- **5-10%:** Bom
- **10-20%:** Aceitável
- **20%+:** Refatoração necessária

---

## 🎓 Melhores Práticas

1. **Execute `npm run check:all:fix` antes de cada commit**
2. **Mantenha complexity em A ou B**
3. **Mantenha duplicação abaixo de 10%**
4. **Adicione type hints em código novo**
5. **Escreva docstrings para funções públicas**
6. **Revise relatórios de segurança do Bandit**
7. **Monitore dead code e remova regularmente**
8. **Use pre-commit hooks sempre**

---

## 📚 Referências

- [Black](https://black.readthedocs.io/)
- [isort](https://pycqa.github.io/isort/)
- [Pylint](https://pylint.pycqa.org/)
- [Flake8](https://flake8.pycqa.org/)
- [MyPy](https://mypy.readthedocs.io/)
- [jscpd](https://github.com/kucherenko/jscpd)
- [Bandit](https://bandit.readthedocs.io/)
- [Radon](https://radon.readthedocs.io/)
- [Vulture](https://github.com/jendrikseipp/vulture)
- [Pre-commit](https://pre-commit.com/)

---

## 🆘 Suporte

Se encontrar problemas ou tiver dúvidas:

1. Verifique a seção [Troubleshooting](#troubleshooting)
2. Consulte a documentação oficial das ferramentas
3. Abra uma issue no repositório

---

**Última atualização:** 2025-11-20
**Versão:** 2.0.0
