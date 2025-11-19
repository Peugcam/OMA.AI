"""
Observability Module - Metrics, Logging, Tracing
Inspirado em AWS CloudWatch, Azure App Insights, Vertex AI Monitoring
"""

import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from collections import defaultdict
import json
from pathlib import Path


# ============================================================================
# STRUCTURED LOGGING
# ============================================================================

class StructuredLogger:
    """
    Logger estruturado similar ao CloudWatch Logs

    Features:
    - JSON formatted logs
    - Correlation IDs
    - Structured metadata
    - Multiple severity levels
    """

    def __init__(self, name: str):
        self.name = name
        self.correlation_id: Optional[str] = None

    def set_correlation_id(self, correlation_id: str):
        """Define correlation ID para rastrear request completo"""
        self.correlation_id = correlation_id

    def _log(self, level: str, message: str, **kwargs):
        """Log estruturado em JSON"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'logger': self.name,
            'message': message,
            'correlation_id': self.correlation_id,
            **kwargs
        }

        # Print JSON formatado
        print(json.dumps(log_entry, ensure_ascii=False))

        # Também salva em arquivo
        self._save_to_file(log_entry)

    def _save_to_file(self, log_entry: dict):
        """Salva logs em arquivo para análise posterior"""
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / f"{datetime.utcnow().strftime('%Y-%m-%d')}.jsonl"

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

    def info(self, message: str, **kwargs):
        """Info level log"""
        self._log('INFO', message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Warning level log"""
        self._log('WARNING', message, **kwargs)

    def error(self, message: str, **kwargs):
        """Error level log"""
        self._log('ERROR', message, **kwargs)

    def debug(self, message: str, **kwargs):
        """Debug level log"""
        self._log('DEBUG', message, **kwargs)


# ============================================================================
# METRICS COLLECTOR
# ============================================================================

@dataclass
class Metric:
    """Métrica individual"""
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    unit: str = "count"


class MetricsCollector:
    """
    Coletor de métricas similar ao Prometheus/CloudWatch Metrics

    Features:
    - Counters (total de requests, erros, etc.)
    - Gauges (requests ativos, memória, etc.)
    - Histograms (latência, tamanho de resposta, etc.)
    - Labels (dimensões para filtrar)
    """

    def __init__(self):
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.metrics_history: List[Metric] = []

    def increment_counter(self, name: str, value: float = 1.0, labels: Dict = None):
        """Incrementa contador (ex: total_requests)"""
        key = self._make_key(name, labels)
        self.counters[key] += value

        metric = Metric(
            name=name,
            value=self.counters[key],
            timestamp=datetime.utcnow(),
            labels=labels or {},
            unit="count"
        )
        self.metrics_history.append(metric)

    def set_gauge(self, name: str, value: float, labels: Dict = None):
        """Define gauge (ex: active_requests)"""
        key = self._make_key(name, labels)
        self.gauges[key] = value

        metric = Metric(
            name=name,
            value=value,
            timestamp=datetime.utcnow(),
            labels=labels or {},
            unit="gauge"
        )
        self.metrics_history.append(metric)

    def observe_histogram(self, name: str, value: float, labels: Dict = None):
        """Adiciona valor ao histograma (ex: latency)"""
        key = self._make_key(name, labels)
        self.histograms[key].append(value)

        metric = Metric(
            name=name,
            value=value,
            timestamp=datetime.utcnow(),
            labels=labels or {},
            unit="histogram"
        )
        self.metrics_history.append(metric)

    def _make_key(self, name: str, labels: Dict = None) -> str:
        """Cria chave única para métrica com labels"""
        if not labels:
            return name
        label_str = ','.join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    def get_counter(self, name: str, labels: Dict = None) -> float:
        """Retorna valor de contador"""
        key = self._make_key(name, labels)
        return self.counters.get(key, 0.0)

    def get_gauge(self, name: str, labels: Dict = None) -> float:
        """Retorna valor de gauge"""
        key = self._make_key(name, labels)
        return self.gauges.get(key, 0.0)

    def get_histogram_stats(self, name: str, labels: Dict = None) -> Dict:
        """Retorna estatísticas do histograma"""
        key = self._make_key(name, labels)
        values = self.histograms.get(key, [])

        if not values:
            return {'count': 0, 'sum': 0, 'avg': 0, 'min': 0, 'max': 0, 'p50': 0, 'p95': 0, 'p99': 0}

        sorted_values = sorted(values)
        count = len(sorted_values)

        return {
            'count': count,
            'sum': sum(sorted_values),
            'avg': sum(sorted_values) / count,
            'min': sorted_values[0],
            'max': sorted_values[-1],
            'p50': self._percentile(sorted_values, 0.50),
            'p95': self._percentile(sorted_values, 0.95),
            'p99': self._percentile(sorted_values, 0.99)
        }

    def _percentile(self, sorted_values: List[float], percentile: float) -> float:
        """Calcula percentil"""
        if not sorted_values:
            return 0.0
        index = int(len(sorted_values) * percentile)
        return sorted_values[min(index, len(sorted_values) - 1)]

    def export_metrics(self) -> Dict:
        """Exporta todas as métricas para análise"""
        return {
            'counters': dict(self.counters),
            'gauges': dict(self.gauges),
            'histograms': {
                name: self.get_histogram_stats(name.split('{')[0], None)
                for name in self.histograms.keys()
            },
            'timestamp': datetime.utcnow().isoformat()
        }

    def save_metrics(self, filepath: str = 'reports/metrics.json'):
        """Salva métricas em arquivo"""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.export_metrics(), f, indent=2, ensure_ascii=False)


# ============================================================================
# COST TRACKER
# ============================================================================

@dataclass
class LLMCall:
    """Registro de chamada LLM"""
    timestamp: datetime
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: float
    agent: str
    status: str  # success, error


class CostTracker:
    """
    Rastreador de custos similar ao AWS Cost Explorer

    Features:
    - Track por modelo
    - Track por agent
    - Track por dia/hora
    - Alertas de orçamento
    """

    # Preços por 1M tokens (OpenRouter - Nov 2024)
    PRICING = {
        'gpt-4o-mini': {'input': 0.15, 'output': 0.60},
        'claude-3-5-sonnet': {'input': 3.00, 'output': 15.00},
        'claude-3-haiku': {'input': 0.25, 'output': 1.25},
        'qwen/qwen-2.5-7b-instruct': {'input': 0.20, 'output': 0.40},
        'meta-llama/llama-3.2-3b-instruct': {'input': 0.06, 'output': 0.06},
        'phi3:mini': {'input': 0.00, 'output': 0.00},  # Local
    }

    def __init__(self):
        self.calls: List[LLMCall] = []
        self.total_cost: float = 0.0
        self.budget_alert_threshold: float = 100.0  # $100

    def track_call(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: float,
        agent: str,
        status: str = 'success'
    ) -> float:
        """Rastreia uma chamada LLM e retorna custo"""
        cost = self.calculate_cost(model, input_tokens, output_tokens)

        call = LLMCall(
            timestamp=datetime.utcnow(),
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            latency_ms=latency_ms,
            agent=agent,
            status=status
        )

        self.calls.append(call)
        self.total_cost += cost

        # Verificar orçamento
        if self.total_cost > self.budget_alert_threshold:
            print(f"⚠️ BUDGET ALERT: Total cost ${self.total_cost:.2f} exceeds threshold ${self.budget_alert_threshold}")

        return cost

    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calcula custo de uma chamada"""
        pricing = self.PRICING.get(model, {'input': 0.50, 'output': 1.00})  # Default pricing

        input_cost = (input_tokens / 1_000_000) * pricing['input']
        output_cost = (output_tokens / 1_000_000) * pricing['output']

        return input_cost + output_cost

    def get_summary(self) -> Dict:
        """Retorna resumo de custos"""
        if not self.calls:
            return {
                'total_cost_usd': 0.0,
                'total_calls': 0,
                'total_tokens': 0,
                'by_model': {},
                'by_agent': {}
            }

        by_model = defaultdict(lambda: {'calls': 0, 'cost': 0.0, 'tokens': 0})
        by_agent = defaultdict(lambda: {'calls': 0, 'cost': 0.0, 'tokens': 0})

        total_tokens = 0

        for call in self.calls:
            tokens = call.input_tokens + call.output_tokens
            total_tokens += tokens

            # Por modelo
            by_model[call.model]['calls'] += 1
            by_model[call.model]['cost'] += call.cost_usd
            by_model[call.model]['tokens'] += tokens

            # Por agent
            by_agent[call.agent]['calls'] += 1
            by_agent[call.agent]['cost'] += call.cost_usd
            by_agent[call.agent]['tokens'] += tokens

        return {
            'total_cost_usd': self.total_cost,
            'total_calls': len(self.calls),
            'total_tokens': total_tokens,
            'avg_cost_per_call': self.total_cost / len(self.calls),
            'by_model': dict(by_model),
            'by_agent': dict(by_agent)
        }

    def print_summary(self):
        """Imprime resumo formatado"""
        summary = self.get_summary()

        print("\n" + "="*60)
        print("💰 COST TRACKING SUMMARY")
        print("="*60)

        print(f"\n📊 Overall:")
        print(f"  Total Cost: ${summary['total_cost_usd']:.4f}")
        print(f"  Total Calls: {summary['total_calls']}")
        print(f"  Total Tokens: {summary['total_tokens']:,}")
        print(f"  Avg Cost/Call: ${summary.get('avg_cost_per_call', 0):.4f}")

        print(f"\n🤖 By Model:")
        for model, stats in summary['by_model'].items():
            print(f"  {model}:")
            print(f"    Calls: {stats['calls']}")
            print(f"    Cost: ${stats['cost']:.4f}")
            print(f"    Tokens: {stats['tokens']:,}")

        print(f"\n👥 By Agent:")
        for agent, stats in summary['by_agent'].items():
            print(f"  {agent}:")
            print(f"    Calls: {stats['calls']}")
            print(f"    Cost: ${stats['cost']:.4f}")
            print(f"    Tokens: {stats['tokens']:,}")

        print("\n" + "="*60 + "\n")


# ============================================================================
# TRACER (Distributed Tracing)
# ============================================================================

@dataclass
class Span:
    """Span de trace (similar ao OpenTelemetry)"""
    span_id: str
    trace_id: str
    name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    status: str = 'in_progress'
    metadata: Dict[str, Any] = field(default_factory=dict)
    parent_span_id: Optional[str] = None


class Tracer:
    """
    Distributed tracing similar ao Jaeger/Zipkin

    Features:
    - Trace requests completos
    - Parent-child relationships
    - Duration tracking
    - Metadata attachment
    """

    def __init__(self):
        self.spans: List[Span] = []
        self.active_spans: Dict[str, Span] = {}

    def start_span(
        self,
        name: str,
        trace_id: str,
        parent_span_id: Optional[str] = None
    ) -> str:
        """Inicia novo span"""
        import uuid

        span_id = str(uuid.uuid4())[:8]

        span = Span(
            span_id=span_id,
            trace_id=trace_id,
            name=name,
            start_time=datetime.utcnow(),
            parent_span_id=parent_span_id
        )

        self.active_spans[span_id] = span
        return span_id

    def end_span(self, span_id: str, status: str = 'success', **metadata):
        """Finaliza span"""
        if span_id not in self.active_spans:
            return

        span = self.active_spans[span_id]
        span.end_time = datetime.utcnow()
        span.duration_ms = (span.end_time - span.start_time).total_seconds() * 1000
        span.status = status
        span.metadata.update(metadata)

        self.spans.append(span)
        del self.active_spans[span_id]

    def get_trace(self, trace_id: str) -> List[Span]:
        """Retorna todos os spans de um trace"""
        return [s for s in self.spans if s.trace_id == trace_id]

    def print_trace(self, trace_id: str):
        """Imprime trace formatado"""
        spans = self.get_trace(trace_id)

        if not spans:
            print(f"No trace found for {trace_id}")
            return

        print(f"\n🔍 TRACE: {trace_id}")
        print("="*60)

        # Ordenar por start_time
        spans.sort(key=lambda s: s.start_time)

        # Calcular total duration
        total_duration = max((s.end_time for s in spans if s.end_time), default=datetime.utcnow()) - \
                        min((s.start_time for s in spans))

        print(f"Total Duration: {total_duration.total_seconds() * 1000:.0f}ms\n")

        for span in spans:
            indent = "  " if span.parent_span_id else ""
            status_icon = "✅" if span.status == 'success' else "❌"

            print(f"{indent}{status_icon} {span.name}")
            print(f"{indent}   Duration: {span.duration_ms:.0f}ms")
            if span.metadata:
                print(f"{indent}   Metadata: {span.metadata}")

        print("="*60 + "\n")


# ============================================================================
# SINGLETON INSTANCES (Global)
# ============================================================================

# Instâncias globais para uso em todo o projeto
metrics = MetricsCollector()
cost_tracker = CostTracker()
tracer = Tracer()


def get_logger(name: str) -> StructuredLogger:
    """Factory para criar loggers estruturados"""
    return StructuredLogger(name)


# ============================================================================
# CONTEXT MANAGER PARA TRACKING AUTOMÁTICO
# ============================================================================

class track_operation:
    """
    Context manager para rastrear operações automaticamente

    Usage:
        with track_operation('generate_script', agent='script', trace_id='abc123'):
            result = await agent.generate_script(state)
    """

    def __init__(self, operation_name: str, agent: str, trace_id: str, parent_span_id: str = None):
        self.operation_name = operation_name
        self.agent = agent
        self.trace_id = trace_id
        self.parent_span_id = parent_span_id
        self.span_id = None
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        self.span_id = tracer.start_span(
            self.operation_name,
            self.trace_id,
            self.parent_span_id
        )

        # Incrementar gauge de operações ativas
        metrics.set_gauge(
            'active_operations',
            metrics.get_gauge('active_operations') + 1,
            {'agent': self.agent}
        )

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000
        status = 'success' if exc_type is None else 'error'

        # Finalizar span
        tracer.end_span(
            self.span_id,
            status=status,
            duration_ms=duration_ms,
            agent=self.agent,
            error=str(exc_val) if exc_val else None
        )

        # Registrar métrica de latência
        metrics.observe_histogram(
            'operation_latency_ms',
            duration_ms,
            {'agent': self.agent, 'operation': self.operation_name}
        )

        # Incrementar contador
        metrics.increment_counter(
            'operations_total',
            labels={'agent': self.agent, 'status': status}
        )

        # Decrementar gauge de operações ativas
        metrics.set_gauge(
            'active_operations',
            metrics.get_gauge('active_operations') - 1,
            {'agent': self.agent}
        )

        # Não suprimir exceção
        return False
