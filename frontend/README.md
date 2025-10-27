# Frontend — Next.js (YouTube → MVP)

This Next.js (App Router, TypeScript) frontend lets users paste a YouTube URL, view project dashboards, and download generated artifacts.

## Quickstart

```
npm install
npm run dev
```

Set `NEXT_PUBLIC_BACKEND_URL` (defaults to `http://localhost:8000`).

## Routes

- `/` — Landing page with form
- `/dashboard` — Lists projects from backend
- `/project/[id]` — Project detail with artifacts
- `/pricing` — Static pricing page

## Pricing & Stripe

- `components/PricingTable.tsx` renders a 3-tier pricing table.
- `lib/checkout.ts` posts to backend `/api/stripe/create-checkout-session` and redirects to the returned URL.
- No `@stripe/stripe-js` is required for this redirect-only flow.
- Configure backend `FRONTEND_URL` and Stripe vars to enable Checkout.
