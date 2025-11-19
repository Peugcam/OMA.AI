# 🎯 OMA - Roadmap de Melhorias vs Cloud Providers

## 📊 Status Atual: O Que Você JÁ TEM

### ✅ Arquitetura Core (100% Completa)
- [x] Supervisor-Worker Pattern
- [x] Task Decomposition
- [x] Parallel Execution (asyncio)
- [x] Smart Routing com Cache
- [x] State Management
- [x] Error Recovery (retry + fallback)
- [x] Multi-Model Support (200+)
- [x] Cost Optimization (16-45x mais barato)

**Veredicto:** Arquitetura está enterprise-ready! 🎉

---

## ⚠️ GAPS: Onde Você PRECISA Melhorar

### 1. 🔍 **OBSERVABILITY & MONITORING** (Gap Crítico!)

#### O Que Você Tem Hoje:
```python
# Apenas logs básicos
self.logger.info("OK - Roteiro gerado")
self.logger.error("ERRO ao gerar roteiro")
```

#### O Que AWS/Azure/Vertex Têm:

**AWS Bedrock:**
```python
# CloudWatch Metrics automáticos
- Agent invocations count
- Average latency per agent
- Error rate per agent
- Token usage per agent
- Cost tracking real-time
- Custom dashboards
- Alertas automáticos
```

**Azure AI:**
```python
# Application Insights
- Distributed tracing
- Dependency tracking
- Performance counters
- Custom metrics
- Correlation IDs
- Request/Response logging
```

**Vertex AI:**
```python
# Cloud Logging + Monitoring
- Structured logs
- Log analytics
- Performance monitoring
- Resource utilization
- Cost attribution
```

#### ❌ O Que Você PRECISA Implementar:

**PRIORIDADE CRÍTICA:**

1. **Distributed Tracing**
```python
# Implementar OpenTelemetry
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger import JaegerExporter

# Tracer para acompanhar fluxo completo
tracer = trace.get_tracer(__name__)

@tracer.start_as_current_span("supervisor.analyze_request")
async def analyze_request(self, brief):
    with tracer.start_as_current_span("call_llm"):
        response = await self.llm.chat(...)
    # Cada span registra: latência, erros, metadata
```

2. **Structured Logging**
```python
# Substituir logs simples por estruturados
import structlog

logger = structlog.get_logger()

# Antes:
self.logger.info("OK - Roteiro gerado")

# Depois:
logger.info(
    "script_generated",
    script_id=script['id'],
    scenes=len(script['scenes']),
    model=self.llm.model,
    latency_ms=elapsed,
    tokens_used=response.usage.total_tokens,
    cost_usd=calculate_cost(response.usage),
    timestamp=datetime.utcnow().isoformat()
)
```

3. **Metrics Collection**
```python
# Prometheus para métricas
from prometheus_client import Counter, Histogram, Gauge

# Contadores
requests_total = Counter(
    'oma_requests_total',
    'Total de requests processados',
    ['agent', 'status']
)

# Histogramas (latência)
request_latency = Histogram(
    'oma_request_latency_seconds',
    'Latência de requests',
    ['agent']
)

# Gauges (estado atual)
active_requests = Gauge(
    'oma_active_requests',
    'Requests em processamento',
    ['agent']
)

# Uso:
with request_latency.labels(agent='script').time():
    result = await agent.generate_script(state)
requests_total.labels(agent='script', status='success').inc()
```

4. **Cost Tracking Real-Time**
```python
# Rastrear custo de cada request
class CostTracker:
    def __init__(self):
        self.costs = []
        self.total = 0.0

    def track_llm_call(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ):
        cost = calculate_cost(model, input_tokens, output_tokens)
        self.costs.append({
            'timestamp': datetime.utcnow(),
            'model': model,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost_usd': cost
        })
        self.total += cost

    def get_summary(self) -> dict:
        return {
            'total_cost_usd': self.total,
            'total_calls': len(self.costs),
            'cost_by_model': self._group_by_model(),
            'avg_cost_per_call': self.total / len(self.costs)
        }
```

**Ferramentas para Implementar:**

| Ferramenta | Uso | Prioridade |
|------------|-----|------------|
| **OpenTelemetry** | Distributed tracing | 🔴 Crítica |
| **Prometheus** | Metrics collection | 🔴 Crítica |
| **Grafana** | Dashboards visuais | 🟡 Alta |
| **Structlog** | Structured logging | 🟡 Alta |
| **Jaeger/Zipkin** | Trace visualization | 🟢 Média |
| **ELK Stack** | Log aggregation | 🟢 Média |

---

### 2. 🎨 **UI/VISUAL BUILDER** (Gap Importante)

#### O Que Você Tem:
```
❌ Sem UI visual
❌ Apenas código Python
❌ Sem visualização de fluxos
```

#### O Que Vertex AI Tem:
```
✅ Agent Builder UI
✅ Visual flow editor
✅ Drag-and-drop agents
✅ Test playground
✅ Real-time debugging
```

#### 💡 O Que Implementar:

**Opção 1: Gradio (Rápido)**
```python
import gradio as gr

def create_ui():
    with gr.Blocks() as app:
        gr.Markdown("# 🎬 OMA - Multi-Agent Video Creator")

        with gr.Tab("Create Video"):
            brief_input = gr.Textbox(label="Video Brief", lines=5)
            submit_btn = gr.Button("Create Video")
            output = gr.Video(label="Generated Video")

        with gr.Tab("Monitor"):
            gr.Plot(label="Agent Activity")
            gr.DataFrame(label="Recent Requests")

        with gr.Tab("Analytics"):
            gr.Plot(label="Cost Over Time")
            gr.Plot(label="Latency Over Time")

        submit_btn.click(
            fn=create_video_async,
            inputs=[brief_input],
            outputs=[output]
        )

    return app

app = create_ui()
app.launch()
```

**Opção 2: Streamlit (Médio)**
```python
import streamlit as st

st.set_page_config(page_title="OMA Dashboard", layout="wide")

# Sidebar
with st.sidebar:
    st.title("🎬 OMA")
    page = st.radio("Navigate", ["Create", "Monitor", "Analytics"])

if page == "Create":
    st.header("Create New Video")
    brief = st.text_area("Video Brief", height=200)
    if st.button("Generate"):
        with st.spinner("Creating video..."):
            result = await create_video(brief)
            st.video(result['video_path'])
            st.json(result['metadata'])

elif page == "Monitor":
    st.header("Real-time Monitoring")
    col1, col2, col3 = st.columns(3)
    col1.metric("Active Requests", active_count)
    col2.metric("Avg Latency", f"{avg_latency}s")
    col3.metric("Cost Today", f"${cost_today}")

    # Live agent activity
    st.line_chart(agent_activity_df)

elif page == "Analytics":
    st.header("Analytics Dashboard")
    # Métricas históricas, custos, etc.
```

**Opção 3: React Dashboard (Complexo mas Profissional)**
```typescript
// Frontend React + Backend FastAPI
// Similar ao que cloud providers têm
```

**Prioridade:** 🟡 Alta (após observability)

---

### 3. 🔐 **GUARDRAILS & SAFETY** (Gap Moderado)

#### O Que Você Tem:
```python
# Apenas validação básica
if not script or "scenes" not in script:
    raise ValueError("Invalid script")
```

#### O Que AWS Bedrock Tem:
```python
# Guardrails automáticos
- Content filtering (toxic, harmful, PII)
- Topic blocking (política, sexo, violência)
- Word filtering (profanidade)
- Sensitive info redaction (CPF, cartão)
- Custom guardrails via config
```

#### 💡 O Que Implementar:

**1. Content Safety**
```python
from transformers import pipeline

class ContentSafety:
    def __init__(self):
        # Model para detectar conteúdo tóxico
        self.toxicity = pipeline(
            "text-classification",
            model="unitary/toxic-bert"
        )

    async def check_content(self, text: str) -> dict:
        """Verifica se conteúdo é seguro"""
        result = self.toxicity(text)[0]

        return {
            'safe': result['label'] == 'non-toxic',
            'score': result['score'],
            'label': result['label']
        }

# Uso no supervisor
safety = ContentSafety()
check = await safety.check_content(brief['description'])
if not check['safe']:
    raise ValueError(f"Unsafe content: {check['label']}")
```

**2. PII Detection**
```python
import re

class PIIDetector:
    def __init__(self):
        self.patterns = {
            'cpf': r'\d{3}\.\d{3}\.\d{3}-\d{2}',
            'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'phone': r'\(\d{2}\)\s?\d{4,5}-\d{4}',
            'credit_card': r'\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}'
        }

    def detect(self, text: str) -> dict:
        """Detecta e redacta PII"""
        found = {}
        redacted = text

        for pii_type, pattern in self.patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                found[pii_type] = len(matches)
                redacted = re.sub(pattern, f'[{pii_type.upper()}_REDACTED]', redacted)

        return {
            'has_pii': len(found) > 0,
            'pii_types': found,
            'redacted_text': redacted
        }
```

**3. Configuração de Guardrails**
```yaml
# guardrails.yaml
guardrails:
  content_safety:
    enabled: true
    block_toxic: true
    block_nsfw: true
    threshold: 0.7

  pii_protection:
    enabled: true
    detect_cpf: true
    detect_email: true
    detect_phone: true
    redact: true

  topic_blocking:
    enabled: true
    blocked_topics:
      - politics
      - religion
      - adult_content

  word_filtering:
    enabled: true
    blocked_words: ['palavra1', 'palavra2']
```

**Prioridade:** 🟢 Média (importante para produção)

---

### 4. 💾 **PERSISTENT STATE MANAGEMENT** (Gap Moderado)

#### O Que Você Tem:
```python
# State apenas em memória (dict)
state = {
    "brief": {...},
    "script": {...},
    # ... perdido se server reiniciar
}
```

#### O Que Cloud Providers Têm:
```python
# AWS: DynamoDB
# Azure: Cosmos DB
# Vertex: Firestore

- State persistido em banco
- Histórico de execuções
- Retry após falhas
- Auditoria completa
```

#### 💡 O Que Implementar:

**Opção 1: Redis (Rápido)**
```python
import redis
import json

class StateManager:
    def __init__(self):
        self.redis = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True
        )

    def save_state(self, request_id: str, state: dict):
        """Salva state no Redis"""
        self.redis.setex(
            f"state:{request_id}",
            3600,  # TTL 1 hora
            json.dumps(state)
        )

    def load_state(self, request_id: str) -> dict:
        """Carrega state do Redis"""
        data = self.redis.get(f"state:{request_id}")
        return json.loads(data) if data else None

    def list_active_requests(self) -> list:
        """Lista requests ativos"""
        keys = self.redis.keys("state:*")
        return [k.split(':')[1] for k in keys]
```

**Opção 2: SQLite (Persistência Local)**
```python
import sqlite3
import json

class StateDB:
    def __init__(self, db_path='oma_state.db'):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS requests (
                id TEXT PRIMARY KEY,
                created_at TIMESTAMP,
                status TEXT,
                state_json TEXT,
                result_json TEXT,
                error TEXT
            )
        ''')

    def save_request(self, request_id: str, state: dict):
        self.conn.execute('''
            INSERT OR REPLACE INTO requests
            (id, created_at, status, state_json)
            VALUES (?, datetime('now'), ?, ?)
        ''', (request_id, 'in_progress', json.dumps(state)))
        self.conn.commit()

    def get_history(self, limit=100):
        cursor = self.conn.execute('''
            SELECT * FROM requests
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        return cursor.fetchall()
```

**Opção 3: PostgreSQL (Produção)**
```python
from sqlalchemy import create_engine, Column, String, JSON
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class VideoRequest(Base):
    __tablename__ = 'video_requests'

    id = Column(String, primary_key=True)
    status = Column(String)
    state = Column(JSON)
    result = Column(JSON)
    metadata = Column(JSON)

engine = create_engine('postgresql://localhost/oma')
Session = sessionmaker(bind=engine)
```

**Prioridade:** 🟡 Alta (crítico para produção)

---

### 5. 🔄 **WORKFLOW ORCHESTRATION** (Gap Baixo)

#### O Que Você Tem:
```python
# Orquestração básica manual
plan = supervisor.create_execution_plan(subtasks)
success, state = await supervisor.execute_plan(plan, state)
```

#### O Que AWS Tem:
```python
# AWS Step Functions
- Visual workflow editor
- State machine definition
- Automatic retry policies
- Conditional branching
- Parallel execution
- Wait states
- Error handling
```

#### 💡 O Que Implementar:

**Opção: Temporal.io (Workflow Engine)**
```python
from temporalio import workflow, activity

@workflow.defn
class VideoCreationWorkflow:
    @workflow.run
    async def run(self, brief: dict) -> dict:
        # Fase 1: Análise
        analysis = await workflow.execute_activity(
            analyze_request,
            brief,
            start_to_close_timeout=timedelta(seconds=30)
        )

        # Fase 2: Parallel agents
        script, visual, audio = await asyncio.gather(
            workflow.execute_activity(
                generate_script,
                analysis,
                start_to_close_timeout=timedelta(seconds=60)
            ),
            workflow.execute_activity(
                plan_visuals,
                analysis,
                start_to_close_timeout=timedelta(seconds=60)
            ),
            workflow.execute_activity(
                produce_audio,
                analysis,
                start_to_close_timeout=timedelta(seconds=90)
            )
        )

        # Fase 3: Edição
        video = await workflow.execute_activity(
            edit_video,
            {'script': script, 'visual': visual, 'audio': audio},
            start_to_close_timeout=timedelta(seconds=120)
        )

        return video
```

**Prioridade:** 🟢 Baixa (nice-to-have)

---

### 6. 🧪 **TESTING & VALIDATION** (Gap Moderado)

#### O Que Você Tem:
```python
# Tests manuais apenas
if __name__ == "__main__":
    asyncio.run(test())
```

#### O Que Precisa:
```python
# Test suite completo
- Unit tests (pytest)
- Integration tests
- End-to-end tests
- Load tests (Locust)
- Contract tests (entre agents)
```

#### 💡 O Que Implementar:

**1. Unit Tests**
```python
# tests/test_supervisor.py
import pytest
from agents import SupervisorAgent

@pytest.mark.asyncio
async def test_analyze_request():
    supervisor = SupervisorAgent()
    brief = {"description": "Test video", "duration": 30}

    analysis = await supervisor.analyze_request(brief)

    assert "objective" in analysis
    assert analysis["duration_seconds"] == 30

@pytest.mark.asyncio
async def test_decompose_task():
    supervisor = SupervisorAgent()
    analysis = {"objective": "Test", "duration_seconds": 30}

    subtasks = await supervisor.decompose_task(analysis)

    assert len(subtasks) >= 4
    assert any(st.type == TaskType.SCRIPT_GENERATION for st in subtasks)
```

**2. Integration Tests**
```python
# tests/test_integration.py
@pytest.mark.asyncio
async def test_full_video_creation():
    supervisor = SupervisorAgent()

    brief = {
        "title": "Test Video",
        "description": "Integration test",
        "duration": 15
    }

    # Full flow
    analysis = await supervisor.analyze_request(brief)
    subtasks = await supervisor.decompose_task(analysis)
    plan = supervisor.create_execution_plan(subtasks)

    state = {"brief": brief, "analysis": analysis}
    success, final_state = await supervisor.execute_plan(plan, state)

    assert success
    assert "video_path" in final_state
```

**3. Load Tests**
```python
# locustfile.py
from locust import HttpUser, task, between

class OMAUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def create_video(self):
        self.client.post("/api/videos", json={
            "title": "Load Test",
            "description": "Test video",
            "duration": 30
        })
```

**Prioridade:** 🟡 Alta (essencial para produção)

---

## 📋 ROADMAP PRIORIZADO

### 🔴 Fase 1: CRÍTICO (1-2 semanas)

1. **Observability Básica**
   - [ ] Implementar structured logging (structlog)
   - [ ] Adicionar cost tracking real-time
   - [ ] Métricas básicas (requests, latency, errors)
   - [ ] Health check endpoint

2. **State Persistence**
   - [ ] Implementar Redis/SQLite para state
   - [ ] Histórico de requests
   - [ ] Retry mechanism

3. **Testing**
   - [ ] Unit tests (cobertura >70%)
   - [ ] Integration tests
   - [ ] CI/CD básico

**Entregável:** Sistema production-ready com observability básica

---

### 🟡 Fase 2: IMPORTANTE (2-4 semanas)

4. **Observability Avançada**
   - [ ] OpenTelemetry + distributed tracing
   - [ ] Prometheus metrics
   - [ ] Grafana dashboards
   - [ ] Alertas automáticos

5. **UI Dashboard**
   - [ ] Gradio UI básico
   - [ ] Monitoring dashboard
   - [ ] Cost analytics
   - [ ] Request history

6. **Guardrails**
   - [ ] Content safety
   - [ ] PII detection
   - [ ] Configuração de policies

**Entregável:** Sistema enterprise-grade com full observability

---

### 🟢 Fase 3: NICE-TO-HAVE (1-2 meses)

7. **Advanced Features**
   - [ ] Workflow engine (Temporal.io)
   - [ ] Advanced UI (React dashboard)
   - [ ] Multi-tenant support
   - [ ] API rate limiting
   - [ ] Caching layer (CDN)

8. **Scalability**
   - [ ] Horizontal scaling
   - [ ] Load balancing
   - [ ] Message queue (RabbitMQ/Kafka)
   - [ ] Container orchestration (K8s)

**Entregável:** Sistema cloud-native escalável

---

## 🎯 COMPARAÇÃO FINAL: Após Implementar Roadmap

| Feature | OMA Hoje | OMA (após roadmap) | AWS/Azure/Vertex |
|---------|----------|--------------------| -----------------|
| **Core Architecture** | ✅ 100% | ✅ 100% | ✅ 100% |
| **Observability** | ⚠️ 30% | ✅ 95% | ✅ 100% |
| **UI/Dashboard** | ❌ 0% | ✅ 80% | ✅ 100% |
| **Guardrails** | ⚠️ 20% | ✅ 80% | ✅ 100% |
| **State Management** | ⚠️ 50% | ✅ 90% | ✅ 100% |
| **Testing** | ⚠️ 30% | ✅ 85% | ✅ 90% |
| **Cost** | ✅ 100% | ✅ 100% | ❌ 10% |
| **Flexibility** | ✅ 100% | ✅ 100% | ❌ 30% |

**CONCLUSÃO:** Após implementar Fase 1 e 2, você terá um sistema **MELHOR** que cloud providers em quase todos os aspectos, mantendo 16-45x menor custo!

---

## 🚀 PRÓXIMOS PASSOS IMEDIATOS

### Esta Semana (Crítico):

1. **Implementar Structured Logging**
```bash
pip install structlog
# Substituir todos os self.logger por structlog
```

2. **Adicionar Cost Tracking**
```python
# Criar CostTracker class
# Integrar em todos os agents
```

3. **Setup Tests**
```bash
pip install pytest pytest-asyncio
mkdir tests
# Criar test_supervisor.py
```

4. **Health Check**
```python
# Adicionar endpoint /health
# Retorna status de todos os components
```

### Próximo Mês (Importante):

5. **OpenTelemetry + Prometheus**
6. **Gradio Dashboard**
7. **Redis State Storage**

**Foco:** Observability first! É o gap mais crítico vs cloud providers.

