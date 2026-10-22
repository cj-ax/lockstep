// Lockstep inventory: run through use_figma in a DRAFT file (never the library).
// Imports each library component (set) by key and reports one part per call, because the
// whole inventory overflows use_figma's 48 KB return limit:
// - PART 'components': variant, boolean, text, instance-swap and slot properties, default
//   variant and size, and the description.
// - PART 'variables': every variable in every collection those components bind, with its
//   first-mode value and the properties components bind it to; plus the text and effect
//   styles the components use. Large libraries take several calls: pass `next` back as OFFSET.
// - PART 'structure': the layer tree of each component's default variant.
// - PART 'styles': text and effect styles by key (STYLE_KEYS), for styles no component uses.
// COMPONENT_KEYS ({ label: key }) and PART are filled in by the caller.
const COMPONENT_KEYS = __COMPONENT_KEYS__;
const PART = __PART__;
// styles only: { label: style key } for text and effect styles no component uses (headings,
// shadows), found with search_design_system. The variables part only sees styles components use.
const STYLE_KEYS = __STYLE_KEYS__;
// variables only: big libraries overflow one call, so collections are returned in name order
// until the budget is spent, with `next` to pass back as OFFSET.
const OFFSET = __OFFSET__;
const BUDGET = 40000;
const MAX_DESCRIPTION = 1500;

async function importAny(key) {
  try { return await figma.importComponentSetByKeyAsync(key); }
  catch (e) { return await figma.importComponentByKeyAsync(key); }
}
const owners = {};
const errors = {};
for (const [label, key] of Object.entries(PART === 'styles' ? {} : COMPONENT_KEYS)) {
  try { owners[label] = await importAny(key); } catch (e) { errors[label] = String(e); }
}

if (PART === 'structure') {
  // The layer tree of each component's default variant: which layers hold the text, icons
  // and slots, which properties drive them, and what ships at a fixed size. Saves the build
  // from probing component internals with throwaway scripts.
  const MAX_DEPTH = 4;
  const tree = (n, depth) => {
    if (depth > MAX_DEPTH) return '';
    const refs = n.componentPropertyReferences && Object.keys(n.componentPropertyReferences).length
      ? ' {' + Object.entries(n.componentPropertyReferences).map(([k, v]) => `${k}:${v.split('#')[0]}`).join(', ') + '}' : '';
    const layout = n.layoutMode && n.layoutMode !== 'NONE' ? ` ${n.layoutMode === 'VERTICAL' ? 'V' : 'H'}` : '';
    const short = v => ({ FIXED: 'fix', HUG: 'hug', FILL: 'fill' })[v] || v;
    const sizing = 'layoutSizingHorizontal' in n && n.parent && n.parent.type !== 'COMPONENT_SET' ? ` ${short(n.layoutSizingHorizontal)}/${short(n.layoutSizingVertical)}` : '';
    const text = n.type === 'TEXT' ? ` "${n.characters.slice(0, 24)}"` : '';
    let s = `${'  '.repeat(depth)}${n.type} ${n.name}${text}${refs}${layout}${sizing} ${Math.round(n.width)}x${Math.round(n.height)}\n`;
    if ('children' in n && n.type !== 'INSTANCE') for (const c of n.children) s += tree(c, depth + 1);
    return s;
  };
  const structure = {};
  for (const [label, node] of Object.entries(owners)) {
    const d = node.type === 'COMPONENT_SET' ? node.defaultVariant : node;
    structure[label] = tree(d, 0).slice(0, 2500);
  }
  return { structure, errors, legend: 'Each line: TYPE name "text" {property refs} H|V (auto layout direction) horizontal/vertical sizing (fix, hug, fill) WxH. Nested instances are not expanded.' };
}

if (PART === 'components') {
  const components = [];
  for (const [label, node] of Object.entries(owners)) {
    const props = {};
    for (const [k, v] of Object.entries(node.componentPropertyDefinitions)) {
      props[k] = v.type === 'VARIANT' ? v.variantOptions : v.type === 'SLOT' ? 'SLOT' : `${v.type}=${JSON.stringify(v.defaultValue)}`;
    }
    const d = node.type === 'COMPONENT_SET' ? node.defaultVariant : node;
    components.push({
      label, name: node.name, type: node.type, variants: node.type === 'COMPONENT_SET' ? node.children.length : 1,
      props, default: d.name, size: [Math.round(d.width), Math.round(d.height)],
      description: (node.description || '').slice(0, MAX_DESCRIPTION),
    });
  }
  return { components, errors };
}

// Resolve a variable value to plain data. An alias follows the mode with the same name in the
// aliased collection (dark to dark), else its first mode. Some libraries store a colour as
// {color, opacity}, each possibly an alias, with opacity in percent: that becomes one hex.
const colCache = new Map();
const resolve = async (value, modeName, depth = 0) => {
  if (value && value.type === 'VARIABLE_ALIAS') {
    if (depth > 6) return null;
    const v = await figma.variables.getVariableByIdAsync(value.id);
    if (!v) return null;
    if (!colCache.has(v.variableCollectionId)) colCache.set(v.variableCollectionId, await figma.variables.getVariableCollectionByIdAsync(v.variableCollectionId));
    const col = colCache.get(v.variableCollectionId);
    const mode = (col && col.modes.find(m => m.name === modeName)) || (col && col.modes[0]);
    return resolve(v.valuesByMode[mode ? mode.modeId : Object.keys(v.valuesByMode)[0]], modeName, depth + 1);
  }
  if (value && typeof value === 'object' && 'color' in value) {
    const c = await resolve(value.color, modeName, depth + 1);
    const o = await resolve(value.opacity, modeName, depth + 1);
    if (typeof c !== 'string' || typeof o !== 'number') return c;
    const a = Math.round(Math.max(0, Math.min(1, (c.length === 9 ? parseInt(c.slice(7), 16) / 255 : 1) * o / 100)) * 255);
    return c.slice(0, 7) + (a < 255 ? a.toString(16).padStart(2, '0') : '');
  }
  if (value && typeof value === 'object' && 'r' in value) {
    const h = n => Math.round(n * 255).toString(16).padStart(2, '0');
    return '#' + h(value.r) + h(value.g) + h(value.b) + (value.a !== undefined && value.a < 1 ? h(value.a) : '');
  }
  return value;
};
const hexOf = c => { const h = n => Math.round(n * 255).toString(16).padStart(2, '0'); return '#' + h(c.r) + h(c.g) + h(c.b) + (c.a !== undefined && c.a < 1 ? h(c.a) : ''); };
const used = new Map(); // variable id -> props bound
const styleIds = new Set();
for (const node of Object.values(owners)) {
  for (const n of [node, ...node.findAll(() => true)]) {
    for (const [prop, b] of Object.entries(n.boundVariables || {})) for (const x of [].concat(b)) if (x && x.id) {
      if (!used.has(x.id)) used.set(x.id, new Set());
      used.get(x.id).add(prop.replace(/^(padding|stroke)(Top|Right|Bottom|Left)(Weight)?$/, '$1').replace(/^(top|bottom)(Left|Right)Radius$/, 'radius'));
    }
    for (const prop of ['textStyleId', 'effectStyleId', 'fillStyleId']) if (prop in n && typeof n[prop] === 'string' && n[prop]) styleIds.add(n[prop]);
  }
}
const collections = new Map();
for (const id of used.keys()) {
  const v = await figma.variables.getVariableByIdAsync(id);
  if (v && !collections.has(v.variableCollectionId)) collections.set(v.variableCollectionId, await figma.variables.getVariableCollectionByIdAsync(v.variableCollectionId));
}
const out = {};
let next = null;
let spent = 0;
const ordered = [...collections.values()].sort((a, b) => a.name.localeCompare(b.name));
for (const [i, col] of ordered.entries()) {
  if (i < OFFSET) continue;
  if (spent > BUDGET) { next = i; break; }
  const rows = [];
  for (const id of col.variableIds) {
    const v = await figma.variables.getVariableByIdAsync(id);
    if (!v) continue;
    // [name, key, first-mode value, how library components bind it, {mode: value} when there are several modes]
    const row = [v.name, v.key, await resolve(v.valuesByMode[col.modes[0].modeId], col.modes[0].name), used.has(id) ? [...used.get(id)].join('/') : ''];
    if (col.modes.length > 1) { const byMode = {}; for (const m of col.modes) byMode[m.name] = await resolve(v.valuesByMode[m.modeId], m.name); row.push(byMode); }
    rows.push(row);
  }
  out[`${col.name} [${col.modes.map(m => m.name).join(',')}]`] = rows;
  spent += JSON.stringify(rows).length;
}
if (PART === 'styles') {
  for (const [label, key] of Object.entries(STYLE_KEYS)) {
    try { styleIds.add((await figma.importStyleByKeyAsync(key)).id); } catch (e) { errors[label] = String(e); }
  }
}
const styles = [];
for (const id of styleIds) {
  const s = await figma.getStyleByIdAsync(id);
  const unit = u => (u.unit === 'AUTO' ? 'auto' : `${Math.round(u.value * 100) / 100}${u.unit === 'PERCENT' ? '%' : 'px'}`);
  const shadow = e => `${e.type === 'INNER_SHADOW' ? 'inset ' : ''}${e.offset.x} ${e.offset.y} ${e.radius} ${e.spread || 0} ${hexOf(e.color)}`;
  // TEXT: "family style size / line height / letter spacing"; EFFECT: each shadow as "x y blur spread colour"
  if (s) styles.push([s.type, s.name, s.key, s.type === 'TEXT' ? `${s.fontName.family} ${s.fontName.style} ${s.fontSize} / ${unit(s.lineHeight)} / ${unit(s.letterSpacing)}`
    : s.type === 'EFFECT' ? s.effects.filter(e => e.type.includes('SHADOW')).map(shadow).join(', ') : '']);
}
if (PART === 'styles') return { styles, errors };
return { collections: out, next, styles: OFFSET ? undefined : styles, errors };
