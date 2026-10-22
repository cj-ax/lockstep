# Build patterns and traps

Collected from building the same settings page on two unrelated libraries (Business@Slalom and
Figma's Simple Design System). Both example builds in `examples/` use these helpers.

## Helpers worth copying

```js
// Import everything up front, in parallel. Import by key works without adding the library.
const sets = Object.fromEntries(await Promise.all(Object.entries(SET_KEYS).map(async ([k, key]) => [k, await figma.importComponentSetByKeyAsync(key)])));
const comps = Object.fromEntries(await Promise.all(Object.entries(COMPONENT_KEYS).map(async ([k, key]) => [k, await figma.importComponentByKeyAsync(key)])));
const vars = Object.fromEntries(await Promise.all(Object.entries(VARIABLE_KEYS).map(async ([k, key]) => [k, await figma.variables.importVariableByKeyAsync(key)])));

// Pick a variant by its properties, from the variant's name ("Size=md, State=enabled").
const variantComponent = (set, props) => {
  const want = Object.entries(props);
  const v = set.children.find(c => { const p = Object.fromEntries(c.name.split(', ').map(x => x.split('='))); return want.every(([k, val]) => p[k] === val); });
  if (!v) throw new Error(`${set.name}: no variant ${JSON.stringify(props)}`);
  return v;
};
const variant = (set, props) => variantComponent(set, props).createInstance();

// Set properties by their base name; the "#123:4" suffix differs per library.
const propKey = (inst, name) => Object.keys(inst.componentProperties).find(k => k.split('#')[0] === name);
const setProps = (inst, props) => { const o = {}; for (const [n, v] of Object.entries(props)) { const k = propKey(inst, n); if (!k) throw new Error(`${inst.name}: no property ${n}`); o[k] = v; } inst.setProperties(o); return inst; };

// Bind tokens on frames you create.
const bindPaint = (v) => [figma.variables.setBoundVariableForPaint({ type: 'SOLID', color: { r: 0, g: 0, b: 0 } }, 'color', v)];
const pad = (f, v) => { for (const p of ['paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft']) f.setBoundVariable(p, v); };
const stack = (dir, name, gap) => { const f = figma.createAutoLayout(dir, { name }); f.fills = []; if (gap) f.setBoundVariable('itemSpacing', gap); return f; };

// This instance's own slot (not a nested instance's).
const slotOf = (inst) => inst.findAll(n => n.type === 'SLOT').find(s => { let p = s.parent; while (p && p.type !== 'INSTANCE') p = p.parent; return p && p.id === inst.id; });
```

## Traps that broke real builds

| Trap | What happens | Do this |
|---|---|---|
| `findAllWithCriteria({ types: ['SLOT'] })` | Misses slots of an instance nested in another (a Dialog Body inside a Dialog) | `findAll(n => n.type === 'SLOT')` |
| Comparing nodes with `===` or `indexOf` | Fails for nested instances, because each lookup returns a new wrapper | Compare `node.id`; use `findIndex(c => c.id === x.id)` |
| `variant(...).mainComponent` to swap | Leaves a stray instance on the canvas | `inst.swapComponent(variantComponent(...))` |
| Library cards and slots ship at a fixed sample height | Content is clipped: fields vanish | After filling: slot `layoutSizingVertical = 'HUG'`, instance `layoutSizingVertical = 'HUG'` |
| A text component set to FILL | Its inner text layer stays auto-width, runs past the card and is cut off | Also set the inner TEXT to `layoutSizingHorizontal = 'FILL'` and `textAutoResize = 'HEIGHT'` |
| Button groups with show/hide booleans | You label the hidden button and the visible one says "Button" | After setting the booleans, label the *visible* nested buttons in order |
| Two text layers with the same name (both "Title") | The subtitle repeats the title | Pick by role: sort by font size, or by parent |
| A variant combination you assume exists | `no variant` error (for example a field that is enabled, has a value and has the label on) | Read the variant list from the inventory and use what exists |
| The default variant | It may be Disabled (one library's Tabs) | Always set every variant property explicitly |
| Layer size and render disagree | A field's layer is full width but its outline renders at the component's default width, and icons float past the box. Two fresh-agent trials hit this | It's Figma's stale internal layout after a scripted resize. Run `settle` on the frames after every build. Then recheck with a screenshot |
| Probing component internals with one-off scripts | Slow, and a probe that touches an unexpected node type throws | Read `inventory.structure.json` from init first |
| `layoutSizingHorizontal = 'FILL'` before appending | Throws | Append to the auto-layout parent first |
| Big returns | `use_figma` rejects returns over 48 KB | Return IDs, names and sizes only |
| Big scripts | The code limit is 50,000 characters | Build 3–4 frames per call; `render.py` checks the size |

## Things the library decides, not you

Read the component descriptions for:
- which variant means what (primary vs neutral, which one is Cancel);
- sizes and where each is allowed;
- destructive-action rules;
- whether switches save immediately (if so, there's no Save button);
- dialog padding and radius;
- label casing.

If the descriptions are thin, use the conventions of the library's own sample compositions, and
list the judgement calls in your report. If the library and the user's codebase disagree, ask
the user which one wins; don't pick silently.
