from typing import Any

from task.tools.users.base import BaseUserServiceTool


class SearchUsersTool(BaseUserServiceTool):

    @property
    def name(self) -> str:
        return "search_users"

    @property
    def description(self) -> str:
        return "Search for users based on various criteria."

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "First name of the user."
                },
                "surname": {
                    "type": "string",
                    "description": "Last name of the user."
                },
                "email": {
                    "type": "string",
                    "description": "Email address of the user."
                },
                "gender": {
                    "type": "string",
                    "description": "Gender of the user."
                }
            }
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        try:
            return str(self.user_client.search_users(**arguments))
        except Exception as e:
            return f"Error while searching users: {str(e)}"
