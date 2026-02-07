import json
from typing import Any

import requests

from task.models.message import Message
from task.models.role import Role
from task.tools.base import BaseTool


class DialClient:

    def __init__(
            self,
            endpoint: str,
            deployment_name: str,
            api_key: str,
            tools: list[BaseTool] | None = None
    ):
        if not api_key:
            raise ValueError("API key is required")
        
        self._endpoint = f"{endpoint}/openai/deployments/{deployment_name}/chat/completions"
        self._api_key = api_key
        
        self._tools_dict = {tool.name: tool for tool in tools} if tools else {}
        self._tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema
                }
            } for tool in tools
        ] if tools else []
        
        # Optional: print endpoint and tools schemas
        # print(f"Endpoint: {self._endpoint}")
        # print(f"Tools: {json.dumps(self._tools, indent=2)}")


    def get_completion(self, messages: list[Message], print_request: bool = True) -> Message:
        headers = {
            "api-key": self._api_key,
            "Content-Type": "application/json"
        }
        
        request_data = {
            "messages": [msg.to_dict() for msg in messages],
        }
        if self._tools:
            request_data["tools"] = self._tools

        if print_request:
            print("Request Messages:")
            for msg in messages:
                print(f"{msg.role}: {msg.content}")

        response = requests.post(self._endpoint, headers=headers, json=request_data)

        if response.status_code == 200:
            response_json = response.json()
            choice = response_json["choices"][0]
            
            # Optional: print choice
            # print(f"Choice: {json.dumps(choice, indent=2)}")
            
            message_data = choice["message"]
            content = message_data.get("content")
            tool_calls = message_data.get("tool_calls")
            
            ai_response = Message(role=Role.ASSISTANT, content=content, tool_calls=tool_calls)
            
            if choice["finish_reason"] == "tool_calls":
                messages.append(ai_response)
                tool_messages = self._process_tool_calls(tool_calls)
                messages.extend(tool_messages)
                return self.get_completion(messages, print_request)
            else:
                return ai_response
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")


    def _process_tool_calls(self, tool_calls: list[dict[str, Any]]) -> list[Message]:
        """Process tool calls and add results to messages."""
        tool_messages = []
        for tool_call in tool_calls:
            tool_call_id = tool_call["id"]
            function = tool_call["function"]
            function_name = function["name"]
            arguments = json.loads(function["arguments"])
            
            tool_execution_result = self._call_tool(function_name, arguments)
            
            tool_messages.append(Message(
                role=Role.TOOL,
                name=function_name,
                tool_call_id=tool_call_id,
                content=tool_execution_result
            ))
            
            print(f"FUNCTION '{function_name}'\n{tool_execution_result}\n{'-'*50}")

        return tool_messages

    def _call_tool(self, function_name: str, arguments: dict[str, Any]) -> str:
        tool = self._tools_dict.get(function_name)
        if tool:
            return tool.execute(arguments)
        else:
            return f"Unknown function: {function_name}"
