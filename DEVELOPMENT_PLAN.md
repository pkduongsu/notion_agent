# Notion Agent Development Plan

## 1. Project Overview

The goal is to create an intelligent agent that integrates with Notion and Google Calendar. The agent will assist users by:
- Providing reminders and follow-ups for important tasks and deadlines.
- Enabling quick search and summarization of content within Notion.
- Allowing for quick input and modification of data in Notion.

This plan focuses on the agent's core functionality first, followed by the development of a simple web UI as a proof of concept.

## 2. Core Technologies

- **Backend:** Python
- **AI/LLM Framework:** Langchain
- **Notion Integration:** Notion API (via `notion-client` Python library or direct HTTP requests)
- **Google Calendar Integration:** Google Calendar API (via `google-api-python-client`)
- **Web UI (PoC):** Flask (for backend API) and HTML/CSS/JavaScript (for frontend), or Streamlit for a simpler UI.

## 3. Development Phases

### Phase 1: Core Agent Functionality (Python Backend)

#### 3.1. Setup and Authentication (Est. 1-2 days)
   - **3.1.1. Notion API Setup:**
      - Create a Notion integration and obtain an API key.
      - Define necessary permissions for the integration (read, write, comment).
      - Securely store API credentials (e.g., using environment variables, `.env` file).
   - **3.1.2. Google Calendar API Setup:**
      - Create a Google Cloud Platform (GCP) project.
      - Enable the Google Calendar API.
      - Set up OAuth 2.0 credentials (client ID and client secret).
      - Implement OAuth 2.0 flow for user authorization and token storage/refresh.
      - Securely store API credentials.
   - **3.1.3. Project Environment:**
      - Set up a Python virtual environment.
      - Install core dependencies: `langchain`, `langchain-google-genai` (or other LLM provider), `notion-client`, `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`, `python-dotenv`.
      - Initialize project structure (e.g., `agent/`, `core/`, `utils/`, `tests/`).

#### 3.2. Notion Integration (Est. 3-5 days)
   - **3.2.1. Notion Client Wrapper:**
      - Develop a Python module (`notion_handler.py`) to encapsulate Notion API interactions.
      - Functions to:
         - List databases.
         - Query databases (with filtering and sorting).
         - Retrieve page content.
         - Create new pages/database entries.
         - Update existing pages/database entries.
   - **3.2.2. Quick Search Functionality:**
      - Implement a function that takes a search query and searches relevant Notion databases/pages.
      - Consider strategies for efficient searching (e.g., targeting specific databases, using Notion's search endpoint).
   - **3.2.3. Summarization Functionality:**
      - Integrate Langchain's summarization chains (e.g., `load_summarize_chain` with `map_reduce` or `refine` strategies).
      - Develop a function that takes Notion page content (or search results) and returns a concise summary.
   - **3.2.4. Quick Input/Modification Functionality:**
      - Design a structured way for the agent to understand input/modification requests (e.g., "Create a task 'X' in database 'Y' with due date 'Z'").
      - Implement functions to parse these requests and interact with the `notion_handler.py` to perform create/update operations.

#### 3.3. Google Calendar Integration (Est. 2-3 days)
   - **3.3.1. Google Calendar Client Wrapper:**
      - Develop a Python module (`calendar_handler.py`) to encapsulate Google Calendar API interactions.
      - Functions to:
         - List calendars.
         - Fetch events from specified calendars within a date range.
         - Create new events.
         - Update existing events.
   - **3.3.2. Task/Deadline Identification:**
      - Implement logic to fetch upcoming events that represent tasks or deadlines.
      - Allow configuration for which calendars to monitor.
   - **3.3.3. Reminder/Follow-Up Logic:**
      - Develop a mechanism to determine when a reminder or follow-up is due (e.g., X days/hours before the event).
      - This could be a scheduled job (using `apscheduler` or similar) or triggered on demand.

#### 3.4. Langchain Agent Implementation (Est. 3-4 days)
   - **3.4.1. Define Tools:**
      - Create Langchain `Tool` objects for each core functionality:
         - `NotionSearchTool`: Uses the Notion search function.
         - `NotionSummarizeTool`: Uses the Notion summarization function.
         - `NotionCreateTool`: Uses the Notion input function.
         - `NotionUpdateTool`: Uses the Notion modification function.
         - `GetCalendarEventsTool`: Uses the Google Calendar fetching function.
         - `CreateCalendarEventTool`: Uses the Google Calendar event creation function.
   - **3.4.2. Agent Initialization:**
      - Choose an appropriate agent type (e.g., ReAct, OpenAI Functions Agent if applicable, or a custom agent).
      - Initialize the agent with the LLM (e.g., Google's Gemini via `ChatGoogleGenerativeAI`) and the defined tools.
   - **3.4.3. Prompt Engineering:**
      - Develop effective system prompts and user prompts to guide the agent's behavior.
      - Ensure the agent can understand natural language requests related to its capabilities (reminders, search, summarization, input/modification).
      - Handle ambiguous requests and ask clarifying questions if necessary.
   - **3.4.4. Agent Core Logic (`agent.py`):**
      - Main script to load configurations, initialize the agent, and process user input.

### Phase 2: Simple Web UI (Proof of Concept) (Est. 3-5 days)

#### 3.5. Backend API (Flask)
   - **3.5.1. API Endpoints:**
      - `/api/agent/query`:
         - Method: POST
         - Input: `{ "query": "user's natural language request" }`
         - Output: `{ "response": "agent's response", "data": "optional_structured_data" }`
         - This endpoint will pass the query to the Langchain agent.
      - `/api/reminders`: (Optional, for proactive display)
         - Method: GET
         - Output: `{ "reminders": [ { "title": "...", "due_date": "...", "source": "Notion/Calendar" } ] }`
   - **3.5.2. Flask App Setup (`app.py`):**
      - Basic Flask application structure.
      - Integration with the agent logic from Phase 1.

#### 3.6. Frontend (HTML, CSS, JavaScript or Streamlit)
   - **Option A: Flask with HTML/CSS/JS**
      - **3.6.1. Basic UI Structure (`templates/index.html`):**
         - Input field for user queries.
         - Display area for agent responses and data.
         - (Optional) Section for reminders.
      - **3.6.2. JavaScript for API Interaction (`static/js/main.js`):**
         - Fetch requests to the Flask API endpoints.
         - Dynamically update the UI with responses.
   - **Option B: Streamlit**
      - **3.6.1. Streamlit App (`streamlit_app.py`):**
         - Use Streamlit components (`st.text_input`, `st.write`, `st.chat_message`) to create the UI.
         - Directly call agent functions from within the Streamlit script. This simplifies the frontend-backend separation for a PoC.

#### 3.7. Deployment (Local)
   - Instructions on how to set up and run the Flask/Streamlit application locally.
   - Include details on managing API keys and environment variables for the web app.

## 4. Key Deliverables

- Python-based agent core with Langchain.
- Integration modules for Notion and Google Calendar.
- A set of Langchain tools for agent functionalities.
- A simple web UI (Flask or Streamlit) demonstrating the agent's capabilities.
- `requirements.txt` for dependencies.
- `README.md` with setup and usage instructions.
- This `DEVELOPMENT_PLAN.md`.

## 5. Potential Challenges & Mitigations

- **API Rate Limits:**
   - Implement respectful API usage (e.g., caching, exponential backoff for retries).
- **Complex User Queries:**
   - Iterative prompt engineering and potentially using more advanced Langchain features (e.g., routers, chains of thought) to handle complex requests.
- **Authentication Flow:**
   - Google OAuth can be complex. Start with a simpler flow (e.g., manual token pasting for PoC if necessary) and refine.
- **Data Security:**
   - Emphasize secure storage of API keys and user tokens from the beginning.
- **Scope Creep:**
   - Stick to the defined functionalities for the PoC. Further enhancements can be planned for later versions.

## 6. Timeline (Estimates)

- **Phase 1 (Core Agent):** 9 - 14 days
- **Phase 2 (Web UI PoC):** 3 - 5 days
- **Total Estimated Time:** 12 - 19 days (This is a rough estimate and can vary based on complexity and developer experience).

This plan provides a structured approach to developing the Notion agent. Each step will involve coding, testing, and iteration.