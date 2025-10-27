# YouTube → MVP (FastAPI + Next.js)

Turn YouTube ideas into MVP prototypes with an AI viability check, spec generation, and downloadable Next.js ZIPs.

## Apps
- Backend: FastAPI under `backend/`
- Frontend: Next.js (App Router) under `frontend/`

## Key Features
- AI viability gate (LLM + fallback): labels each submission and scores viability.
- Pipeline gating: skips heavy generation for low-viability content.
- Prototype generation: produces a Next.js + Tailwind ZIP.
- Pricing & Stripe: 3-tier pricing UI + backend Checkout session route.

## Deploy

Frontend (Vercel):
- Set project root to `frontend/`.
- Env: `NEXT_PUBLIC_BACKEND_URL=https://<your-backend>`

Backend (Render example):
- See `render.yaml` and `backend/README.md`.
- Attach persistent disk and set env vars: `ARTIFACTS_DIR`, `BACKEND_BASE_URL`, `FRONTEND_URL`, `ALLOWED_ORIGINS`, optional `OPENAI_API_KEY` and Stripe vars.

## Stripe
- Configure in backend env: `STRIPE_SECRET_KEY`, `STRIPE_PRICE_FREE`, `STRIPE_PRICE_PRO`, `STRIPE_PRICE_STUDIO`, `FRONTEND_URL`.
- Frontend uses redirect-only flow via `/api/stripe/create-checkout-session`.

## Changelog
See `CHANGELOG.md`.

