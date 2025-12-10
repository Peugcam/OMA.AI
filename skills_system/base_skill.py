"""
🧠 SKILLS SYSTEM - BASE
Sistema universal de Skills inspirado na Anthropic

Conceitos:
- Skill = Conhecimento procedural empacotado
- Reutilizável entre agentes
- Componível (combina com outras skills)
- Versionado e evolutivo
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path
from abc import ABC, abstractmethod


@dataclass
class SkillMetadata:
    """Metadados de uma skill"""
    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = "System"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    usage_count: int = 0
    success_rate: float = 0.0


@dataclass
class SkillProcedure:
    """Procedimento estruturado de uma skill"""
    steps: List[str]
    checklist: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    tips: List[str] = field(default_factory=list)


class Skill(ABC):
    """
    Base class para todas as Skills

    Skill = Conhecimento procedural empacotado e reutilizável

    Componentes:
    - Metadata: Informações sobre a skill
    - Procedure: Passos estruturados
    - Best Practices: Melhores práticas
    - Examples: Exemplos práticos
    - Common Pitfalls: Erros comuns a evitar
    """

    def __init__(self):
        self.metadata = SkillMetadata(
            name=self.__class__.__name__,
            description=self.__doc__ or ""
        )
        self.procedure: Optional[SkillProcedure] = None
        self.best_practices: List[str] = []
        self.examples: Dict[str, str] = {}
        self.common_pitfalls: List[str] = []
        self.context_hints: List[str] = []

    @abstractmethod
    def get_procedure(self) -> SkillProcedure:
        """Retorna procedimento estruturado da skill"""
        pass

    @abstractmethod
    def get_best_practices(self) -> List[str]:
        """Retorna melhores práticas"""
        pass

    def get_examples(self) -> Dict[str, str]:
        """Retorna exemplos práticos"""
        return self.examples

    def get_common_pitfalls(self) -> List[str]:
        """Retorna erros comuns"""
        return self.common_pitfalls

    def apply(self, task: str, context: str = "") -> str:
        """
        Aplica skill a uma tarefa

        Args:
            task: Descrição da tarefa
            context: Contexto adicional (ex: RAG)

        Returns:
            Prompt formatado com skill + contexto
        """
        procedure = self.get_procedure()
        best_practices = self.get_best_practices()
        examples = self.get_examples()
        pitfalls = self.get_common_pitfalls()

        # Formatar passos
        steps_text = "\n".join([
            f"{i+1}. {step}"
            for i, step in enumerate(procedure.steps)
        ])

        # Formatar checklist
        checklist_text = "\n".join([
            f"☐ {item}"
            for item in procedure.checklist
        ]) if procedure.checklist else "Nenhum item no checklist."

        # Formatar best practices
        practices_text = "\n".join([
            f"✓ {practice}"
            for practice in best_practices
        ])

        # Formatar warnings
        warnings_text = "\n".join([
            f"⚠️ {warning}"
            for warning in procedure.warnings
        ]) if procedure.warnings else "Nenhum warning."

        # Formatar exemplos
        examples_text = ""
        if examples:
            examples_text = "\n\n".join([
                f"**Exemplo: {name}**\n```\n{code}\n```"
                for name, code in examples.items()
            ])

        # Formatar pitfalls
        pitfalls_text = "\n".join([
            f"❌ {pitfall}"
            for pitfall in pitfalls
        ]) if pitfalls else "Nenhum pitfall conhecido."

        # Montar prompt completo
        prompt = f"""
═══════════════════════════════════════════════════════════
🧠 SKILL ATIVA: {self.metadata.name} v{self.metadata.version}
═══════════════════════════════════════════════════════════

📋 DESCRIÇÃO:
{self.metadata.description}

───────────────────────────────────────────────────────────
📝 PROCEDIMENTO (Siga estes passos):
───────────────────────────────────────────────────────────

{steps_text}

───────────────────────────────────────────────────────────
✅ CHECKLIST DE QUALIDADE:
───────────────────────────────────────────────────────────

{checklist_text}

───────────────────────────────────────────────────────────
💡 MELHORES PRÁTICAS:
───────────────────────────────────────────────────────────

{practices_text}

───────────────────────────────────────────────────────────
⚠️ AVISOS IMPORTANTES:
───────────────────────────────────────────────────────────

{warnings_text}

───────────────────────────────────────────────────────────
❌ ERROS COMUNS A EVITAR:
───────────────────────────────────────────────────────────

{pitfalls_text}

───────────────────────────────────────────────────────────
📚 EXEMPLOS DE REFERÊNCIA:
───────────────────────────────────────────────────────────

{examples_text if examples_text else "Nenhum exemplo disponível."}

{"═══════════════════════════════════════════════════════════" if context else ""}
{"🔍 CONTEXTO ESPECÍFICO (RAG):" if context else ""}
{"═══════════════════════════════════════════════════════════" if context else ""}

{context if context else ""}

═══════════════════════════════════════════════════════════
🎯 TAREFA ATUAL:
═══════════════════════════════════════════════════════════

{task}

═══════════════════════════════════════════════════════════
💬 INSTRUÇÕES:
═══════════════════════════════════════════════════════════

Execute a tarefa seguindo rigorosamente:
1. O PROCEDIMENTO estruturado acima
2. As MELHORES PRÁTICAS listadas
3. Evite os ERROS COMUNS mencionados
4. Use os EXEMPLOS como referência quando relevante
5. Se houver CONTEXTO RAG, adapte o procedimento a ele

Gere uma resposta completa, estruturada e profissional.
"""

        # Incrementar uso
        self.metadata.usage_count += 1
        self.metadata.updated_at = datetime.now().isoformat()

        return prompt

    def to_dict(self) -> Dict[str, Any]:
        """Serializa skill para dict"""
        return {
            "metadata": {
                "name": self.metadata.name,
                "version": self.metadata.version,
                "description": self.metadata.description,
                "author": self.metadata.author,
                "created_at": self.metadata.created_at,
                "updated_at": self.metadata.updated_at,
                "tags": self.metadata.tags,
                "dependencies": self.metadata.dependencies,
                "usage_count": self.metadata.usage_count,
                "success_rate": self.metadata.success_rate
            },
            "procedure": {
                "steps": self.get_procedure().steps,
                "checklist": self.get_procedure().checklist,
                "warnings": self.get_procedure().warnings,
                "tips": self.get_procedure().tips
            } if self.get_procedure() else None,
            "best_practices": self.get_best_practices(),
            "examples": self.get_examples(),
            "common_pitfalls": self.get_common_pitfalls()
        }

    def save(self, directory: str = "./skills_library"):
        """Salva skill em arquivo JSON"""
        Path(directory).mkdir(parents=True, exist_ok=True)

        filename = f"{self.metadata.name}_{self.metadata.version}.json"
        filepath = Path(directory) / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

        return str(filepath)

    def __repr__(self):
        return f"<Skill: {self.metadata.name} v{self.metadata.version}>"


class SkillTemplate(Skill):
    """
    Template para criar skills rapidamente

    Uso:
    ```python
    skill = SkillTemplate(
        name="MinhaSkill",
        description="Faz X e Y",
        steps=["Passo 1", "Passo 2"],
        best_practices=["Prática 1", "Prática 2"]
    )
    ```
    """

    def __init__(
        self,
        name: str,
        description: str,
        steps: List[str],
        best_practices: List[str],
        examples: Dict[str, str] = None,
        checklist: List[str] = None,
        warnings: List[str] = None,
        pitfalls: List[str] = None
    ):
        super().__init__()
        self.metadata.name = name
        self.metadata.description = description

        self._steps = steps
        self._best_practices = best_practices
        self.examples = examples or {}
        self._checklist = checklist or []
        self._warnings = warnings or []
        self.common_pitfalls = pitfalls or []

    def get_procedure(self) -> SkillProcedure:
        return SkillProcedure(
            steps=self._steps,
            checklist=self._checklist,
            warnings=self._warnings
        )

    def get_best_practices(self) -> List[str]:
        return self._best_practices


# ═══════════════════════════════════════════════════════════
# EXEMPLO DE USO
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Criar skill de exemplo
    skill = SkillTemplate(
        name="DockerDeployment",
        description="Deploy profissional de aplicações com Docker",
        steps=[
            "Criar Dockerfile multi-stage otimizado",
            "Configurar .dockerignore para reduzir tamanho",
            "Build da imagem: docker build -t app:latest .",
            "Testar localmente: docker run -p 8000:8000 app",
            "Tag para registry: docker tag app registry.com/app",
            "Push: docker push registry.com/app",
            "Deploy no ambiente de produção"
        ],
        best_practices=[
            "Sempre use multi-stage builds para reduzir tamanho",
            "Minimize layers combinando comandos RUN",
            "Use .dockerignore igual ao .gitignore",
            "Nunca exponha secrets em ENV",
            "Adicione health checks",
            "Use specific tags, nunca 'latest' em prod"
        ],
        checklist=[
            "Dockerfile otimizado com multi-stage",
            ".dockerignore configurado",
            "Health check implementado",
            "Secrets via environment variables",
            "Logs configurados para stdout/stderr",
            "Image taggeada corretamente"
        ],
        warnings=[
            "Não use 'latest' tag em produção",
            "Cuidado com tamanho de imagem (>1GB = problema)",
            "Sempre teste localmente antes do push"
        ],
        pitfalls=[
            "Esquecer .dockerignore (imagem gigante)",
            "Copiar node_modules ou venv (desnecessário)",
            "Não usar multi-stage (imagem pesada)",
            "Expor senhas em ENV (security risk)"
        ],
        examples={
            "Dockerfile Python": """FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
WORKDIR /app
COPY . .
EXPOSE 8000
CMD ["python", "main.py"]""",

            ".dockerignore": """__pycache__
*.pyc
.git
.env
venv/
node_modules/
.pytest_cache/"""
        }
    )

    # Aplicar skill a uma tarefa
    task = "Deployar minha API FastAPI no Google Cloud Run"

    # Sem contexto RAG
    prompt = skill.apply(task)
    print(prompt)

    # Com contexto RAG (simulado)
    context_rag = """
    CONTEXTO DO PROJETO (RAG):
    - App FastAPI rodando na porta 8000
    - Usa PostgreSQL (variável DB_URL)
    - Arquivo requirements.txt existe
    - Já tem .env com secrets
    """

    prompt_with_rag = skill.apply(task, context_rag)
    print("\n" + "="*80 + "\n")
    print(prompt_with_rag)

    # Salvar skill
    filepath = skill.save()
    print(f"\n✅ Skill salva em: {filepath}")
