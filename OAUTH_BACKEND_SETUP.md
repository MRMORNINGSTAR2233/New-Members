# Backend Setup Guide for OAuth Integration

## Required Endpoints for OAuth

To make OAuth work correctly with Google and other providers, your backend needs to implement these endpoints:

### Google OAuth Endpoints

1. **POST /api/auth/google/token** or **POST /api/auth/google/callback**
   
   This endpoint exchanges the authorization code for tokens.
   
   Request:
   ```json
   {
     "code": "4/0AVMBsJ...",
     "redirect_uri": "http://localhost:8000/auth/google/callback"
   }
   ```
   
   Response:
   ```json
   {
     "access_token": "ya29.a0AfB_...",
     "token_type": "Bearer",
     "expires_in": 3599,
     "refresh_token": "1//0ghwX..."
   }
   ```

### Redirect URIs Registered with Google

Make sure these URIs are registered in your Google Cloud Console:

- http://localhost:8000/auth/google/callback
- http://localhost:5173/auth/google/callback
- http://localhost:3000/auth/google/callback

## Quick Fix for Python Backend

If using Flask, add these routes to your main.py:

```python
@app.route('/api/auth/google/token', methods=['POST'])
def google_token_exchange():
    data = request.json
    code = data.get('code')
    redirect_uri = data.get('redirect_uri')
    
    # Exchange code for token using Google's OAuth API
    token_url = 'https://oauth2.googleapis.com/token'
    token_data = {
        'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
        'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
        'code': code,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    
    response = requests.post(token_url, data=token_data)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': 'Token exchange failed', 'details': response.text}, response.status_code
```

If using FastAPI:

```python
@app.post("/api/auth/google/token")
async def google_token_exchange(request: GoogleTokenRequest):
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
        "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
        "code": request.code,
        "redirect_uri": request.redirect_uri,
        "grant_type": "authorization_code"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=token_data)
        
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Token exchange failed: {response.text}"
        )
```
