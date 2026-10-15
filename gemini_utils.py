import os
from typing import Optional

def _fallback(details: dict) -> str:
    planner = details.get("planner", "home")
    budget = float(details.get("budget", 0))
    preferences = details.get("preferences") or "value for money"
    if planner == "home":
        focus = details.get("room_type") or "your chosen room"
        return (
            f"PocketSmart AI — Home Plan\\n\\nBudget: ₹{budget:,.0f}\\nRoom: {focus}\\n"
            f"Preference: {preferences}\\n\\nSuggested budget split:\\n"
            f"• Essential furniture: ₹{budget*0.40:,.0f}\\n"
            f"• Lighting and fans: ₹{budget*0.20:,.0f}\\n"
            f"• Storage and organisation: ₹{budget*0.20:,.0f}\\n"
            f"• Decor and finishing touches: ₹{budget*0.10:,.0f}\\n"
            f"• Emergency buffer: ₹{budget*0.10:,.0f}\\n\\n"
            "Compare current prices on Amazon, IKEA, and Flipkart. These are planning estimates, "
            "not live product prices."
        )
    if planner == "party":
        guests = details.get("guests") or 0
        event = details.get("event_type") or "celebration"
        return (
            f"PocketSmart AI — Party Plan\\n\\nBudget: ₹{budget:,.0f}\\nEvent: {event}\\n"
            f"Guests: {guests}\\n\\nSuggested budget split:\\n"
            f"• Food and drinks (45%): ₹{budget*0.45:,.0f}\\n"
            f"• Venue (25%): ₹{budget*0.25:,.0f}\\n"
            f"• Decorations (15%): ₹{budget*0.15:,.0f}\\n"
            f"• Activities/music (5%): ₹{budget*0.05:,.0f}\\n"
            f"• Buffer (10%): ₹{budget*0.10:,.0f}\\n\\n"
            "Check local quotes and delivery fees before confirming vendors."
        )
    return (
        f"PocketSmart AI — Jewelry Plan\\n\\nBudget: ₹{budget:,.0f}\\n"
        f"Occasion: {details.get('occasion') or 'special occasion'}\\n"
        f"Style: {details.get('style') or preferences}\\n\\n"
        f"• Keep the main jewelry purchase near 70% of your budget (₹{budget*0.70:,.0f}).\\n"
        f"• Reserve 20% (₹{budget*0.20:,.0f}) for matching pieces and 10% (₹{budget*0.10:,.0f}) as a buffer.\\n"
        "• Compare materials, size, seller reviews, return policy, and delivery charges on Amazon and Flipkart.\\n"
        "These are planning suggestions, not live product listings."
    )


def generate_recommendations(details: dict, image_bytes: Optional[bytes] = None,
                             image_mime: Optional[str] = None) -> str:
    """Use Gemini when an API key is configured; otherwise return useful demo recommendations."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return _fallback(details)

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    planner = details.get("planner", "home")
    prompt = f"""
You are PocketSmart AI, a practical budget recommendation assistant.
Respond in simple, clear English. The currency is Indian Rupees (₹).
Do not claim that you checked live prices or inventory. Provide estimates and tell the user
to verify current prices on official shopping/vendor websites. Keep total suggested allocations
within the user's budget and show the arithmetic.

User details:
Planner: {planner}
Total budget: ₹{float(details.get('budget', 0)):,.0f}
Preferences: {details.get('preferences') or 'not specified'}
Room type: {details.get('room_type') or 'not specified'}
Event type: {details.get('event_type') or 'not specified'}
Guest count: {details.get('guests') or 'not specified'}
Occasion: {details.get('occasion') or 'not specified'}
Jewelry style: {details.get('style') or 'not specified'}

Give:
1. A short plan summary.
2. A budget allocation table/list with amounts that add up to no more than the budget.
3. 3-5 practical suggestions, with relevant platforms such as Amazon, Flipkart, IKEA,
   Swiggy, Zomato, or OYO only where appropriate.
4. A reminder to verify price, availability, delivery, and return policy.
If this is the jewelry planner and an outfit image is attached, consider its colors and overall
style without identifying the person in the image.
"""
    contents = [prompt]
    if image_bytes:
        contents.append(types.Part.from_bytes(data=image_bytes, mime_type=image_mime or "image/jpeg"))
    response = client.models.generate_content(model=model, contents=contents)
    text = getattr(response, "text", None)
    return text.strip() if text else _fallback(details)
  
