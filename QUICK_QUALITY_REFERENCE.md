# 🚀 Quick Reference - Quality Tools

Comandos rápidos para análise de qualidade de código.

## 📦 Setup Inicial

```bash
npm run setup  # Instala tudo e configura hooks
```

## ⚡ Comandos Mais Usados

### Análise Completa
```bash
npm run check:all           # Verificar tudo
npm run check:all:fix       # Verificar + corrigir automaticamente
npm run check:all:verbose   # Modo detalhado
```

### Fix Rápido
```bash
black . && isort .  # Formata código + organiza imports
```

### Individual
```bash
npm run check:format        # Só formatação
npm run check:imports       # Só imports
npm run check:lint:pylint   # Pylint custom
npm run check:lint:flake8   # Flake8 + plugins
npm run check:types         # MyPy type check
npm run check:duplicates    # Código duplicado
npm run check:security      # Bandit security
npm run check:complexity    # Radon complexity
npm run check:deadcode      # Código não usado
```

## 🔨 Windows

```batch
RUN_QUALITY_CHECKS.bat           # Rodar tudo
RUN_QUALITY_CHECKS.bat --fix     # Rodar + corrigir
RUN_QUALITY_CHECKS.bat -v        # Modo verbose
```

## 🎯 Pre-commit

```bash
pre-commit install     # Instalar hooks
pre-commit run         # Rodar manualmente
git commit --no-verify # Pular (NÃO RECOMENDADO!)
```

## 📊 Relatórios

```bash
npm run report:duplicates  # Duplicação (HTML)
npm run report:coverage    # Cobertura de testes (HTML)
```

## 🧹 Limpeza

```bash
npm run clean  # Remove cache e relatórios
```

## 🆘 Troubleshooting

```bash
# Dependências não encontradas
pip install -r requirements_analysis.txt
npm install

# Limpar tudo
npm run clean
pre-commit clean
pre-commit uninstall
pre-commit install
```

## 📋 Checklist Antes do Commit

- [ ] `black . && isort .` - Formatar código
- [ ] `npm run check:duplicates` - Verificar duplicação
- [ ] `npm run check:types` - Type check (se possível)
- [ ] `npm test` - Rodar testes
- [ ] Commit! (hooks farão o resto)

## 🎓 Metas de Qualidade

| Métrica | Meta |
|---------|------|
| Duplicação | < 10% |
| Complexity (CC) | A ou B |
| Maintainability | A ou B |
| Test Coverage | > 80% |
| Security Issues | 0 |

---

Para guia completo: **[QUALITY_TOOLS_GUIDE.md](./QUALITY_TOOLS_GUIDE.md)**
