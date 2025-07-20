# Google API Integration Setup Guide

This guide will help you set up Google API integrations for Gmail, Google Calendar, and Google Meet in your Prompt Fusion AI Nexus application.

## Prerequisites

- A Google account
- Access to Google Cloud Console
- Node.js and npm installed
- Your application running locally or deployed

## Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top of the page
3. Click "New Project"
4. Enter a project name (e.g., "Prompt Fusion AI Nexus")
5. Click "Create"

## Step 2: Enable Required APIs

1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for and enable the following APIs:
   - **Gmail API** - For email functionality
   - **Google Calendar API** - For calendar and meeting scheduling
   - **Google Drive API** - For file access (optional)

For each API:
1. Click on the API name
2. Click "Enable"
3. Wait for the API to be enabled

## Step 3: Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Choose "External" user type (unless you have a Google Workspace account)
3. Click "Create"
4. Fill in the required information:
   - **App name**: Prompt Fusion AI Nexus
   - **User support email**: aknbo30@gmail.com
   - **Developer contact information**: aknbo30@gmail.com
   - **App domain** (optional): http://localhost:8081
   - **Authorized domains**: localhost
5. Click "Save and Continue"

6. **IMPORTANT - Scopes Configuration**:
   - On the "Scopes" page, click "Add or Remove Scopes"
   - **For development, start with these basic scopes**:
     - `../auth/userinfo.email`
     - `../auth/userinfo.profile`
     - `openid`
   - **DO NOT add sensitive scopes initially** (Gmail, Calendar) until basic auth works
   - Click "Update" and then "Save and Continue"

7. **Test Users Configuration**:
   - Add test users: **aknbo30@gmail.com**
   - Add any other emails you want to test with
   - Click "Add Users" then "Save and Continue"

8. **Summary**: Review and click "Back to Dashboard"

## Step 4: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Choose "Web application" as the application type
4. Enter a name (e.g., "Prompt Fusion Web Client")
5. Add authorized JavaScript origins:
   - For development: `http://localhost:5173`
   - For production: `https://yourdomain.com`
6. Add authorized redirect URIs:
   - For development: `http://localhost:5173/auth/google/callback`
   - For production: `https://yourdomain.com/auth/google/callback`
7. Click "Create"
8. Copy the **Client ID** and **Client Secret** - you'll need these for your environment variables

## Step 5: Configure Environment Variables

1. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and add your Google API credentials:
   ```env
   VITE_GOOGLE_CLIENT_ID=your_actual_client_id_here
   VITE_GOOGLE_CLIENT_SECRET=your_actual_client_secret_here
   VITE_GOOGLE_REDIRECT_URI=http://localhost:5173/auth/google/callback
   VITE_GOOGLE_PROJECT_ID=your_project_id_here
   ```

## Step 6: Install Dependencies

The required Google API dependencies should already be installed. If not, run:

```bash
npm install googleapis google-auth-library @google-cloud/local-auth
```

## Step 7: Test the Integration

1. Start your development server:
   ```bash
   npm run dev
   ```

2. Open your application in the browser
3. Try using natural language commands like:
   - "Send an email to john@example.com with subject 'Test' and body 'Hello world'"
   - "Schedule a meeting tomorrow at 2 PM"
   - "Create a Google Meet for the team standup"

## Step 8: Publish Your App (Production)

For production use, you'll need to:

1. **Verify your domain** in Google Cloud Console
2. **Submit your app for verification** if you're requesting sensitive scopes
3. **Update your OAuth consent screen** to remove the "testing" status
4. **Add your production domain** to authorized origins and redirect URIs

## Troubleshooting

### Common Issues

1. **"This app isn't verified" warning**
   - This is normal during development
   - Click "Advanced" > "Go to [App Name] (unsafe)" to continue
   - For production, submit your app for Google verification

2. **"Access blocked" error**
   - Make sure all required APIs are enabled
   - Check that your redirect URI exactly matches what's configured in Google Cloud Console
   - Verify that your domain is added to authorized origins

3. **"Invalid client" error**
   - Double-check your Client ID and Client Secret in the `.env` file
   - Make sure there are no extra spaces or characters

4. **Scope errors**
   - Ensure all required scopes are added to your OAuth consent screen
   - Try re-authenticating to get the new scopes

### Testing Scopes

You can test individual scopes by using these example queries:

- **Gmail**: "Search for emails from john@example.com"
- **Calendar**: "Show my meetings for today"
- **Meet**: "Create an instant meeting"

## Security Best Practices

1. **Never commit your `.env` file** to version control
2. **Use environment-specific credentials** for development vs. production
3. **Regularly rotate your client secrets**
4. **Monitor API usage** in Google Cloud Console
5. **Implement proper error handling** for expired tokens
6. **Use HTTPS in production** for secure token exchange

## API Limits and Quotas

Be aware of Google API quotas:

- **Gmail API**: 1 billion quota units per day
- **Calendar API**: 1 million requests per day
- **Drive API**: 1 billion queries per day

Monitor your usage in the Google Cloud Console under "APIs & Services" > "Quotas".

## Support

If you encounter issues:

1. Check the [Google API documentation](https://developers.google.com/apis-explorer)
2. Review the [OAuth 2.0 documentation](https://developers.google.com/identity/protocols/oauth2)
3. Check the browser console for detailed error messages
4. Verify your API quotas haven't been exceeded

## Next Steps

Once you have Google integration working:

1. **Add more AI-powered features** like smart email categorization
2. **Implement calendar analytics** and meeting insights
3. **Add Google Drive integration** for document management
4. **Create workflow automation** between different Google services
5. **Add voice commands** for hands-free operation

Your Google API integration is now ready to use! The AI assistant can now help you manage emails, schedule meetings, and create Google Meet sessions through natural language commands.
