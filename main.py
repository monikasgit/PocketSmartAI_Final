import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Form, File, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from gemini_utils import generate_recommendations

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="PocketSmart AI", description="Smart budget and recommendation assistant")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": None, "error": None})


@app.post("/recommend", response_class=HTMLResponse)
async def recommend(
    request: Request,
    planner: str = Form(...),
    budget: float = Form(...),
    preferences: str = Form(""),
    guests: Optional[int] = Form(None),
    event_type: str = Form(""),
    room_type: str = Form(""),
    occasion: str = Form(""),
    style: str = Form(""),
    outfit_image: Optional[UploadFile] = File(None),
):
    if budget <= 0:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "result": None, "error": "Please enter a budget greater than 0."},
            status_code=400,
        )

    image_bytes = None
    image_mime = None
    if outfit_image and outfit_image.filename:
        image_bytes = await outfit_image.read()
        image_mime = outfit_image.content_type or "image/jpeg"
        if len(image_bytes) > 5 * 1024 * 1024:
            return templates.TemplateResponse(
                "index.html",
                {"request": request, "result": None, "error": "Please upload an image smaller than 5 MB."},
                status_code=400,
            )

    details = {
        "planner": planner,
        "budget": budget,
        "preferences": preferences.strip(),
        "guests": guests,
        "event_type": event_type.strip(),
        "room_type": room_type.strip(),
        "occasion": occasion.strip(),
        "style": style.strip(),
    }

    try:
        result = generate_recommendations(details, image_bytes=image_bytes, image_mime=image_mime)
    except Exception as exc:
        # Keep the app usable even if the AI service is unavailable.
        result = (
            "AI service could not be reached, so here is a planning checklist instead.\\n\\n"
            f"Planner: {planner.title()}\\nBudget: ₹{budget:,.0f}\\n"
            "1. Keep 10% of the budget as a buffer.\\n"
            "2. Compare prices from at least two sellers before buying.\\n"
            "3. Check delivery charges, reviews, and return policies.\\n"
            "4. Choose the most important items first and adjust the rest to fit the budget.\\n\\n"
            f"Technical note: {str(exc)[:180]}"
        )

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "result": result, "error": None, "last_planner": planner},
    )


@app.get("/health")
async def health():
    return {"status": "ok", "app": "PocketSmart AI"}
