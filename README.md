# ZenBox AI

Your AI-powered productivity companion that unifies search, automation, and intelligence across all your favorite tools and platforms.

## Features

- 🔍 **Intelligent Search Interface** - Natural language search with AI-powered actions
- 📧 **Gmail Integration** - Send emails, search messages, and manage your inbox
- 📅 **Google Calendar** - Schedule meetings, manage events, and view your calendar
- 🎥 **Google Meet** - Create instant meetings and manage video calls
- 🤖 **AI Assistant** - Process natural language commands and automate workflows
- 🎨 **Modern UI** - Beautiful, responsive interface with dark/light mode
- 🔔 **Real-time Notifications** - Stay updated with action results and status changes
- 📊 **Analytics Dashboard** - Monitor usage and performance metrics

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd zenbox-ai
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up Google API credentials** (see [Google API Setup Guide](./GOOGLE_API_SETUP.md))
   ```bash
   cp .env.example .env
   # Edit .env with your Google API credentials
   ```

4. **Start the development server**
   ```bash
   npm run dev
   ```

5. **Open your browser** and navigate to `http://localhost:5173`

## 🤖 OpenAI Integration

ZenBox AI uses OpenAI's GPT models to analyze your search queries and provide intelligent suggestions.

### Setup:
1. Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Add to your `.env` file: `VITE_OPENAI_API_KEY=your-api-key-here`
3. Restart the development server

### Features:
- **Smart Query Analysis**: Automatically detects if your input is valid or gibberish
- **Task Classification**: Categorizes queries (email, calendar, search, meeting, etc.)
- **AI Suggestions**: Provides actionable steps and execution options
- **Confidence Scoring**: Shows how confident the AI is about understanding your request

### Example Queries:
- *"Send an email to john@example.com about the project update"*
- *"Schedule a team meeting for tomorrow at 2 PM"*
- *"Create a Google Meet for the quarterly review"*
- *"Find my calendar events for this week"*

## Google API Setup

For detailed instructions on setting up Google API integration, see the [Google API Setup Guide](./GOOGLE_API_SETUP.md).

### Quick Setup Summary:

1. Create a Google Cloud Project
2. Enable Gmail, Calendar, and Drive APIs
3. Configure OAuth consent screen
4. Create OAuth 2.0 credentials
5. Add credentials to your `.env` file

## Usage Examples

### Natural Language Commands

The AI assistant can understand and execute various commands:

**Email Actions:**
- "Send an email to john@example.com with subject 'Meeting Tomorrow'"
- "Search for emails from my manager"
- "Reply to the latest email from the team"

**Calendar Actions:**
- "Schedule a meeting tomorrow at 2 PM"
- "Create a team standup for next Monday"
- "Show my meetings for today"

**Google Meet Actions:**
- "Create an instant meeting"
- "Schedule a Google Meet for the presentation"
- "Create a video call with the team"

**Search Actions:**
- "Find all emails about the project"
- "Search my calendar for meetings with John"
- "Show me everything related to the quarterly review"

## Architecture

### Frontend
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **shadcn/ui** for UI components
- **React Router** for navigation
- **React Query** for data fetching

### Google Integration
- **Google APIs Client Library** for authentication
- **Gmail API** for email management
- **Google Calendar API** for calendar operations
- **Google Meet** integration via Calendar API

### State Management
- **React Context** for global state
- **Custom hooks** for Google services
- **Notification system** for real-time updates

## Project Structure

```
src/
├── components/           # Reusable UI components
│   ├── ui/              # shadcn/ui components
│   ├── SearchInterface.tsx
│   ├── IntegrationDashboard.tsx
│   └── NotificationCenter.tsx
├── contexts/            # React contexts
│   ├── GoogleIntegrationContext.tsx
│   ├── NotificationContext.tsx
│   └── ThemeContext.tsx
├── services/            # API services
│   └── google/          # Google API integrations
│       ├── auth.ts
│       ├── gmail.ts
│       ├── calendar.ts
│       ├── meet.ts
│       └── index.ts
├── pages/               # Page components
├── hooks/               # Custom hooks
└── lib/                 # Utilities
```

## Environment Variables

Create a `.env` file with the following variables:

```env
# Google API Configuration
VITE_GOOGLE_CLIENT_ID=your_google_client_id
VITE_GOOGLE_CLIENT_SECRET=your_google_client_secret
VITE_GOOGLE_REDIRECT_URI=http://localhost:5173/auth/google/callback
VITE_GOOGLE_PROJECT_ID=your_google_project_id
```

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript checks

### Adding New Integrations

1. Create a new service in `src/services/`
2. Add authentication logic
3. Create API methods
4. Update the integration context
5. Add UI components
6. Update the dashboard

## Deployment

### Production Build

```bash
npm run build
```

### Environment Setup

1. Update environment variables for production
2. Configure OAuth redirect URIs for your domain
3. Submit app for Google verification (if needed)
4. Deploy to your hosting platform

### Hosting Platforms

This app can be deployed to:
- **Vercel** (recommended)
- **Netlify**
- **AWS Amplify**
- **Google Cloud Platform**

## Security

- OAuth 2.0 for secure authentication
- Environment variables for sensitive data
- HTTPS required in production
- Token refresh handling
- Scope-based permissions

## Troubleshooting

### Common Issues

**"This app isn't verified" warning**
- Normal during development
- Click "Advanced" → "Go to [App Name] (unsafe)"
- Submit for verification in production

**Authentication errors**
- Check client ID and secret
- Verify redirect URI matches exactly
- Ensure APIs are enabled

**API quota exceeded**
- Monitor usage in Google Cloud Console
- Implement rate limiting
- Consider upgrading quotas

**Token expiration**
- Tokens are automatically refreshed
- Re-authenticate if refresh fails
- Check token storage

## Technologies Used

This project is built with:

- **Vite** - Fast build tool and dev server
- **TypeScript** - Type-safe JavaScript
- **React 18** - Modern React with hooks
- **shadcn/ui** - Beautiful UI components
- **Tailwind CSS** - Utility-first CSS framework
- **Google APIs** - Gmail, Calendar, Meet integration
- **React Query** - Data fetching and caching
- **React Router** - Client-side routing

---

Built with ❤️ using React, TypeScript, and Google APIs
