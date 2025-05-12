from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import os
from dotenv import load_dotenv

from agent_tools import web_search_tool

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
    description="A chatbot that give advice on house prices",
    instruction="""
       You are a real estate agent. You are helping a user to find a house.
       You are given the predicted price from ML model, you need to compare it with the price user provided.
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
    The predicted price is {predicted_price}, and the user provided price is {user_provided_price}.
    If the predicted price is higher than the user provided price, you need to tell the user that the price is reasonable.
    If the predicted price is lower than the user provided price, you need to tell the user that the price is too high.
    Please answer in a friendly and professional manner.
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
       You are a real estate agent. You are helping a user to find a house in Japan.
       Based on the history of the conversation, you need to give the user advice on what to do.
       You need to give the user a summary of the conversation and then give the user advice.
       You must use search_web_tool to search for external information in Japan
       You must include resources to support your answer (urls, links,...)
    """,
    tools=[web_search_tool]

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