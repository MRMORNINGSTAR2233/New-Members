# OAuth Integration Guide

This guide explains how to set up real OAuth authentication for Google, Slack, and Jira integrations in ZenBox AI.

## 🔐 **OAuth Providers Supported**

### **1. Google OAuth**
- **Services**: Gmail, Google Calendar, Google Meet
- **Scopes**: Email, Calendar, Drive, Profile
- **Status**: ✅ Fully implemented with real API integration

### **2. Slack OAuth**
- **Services**: Team communication, channels, direct messages
- **Scopes**: Channels, chat, files, users, team
- **Status**: 🔧 OAuth flow implemented, API integration ready

### **3. Jira OAuth (Atlassian)**
- **Services**: Issue tracking, project management, workflows
- **Scopes**: Read/write Jira work, user access
- **Status**: 🔧 OAuth flow implemented, API integration ready

## 🚀 **Setup Instructions**

### **Step 1: Environment Configuration**

Copy the OAuth credentials to your `.env` file:

```bash
# Google OAuth (Already configured)
VITE_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
VITE_GOOGLE_CLIENT_SECRET=your-google-client-secret
VITE_GOOGLE_REDIRECT_URI=http://localhost:5173/auth/google/callback

# Slack OAuth
VITE_SLACK_CLIENT_ID=your-slack-client-id
VITE_SLACK_CLIENT_SECRET=your-slack-client-secret
VITE_SLACK_REDIRECT_URI=http://localhost:5173/auth/slack/callback

# Jira OAuth
VITE_JIRA_CLIENT_ID=your-jira-client-id
VITE_JIRA_CLIENT_SECRET=your-jira-client-secret
VITE_JIRA_REDIRECT_URI=http://localhost:5173/auth/jira/callback

# OAuth Mode
VITE_OAUTH_MODE=redirect
VITE_ENABLE_OAUTH_INTEGRATIONS=true
```

### **Step 2: Google OAuth Setup** ✅ (Already Done)

Your Google OAuth is already configured and working!

### **Step 3: Slack OAuth Setup**

1. **Go to Slack API**: https://api.slack.com/apps
2. **Create New App**: "From scratch"
3. **App Name**: "ZenBox AI"
4. **Workspace**: Select your workspace
5. **OAuth & Permissions**:
   - Add Redirect URL: `http://localhost:5173/auth/slack/callback`
   - Add Scopes:
     - `channels:read` - View basic information about public channels
     - `chat:write` - Send messages as ZenBox AI
     - `files:read` - View files shared in channels
     - `users:read` - View people in workspace
     - `team:read` - View basic information about workspace
6. **Install App**: Install to your workspace
7. **Copy Credentials**: Client ID and Client Secret to `.env`

### **Step 4: Jira OAuth Setup**

1. **Go to Atlassian Developer Console**: https://developer.atlassian.com/
2. **Create App**: "OAuth 2.0 (3LO)"
3. **App Details**:
   - Name: "ZenBox AI"
   - Description: "AI-powered productivity companion"
4. **OAuth 2.0 (3LO)**:
   - Callback URL: `http://localhost:5173/auth/jira/callback`
   - Scopes:
     - `read:jira-work` - Read project and issue data
     - `write:jira-work` - Create and edit issues
     - `read:jira-user` - Read user information
     - `offline_access` - Refresh tokens
5. **Distribution**: Enable for your organization
6. **Copy Credentials**: Client ID and Client Secret to `.env`

## 🔄 **OAuth Flow Process**

### **User Experience:**
1. **Click "Connect" button** for any tool (Slack, Jira)
2. **Redirect to provider** OAuth authorization page
3. **User grants permissions** to ZenBox AI
4. **Redirect back** to ZenBox AI with authorization code
5. **Exchange code for tokens** and store securely
6. **Show success message** and enable tool features

### **Technical Flow:**
```
1. User clicks Connect → 2. Generate OAuth URL → 3. Redirect to Provider → 
4. User Authorizes → 5. Callback with Code → 6. Exchange for Tokens → 
7. Store Tokens → 8. Update UI → 9. Enable Features
```

## 🎯 **Features Enabled After Connection**

### **Google Services** (Already Working):
- ✅ **Gmail**: Send emails, read messages, search
- ✅ **Calendar**: Create events, schedule meetings
- ✅ **Meet**: Generate meeting links, join calls

### **Slack Integration** (Ready for API):
- 📝 **Send Messages**: Post to channels and DMs
- 🔍 **Search Channels**: Find conversations and files
- 👥 **Team Info**: Access workspace and user data
- 📁 **File Sharing**: Upload and access shared files

### **Jira Integration** (Ready for API):
- 🎯 **Issue Management**: Create, update, search issues
- 📊 **Project Tracking**: View project status and progress
- 🏃 **Sprint Planning**: Manage sprints and backlogs
- 🔄 **Workflow Automation**: Trigger status changes

## 🛡️ **Security Features**

### **OAuth Security:**
- **State Parameter**: Prevents CSRF attacks
- **Secure Token Storage**: Encrypted local storage
- **Token Refresh**: Automatic token renewal
- **Scope Limitation**: Minimal required permissions

### **Data Protection:**
- **No Password Storage**: Only OAuth tokens
- **Encrypted Communication**: HTTPS only
- **Token Expiration**: Automatic cleanup
- **User Control**: Easy disconnect option

## 🧪 **Testing OAuth Integration**

### **Test Google (Already Working):**
1. Go to `/dashboard/integrations`
2. Click "All Tools" tab
3. Verify Google services show as connected
4. Test email/calendar actions in Global Search

### **Test Slack:**
1. Configure Slack OAuth credentials
2. Click "Connect" on Slack card
3. Complete OAuth flow
4. Verify connection status
5. Test Slack actions (when API is implemented)

### **Test Jira:**
1. Configure Jira OAuth credentials
2. Click "Connect" on Jira card
3. Complete OAuth flow
4. Verify connection status
5. Test Jira actions (when API is implemented)

## 🔧 **Development Notes**

### **OAuth Service Features:**
- **Multi-provider Support**: Extensible for new providers
- **Token Management**: Automatic refresh and storage
- **Error Handling**: Graceful failure recovery
- **State Management**: Secure flow validation

### **UI Components:**
- **Connection Status**: Real-time connection indicators
- **User Info Display**: Show connected account details
- **Error Messages**: Clear error communication
- **Loading States**: Smooth connection process

### **Callback Handling:**
- **Universal Callback**: Single component handles all providers
- **Error Recovery**: Retry and fallback options
- **Success Feedback**: Clear completion confirmation
- **Auto-redirect**: Return to integrations page

## 🚀 **Next Steps**

### **Immediate (Ready Now):**
1. ✅ **Google Integration**: Fully working with real APIs
2. 🔧 **OAuth Flows**: Complete for Slack and Jira
3. 🎨 **UI Components**: Professional connection management

### **API Implementation (Next Phase):**
1. **Slack API Service**: Implement message sending, channel search
2. **Jira API Service**: Implement issue management, project tracking
3. **Action Integration**: Connect OAuth tools to Global Search actions
4. **Real-time Sync**: Background data synchronization

### **Production Deployment:**
1. **Environment Variables**: Configure production OAuth apps
2. **Domain Setup**: Update redirect URIs for production domain
3. **SSL Certificates**: Ensure HTTPS for OAuth security
4. **Monitoring**: Track OAuth success rates and errors

## 🎉 **Current Status**

✅ **Google OAuth**: Fully implemented and working  
🔧 **Slack OAuth**: Flow complete, API integration ready  
🔧 **Jira OAuth**: Flow complete, API integration ready  
🎨 **UI/UX**: Professional connection management interface  
🛡️ **Security**: Enterprise-grade OAuth implementation  

The OAuth integration system is now ready for connecting multiple tools with secure, professional authentication flows!
