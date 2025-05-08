from google.adk.agents import LlmAgent
import asyncio
from dotenv import load_dotenv
from .tools import get_notion_tools, init_notion_tools


load_dotenv()


root_agent = LlmAgent(
    model="gemini-2.0-flash-001", 
    name="notion_assistant",
    description="Assistant that helps manage Notion workspaces",
    instruction="You are an assistant that helps users manage their Notion workspace. Use the tools available to you to interact with Notion databases and pages.",
    tools=get_notion_tools()
)

async def initialize_agent(callback_context=None, **kwargs):
    await init_notion_tools()
    root_agent.tools = get_notion_tools()
    print("Agent tools updated with Notion tools")

# Create a wrapper function that can be called synchronously
def initialize_agent_wrapper(callback_context=None, **kwargs):
    try:
        loop = asyncio.get_event_loop()
        asyncio.create_task(initialize_agent(callback_context, **kwargs))
    except RuntimeError:
        asyncio.run(initialize_agent(callback_context, **kwargs))

# Register the wrapper function as the callback
root_agent.before_agent_callback = initialize_agent_wrapper