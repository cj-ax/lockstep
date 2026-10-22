# Slalom library inventory (read 2026-10-21 via use_figma in draft w3v1epae69aKLLEOKCkr88)

Method: importComponentSetByKeyAsync for each needed component (keys from search_design_system),
then walked every variant's boundVariables and expanded each collection found via
getVariableCollectionByIdAsync(...).variableIds. Works without the library being "added" to the draft.

Collections reached: space variables (pa-*, px-*, ga-*, elevation), Radius (radius-0/m/l/xl = 0/4/8/24),
Color Semantic Variables (updated) [Light, Dark] 54+ vars, Font Variables (weight 400/700),
border variables (border-sm 1, border-md 2), plus stray older collections (Colors, Radius
[Business/Me @ Slalom], Corner radius, Brand colors) that some variants still bind.

Text styles used by components: Heading 6 (Slalom Sans Bold 20), Body-1 (16), Body-2 (14), Caption (12),
button-{lg,md,sm}-{upcase,ttlcase}. Effect style: surface-shadow.
Other heading styles found by search: Heading 3/4/5 (keys in build script).
