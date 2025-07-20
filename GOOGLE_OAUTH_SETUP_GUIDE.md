# Google OAuth Setup Guide for Production

## Current Status: Development Mode
The application is currently running in **development mode** with mock Google API responses. This allows you to test the UI and functionality without configuring OAuth consent screen.

## To Enable Real Google API Access

### Step 1: Configure OAuth Consent Screen

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Select your project**: `ai-nexus-466121`
3. **Navigate to**: APIs & Services → OAuth consent screen

### Step 2: Basic Configuration

1. **User Type**: Choose "External" (unless you have Google Workspace)
2. **App Information**:
   - **App name**: `Prompt Fusion AI Nexus`
   - **User support email**: `aknbo30@gmail.com`
   - **Developer contact information**: `aknbo30@gmail.com`
   - **App domain**: `http://localhost:8081` (for development)
   - **Authorized domains**: `localhost`

### Step 3: Scopes Configuration

**For initial testing, start with basic scopes**:
- `../auth/userinfo.email`
- `../auth/userinfo.profile` 
- `openid`

**Once basic auth works, add these sensitive scopes**:
- `https://www.googleapis.com/auth/gmail.readonly`
- `https://www.googleapis.com/auth/gmail.send`
- `https://www.googleapis.com/auth/gmail.compose`
- `https://www.googleapis.com/auth/calendar`
- `https://www.googleapis.com/auth/calendar.events`

### Step 4: Test Users

Add these email addresses as test users:
- `aknbo30@gmail.com`
- Any other emails you want to test with

### Step 5: Publishing Status

For development: Keep in "Testing" mode
For production: Submit for verification (required for sensitive scopes)

## Code Changes Needed for Production

### 1. Update Authentication Context

Replace the mock authentication in `src/contexts/GoogleIntegrationContext.tsx`:

```typescript
// Replace the mock authentication with real OAuth flow
const authenticate = async () => {
  if (!manager) {
    setError('Google integration not initialized');
    return;
  }

  setIsLoading(true);
  setError(null);

  try {
    const tokens = await manager.authenticate(); // Real OAuth flow
    localStorage.setItem('google_tokens', JSON.stringify(tokens));
    setIsAuthenticated(true);
    updateStatus(manager);
  } catch (error) {
    console.error('Error during authentication:', error);
    setError('Failed to authenticate with Google');
  } finally {
    setIsLoading(false);
  }
};
```

### 2. Update Service Implementations

Replace mock implementations in:
- `src/services/google/gmail.ts`
- `src/services/google/calendar.ts`

With real API calls using `window.gapi.client`.

### 3. Environment Variables

Ensure these are set in your `.env` file:
```
VITE_GOOGLE_CLIENT_ID=your_actual_client_id
VITE_GOOGLE_CLIENT_SECRET=your_client_secret
VITE_GOOGLE_API_KEY=your_api_key
VITE_GOOGLE_REDIRECT_URI=http://localhost:8081/auth/google/callback
```

## Testing the OAuth Flow

1. **Start with basic scopes** (email, profile, openid)
2. **Test authentication** - should work without "Access blocked" error
3. **Gradually add sensitive scopes** (Gmail, Calendar)
4. **Add your email as test user** for each scope addition

## Common Issues

### "Access blocked" Error
- App not in testing mode
- User not added as test user
- Sensitive scopes without verification

### "Invalid client" Error
- Wrong client ID in environment variables
- Client ID doesn't match OAuth consent screen

### "Redirect URI mismatch"
- Authorized redirect URIs not configured
- URI in code doesn't match console settings

## Current Development Benefits

✅ **Test UI/UX** without OAuth complexity
✅ **Develop features** with predictable mock data  
✅ **Debug functionality** without API rate limits
✅ **Demo the application** to stakeholders

## Next Steps

1. **Test current demo mode** thoroughly
2. **Configure OAuth consent screen** when ready for real APIs
3. **Switch to production mode** by updating the authentication code
4. **Submit for verification** if using sensitive scopes in production

---

**Note**: The current mock implementation provides the same user experience as real APIs, making it perfect for development and testing!
