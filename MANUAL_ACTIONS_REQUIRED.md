# Manual actions required

The following items intentionally block a production cutover, but not continued
development or the current client demo:

1. In GitHub Packages, make the container package readable by the Dokploy host,
   or configure Dokploy with a GitHub Container Registry credential that has
   package read access. The host could not pull the earlier GHCR image.
2. Let the `Build client image` workflow finish, then verify Dokploy can pull its
   immutable `sha-<full git sha>` tag before replacing the demo stack.
3. Create a separate Dokploy staging environment with its own hostname,
   database, secrets, and volumes.
4. Back up and migrate the current demo site content before the production
   Compose cutover. Do not replace the existing frontend container first: its
   emergency application filesystem is not durable.
5. Supply the approved Whitehouse logo, colours, typography, favicons, and image
   usage rights. The current client tokens are deliberately neutral defaults.
6. Configure off-server automated backups and perform a restore test. Object
   storage can be added after credentials and retention requirements are agreed.
