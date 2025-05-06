from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
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

house_price_agent = Agent(
    name="house_price_agent",
    model=AGENT_MODEL,
    description="A chatbot that give advice on house prices, where the price is reasonable.",
    instruction="""
        You are a real estate agent in Japan. You are helping a user to find a house in Japan.
        You are given the predicted price from ML model, you need to compare it with the price user provided.
        If the predicted price is significantly higher than the user provided price, you need to tell the user that the price is too high.
        If the predicted price is significantly lower than the user provided price, you need to tell the user that this may be a scam, and be careful.
        If the predicted price is in reasonable range, you need to tell the user that the price is reasonable.
        Show the user the predicted price and the user provided price.
    """,
    )


session_service = InMemorySessionService()
price_runner = Runner(
    agent=house_price_agent,
    app_name="House_price_chatbot",
    session_service=session_service
)
USER_ID = "user_1"
SESSION_ID = "session_1"


async def execute(predicted_price: float, user_provided_price: float):
    session_service.create_session(
        app_name="House_price_chatbot",
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    prompt = f"""
    The predicted price is {predicted_price}, and the price user recieved from the landlord is {user_provided_price}.
    Please tell the user if the price is reasonable.
    """
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    async for event in price_runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
        if event.is_final_response():
            response_text = event.content.parts[0].text
            yield response_text


housing_agent = Agent(
    name="housing_agent",
    model=AGENT_MODEL,
    description="A chatbot that give advice on house prices, what to do at the current situation.",
    instruction="""
        You are a real estate agent in Japan. You are helping a user to find a house in Japan.
        Based on the history of the conversation, you need to give the user advice on what to do.
        You can use the google search tool to find the information you need.""",
    tools = [google_search],
)

housing_runner = Runner(
    agent=housing_agent,
    app_name="housing_agent",
    session_service=session_service
)

async def follow_up(prompt: str):
    session_service.create_session(
        app_name="housing_agent",
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    prompt = f"""
    The user asked: {prompt}
    """
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    async for event in housing_runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
        if event.is_final_response():
            response_text = event.content.parts[0].text
            yield response_text