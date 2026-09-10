# Deployment runbook

## Environments

Maintain two independent Dokploy environments:

- **Staging** uses a staging hostname, separate database, and separate named
  volumes. It may track the moving `staging` image tag for convenience.
- **Production** uses `whitehouse-learning.kylodo.com`, production-only secrets
  and volumes, and an immutable `sha-<full git sha>` image tag or digest.

Never point staging at production volumes. Never test a migration for the first
time against production.

The long-lived Git branches are:

- `staging`, where feature work and automated upstream upgrade pull requests
  are validated;
- `client-production`, which represents the reviewed production source;
- short-lived `upgrade/frappe-vX.Y.Z` branches created from `staging`.

## Build and promote

1. Merge reviewed work into `staging`.
2. Wait for `Build client image` and the test workflows to pass.
3. Deploy the workflow's immutable SHA image to staging with
   `deploy/compose.production.yml`.
4. Smoke-test login, course catalogue, enrollment, lesson progress, quiz
   submission, profile, certificate generation, background jobs, email, and the
   mobile layout.
5. Merge the same reviewed commit into `client-production`.
6. Back up production before changing the image.
7. Set production `CLIENT_IMAGE` to the exact SHA image and deploy. The
   one-shot `migrate` service must finish successfully before runtime services
   start.
8. Repeat the smoke tests and retain the previous image reference and backup.

Moving tags such as `staging` and `client-production` are discovery aids only.
They are not acceptable production release identifiers.

## Backup gate

Before each production migration, create and copy off-server:

- a Frappe site backup including private and public files;
- a database-native backup;
- the active `site_config.json` and common site configuration;
- the current `CLIENT_IMAGE` tag and resolved digest.

Verify that the backup exists outside the Dokploy host and record a restore test.
Credentials and backup contents must not be committed to this repository.

## Rollback

If the release fails before a migration, restore the previous immutable
`CLIENT_IMAGE` and redeploy. If a schema migration completed, do not assume an
old image can run against the new schema: stop writes, restore the matching
pre-deploy database and site-file backups, restore the previous image, and then
run smoke tests.

## Upstream releases

The daily `Check upstream stable release` workflow finds stable semantic-version
tags from `frappe/lms`. When a newer tag exists it merges that tag into an
`upgrade/frappe-vX.Y.Z` branch and opens a pull request to `staging`. Conflicts
create an issue and never change production. Review upstream release notes and
migrations before merging.

After staging validation, promote the tested commit and exact image digest to
production manually. Update `.frappe-docker-version` separately when adopting a
new reviewed build definition.
