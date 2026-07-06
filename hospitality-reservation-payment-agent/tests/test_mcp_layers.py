# tests/test_mcp_layers.py
import unittest
from agent_mcp.server import MCPServer
from agent_mcp.tools import (
    check_availability_tool,
    calculate_price_tool,
    create_payment_link_tool,
    check_payment_status_tool,
    confirm_reservation_tool,
    cancel_reservation_tool,
    issue_refund_tool,
    save_reservation_report_tool
)

class TestMCPLayers(unittest.TestCase):
    """
    Verification suite for Phase 4 MCP layer.
    """

    def test_imports_and_instantiation(self):
        # 1. Verify individual tool imports
        self.assertIsNotNone(check_availability_tool)
        self.assertIsNotNone(calculate_price_tool)
        self.assertIsNotNone(create_payment_link_tool)
        self.assertIsNotNone(check_payment_status_tool)
        self.assertIsNotNone(confirm_reservation_tool)
        self.assertIsNotNone(cancel_reservation_tool)
        self.assertIsNotNone(issue_refund_tool)
        self.assertIsNotNone(save_reservation_report_tool)

        # 2. Instantiate server
        server = MCPServer()
        self.assertIsNotNone(server)

        # 3. List tools
        tools = server.list_tools()
        self.assertEqual(len(tools), 8)
        tool_names = [t["name"] for t in tools]
        self.assertIn("check_availability", tool_names)
        self.assertIn("calculate_price", tool_names)
        self.assertIn("create_payment_link", tool_names)

        # 4. Call check_availability
        avail_res = server.call_tool("check_availability", room_id="deluxe-suite", check_in="2026-07-10", check_out="2026-07-15")
        self.assertIn("available", avail_res)
        self.assertEqual(avail_res["room_id"], "deluxe-suite")

        # 5. Call calculate_price
        price_res = server.call_tool("calculate_price", room_id="deluxe-suite", check_in="2026-07-10", check_out="2026-07-15", guests=2)
        self.assertIn("total_price", price_res)
        self.assertEqual(price_res["nights"], 5)

        # 6. Call create_payment_link
        pay_res = server.call_tool("create_payment_link", reservation_id="res_001", amount=1250.0)
        self.assertIn("payment_link", pay_res)
        self.assertEqual(pay_res["reservation_id"], "res_001")
        self.assertIn("sandbox.stripe", pay_res["payment_link"])

if __name__ == "__main__":
    unittest.main()
