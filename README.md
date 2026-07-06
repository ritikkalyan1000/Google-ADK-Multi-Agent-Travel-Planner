# Google-ADK-Multi-Agent-Travel-Planner
Built a multi-agent planning assistant using Google ADK, LiteLLM, OpenAI GPT-4o Mini, Google Search, and a custom weather API tool to support real-time trip planning and weather-aware recommendations.


@"
# Google ADK Multi-Agent Travel Planner

This is a small multi-agent AI assistant built using Google Agent Development Kit. The project uses a root planner agent, a weather agent, and a Google Search agent to help users with travel planning, weather-related questions, and current information.

## Project Overview

The main goal of this project is to understand how multi-agent systems work in Google ADK. The application uses different agents for different responsibilities and connects them through a root planning agent.

The root agent acts as the main assistant. It receives the user query and decides whether to use the weather agent or the search agent tool.

## Features

- Built with Google Agent Development Kit
- Uses a root planner agent
- Uses a custom weather function tool
- Uses Google Search through a specialist search agent
- Uses AgentTool to connect another agent as a tool
- Uses LiteLLM to run OpenAI GPT-4o Mini
- Uses InMemorySessionService for session handling
- Uses Runner to execute the agent
- Supports async conversation flow
- Can be extended with a Streamlit frontend

## Agents Used

### Root Planner Agent

The root planner agent is the main agent of the application. It handles the user query and has access to the weather agent and search agent tool.

### Weather Agent

The weather agent uses a custom Python function called `weather_details`. This function calls the wttr.in weather API and returns weather information for a city.

### Search Agent

The search agent uses the Google Search tool. It is used when the user asks about current information, places, attractions, opening hours, or anything that may change over time.

## Tech Stack

- Python
- Google ADK
- LiteLLM
- OpenAI GPT-4o Mini
- Google Search Tool
- wttr.in Weather API
- dotenv
- asyncio
- Streamlit

## How the Code Works

1. The application loads environment variables using `dotenv`.
2. A custom weather tool is created using a Python function.
3. A weather agent is created and connected with the weather tool.
4. A search agent is created and connected with Google Search.
5. The search agent is converted into a tool using `AgentTool`.
6. A root planner agent is created.
7. The application creates an in-memory session using `InMemorySessionService`.
8. The `Runner` runs the root agent.
9. The user can ask questions in a loop.
10. The final response is printed in the terminal.

## Setup

Clone the repository:

```bash
git clone https://github.com/ritikkalyan1000/Google-ADK-Multi-Agent-Travel-Planner.git
cd Google-ADK-Multi-Agent-Travel-Planner
