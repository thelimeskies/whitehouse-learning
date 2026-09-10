# Manual actions required

The following items intentionally block a production cutover, but not continued
development or the current client demo:

1. Verify the Dokploy host can pull the published immutable
   `sha-<full git sha>` image before replacing the demo stack. Anonymous GHCR
   manifest access now succeeds outside the host.
2. Create a separate Dokploy staging environment with its own hostname,
   database, secrets, and volumes.
3. Back up and migrate the current demo site content before the production
   Compose cutover. Do not replace the existing frontend container first: its
   emergency application filesystem is not durable.
4. Supply the approved Whitehouse logo, colours, typography, favicons, and image
   usage rights. The current client tokens are deliberately neutral defaults.
5. Configure off-server automated backups and perform a restore test. Object
   storage can be added after credentials and retention requirements are agreed.
