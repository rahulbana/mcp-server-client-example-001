"""OpenAI tool-calling agent that drives MCP tools."""
from __future__ import annotations

import json
import logging
from typing import Any

from openai import AsyncOpenAI

from client.mcp_session import ClientSession, call_tool

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are an inventory assistant for a grocery/fruit store.
You help users manage their inventory by calling the available tools.
Always confirm what you did after each action.
When listing items, present them in a readable table format.
"""


class InventoryAgent:
    def __init__(self, session: ClientSession, tools: list[dict], model: str, api_key: str) -> None:
        self._session = session
        self._tools = self._adapt_tools(tools)
        self._model = model
        self._client = AsyncOpenAI(api_key=api_key)
        self._history: list[dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]

    @staticmethod
    def _adapt_tools(tools: list[dict]) -> list[dict]:
        """Convert MCP tool descriptors to OpenAI function-calling format."""
        adapted = []
        for t in tools:
            adapted.append(
                {
                    "type": "function",
                    "function": {
                        "name": t["name"],
                        "description": t.get("description", ""),
                        "parameters": t.get("input_schema") or {"type": "object", "properties": {}},
                    },
                }
            )
        return adapted

    async def chat(self, user_message: str) -> str:
        self._history.append({"role": "user", "content": user_message})

        while True:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=self._history,
                tools=self._tools,
                tool_choice="auto",
            )
            msg = response.choices[0].message

            # Append assistant turn (may contain tool_calls)
            self._history.append(msg.model_dump(exclude_unset=False))

            if not msg.tool_calls:
                return msg.content or ""

            # Execute each tool call and feed results back
            for tc in msg.tool_calls:
                fn_name = tc.function.name
                fn_args = json.loads(tc.function.arguments)
                logger.info("Calling MCP tool %s with %s", fn_name, fn_args)

                tool_result = await call_tool(self._session, fn_name, fn_args)

                self._history.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": tool_result,
                    }
                )

    def reset(self) -> None:
        self._history = [self._history[0]]  # keep system prompt
