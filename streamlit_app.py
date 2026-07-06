import asyncio
import uuid
import requests
import streamlit as st
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService

# from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from google.adk.runners import Runner
from google.genai import types
from google.adk.models.lite_llm import LiteLlm
from langchain_community.tools import TavilySearchResults

load_dotenv()


APP_NAME = "planning_application"
USER_ID = "streamlit_user"


def tavily_search(query: str) -> dict:
    """
    Return the search results for a specific query using Tavily API
    """
    tavily_tool = TavilySearchResults(max_results=3)

    result = tavily_tool.invoke({"query": query})

    return result


def weather_details(city: str) -> dict:
    """
    Return the weather information for a specific city.
    """
    try:
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()

    except requests.RequestException as e:
        return {
            "error": f"Could not fetch weather details for {city}. Reason: {str(e)}"
        }


def create_agents():
    weather_agent = LlmAgent(
        name="weather_agent",
        model=LiteLlm(model="openai/gpt-4o-mini"),
        description="Tell the weather details of a city.",
        instruction="""
        You are a helpful weather assistant.
        If the user asks anything related to weather, use the weather_details tool.
        Give a short and useful weather summary.
        """,
        tools=[weather_details],
    )

    search_agent = LlmAgent(
        name="search_agent",
        # model="gemini-2.5-flash",
        model=LiteLlm(model="openai/gpt-4o-mini"),
        description="Search online for current information using tavily Search.",
        instruction="""
        You are a Google Search specialist.
        Use tavily Search when the user asks about current events, places,
        attractions, opening hours, latest information, or anything that may change over time.
        Return a short and useful summary.
        """,
        tools=[tavily_search],
    )

    search_tool = AgentTool(agent=search_agent)

    root_agent = LlmAgent(
        name="root_planner_agent",
        model=LiteLlm(model="openai/gpt-4o-mini"),
        instruction="""
        You are a helpful planning assistant.

        You can help users plan trips, activities, and general tasks.
        You have access to:
        1. A weather agent for weather-related questions.
        2. A search agent tool for current online information.

        Use the correct tool or agent when needed.
        Give clear and practical answers.
        """,
        sub_agents=[weather_agent],
        tools=[search_tool],
    )

    return root_agent


async def initialize_adk():
    session_service = InMemorySessionService()

    session_id = str(uuid.uuid4())

    await session_service.create_session(
        session_id=session_id,
        user_id=USER_ID,
        app_name=APP_NAME,
    )

    root_agent = create_agents()

    runner = Runner(
        agent=root_agent,
        session_service=session_service,
        app_name=APP_NAME,
    )

    return runner, session_id


async def call_agent_async(user_message: str):
    content = types.Content(
        role="user",
        parts=[types.Part(text=user_message)],
    )

    events = st.session_state.runner.run_async(
        user_id=USER_ID,
        session_id=st.session_state.session_id,
        new_message=content,
    )

    final_response = ""

    async for event in events:
        if event.content and event.content.parts:
            text = event.content.parts[0].text

            if event.is_final_response():
                final_response = text

    return final_response


def run_async_task(coro):
    return asyncio.run(coro)


st.set_page_config(
    page_title="Google ADK Planner Agent",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 Google ADK Multi-Agent Planner")
st.caption("Travel planning assistant with weather and Google Search support")


if "runner" not in st.session_state:
    runner, session_id = run_async_task(initialize_adk())
    st.session_state.runner = runner
    st.session_state.session_id = session_id

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi! I can help you plan trips, check weather, and search current information.",
        }
    ]


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


user_input = st.chat_input("Ask me something...")

if user_input:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input,
        }
    )

    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = run_async_task(call_agent_async(user_input))

                if not response:
                    response = "I could not generate a final response."

            except Exception as e:
                response = f"Error: {str(e)}"

            st.write(response)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
        }
    )
