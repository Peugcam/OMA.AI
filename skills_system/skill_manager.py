"""
🎯 SKILL MANAGER - Gerenciador Central de Skills
Integra Skills + RAG para expertise contextualizada

Features:
- Biblioteca de skills centralizada
- Integração automática com RAG
- Recomendação inteligente de skills
- Tracking de uso e performance
- Versionamento
- Cache de skills
"""

from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import json
from datetime import datetime
from collections import defaultdict

from skills_system.base_skill import Skill, SkillTemplate


class SkillManager:
    """
    Gerenciador central de Skills

    Responsabilidades:
    - Carregar/descarregar skills dinamicamente
    - Integrar com RAG para contexto
    - Recomendar skills apropriadas
    - Tracking de performance
    - Aprendizado de combinações
    """

    def __init__(self, rag_system=None, skills_dir: str = "./skills_library"):
        """
        Inicializa SkillManager

        Args:
            rag_system: Sistema RAG para buscar contexto (OmaSearchToolV2)
            skills_dir: Diretório de skills
        """
        self.rag_system = rag_system
        self.skills_dir = Path(skills_dir)
        self.skills_dir.mkdir(parents=True, exist_ok=True)

        # Biblioteca de skills carregadas
        self.skills: Dict[str, Skill] = {}

        # Metadata de uso
        self.usage_stats = defaultdict(lambda: {
            "total_uses": 0,
            "successful_uses": 0,
            "avg_latency": 0.0,
            "last_used": None,
            "user_ratings": []
        })

        # Combinações que funcionam bem juntas
        self.skill_combinations = defaultdict(int)

        # Cache de recommendations
        self._recommendation_cache = {}

        print(f"✅ SkillManager inicializado")
        print(f"   Skills dir: {self.skills_dir}")
        print(f"   RAG: {'Disponível' if rag_system else 'Não disponível'}")

    # ═══════════════════════════════════════════════════════════
    # GERENCIAMENTO DE SKILLS
    # ═══════════════════════════════════════════════════════════

    def register_skill(self, skill: Skill) -> str:
        """
        Registra uma skill na biblioteca

        Args:
            skill: Skill a registrar

        Returns:
            ID da skill registrada
        """
        skill_id = f"{skill.metadata.name}_{skill.metadata.version}"

        self.skills[skill_id] = skill

        # Salvar no disco
        skill.save(str(self.skills_dir))

        print(f"✅ Skill registrada: {skill_id}")

        return skill_id

    def load_skill(self, skill_id: str) -> Optional[Skill]:
        """Carrega skill por ID"""
        return self.skills.get(skill_id)

    def unload_skill(self, skill_id: str):
        """Remove skill da memória"""
        if skill_id in self.skills:
            del self.skills[skill_id]
            print(f"🗑️  Skill removida: {skill_id}")

    def list_skills(self, tag: str = None) -> List[str]:
        """
        Lista skills disponíveis

        Args:
            tag: Filtrar por tag

        Returns:
            Lista de skill IDs
        """
        if tag:
            return [
                skill_id for skill_id, skill in self.skills.items()
                if tag in skill.metadata.tags
            ]
        return list(self.skills.keys())

    def search_skills(self, query: str) -> List[Tuple[str, float]]:
        """
        Busca skills por query

        Args:
            query: Termo de busca

        Returns:
            Lista de (skill_id, relevance_score)
        """
        results = []
        query_lower = query.lower()

        for skill_id, skill in self.skills.items():
            score = 0.0

            # Match em nome
            if query_lower in skill.metadata.name.lower():
                score += 1.0

            # Match em descrição
            if query_lower in skill.metadata.description.lower():
                score += 0.5

            # Match em tags
            for tag in skill.metadata.tags:
                if query_lower in tag.lower():
                    score += 0.3

            if score > 0:
                results.append((skill_id, score))

        # Ordenar por relevância
        results.sort(key=lambda x: x[1], reverse=True)

        return results

    # ═══════════════════════════════════════════════════════════
    # INTEGRAÇÃO COM RAG
    # ═══════════════════════════════════════════════════════════

    def execute_with_rag(
        self,
        skill_id: str,
        task: str,
        rag_query: str = None,
        top_k: int = 5
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Executa skill COM contexto RAG

        Args:
            skill_id: ID da skill
            task: Tarefa a executar
            rag_query: Query para RAG (usa task se None)
            top_k: Número de chunks RAG

        Returns:
            (prompt_completo, metadata)
        """
        # Carregar skill
        skill = self.load_skill(skill_id)
        if not skill:
            raise ValueError(f"Skill não encontrada: {skill_id}")

        # Buscar contexto no RAG
        rag_context = ""
        rag_metadata = {}

        if self.rag_system:
            query = rag_query or task

            try:
                result = self.rag_system.search(query, top_k=top_k)

                if result["success"] and result["chunks"]:
                    # Formatar contexto
                    context_parts = []
                    for i, (chunk, fonte) in enumerate(zip(result["chunks"], result["fontes"]), 1):
                        context_parts.append(f"[Chunk {i} - Fonte: {fonte}]\n{chunk}\n")

                    rag_context = "\n".join(context_parts)

                    rag_metadata = {
                        "chunks_found": len(result["chunks"]),
                        "sources": result["fontes"],
                        "cached": result.get("cached", False)
                    }

                    print(f"🔍 RAG encontrou {len(result['chunks'])} chunks relevantes")

            except Exception as e:
                print(f"⚠️  Erro no RAG: {e}")
                rag_context = ""

        # Aplicar skill com contexto
        prompt = skill.apply(task, rag_context)

        # Metadata
        metadata = {
            "skill_id": skill_id,
            "skill_version": skill.metadata.version,
            "task": task,
            "rag_used": bool(rag_context),
            "rag_metadata": rag_metadata,
            "timestamp": datetime.now().isoformat()
        }

        # Atualizar estatísticas
        self._update_usage(skill_id)

        return prompt, metadata

    def execute_multi_skill(
        self,
        skill_ids: List[str],
        task: str,
        rag_query: str = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Executa MÚLTIPLAS skills combinadas

        Args:
            skill_ids: Lista de skill IDs
            task: Tarefa a executar
            rag_query: Query para RAG

        Returns:
            (prompt_combinado, metadata)
        """
        # Buscar contexto RAG (uma vez só)
        rag_context = ""

        if self.rag_system and rag_query:
            try:
                result = self.rag_system.search(rag_query or task, top_k=5)
                if result["success"] and result["chunks"]:
                    context_parts = []
                    for chunk, fonte in zip(result["chunks"], result["fontes"]):
                        context_parts.append(f"[Fonte: {fonte}]\n{chunk}\n")
                    rag_context = "\n".join(context_parts)
            except Exception as e:
                print(f"⚠️  Erro no RAG: {e}")

        # Combinar todas as skills
        combined_procedures = []
        combined_practices = []
        combined_examples = {}
        combined_warnings = []

        for skill_id in skill_ids:
            skill = self.load_skill(skill_id)
            if not skill:
                print(f"⚠️  Skill não encontrada: {skill_id}")
                continue

            # Coletar de cada skill
            proc = skill.get_procedure()
            combined_procedures.extend(proc.steps)
            combined_practices.extend(skill.get_best_practices())
            combined_examples.update(skill.get_examples())
            combined_warnings.extend(proc.warnings if proc.warnings else [])

        # Montar prompt combinado
        prompt = f"""
═══════════════════════════════════════════════════════════
🧠 SKILLS ATIVAS: {len(skill_ids)} skills combinadas
═══════════════════════════════════════════════════════════

Skills carregadas:
{chr(10).join(f"  • {sid}" for sid in skill_ids)}

───────────────────────────────────────────────────────────
📝 PROCEDIMENTO COMBINADO:
───────────────────────────────────────────────────────────

{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(combined_procedures))}

───────────────────────────────────────────────────────────
💡 MELHORES PRÁTICAS (Todas as Skills):
───────────────────────────────────────────────────────────

{chr(10).join(f"✓ {practice}" for practice in combined_practices)}

───────────────────────────────────────────────────────────
⚠️ AVISOS IMPORTANTES:
───────────────────────────────────────────────────────────

{chr(10).join(f"⚠️ {warning}" for warning in combined_warnings) if combined_warnings else "Nenhum aviso."}

{"═══════════════════════════════════════════════════════════" if rag_context else ""}
{"🔍 CONTEXTO ESPECÍFICO (RAG):" if rag_context else ""}
{"═══════════════════════════════════════════════════════════" if rag_context else ""}

{rag_context if rag_context else ""}

═══════════════════════════════════════════════════════════
🎯 TAREFA ATUAL:
═══════════════════════════════════════════════════════════

{task}

═══════════════════════════════════════════════════════════
💬 INSTRUÇÕES:
═══════════════════════════════════════════════════════════

Execute a tarefa combinando TODAS as skills acima:
1. Siga os procedimentos de TODAS as skills
2. Aplique as melhores práticas combinadas
3. Considere todos os avisos
4. Se houver contexto RAG, adapte a ele

Gere resposta que demonstre expertise de MÚLTIPLOS domínios.
"""

        # Registrar combinação bem-sucedida
        combo_key = "|".join(sorted(skill_ids))
        self.skill_combinations[combo_key] += 1

        metadata = {
            "skills_used": skill_ids,
            "skill_count": len(skill_ids),
            "task": task,
            "rag_used": bool(rag_context),
            "timestamp": datetime.now().isoformat()
        }

        return prompt, metadata

    # ═══════════════════════════════════════════════════════════
    # RECOMENDAÇÃO INTELIGENTE
    # ═══════════════════════════════════════════════════════════

    def recommend_skills(
        self,
        task: str,
        max_skills: int = 3
    ) -> List[Tuple[str, float, str]]:
        """
        Recomenda skills apropriadas para uma tarefa

        Args:
            task: Descrição da tarefa
            max_skills: Número máximo de skills

        Returns:
            Lista de (skill_id, confidence_score, reason)
        """
        # Cache check
        cache_key = task.lower()[:100]
        if cache_key in self._recommendation_cache:
            return self._recommendation_cache[cache_key]

        recommendations = []

        # Keywords para matching
        task_lower = task.lower()

        for skill_id, skill in self.skills.items():
            score = 0.0
            reasons = []

            # Match em nome
            name_words = skill.metadata.name.lower().split("_")
            for word in name_words:
                if word in task_lower:
                    score += 0.3
                    reasons.append(f"Nome contém '{word}'")

            # Match em descrição
            desc_words = skill.metadata.description.lower().split()
            matches = sum(1 for word in desc_words if word in task_lower)
            if matches > 0:
                score += 0.2 * min(matches, 3)
                reasons.append(f"{matches} palavras da descrição")

            # Match em tags
            for tag in skill.metadata.tags:
                if tag.lower() in task_lower:
                    score += 0.4
                    reasons.append(f"Tag '{tag}'")

            # Boost por usage (skills populares)
            usage = self.usage_stats[skill_id]["total_uses"]
            if usage > 0:
                score += min(0.1, usage / 100)
                reasons.append(f"Usada {usage}x")

            # Boost por success rate
            success_rate = self._get_success_rate(skill_id)
            if success_rate > 0:
                score += 0.2 * success_rate
                reasons.append(f"{success_rate*100:.0f}% sucesso")

            if score > 0:
                reason = ", ".join(reasons[:2])  # Top 2 reasons
                recommendations.append((skill_id, score, reason))

        # Ordenar por score
        recommendations.sort(key=lambda x: x[1], reverse=True)

        # Retornar top N
        result = recommendations[:max_skills]

        # Cache
        self._recommendation_cache[cache_key] = result

        return result

    def get_best_combination(
        self,
        task: str,
        max_skills: int = 3
    ) -> List[str]:
        """
        Retorna melhor combinação de skills para tarefa

        Args:
            task: Descrição da tarefa
            max_skills: Máximo de skills

        Returns:
            Lista de skill IDs recomendados
        """
        recommendations = self.recommend_skills(task, max_skills)

        skill_ids = [skill_id for skill_id, score, reason in recommendations]

        # Log recomendações
        print(f"\n💡 Recomendações para: '{task}'")
        for skill_id, score, reason in recommendations:
            print(f"   {skill_id} (score: {score:.2f}) - {reason}")

        return skill_ids

    # ═══════════════════════════════════════════════════════════
    # TRACKING E ANALYTICS
    # ═══════════════════════════════════════════════════════════

    def _update_usage(self, skill_id: str, success: bool = True):
        """Atualiza estatísticas de uso"""
        stats = self.usage_stats[skill_id]
        stats["total_uses"] += 1
        if success:
            stats["successful_uses"] += 1
        stats["last_used"] = datetime.now().isoformat()

    def _get_success_rate(self, skill_id: str) -> float:
        """Calcula taxa de sucesso de uma skill"""
        stats = self.usage_stats[skill_id]
        if stats["total_uses"] == 0:
            return 0.0
        return stats["successful_uses"] / stats["total_uses"]

    def report_success(self, skill_id: str, rating: int = None):
        """
        Reporta sucesso de uma skill

        Args:
            skill_id: ID da skill
            rating: Nota de 1-5 (opcional)
        """
        self._update_usage(skill_id, success=True)

        if rating:
            self.usage_stats[skill_id]["user_ratings"].append(rating)

    def report_failure(self, skill_id: str):
        """Reporta falha de uma skill"""
        self._update_usage(skill_id, success=False)

    def get_stats(self, skill_id: str = None) -> Dict[str, Any]:
        """
        Retorna estatísticas

        Args:
            skill_id: ID específico ou None para todas

        Returns:
            Dicionário de estatísticas
        """
        if skill_id:
            return dict(self.usage_stats[skill_id])

        # Estatísticas gerais
        total_skills = len(self.skills)
        total_uses = sum(s["total_uses"] for s in self.usage_stats.values())

        # Top skills
        top_skills = sorted(
            self.usage_stats.items(),
            key=lambda x: x[1]["total_uses"],
            reverse=True
        )[:5]

        # Top combinations
        top_combos = sorted(
            self.skill_combinations.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        return {
            "total_skills": total_skills,
            "total_uses": total_uses,
            "top_skills": [
                {
                    "skill_id": sid,
                    "uses": stats["total_uses"],
                    "success_rate": self._get_success_rate(sid)
                }
                for sid, stats in top_skills
            ],
            "top_combinations": [
                {
                    "skills": combo.split("|"),
                    "uses": count
                }
                for combo, count in top_combos
            ]
        }

    def print_stats(self):
        """Imprime estatísticas formatadas"""
        stats = self.get_stats()

        print("\n" + "="*60)
        print("📊 SKILL MANAGER - ESTATÍSTICAS")
        print("="*60)
        print(f"\n📦 Total de Skills: {stats['total_skills']}")
        print(f"🔄 Total de Usos: {stats['total_uses']}")

        print(f"\n🏆 Top 5 Skills Mais Usadas:")
        for i, skill in enumerate(stats['top_skills'], 1):
            print(f"  {i}. {skill['skill_id']}")
            print(f"     Usos: {skill['uses']} | Sucesso: {skill['success_rate']*100:.0f}%")

        if stats['top_combinations']:
            print(f"\n🔗 Top Combinações de Skills:")
            for i, combo in enumerate(stats['top_combinations'], 1):
                print(f"  {i}. {' + '.join(combo['skills'])}")
                print(f"     Usada {combo['uses']}x")

        print("\n" + "="*60 + "\n")

    # ═══════════════════════════════════════════════════════════
    # PERSISTÊNCIA
    # ═══════════════════════════════════════════════════════════

    def save_state(self, filepath: str = "./skill_manager_state.json"):
        """Salva estado do manager"""
        state = {
            "usage_stats": dict(self.usage_stats),
            "skill_combinations": dict(self.skill_combinations),
            "timestamp": datetime.now().isoformat()
        }

        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)

        print(f"💾 Estado salvo em: {filepath}")

    def load_state(self, filepath: str = "./skill_manager_state.json"):
        """Carrega estado do manager"""
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)

            self.usage_stats = defaultdict(
                lambda: {
                    "total_uses": 0,
                    "successful_uses": 0,
                    "avg_latency": 0.0,
                    "last_used": None,
                    "user_ratings": []
                },
                state.get("usage_stats", {})
            )

            self.skill_combinations = defaultdict(
                int,
                state.get("skill_combinations", {})
            )

            print(f"📂 Estado carregado de: {filepath}")

        except FileNotFoundError:
            print(f"⚠️  Arquivo não encontrado: {filepath}")


# ═══════════════════════════════════════════════════════════
# EXEMPLO DE USO
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Simular RAG system (você usaria OmaSearchToolV2 real)
    class MockRAG:
        def search(self, query, top_k=5):
            return {
                "success": True,
                "chunks": [
                    "Docker permite containerizar aplicações...",
                    "Use multi-stage builds para otimizar..."
                ],
                "fontes": ["docs/docker.md", "docs/best_practices.md"]
            }

    # Criar manager
    rag = MockRAG()
    manager = SkillManager(rag_system=rag)

    # Criar e registrar skill
    docker_skill = SkillTemplate(
        name="DockerDeployment",
        description="Deploy profissional com Docker",
        steps=[
            "Criar Dockerfile otimizado",
            "Configurar .dockerignore",
            "Build: docker build -t app .",
            "Test: docker run -p 8000:8000 app",
            "Deploy em produção"
        ],
        best_practices=[
            "Use multi-stage builds",
            "Minimize layers",
            "Nunca exponha secrets"
        ]
    )

    skill_id = manager.register_skill(docker_skill)

    # Executar com RAG
    print("\n" + "="*60)
    print("EXECUTANDO SKILL COM RAG")
    print("="*60)

    prompt, metadata = manager.execute_with_rag(
        skill_id=skill_id,
        task="Deployar minha API FastAPI no Google Cloud Run"
    )

    print(prompt)
    print("\n📊 Metadata:", json.dumps(metadata, indent=2))

    # Recomendar skills
    print("\n" + "="*60)
    print("RECOMENDAÇÃO DE SKILLS")
    print("="*60)

    recommendations = manager.recommend_skills(
        "Como fazer deploy com Docker?",
        max_skills=3
    )

    for skill_id, score, reason in recommendations:
        print(f"\n✓ {skill_id}")
        print(f"  Score: {score:.2f}")
        print(f"  Motivo: {reason}")

    # Estatísticas
    manager.print_stats()
