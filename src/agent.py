import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage

from tools import TOOLS, TOOL_BY_NAME


load_dotenv()

OPENROUTER_MODEL = "openai/gpt-oss-120b:free"


SYSTEM_PROMPT = """
You are a careful customer-support operations agent.

Rules:
- Use tools when you need order facts.
- Do not invent order status, ETA, refund amount, or refund result.
- calculate_refund is read-only.
- create_refund_request is a write action.
- Never call create_refund_request unless the user explicitly asks to create/approve a refund
  and provides an approval code.
- If approval is missing, explain what is needed.
- Keep answers concise.
"""


def build_llm():
    return ChatOpenAI(
        temperature=0,
        model=OPENROUTER_MODEL,
        api_key=os.environ["OPENROUTER_API_KEY"],
        base_url="https://openrouter.ai/api/v1",
    )


def run_agent(user_input: str, max_steps: int = 5) -> dict:
    llm = build_llm()
    llm_with_tools = llm.bind_tools(TOOLS)

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_input),
    ]

    trace = []

    for step in range(max_steps):
        ai_msg = llm_with_tools.invoke(messages)
        messages.append(ai_msg)

        tool_calls = getattr(ai_msg, "tool_calls", None) or []

        if not tool_calls:
            return {
                "answer": ai_msg.content,
                "trace": trace,
                "stopped_reason": "final_answer",
            }

        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call.get("args", {})
            tool_id = tool_call["id"]

            if tool_name not in TOOL_BY_NAME:
                tool_result = f"Unknown tool: {tool_name}"
            else:
                tool_result = TOOL_BY_NAME[tool_name].invoke(tool_args)

            trace.append({
                "step": step,
                "tool": tool_name,
                "args": tool_args,
                "result": str(tool_result),
            })

            messages.append(
                ToolMessage(
                    content=str(tool_result),
                    tool_call_id=tool_id,
                )
            )

    return {
        "answer": "Agent stopped because max_steps was reached.",
        "trace": trace,
        "stopped_reason": "max_steps",
    }