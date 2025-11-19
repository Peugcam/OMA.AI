"""
OMA Dashboard - Gradio UI
100% GRATUITO - Roda local
"""

import gradio as gr
import json
from datetime import datetime
from pathlib import Path

# Import core modules
try:
    from core.observability import metrics, cost_tracker, tracer
    from core.state_manager import state_manager
except ImportError:
    print("⚠️ Core modules not found. Run from project root.")
    metrics = None
    cost_tracker = None
    state_manager = None


# ============================================================================
# DASHBOARD FUNCTIONS
# ============================================================================

def get_metrics_summary():
    """Retorna resumo de métricas"""
    if not metrics:
        return "Metrics not available"

    exported = metrics.export_metrics()

    summary = f"""
# 📊 Metrics Summary

## Counters
```json
{json.dumps(exported['counters'], indent=2)}
```

## Gauges
```json
{json.dumps(exported['gauges'], indent=2)}
```

## Histograms
```json
{json.dumps(exported['histograms'], indent=2)}
```

Last updated: {exported['timestamp']}
"""
    return summary


def get_cost_summary():
    """Retorna resumo de custos"""
    if not cost_tracker:
        return "Cost tracker not available"

    summary = cost_tracker.get_summary()

    output = f"""
# 💰 Cost Tracking Summary

## Overall
- **Total Cost:** ${summary['total_cost_usd']:.4f}
- **Total Calls:** {summary['total_calls']}
- **Total Tokens:** {summary['total_tokens']:,}
- **Avg Cost/Call:** ${summary.get('avg_cost_per_call', 0):.4f}

## By Model
"""

    for model, stats in summary['by_model'].items():
        output += f"""
### {model}
- Calls: {stats['calls']}
- Cost: ${stats['cost']:.4f}
- Tokens: {stats['tokens']:,}
"""

    output += "\n## By Agent\n"

    for agent, stats in summary['by_agent'].items():
        output += f"""
### {agent}
- Calls: {stats['calls']}
- Cost: ${stats['cost']:.4f}
- Tokens: {stats['tokens']:,}
"""

    return output


def get_requests_history(status_filter=None):
    """Retorna histórico de requests"""
    if not state_manager:
        return []

    requests = state_manager.list_requests(status=status_filter, limit=50)

    # Convert to list of lists for DataFrame
    return [
        [
            req['request_id'],
            req['created_at'],
            req['updated_at'],
            req['status']
        ]
        for req in requests
    ]


def get_stats():
    """Retorna estatísticas gerais"""
    if not state_manager:
        return "State manager not available"

    stats = state_manager.get_stats()

    return f"""
# 📈 Overall Statistics

- **Total Requests:** {stats['total']}
- **Completed:** {stats['completed']} ✅
- **In Progress:** {stats['in_progress']} 🔄
- **Failed:** {stats['failed']} ❌
- **Pending:** {stats['pending']} ⏳
- **Success Rate:** {stats['success_rate']:.1f}%
"""


def view_request_details(request_id):
    """Mostra detalhes de um request"""
    if not state_manager or not request_id:
        return "Enter a request ID"

    req = state_manager.get_request(request_id)

    if not req:
        return f"❌ Request '{request_id}' not found"

    output = f"""
# 🔍 Request Details: {request_id}

## Status
- **Status:** {req['status']}
- **Created:** {req['created_at']}
- **Updated:** {req['updated_at']}
"""

    if req.get('error'):
        output += f"\n## ❌ Error\n```\n{req['error']}\n```\n"

    if req.get('state'):
        output += f"\n## 📋 State\n```json\n{json.dumps(req['state'], indent=2, ensure_ascii=False)}\n```\n"

    if req.get('result'):
        output += f"\n## ✅ Result\n```json\n{json.dumps(req['result'], indent=2, ensure_ascii=False)}\n```\n"

    return output


def create_test_request():
    """Cria request de teste"""
    import uuid

    request_id = f"test_{uuid.uuid4().hex[:8]}"

    state = {
        "brief": {
            "title": "Test Video",
            "description": "Dashboard test request",
            "duration": 30
        },
        "created_from": "dashboard",
        "timestamp": datetime.now().isoformat()
    }

    if state_manager:
        state_manager.save_request(request_id, state, status="pending")
        return f"✅ Created test request: {request_id}"
    else:
        return "❌ State manager not available"


# ============================================================================
# GRADIO UI
# ============================================================================

def create_dashboard():
    """Cria dashboard Gradio"""

    with gr.Blocks(title="OMA Dashboard", theme=gr.themes.Soft()) as app:
        gr.Markdown("""
        # 🎬 OMA Dashboard
        ### Multi-Agent Video Creation Platform

        Monitor metrics, costs, and requests in real-time.
        """)

        with gr.Tabs():
            # TAB 1: Overview
            with gr.Tab("📊 Overview"):
                gr.Markdown("## System Status")

                with gr.Row():
                    stats_output = gr.Markdown(value=get_stats())

                gr.Markdown("## Recent Activity")

                refresh_btn = gr.Button("🔄 Refresh", variant="primary")

                def refresh_overview():
                    return get_stats()

                refresh_btn.click(fn=refresh_overview, outputs=[stats_output])

            # TAB 2: Metrics
            with gr.Tab("📈 Metrics"):
                gr.Markdown("## Performance Metrics")

                metrics_output = gr.Markdown(value=get_metrics_summary())

                refresh_metrics_btn = gr.Button("🔄 Refresh Metrics")

                refresh_metrics_btn.click(
                    fn=get_metrics_summary,
                    outputs=[metrics_output]
                )

            # TAB 3: Cost Tracking
            with gr.Tab("💰 Costs"):
                gr.Markdown("## Cost Tracking")

                cost_output = gr.Markdown(value=get_cost_summary())

                refresh_cost_btn = gr.Button("🔄 Refresh Costs")

                refresh_cost_btn.click(
                    fn=get_cost_summary,
                    outputs=[cost_output]
                )

            # TAB 4: Requests
            with gr.Tab("📋 Requests"):
                gr.Markdown("## Request History")

                with gr.Row():
                    status_filter = gr.Dropdown(
                        choices=["all", "pending", "in_progress", "completed", "failed"],
                        value="all",
                        label="Filter by Status"
                    )

                requests_table = gr.Dataframe(
                    headers=["Request ID", "Created", "Updated", "Status"],
                    value=get_requests_history(),
                    label="Recent Requests"
                )

                def filter_requests(status):
                    return get_requests_history(None if status == "all" else status)

                status_filter.change(
                    fn=filter_requests,
                    inputs=[status_filter],
                    outputs=[requests_table]
                )

                refresh_requests_btn = gr.Button("🔄 Refresh Requests")

                refresh_requests_btn.click(
                    fn=lambda s: filter_requests(s),
                    inputs=[status_filter],
                    outputs=[requests_table]
                )

            # TAB 5: Request Details
            with gr.Tab("🔍 Request Details"):
                gr.Markdown("## View Request Details")

                request_id_input = gr.Textbox(
                    label="Request ID",
                    placeholder="Enter request ID..."
                )

                view_btn = gr.Button("View Details", variant="primary")

                details_output = gr.Markdown()

                view_btn.click(
                    fn=view_request_details,
                    inputs=[request_id_input],
                    outputs=[details_output]
                )

            # TAB 6: Tools
            with gr.Tab("🛠️ Tools"):
                gr.Markdown("## Testing Tools")

                create_test_btn = gr.Button("Create Test Request", variant="secondary")
                test_output = gr.Textbox(label="Result")

                create_test_btn.click(
                    fn=create_test_request,
                    outputs=[test_output]
                )

                gr.Markdown("---")

                gr.Markdown("""
                ### About
                - **Version:** 1.0.0
                - **Cost:** 100% FREE (Gradio local)
                - **Open Source:** Yes
                - **Similar to:** AWS CloudWatch Console, Azure Portal, GCP Console
                """)

        gr.Markdown("""
        ---
        **OMA Dashboard** - Enterprise monitoring sem custo!
        """)

    return app


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("🚀 Starting OMA Dashboard...")
    print("📊 100% GRATUITO - Roda local!")
    print("")

    app = create_dashboard()

    # Launch dashboard
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,  # Set to True for public link (optional)
        show_error=True
    )
