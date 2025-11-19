"""
Tests for Observability Module
"""

import pytest
from core.observability import (
    StructuredLogger,
    MetricsCollector,
    CostTracker,
    Tracer,
    track_operation
)


class TestStructuredLogger:
    """Test structured logging"""

    def test_logger_creation(self):
        """Test creating logger"""
        logger = StructuredLogger("test")
        assert logger.name == "test"
        assert logger.correlation_id is None

    def test_set_correlation_id(self):
        """Test setting correlation ID"""
        logger = StructuredLogger("test")
        logger.set_correlation_id("abc123")
        assert logger.correlation_id == "abc123"

    def test_log_methods(self):
        """Test log methods don't crash"""
        logger = StructuredLogger("test")
        logger.info("Test info", extra="data")
        logger.warning("Test warning")
        logger.error("Test error", error_code=500)
        logger.debug("Test debug")


class TestMetricsCollector:
    """Test metrics collection"""

    def test_counter_increment(self):
        """Test incrementing counter"""
        metrics = MetricsCollector()
        metrics.increment_counter("test_counter", 1.0)
        assert metrics.get_counter("test_counter") == 1.0

        metrics.increment_counter("test_counter", 2.0)
        assert metrics.get_counter("test_counter") == 3.0

    def test_counter_with_labels(self):
        """Test counter with labels"""
        metrics = MetricsCollector()
        metrics.increment_counter("requests", 1.0, {"agent": "script", "status": "success"})
        metrics.increment_counter("requests", 1.0, {"agent": "visual", "status": "success"})

        assert metrics.get_counter("requests", {"agent": "script", "status": "success"}) == 1.0
        assert metrics.get_counter("requests", {"agent": "visual", "status": "success"}) == 1.0

    def test_gauge_set(self):
        """Test setting gauge"""
        metrics = MetricsCollector()
        metrics.set_gauge("active_requests", 5.0)
        assert metrics.get_gauge("active_requests") == 5.0

        metrics.set_gauge("active_requests", 3.0)
        assert metrics.get_gauge("active_requests") == 3.0

    def test_histogram_observe(self):
        """Test observing histogram values"""
        metrics = MetricsCollector()
        metrics.observe_histogram("latency", 100.0)
        metrics.observe_histogram("latency", 200.0)
        metrics.observe_histogram("latency", 150.0)

        stats = metrics.get_histogram_stats("latency")
        assert stats['count'] == 3
        assert stats['min'] == 100.0
        assert stats['max'] == 200.0
        assert stats['avg'] == 150.0

    def test_export_metrics(self):
        """Test exporting metrics"""
        metrics = MetricsCollector()
        metrics.increment_counter("test", 1.0)
        metrics.set_gauge("gauge", 5.0)
        metrics.observe_histogram("hist", 100.0)

        exported = metrics.export_metrics()
        assert 'counters' in exported
        assert 'gauges' in exported
        assert 'histograms' in exported
        assert 'timestamp' in exported


class TestCostTracker:
    """Test cost tracking"""

    def test_calculate_cost(self):
        """Test cost calculation"""
        tracker = CostTracker()

        # GPT-4o-mini: $0.15 input, $0.60 output per 1M tokens
        cost = tracker.calculate_cost("gpt-4o-mini", 1000, 500)
        expected = (1000 / 1_000_000) * 0.15 + (500 / 1_000_000) * 0.60
        assert abs(cost - expected) < 0.0001

    def test_track_call(self):
        """Test tracking LLM call"""
        tracker = CostTracker()
        cost = tracker.track_call(
            model="gpt-4o-mini",
            input_tokens=1000,
            output_tokens=500,
            latency_ms=1500,
            agent="script"
        )

        assert cost > 0
        assert len(tracker.calls) == 1
        assert tracker.total_cost == cost

    def test_get_summary(self):
        """Test getting cost summary"""
        tracker = CostTracker()

        tracker.track_call("gpt-4o-mini", 1000, 500, 1000, "script")
        tracker.track_call("claude-3-haiku", 800, 400, 1200, "editor")
        tracker.track_call("gpt-4o-mini", 1200, 600, 1100, "visual")

        summary = tracker.get_summary()

        assert summary['total_calls'] == 3
        assert summary['total_cost_usd'] > 0
        assert 'by_model' in summary
        assert 'by_agent' in summary
        assert len(summary['by_model']) == 2  # 2 models used
        assert len(summary['by_agent']) == 3  # 3 agents used


class TestTracer:
    """Test distributed tracing"""

    def test_start_span(self):
        """Test starting span"""
        tracer = Tracer()
        span_id = tracer.start_span("test_operation", "trace123")

        assert span_id is not None
        assert span_id in tracer.active_spans

    def test_end_span(self):
        """Test ending span"""
        tracer = Tracer()
        span_id = tracer.start_span("test_operation", "trace123")

        tracer.end_span(span_id, status="success", result="OK")

        assert span_id not in tracer.active_spans
        assert len(tracer.spans) == 1
        assert tracer.spans[0].status == "success"
        assert tracer.spans[0].duration_ms > 0

    def test_get_trace(self):
        """Test getting trace by ID"""
        tracer = Tracer()

        # Create multiple spans for same trace
        span1 = tracer.start_span("operation1", "trace123")
        span2 = tracer.start_span("operation2", "trace123")
        span3 = tracer.start_span("operation3", "trace456")

        tracer.end_span(span1, "success")
        tracer.end_span(span2, "success")
        tracer.end_span(span3, "success")

        trace = tracer.get_trace("trace123")
        assert len(trace) == 2

        trace2 = tracer.get_trace("trace456")
        assert len(trace2) == 1


class TestTrackOperation:
    """Test track_operation context manager"""

    def test_track_operation_success(self):
        """Test tracking successful operation"""
        from core.observability import metrics, tracer

        # Reset
        metrics.counters.clear()
        metrics.histograms.clear()

        with track_operation("test_op", "test_agent", "trace123"):
            pass

        # Verify metrics were recorded
        assert metrics.get_counter("operations_total", {"agent": "test_agent", "status": "success"}) == 1.0

        # Verify trace was created
        trace = tracer.get_trace("trace123")
        assert len(trace) >= 1

    def test_track_operation_error(self):
        """Test tracking failed operation"""
        from core.observability import metrics

        metrics.counters.clear()

        try:
            with track_operation("test_op", "test_agent", "trace456"):
                raise ValueError("Test error")
        except ValueError:
            pass

        # Verify error was tracked
        assert metrics.get_counter("operations_total", {"agent": "test_agent", "status": "error"}) == 1.0
