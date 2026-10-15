import os
from typing import Optional


def _fallback(details: dict) -> str:
    planner = details.get("planner", "home")
    budget = float(details.get("budget", 0))
    preferences = details.get("preferences") or "value for money"

    if planner == "home":
        focus = details.get("room_type") or "your chosen room"

        return (
            f"PocketSmart AI - Home Plan\n\n"
            f"Budget: ₹{budget:,.0f}\n"
            f"Room: {focus}\n"
            f"Preference: {preferences}\n\n"
            f"Suggested Budget Split:\n"
            f"- Essential furniture: ₹{budget * 0.40:,.0f}\n"
            f"- Lighting and fans: ₹{budget * 0.20:,.0f}\n"
            f"- Storage and organisation: ₹{budget * 0.20:,.0f}\n"
            f"- Decor and finishing touches: ₹{budget * 0.10:,.0f}\n"
            f"- Emergency buffer: ₹{budget * 0.10:,.0f}\n\n"
            "Compare current prices before buying. These are planning "
            "estimates, not live product prices."
        )

    if planner == "party":
        guests = details.get("guests") or 0
        event = details.get("event_type") or "celebration"

        return (
            f"PocketSmart AI - Party Plan\n\n"
            f"Budget: ₹{budget:,.0f}\n"
            f"Event: {event}\n"
            f"Guests: {guests}\n\n"
            f"Suggested Budget Split:\n"
            f"- Food and drinks (45%): ₹{budget * 0.45:,.0f}\n"
            f"- Venue (25%): ₹{budget * 0.25:,.0f}\n"
            f"- Decorations (15%): ₹{budget * 0.15:,.0f}\n"
            f"- Activities and music (5%): ₹{budget * 0.05:,.0f}\n"
            f"- Emergency buffer (10%): ₹{budget * 0.10:,.0f}\n\n"
            "Check local prices and delivery fees before confirming vendors."
        )

    return (
        f"PocketSmart AI - Jewelry Plan\n\n"
        f"Budget: ₹{budget:,.0f}\n"
        f"Occasion: {details.get('occasion') or 'special occasion'}\n"
        f"Style: {details.get('style') or preferences}\n\n"
        f"- Main jewelry purchase (70%): ₹{budget * 0.70:,.0f}\n"
        f"- Matching pieces (20%): ₹{budget * 0.20:,.0f}\n"
        f"- Emergency buffer (10%): ₹{budget * 0.10:,.0f}\n\n"
        "Compare materials, seller reviews, return policies, and delivery "
        "charges before purchasing. These are planning suggestions, "
        "not live product listings."
    )


def generate_recommendations(
    details: dict,
    image_bytes: Optional[bytes] = None,
    image_mime: Optional[str] = None,
) -> str:

    """Generate recommendations using Gemini or fallback suggestions."""

    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not api_key:
        return _fallback(details)

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        model = os.getenv(
            "GEMINI_MODEL",
            "gemini-2.5-flash"
        )

        planner = details.get("planner", "home")
        budget = float(details.get("budget", 0))

        prompt = f"""
You are PocketSmart AI, a budget recommendation assistant.

Respond in simple English.
Use Indian Rupees (₹).
Do not claim to have checked live prices.

User details:
Planner: {planner}
Budget: ₹{budget:,.0f}
Preferences: {details.get('preferences') or 'Not specified'}
Room type: {details.get('room_type') or 'Not specified'}
Event type: {details.get('event_type') or 'Not specified'}
Guests: {details.get('guests') or 'Not specified'}
Occasion: {details.get('occasion') or 'Not specified'}
Jewelry style: {details.get('style') or 'Not specified'}

Provide:
1. A short plan summary.
2. A budget breakdown that does not exceed the total budget.
3. Three to five practical suggestions.
4. A reminder to verify current prices and availability.

If a jewelry planner image is attached, consider its colors
and overall style without identifying the person.
"""

        contents = [prompt]

        if image_bytes:
            contents.append(
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=image_mime or "image/jpeg",
                )
            )

        response = client.models.generate_content(
            model=model,
            contents=contents,
        )

        result = getattr(response, "text", None)

        if result and result.strip():
            return result.strip()

        return _fallback(details)

    except Exception:
        return _fallback(details)
