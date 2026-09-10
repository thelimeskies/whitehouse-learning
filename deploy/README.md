# Whitehouse Learning on Dokploy

This directory contains the demo deployment definition for Dokploy.

- Compose path: `./deploy/dokploy-compose.yml`
- Public service: `frontend`
- Container port: `8080`
- Initial route: `/lms`
- Required Dokploy variables: `DB_PASSWORD`, `ADMIN_PASSWORD`
- Optional site override: `SITE_NAME` (defaults to `whitehouse-learning-demo`)

The demo currently tracks the official `ghcr.io/frappe/lms:stable` image. Before a
production launch, replace `stable` with an immutable image digest produced by the
repository release workflow and configure off-server database and site backups.
