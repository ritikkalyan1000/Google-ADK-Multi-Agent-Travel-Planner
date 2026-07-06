import requests
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from dotenv import load_dotenv

from google.adk.runners import Runner
from google.genai import types
import asyncio

from google.adk.models.lite_llm import LiteLlm

load_dotenv()


session_id = "user_session_1"
user_id = "user_anonymous_1"
app_name = "planning_application"


def weather_details(city: str) -> dict:
    """
    Return the weather information for a specific city
    """
    url = f"https://wttr.in/{city}?format=j1"
    response = requests.get(url)

    return response.json()


# abc = weather_details("toronto")
# print(abc)

weather_agent = LlmAgent(
    name="weather_agent",
    # model="gemini-2.5-flash",
    model=LiteLlm(model="openai/gpt-4o-mini"),
    description="tell the weather details of a city",
    instruction="you are helpful assistant and have access to weather details using tools. so if user ask question related to weather then you use the tool to answer the user query",
    tools=[weather_details],
)
search_agent = LlmAgent(
    name="search_agent",
    model="gemini-2.5-flash",
    # model=LiteLlm(model="openai/gpt-4o-mini"),
    description="you have capability to go online to fetch details about any topic using google search",
    instruction="""
    You are a Google Search specialist.
    Use Google Search when the user asks about current events, places, attractions,
    opening hours, latest information, or anything that may change over time.
    Return a short and useful summary.
    """,
    tools=[google_search],
)

search_tool = AgentTool(agent=search_agent)

root_agent = LlmAgent(
    name="root_planner_agent",
    # model="gemini-2.5-flash",
    model=LiteLlm(model="openai/gpt-4o-mini"),
    instruction="you are helpful planner assistant and have access to sub agents which have ability to provide you weather details and also google search to know more about things asked by user so to plan comfortably",
    sub_agents=[weather_agent],
    tools=[search_tool],
)


async def main():

    session_service = InMemorySessionService()

    await session_service.create_session(
        session_id=session_id, user_id=user_id, app_name=app_name
    )

    # understanding the sessions params
    print("####################S")
    list_of_sessions = await session_service.list_sessions(
        app_name=app_name, user_id=user_id
    )
    for session in list_of_sessions:
        print(session)
    print("####################E")

    runner = Runner(
        agent=root_agent,
        session_service=session_service,
        app_name=app_name,
    )

    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            print("exiting the application")
            break

        print(user_input)

        content = types.Content(role="user", parts=[types.Part(text=user_input)])

        events = runner.run_async(
            user_id=user_id, session_id=session_id, new_message=content
        )

        async for event in events:
            print(event)

            if event.content and event.content.parts:

                text = event.content.parts[0].text
                print(text)
                if event.is_final_response():
                    print("final response ", text)

        print("####################S")
        list_of_sessions = await session_service.list_sessions(
            app_name=app_name, user_id=user_id
        )
        for session in list_of_sessions:
            print(session)

        print("####################E")


if __name__ == "__main__":
    asyncio.run(main())
