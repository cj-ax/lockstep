# Lockstep (working name)

An org-agnostic tool for writing to Figma faithfully with an organization's own design library, then scoring and fixing the result. This folder is the first spike, which uses the Business@Slalom library as the test bed. Results are in [REPORT.md](REPORT.md).

## Run the loop

All scripts run through the Figma MCP's `use_figma` tool, in a draft file. Never run them against a library file. Each script has a placeholder at the top that you replace before sending it:

| Script | Placeholder | What it does |
|---|---|---|
| `figma/build-settings.js` | `__WHICH__` (e.g. `['Profile', 'Notifications', 'Account', 'Dialog']`) and `__VERSION__` (the canvas row) | Builds the settings page from library instances and variables |
| `figma/score.js` | `__ROOT_IDS__` (frame IDs) | Read-only. Returns the faithfulness percentages, integrity issues and a ranked list of offending nodes |
| `figma/fix.js` | `__ROOT_IDS__` | Binds raw values that exactly match a library token, and lists the rest as decisions |
| `figma/inventory.js` | `__COMPONENT_KEYS__` | Read-only. Returns component properties, descriptions, and the variables those components bind, with values |

The loop: build → score → read the offenders and a screenshot → fix (rerun the build with corrections, or run `fix.js`) → rescore.
