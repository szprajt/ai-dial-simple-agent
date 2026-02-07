import os

from task.client import DialClient
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role
from task.prompts import SYSTEM_PROMPT
from task.tools.users.create_user_tool import CreateUserTool
from task.tools.users.delete_user_tool import DeleteUserTool
from task.tools.users.get_user_by_id_tool import GetUserByIdTool
from task.tools.users.search_users_tool import SearchUsersTool
from task.tools.users.update_user_tool import UpdateUserTool
from task.tools.users.user_client import UserClient
from task.tools.web_search import WebSearchTool

DIAL_ENDPOINT = "https://ai-proxy.lab.epam.com"
API_KEY = os.getenv('DIAL_API_KEY')

def main():
    # 1. Create UserClient
    # UserClient uses USER_SERVICE_ENDPOINT constant defined in its module (http://localhost:8041)
    user_client = UserClient()

    # 2. Create DialClient with all tools
    tools = [
        WebSearchTool(api_key=API_KEY, endpoint=DIAL_ENDPOINT),
        GetUserByIdTool(user_client),
        SearchUsersTool(user_client),
        CreateUserTool(user_client),
        UpdateUserTool(user_client),
        DeleteUserTool(user_client)
    ]
    
    dial_client = DialClient(
        endpoint=DIAL_ENDPOINT,
        deployment_name="gpt-4", # Or whatever model you are using
        api_key=API_KEY,
        tools=tools
    )

    # 3. Create Conversation and add there first System message with SYSTEM_PROMPT
    conversation = Conversation()
    conversation.add_message(Message(role=Role.SYSTEM, content=SYSTEM_PROMPT))

    # 4. Run infinite loop
    print("Agent started. Type 'exit' to quit.")
    while True:
        try:
            user_input = input("> ").strip()
            if user_input.lower() in ["exit", "quit"]:
                break
            
            if not user_input:
                continue

            # Add User message to Conversation
            conversation.add_message(Message(role=Role.USER, content=user_input))

            # Call DialClient with conversation history
            response_message = dial_client.get_completion(conversation.messages)

            # Add Assistant message to Conversation and print its content
            conversation.add_message(response_message)
            print(f"Assistant: {response_message.content}")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()

# Request sample:
# Add Andrej Karpathy as a new user
