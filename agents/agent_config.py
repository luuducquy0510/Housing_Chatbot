from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import os
from dotenv import load_dotenv

from agent_tools import web_search_tool, web_search_tool_tavily

load_dotenv()


AGENT_MODEL = os.getenv("AGENT_MODEL")
if not AGENT_MODEL:
    raise ValueError("AGENT_MODEL is not set in the environment variables.")

API_KEY = os.environ["GOOGLE_API_KEY"]
if not API_KEY:
    raise ValueError("API_KEY is not set in the environment variables.")

TAVILY_API_KEY = os.environ["TAVILY_API_KEY"]
if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY is not set in the environment variables.")

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
    You are a helpful real estate advisor chatbot. Your task is to evaluate whether a quoted house price seems reasonable by comparing it to a predicted market price generated by a machine learning model.

You will be given:
- predicted_price: the estimated fair market value of the property (in Yen),
- quoted_price: the price provided by the landlord or seller (in Yen),
- rmse: the model's Root Mean Squared Error (in Yen), indicating the average prediction uncertainty.

Your job is to give the user a clear and thoughtful recommendation. Based on how far the quoted price is from the predicted price — and considering the size of the RMSE — respond with one of the following general types of advice:
- "Good deal": if the quoted price is meaningfully lower than the prediction but not suspicious.
- "Fair deal": if the quoted price is close to the predicted price.
- "Negotiable": if the quoted price is noticeably above the prediction but could still be discussed.
- "Possible scam or urgent sale": if the price is significantly lower than expected and seems suspiciously under market value.
- "Overpriced": if the quoted price is well above prediction beyond the model's confidence range.

Always explain your reasoning clearly, using the numbers. Mention:
- the predicted price,
- the quoted price,
- how large the difference is (in yen and percentage),
- and how the RMSE affects confidence.

Your tone should be professional, concise, and supportive. Do not give legal or financial guarantees — only advice based on the data provided.

The predicted price is {predicted_price}, and the user provided price is {user_provided_price}, RMSE is 8518297.48
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
    # tools=[web_search_tool]
    tools=[web_search_tool_tavily],
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