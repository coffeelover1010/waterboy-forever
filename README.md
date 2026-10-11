# Waterboy Forever

![Waterboy Forever trade window](release-media/trade.png)

- Adds a full stack of conjured water to trades with mana classes.
- Hunters get food and water; warriors get food only.
- Picks the highest available rank the other player can use.
- Uses full stacks already in your bags. Does not conjure or split stacks.
- You click Trade to finish. Existing trade items are left alone.
- `/waterboy on` or `/waterboy off` to toggle. `/watertrade` also works.

For WoW Forever beta, client 1.60.1 (Interface 16001). Enabled by default.

## Installation

Put the `WaterboyForever` folder in `_classic_beta_/Interface/AddOns`.
Remove the older `WaterTradeForever` addon if installed. The saved-variable name is retained for compatibility; when upgrading locally, copy its saved-variable file to `WaterboyForever.lua` while WoW is closed to preserve the toggle.

## Validation

Run `uv run --with lupa python tests/check.py` for offline behavior checks.
Live client verification is still pending: after `/reload`, trade with a hunter and a warrior with eligible full stacks in your bags. Verify both hunter stacks, food only for the warrior, and manual acceptance. Check that removing an offered item does not refill it.

## Limits

Skips combat, busy cursors, unknown players and unusable stacks. Supports Classic conjured food and water item IDs. One offer per trade, with brief retries for delayed item or player information. Automatic placement depends on the client's protected API behavior.
