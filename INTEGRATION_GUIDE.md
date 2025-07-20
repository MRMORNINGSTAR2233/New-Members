# Test-Agents Integration Guide

This guide explains how the Global Search Page is integrated with the Test-Agents backend for real Google services (Gmail, Calendar, Meet) actions.

## Overview

The integration connects the React frontend with the Test-Agents Express backend to enable real action execution for:
- **Gmail Actions**: Send emails, read emails, compose messages
- **Calendar Actions**: Schedule meetings, check availability, create events
- **Meet Actions**: Create Google Meet links, schedule video calls
- **Orchestrator Actions**: Complex workflows combining multiple services

## Architecture

```
React Frontend (Global Search Page)
    ↓
TestAgentsService (HTTP Client)
    ↓
Test-Agents Backend (Express Server)
    ↓
Google APIs (Gmail, Calendar, Meet)
```

## Components

### 1. TestAgentsService (`src/services/testAgentsService.ts`)
- HTTP client for communicating with the Test-Agents backend
- Handles action execution, quick actions, and status checks
- Provides error handling and fallback to demo mode

### 2. GlobalSearchPage (`src/pages/GlobalSearchPage.tsx`)
- Main page component with backend integration
- Checks backend availability on mount
- Routes actions to real backend or demo mode

### 3. ActionExecutionFlow (`src/components/ActionExecutionFlow.tsx`)
- Enhanced to support real backend execution
- Shows real-time progress for backend actions
- Falls back to demo mode if backend unavailable

### 4. GlobalSearchInterface (`src/components/GlobalSearchInterface.tsx`)
- Updated with Google-specific quick actions
- Trending tasks with priority and agent routing
- Backend status indicator

### 5. BackendStatus (`src/components/BackendStatus.tsx`)
- Shows connection status to Test-Agents backend
- Displays available agents and authorization status
- Provides connection testing and refresh

## Quick Actions

The interface provides these quick actions that connect to real Google services:

1. **Send project update email** → Gmail Agent
2. **Schedule team meeting** → Calendar Agent  
3. **Create Google Meet for standup** → Calendar Agent (with Meet)
4. **Read recent emails** → Gmail Agent
5. **Check today's schedule** → Calendar Agent
6. **Daily briefing** → Orchestrator Agent

## Trending Tasks

AI-suggested tasks with priority levels and agent routing:

- **High Priority**: Urgent emails, important meetings
- **Medium Priority**: Regular tasks, planning activities  
- **Low Priority**: Appreciation emails, optional tasks

Each task is automatically routed to the appropriate agent (Gmail, Calendar, or Orchestrator).

## Backend Integration

### Starting the Test-Agents Backend

1. Navigate to the Test-Agents directory:
   ```bash
   cd public/Test-Agents
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the server:
   ```bash
   npm start
   ```

The backend will be available at `http://localhost:3000`.

### Backend Endpoints Used

- `GET /health` - Health check
- `GET /api/agents/status` - Agent status and authorization
- `GET /api/agents/capabilities` - Available agent capabilities
- `POST /api/agents/execute` - Execute actions
- `POST /api/agents/quick/{action}` - Quick actions
- `POST /api/agents/chat` - Natural language processing

### Authentication

The backend handles Google OAuth authentication for:
- Gmail API access
- Google Calendar API access
- Google Meet integration

## Demo vs Live Mode

### Demo Mode (Backend Unavailable)
- Uses mock data and simulated responses
- No real Google API calls
- Instant execution with fake results

### Live Mode (Backend Available)
- Real Google API integration
- Actual email sending and calendar management
- Real-time execution with progress tracking

## Error Handling

The integration includes comprehensive error handling:

1. **Connection Errors**: Falls back to demo mode
2. **Authentication Errors**: Shows auth required messages
3. **API Errors**: Displays specific error messages
4. **Timeout Errors**: Provides retry options

## Testing

Use the test utilities to verify the integration:

```typescript
import { testBackendConnection, runAllBackendTests } from '@/utils/testBackendConnection';

// Test connection
const result = await testBackendConnection();

// Run all tests
const allResults = await runAllBackendTests();
```

## Monitoring

The BackendStatus component provides real-time monitoring:
- Connection status
- Available agents
- Authorization status
- Error messages and troubleshooting

## Troubleshooting

### Backend Not Available
- Ensure Test-Agents server is running on port 3000
- Check network connectivity
- Verify no firewall blocking

### Authentication Issues
- Complete Google OAuth setup in Test-Agents
- Check API credentials and scopes
- Verify user permissions

### Action Failures
- Check backend logs for detailed errors
- Verify Google API quotas and limits
- Ensure proper service account setup

## Future Enhancements

Planned improvements:
- Real-time action progress streaming
- Batch action execution
- Advanced error recovery
- Performance monitoring
- Action history and analytics
