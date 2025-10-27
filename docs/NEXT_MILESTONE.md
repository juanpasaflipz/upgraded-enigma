# Next Milestone: Storage, Billing Webhooks, Database

Goal: production-hardening by moving artifacts to S3, handling Stripe lifecycle via webhooks, and adopting Postgres with migrations.

## 1) S3 Artifact Storage
- Add env: `STORAGE_BACKEND=s3|disk` (default `disk`).
- Add env: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `S3_BUCKET`.
- Implement storage adapter API: `save_text(project_id, name, content)`, `save_file(project_id, name, bytes)`, `public_url(path)`.
- Update pipeline to write transcripts/spec/zip via adapter.
- Keep `disk` path for local dev; `s3` for production.

Acceptance:
- Artifacts upload to S3 and are accessible via HTTPS public URLs.

## 2) Stripe Webhook
- Add route: `POST /api/stripe/webhook` verifying signature header.
- Env: `STRIPE_WEBHOOK_SECRET`.
- Minimal user model and subscription status fields.
- On `checkout.session.completed` and `customer.subscription.updated`:
  - Mark user plan accordingly.

Acceptance:
- Stripe dashboard events update user plan in DB.

## 3) Postgres + Migrations
- Switch `DATABASE_URL` to Postgres in production.
- Add Alembic for migrations and provide a `make migrate` workflow.
- Write an initial migration capturing current schema.

Acceptance:
- DB schema bootstraps via migrations on Postgres.

## Rollout Plan
1. Land storage adapter + feature flag.
2. Add webhook with no-op handlers; then wire user model.
3. Introduce Alembic and Postgres in staging; then prod.

