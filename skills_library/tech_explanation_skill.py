"""
🎓 TECH EXPLANATION SKILL
Skill para explicar conceitos técnicos complexos de forma simples
Baseada na Técnica Feynman + Analogias do Mundo Real
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from skills_system.base_skill import Skill, SkillProcedure


class TechExplanationSkill(Skill):
    """
    Skill para transformar conceitos técnicos em explicações acessíveis

    Usa Técnica Feynman + Sistema de Analogias
    Ideal para vídeos educacionais e documentação
    """

    def __init__(self):
        super().__init__()
        self.metadata.name = "TechExplanationSkill"
        self.metadata.version = "1.0.0"
        self.metadata.description = "Explica conceitos técnicos complexos de forma simples e memorável"
        self.metadata.tags = ["education", "explanation", "teaching", "simplification"]
        self.metadata.author = "OMA System"

        # Exemplos práticos
        self.examples = {
            "Machine Learning Explicado": """
CONCEITO: Machine Learning

ANALOGIA BASE:
"Machine Learning é como ensinar uma criança a identificar frutas.

Você não dá regras: 'se redondo e vermelho = maçã'
Você MOSTRA 100 fotos de maçãs.
A criança aprende sozinha os padrões.

ML = mostrar exemplos → computador aprende padrões → aplica em novos casos"

CAMADAS DE COMPLEXIDADE:

🟢 NÍVEL 1 (Criança de 8 anos):
"É ensinar computador a aprender sozinho, igual você aprendeu a andar de bike"

🟡 NÍVEL 2 (Adolescente):
"É dar exemplos ao computador. Ele encontra padrões e usa em situações novas.
Ex: mostrar 1000 emails → ele aprende o que é spam → filtra sozinho"

🔴 NÍVEL 3 (Técnico):
"Algoritmos que otimizam função objetivo baseados em dados históricos.
Supervisionado: labels conhecidos. Não-supervisionado: descobre padrões.
Reforço: aprende por tentativa e erro com rewards"

EXEMPLO PRÁTICO:
Netflix recomendações:
- DADOS: você assistiu 100 filmes
- PADRÃO: gosta de suspense + final feliz
- APLICAÇÃO: recomenda "filme X" que combina isso

ERRO COMUM CORRIGIDO:
❌ "ML é IA que pensa sozinha"
✅ "ML encontra padrões em dados. Não 'pensa', reconhece similaridades"
""",

            "API Explicado": """
CONCEITO: API (Application Programming Interface)

ANALOGIA BASE:
"API é como cardápio de restaurante.

VOCÊ (app) não precisa saber:
- Como fazer o prato
- Onde fica a cozinha
- Quem é o chef

VOCÊ só precisa:
- Ler o cardápio (documentação)
- Fazer pedido (request)
- Receber prato pronto (response)

API = cardápio de funções que outro sistema oferece"

CAMADAS:

🟢 NÍVEL 1:
"É um garçom entre dois programas. Um pede, outro entrega"

🟡 NÍVEL 2:
"Contrato: 'Se você me mandar X, eu te devolvo Y'
Exemplo: manda CEP → recebe endereço completo"

🔴 NÍVEL 3:
"Interface padronizada (REST, GraphQL, gRPC) para comunicação entre sistemas.
Define endpoints, métodos HTTP, formato de dados (JSON/XML), autenticação"

EXEMPLO PRÁTICO:
Login com Google:
- SEU APP pede: "quero dados do usuário"
- API GOOGLE: "ok, aqui está nome, email, foto"
- Você NÃO vê senha, NÃO acessa servidor Google

ERRO COMUM CORRIGIDO:
❌ "API é um site"
✅ "API é porta de comunicação. Site é interface visual"
"""
        }

        # Erros comuns
        self.common_pitfalls = [
            "Começar pelo conceito técnico (perde logo de cara)",
            "Usar jargão sem definir antes",
            "Analogia muito distante da realidade técnica",
            "Não mostrar exemplo prático concreto",
            "Explicação com mais de 3 níveis de profundidade",
            "Esquecer de corrigir conceitos errados comuns",
            "Não conectar com uso real no dia-a-dia",
            "Linguagem passiva e impessoal"
        ]

    def get_procedure(self) -> SkillProcedure:
        return SkillProcedure(
            steps=[
                "1. ESCOLHA ANALOGIA do mundo real (restaurante, criança, carro, etc)",
                "2. EXPLIQUE BÁSICO em 1 frase de 10 palavras",
                "3. CAMADAS PROGRESSIVAS: nível 1 (criança) → 2 (teen) → 3 (técnico)",
                "4. EXEMPLO PRÁTICO concreto que todos conhecem",
                "5. CORRIJA conceito errado comum sobre o tema",
                "6. CONECTE ao uso real no cotidiano"
            ],
            checklist=[
                "Analogia do mundo real clara?",
                "Primeira frase com max 10 palavras?",
                "3 níveis de profundidade?",
                "Exemplo prático reconhecível?",
                "Corrigiu misconception comum?",
                "Conectou ao uso cotidiano?",
                "Zero jargão não explicado?",
                "Tom conversacional (você/seu)?",
                "Visual simples planejado?",
                "Testável com criança de 8 anos?"
            ],
            warnings=[
                "⚠️ NUNCA comece com definição técnica formal",
                "⚠️ NUNCA use mais de 3 níveis de profundidade",
                "⚠️ NUNCA assuma conhecimento prévio",
                "⚠️ NUNCA faça analogia que precisa ser explicada",
                "⚠️ NUNCA esqueça o 'Por que eu deveria me importar?'"
            ],
            tips=[
                "💡 Técnica Feynman: se não consegue explicar para criança, não entendeu",
                "💡 Analogias físicas > abstratas (carro vs conceito filosófico)",
                "💡 Use VERBOS de ação: conecta, transforma, envia",
                "💡 Diagrama simples > mil palavras (planeje visual)",
                "💡 Termine sempre com 'Agora você sabe o suficiente para usar'"
            ]
        )

    def get_best_practices(self) -> list:
        return [
            "✓ REGRA FUNDAMENTAL: Explique como se fosse para seu avô/avó",
            "✓ Uma ANALOGIA principal + exemplos secundários",
            "✓ Estrutura SEMPRE: O que é → Como funciona → Pra que serve → Exemplo real",
            "✓ Evite 'basicamente', 'simplesmente', 'apenas' (condescendente)",
            "✓ Use VOCÊ/SEU (não 'o usuário', 'a pessoa')",
            "✓ Números CONCRETOS: '3 passos' melhor que 'alguns passos'",
            "✓ Corrija MITOS: 'Muitos pensam X, mas na verdade é Y'",
            "✓ Conecte ao CONHECIDO: 'Igual quando você [ação cotidiana]'",
            "✓ Visual PROGRESSIVO: começa simples → adiciona complexidade",
            "✓ TESTE final: consegue explicar em 30 segundos?"
        ]


if __name__ == "__main__":
    # Teste da skill
    skill = TechExplanationSkill()

    task = """
    Explicar "Docker e Containers" para:
    - Público: Devs iniciantes que só conhecem HTML/CSS/JS
    - Contexto: Vão usar Docker no primeiro projeto backend
    - Objetivo: Entender o suficiente para usar docker-compose
    """

    print(skill.apply(task))

    # Salvar
    filepath = skill.save()
    print(f"\n✅ Skill salva em: {filepath}")
