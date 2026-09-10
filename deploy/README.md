# Whitehouse Learning on Dokploy

The live demo must remain on its current raw Compose definition until the custom
image has built successfully and its data has been backed up. The production
replacement is `deploy/compose.production.yml`.

- Compose path: `./deploy/compose.production.yml`
- Public service: `frontend`
- Container port: `8080`
- Application route: `/lms`
- Required variables: `CLIENT_IMAGE`, `SITE_NAME`, `DB_PASSWORD`, `ADMIN_PASSWORD`

`CLIENT_IMAGE` must be an immutable `sha-<full git sha>` tag (or digest) emitted
by the `Build client image` workflow. Do not use `latest`, `stable`, or the moving
branch tag in production. See `docs/operations/DEPLOYMENT.md` for the promotion,
backup, migration, smoke-test, and rollback sequence.
