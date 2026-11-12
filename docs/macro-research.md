# Mage macro approach — 12 November 2026

## Evidence

The installed addon targets Forever Interface 16001 and already uses modern container APIs. This does not prove all current retail macro features work on Forever.

Blizzard's Classic UI source (public mirror, inspected 12 November 2026):
- https://github.com/Gethe/wow-ui-source/blob/classic/Interface/AddOns/Blizzard_MacroUI/Blizzard_MacroUI.lua — uses MAX_ACCOUNT_MACROS and MAX_CHARACTER_MACROS, GetNumMacros, GetMacroInfo, and indexed EditMacro; character indices start after the account range. Use client constants instead of assumed capacities.
- Local extracted Classic source: `cf-ui-research/classic-era-source/Interface/AddOns/Blizzard_MacroUI/Blizzard_MacroIconSelector.lua`, line 109, calls CreateMacro with name, icon, body and a character flag. This is comparative client evidence, not a Forever execution test.
- https://github.com/Gethe/wow-ui-source/blob/classic/Interface/AddOns/Blizzard_FrameXML/SecureTemplates.lua — secure action dispatch handles player-triggered macro actions. Keep casting in ordinary action-bar macros.

## Design

Use a small built-in template catalogue, resolve spell names through C_Spell.GetSpellName (legacy GetSpellInfo fallback), and omit rank suffixes. Conservative 255-byte validation avoids silent truncation, including multibyte spell names. Treat this as a compatibility ceiling, not a claim that every future client has an identical limit.

Create only on an explicit button click outside combat, with per-character storage initially selected. Inspect both macro scopes for the exact generated name, refuse collisions, check the selected scope's capacity, catch API rejection, then verify the saved name/body. Never silently overwrite or recreate edited macros. No EditMacro, DeleteMacro, automatic binding or bar-placement calls are used. Copyable preview remains available if macro creation is unavailable.

Use ordinary /cast, #showtooltip, optional /stopcasting for Counterspell, and cast/cancel Ice Block plus optional separate cancellation. No rotation automation, cooldown decisions, spellcasting Lua, chained macros or /castsequence rotations. Focus/mouseover conditions choose eligible units, not an in-range unit or a rotation action. Ice Block cancellation precedes casting so subsequent presses can exit.

All supported cities are offered rather than guessing Forever's faction or trainer rules. Spell-data lookup does not establish that a character has learned a spell; the interface explains the requirement. New ranks should resolve through rankless casts, which needs live confirmation on Forever.

## Live acceptance still required

Reload; open both slash and AddOns settings entries; inspect layout and bag totals; change options and relog to verify persistence. Create selected macros, inspect /macro and place them manually. Test current-target, focus and mouseover paths, helpful fallback, localized names, highest learned ranks, Counterspell interruption and same-button Ice Block cancellation. Check full storage and combat feedback. Confirm one existing trade with configured class preferences and manual acceptance. Do not describe these checks as passed until observed. CurseForge text/publication is a separate follow-up.

## Utility revision after user review

Researched 12 November 2026:
- https://www.icy-veins.com/wow-classic/classic-guide-to-mages-best-macros — authored Classic guide: stopcasting, cast/cancel Ice Block, mouseover utility and combined food/water.
- https://www.60.tools/macros/mage — Forever macro catalogue: cursor Blizzard, non-toggling wand, channel protection and Shift-cancel Slow Fall patterns.

Implemented these patterns without importing talent-dependent burst sequences. Plain spell/travel shortcuts are still available and documented as such. Offline generation and UI checks cannot verify spell execution on Forever.
