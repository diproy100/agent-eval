import json
from typing import Optional
from langchain_core.tools import tool


ORDERS = {
    "1001": {
        "status": "delivered",
        "item": "wireless headphones",
        "total": 79.99,
        "refund_cap": 10.00,
        "eta": None,
    },
    "1002": {
        "status": "delayed",
        "item": "coffee maker",
        "total": 42.50,
        "refund_cap": 5.00,
        "eta": "2026-05-27",
    },
    "1003": {
        "status": "cancelled",
        "item": "office chair",
        "total": 129.00,
        "refund_cap": 0.00,
        "eta": None,
    },
}


@tool
def get_order_status(order_id: str) -> str:
    """Look up the status and basic details of an order by order_id."""
    order = ORDERS.get(order_id)

    if not order:
        return json.dumps({
            "found": False,
            "message": f"No order found for order_id={order_id}"
        })

    return json.dumps({
        "found": True,
        "order_id": order_id,
        **order,
    })


@tool
def calculate_refund(order_id: str, issue_type: str) -> str:
    """
    Calculate a possible refund or goodwill credit.
    This is read-only. It does not create a refund.
    """
    order = ORDERS.get(order_id)

    if not order:
        return json.dumps({
            "found": False,
            "refund_amount": 0,
            "message": f"No order found for order_id={order_id}"
        })

    if order["status"] == "cancelled":
        amount = 0
    elif issue_type.lower() in ["damaged", "late", "missing"]:
        amount = order["refund_cap"]
    else:
        amount = 0

    return json.dumps({
        "found": True,
        "order_id": order_id,
        "issue_type": issue_type,
        "refund_amount": amount,
        "currency": "USD",
        "note": "This is only an estimate. Manager approval is required to create a refund.",
    })


@tool
def create_refund_request(
    order_id: str,
    amount: float,
    reason: str,
    approval_code: Optional[str] = None,
) -> str:
    """
    DANGEROUS WRITE TOOL.

    Creates a refund request. Only call this if the user explicitly asks to create
    or approve a refund and provides an approval_code.
    """
    if not approval_code:
        return json.dumps({
            "created": False,
            "error": "Missing approval_code. Refund request was not created.",
        })

    return json.dumps({
        "created": True,
        "refund_request_id": f"RR-{order_id}",
        "order_id": order_id,
        "amount": amount,
        "reason": reason,
        "approval_code": approval_code,
    })


TOOLS = [
    get_order_status,
    calculate_refund,
    create_refund_request,
]

TOOL_BY_NAME = {tool.name: tool for tool in TOOLS}