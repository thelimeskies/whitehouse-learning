# Client UI boundary

Place Whitehouse-specific UI, styles, and assets in this directory. Keeping the
custom layer isolated makes upstream Frappe Learning upgrades easier to review.

- `styles/tokens.css` owns brand primitives.
- `styles/client.css` owns client-prefixed reusable styles.
- `assets/` owns approved logos, illustrations, and fonts.
- New client components should use a `Client` prefix and avoid modifying shared
  upstream components unless the behaviour genuinely belongs upstream.

The current palette is a neutral demo default. Replace the tokens and assets
after the client supplies an approved brand pack; do not infer a production
identity from a screenshot.
