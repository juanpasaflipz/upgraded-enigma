## v0.1.0 — Viability + Monetization MVP

Date: 2025-10-27

Highlights:
- Viability gate: LLM + heuristic fallback, labels + score + reason.
- Pipeline gating: skip heavy generation when below thresholds.
- Stripe: checkout session route with safe fallback.
- Pricing: drop-in PricingTable component wired to checkout.
- UI: ViabilityBadge + tooltip on dashboard and project page.
- Deploy: Render service file and Vercel config; configurable CORS.
- Tests: viability endpoint smoke tests.

Breaking changes:
- Adds columns to `project` table (SQLite safe ALTERs on startup).

