from fastapi import APIRouter, Query, HTTPException
import os

router = APIRouter(prefix="/api/stripe", tags=["billing"])

try:
    import stripe  # type: ignore
except Exception:  # pragma: no cover
    stripe = None  # fallback when package missing


@router.post("/create-checkout-session")
def create_checkout_session(plan: str = Query("pro")):
    secret = os.getenv("STRIPE_SECRET_KEY")
    domain = os.getenv("FRONTEND_URL", "http://localhost:3000")
    price_id = {
        "free": os.getenv("STRIPE_PRICE_FREE"),
        "pro": os.getenv("STRIPE_PRICE_PRO"),
        "studio": os.getenv("STRIPE_PRICE_STUDIO"),
    }.get(plan.lower(), os.getenv("STRIPE_PRICE_PRO"))

    # Graceful fallback when not configured
    if not secret or not price_id or not stripe:
        # Return a dummy URL so the button remains harmless in dev
        return {"url": f"{domain}/pricing"}

    stripe.api_key = secret
    try:
        session = stripe.checkout.Session.create(  # type: ignore[attr-defined]
            payment_method_types=["card"],
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=f"{domain}/success",
            cancel_url=f"{domain}/pricing",
        )
        return {"url": session.url}
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e))

