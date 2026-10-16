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

app = FastAPI(
    title="PocketSmart AI",
    description="Smart budget and recommendation assistant"
)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)

templates = Jinja2Templates(
    directory=BASE_DIR / "templates"
)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": None,
            "error": None
        }
    )


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
    outfit_image: Optional[UploadFile] = File(None)
):

    # Validate planner type
    if planner not in {"home", "party", "jewelry"}:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "result": None,
                "error": "Please select a valid planner."
            },
            status_code=400
        )

    # Validate budget
    if budget <= 0:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "result": None,
                "error": "Please enter a budget greater than 0."
            },
            status_code=400
        )

    # Validate party guests
    if planner == "party" and (guests is None or guests < 1):
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "result": None,
                "error": "Please enter at least one guest."
            },
            status_code=400
        )

    image_bytes = None
    image_mime = None

    # Process optional outfit image
    if outfit_image and outfit_image.filename:

        image_bytes = await outfit_image.read()
        image_mime = outfit_image.content_type or "image/jpeg"

        if len(image_bytes) > 5 * 1024 * 1024:
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "result": None,
                    "error": "Please upload an image smaller than 5 MB."
                },
                status_code=400
            )

        if not image_mime.startswith("image/"):
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "result": None,
                    "error": "Please upload a valid image file."
                },
                status_code=400
            )

        if planner != "jewelry":
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "result": None,
                    "error": "Image upload is available only for the jewelry planner."
                },
                status_code=400
            )

    # Collect user details
    details = {
        "planner": planner,
        "budget": budget,
        "preferences": preferences.strip(),
        "guests": guests,
        "event_type": event_type.strip(),
        "room_type": room_type.strip(),
        "occasion": occasion.strip(),
        "style": style.strip()
    }

    try:

        result = generate_recommendations(
            details,
            image_bytes=image_bytes,
            image_mime=image_mime
        )

    except Exception:
        result = (
            "AI recommendations are temporarily unavailable.\n\n"
            f"Planner: {planner.title()}\n"
            f"Budget: ₹{budget:,.0f}\n\n"
            "Please try again later."
        )

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": result,
            "error": None,
            "last_planner": planner
        }
    )


@app.get("/health")
async def health():

    return {
        "status": "ok",
        "app": "PocketSmart AI"
}
