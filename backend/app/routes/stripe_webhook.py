from fastapi import APIRouter, Header, HTTPException, Request
import os

router = APIRouter(prefix="/api/stripe", tags=["billing"])

try:
    import stripe  # type: ignore
except Exception:  # pragma: no cover
    stripe = None  # type: ignore


@router.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None, alias="Stripe-Signature")):
    secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    if not secret or not stripe:
        # Not configured; accept silently in dev
        return {"received": True}
    try:
        raw = await request.body()
        event = stripe.Webhook.construct_event(raw, stripe_signature, secret)  # type: ignore[attr-defined]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # TODO: handle events (checkout.session.completed, customer.subscription.updated)
    # For now, just acknowledge
    return {"id": event.get("id"), "type": event.get("type"), "received": True}

