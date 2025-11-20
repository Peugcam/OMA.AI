"""
Teste rápido de detecção de keywords
"""
test_descriptions = [
    "pessoa trabalhando no computador",
    "professor explicando conceitos",
    "aula sobre programação",
    "gráfico mostrando dados",
    "logo holográfico flutuando",
    "equipe em reunião"
]

people_keywords = ['pessoa', 'pessoas', 'rosto', 'mão', 'mãos', 'equipe',
                   'grupo', 'trabalhando', 'sorrindo', 'olhando', 'reunião',
                   'professor', 'estudante', 'apresentador', 'instrutor',
                   'explicando', 'ensinando', 'aula', 'palestra', 'apresentação',
                   'homem', 'mulher', 'jovem', 'adulto', 'criança',
                   'falando', 'conversando', 'interagindo', 'gesticulando']

print("Teste de detecção de keywords:\n")
for desc in test_descriptions:
    desc_lower = desc.lower()
    matched = any(keyword in desc_lower for keyword in people_keywords)
    result = "PEXELS" if matched else "STABILITY"
    print(f"{result:12} | {desc}")
    if matched:
        keywords_found = [kw for kw in people_keywords if kw in desc_lower]
        print(f"             └─ Keywords: {', '.join(keywords_found)}")
