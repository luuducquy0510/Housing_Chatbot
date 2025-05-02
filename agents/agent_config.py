from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import os
from dotenv import load_dotenv
load_dotenv()


AGENT_MODEL = os.getenv("AGENT_MODEL")
if not AGENT_MODEL:
    raise ValueError("AGENT_MODEL is not set in the environment variables.")
API_KEY = os.environ["GOOGLE_API_KEY"]
if not API_KEY:
    raise ValueError("API_KEY is not set in the environment variables.")

healthcare_agent = Agent(
    name="healthcare_agent",
    model=AGENT_MODEL,
    description="A healthcare agent that provides information about medical conditions, symptoms, and treatments.",
    instruction="""
        You are a healthcare agent. Your task is to provide information about medical conditions, symptoms, and treatments.
        You should answer questions related to healthcare and provide relevant information to the user.
        You will be given classification form ML output, and you should provide a response based on the classification.
    """,
    # tools=[web_search_tool]
)


session_service = InMemorySessionService()
runner = Runner(
    agent=healthcare_agent,
    app_name="healthcare_chatbot",
    session_service=session_service
)
USER_ID = "user_1"
SESSION_ID = "session_1"


async def execute(request):
    session_service.create_session(
        app_name="healthcare_chatbot",
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    prompt = f"""
        Nothing for now
    """
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
        if event.is_final_response():
            response_text = event.content.parts[0].text
            yield response_text