# AI Backend Integration Platform

A production-ready FastAPI backend that integrates with Gmail, Google Calendar, LangChain/LangGraph agents (powered by Gemini 1.5 Flash), ChromaDB for vector storage, and Slack/Jira webhooks.

## Project Structure

```
app/
  ├── main.py                # FastAPI application entry point
  ├── api/                   # API routes
  │   └── routes/            # Endpoint implementations
  │       ├── auth.py        # Authentication routes
  │       ├── calendar.py    # Calendar API routes
  │       ├── email.py       # Email API routes
  │       ├── jira.py        # Jira API routes
  │       └── slack.py       # Slack API routes
  ├── core/                  # Core application components
  │   └── config.py          # Configuration management
  ├── models/                # Pydantic data models
  │   ├── calendar.py        # Calendar data models
  │   ├── email.py           # Email data models
  │   ├── jira.py            # Jira data models
  │   └── slack.py           # Slack data models
  ├── services/              # Service integrations
  │   ├── agents/            # LangChain/LangGraph agents
  │   │   ├── calendar_agent.py  # Calendar integration
  │   │   ├── gmail_agent.py     # Gmail integration
  │   │   ├── jira_agent.py      # Jira integration
  │   │   ├── llm_agents.py      # LLM sub-agents
  │   │   └── slack_agent.py     # Slack integration
  │   ├── auth/              # Authentication services
  │   │   └── google_auth.py     # Google OAuth2 integration
  │   ├── llm/               # LLM integrations
  │   │   └── gemini_provider.py # Gemini API integration
  │   └── vector/            # Vector storage services
  │       └── chroma_service.py   # ChromaDB integration
  └── utils/                 # Utility functions
      └── audit_logger.py    # Audit logging functionality
```

## Setup Instructions

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   Copy the example.env file to .env and fill in your credentials:

   ```bash
   cp example.env .env
   # Edit .env with your preferred editor
   ```

5. **Run the application**

   ```bash
   python run.py
   ```

   This will start the server at http://localhost:8000 with auto-reload enabled.

## API Documentation

Once the server is running, you can access the automatic API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Security & Privacy Notes

### Security Best Practices

1. **HTTPS Enforcement**
   - Always use HTTPS in production to encrypt data in transit.
   - Configure your web server or reverse proxy (like Nginx) to handle TLS termination.
   - Redirect all HTTP traffic to HTTPS.

2. **OAuth2 Security**
   - Restrict Google OAuth redirect URIs to specific, controlled domains.
   - Store client secrets securely, never commit them to version control.
   - Implement PKCE (Proof Key for Code Exchange) for added security.

3. **API Authentication**
   - All endpoints should require proper authentication in production.
   - Implement JWT or session-based authentication for API users.
   - Use rate limiting to prevent abuse.

4. **Webhook Security**
   - Always verify Slack signature for all incoming webhooks.
   - Use secret tokens for Jira webhooks and validate them.
   - Implement IP allowlisting if possible.

### Privacy Considerations

1. **Data Storage**
   - Audit logs should be stored securely with access controls.
   - Consider encryption at rest for sensitive data.
   - Implement proper data retention and deletion policies.

2. **User Consent**
   - Ensure users understand what data is being accessed through OAuth.
   - Implement clear consent flows for email and calendar access.
   - Only request the minimum scopes needed for functionality.

3. **Data Handling**
   - Minimize storage of email content or calendar details.
   - Implement proper data minimization practices.
   - Consider anonymizing data when possible.

4. **LLM Security**
   - Be aware of prompt injection risks with LLMs.
   - Implement input validation and sanitization.
   - Monitor for sensitive data leakage in LLM inputs and outputs.
   - Use content filtering and safety settings in the Gemini API.

### Compliance

- Ensure compliance with relevant regulations like GDPR, CCPA, etc.
- Implement proper data subject access and deletion capabilities.
- Consider data sovereignty requirements for international deployments.