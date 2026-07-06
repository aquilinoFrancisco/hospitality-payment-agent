# agent_mcp/tools/save_reservation_report.py
import os
import json

def save_reservation_report_tool(report_payload: dict) -> dict:
    """
    MCP Tool: Save structural JSON receipt report to the reports/ directory.
    """
    report_id = report_payload.get("report_id") or report_payload.get("reservation_id") or "report_generic"
    
    # Resolve absolute path to hospitality-reservation-payment-agent/reports
    reports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "reports"))
    os.makedirs(reports_dir, exist_ok=True)
    
    file_path = os.path.join(reports_dir, f"report_{report_id}.json")
    
    try:
        with open(file_path, "w") as f:
            json.dump(report_payload, f, indent=2)
        status = "SAVED"
    except Exception as e:
        status = f"FAILED: {str(e)}"
        
    return {
        "report_id": report_id,
        "file_path": f"reports/report_{report_id}.json",
        "status": status
    }

