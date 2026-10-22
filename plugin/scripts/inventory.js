// Lockstep inventory: run through use_figma in a DRAFT file (never the library).
// Imports each library component (set) by key and reports one of two parts, because the
// whole inventory overflows use_figma's 48 KB return limit:
// - PART 'components': variant, boolean, text, instance-swap and slot properties, default
//   variant and size, and the description.
// - PART 'variables': every variable in every collection those components bind, with its
//   first-mode value and the properties components bind it to; plus the text and effect
//   styles the components use.
// COMPONENT_KEYS ({ label: key }) and PART are filled in by the caller.
const COMPONENT_KEYS = __COMPONENT_KEYS__;
const PART = __PART__;
const MAX_DESCRIPTION = 1500;

async function importAny(key) {
  try { return await figma.importComponentSetByKeyAsync(key); }
  catch (e) { return await figma.importComponentByKeyAsync(key); }
}
const owners = {};
const errors = {};
for (const [label, key] of Object.entries(COMPONENT_KEYS)) {
  try { owners[label] = await importAny(key); } catch (e) { errors[label] = String(e); }
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

const resolve = async (value, depth = 0) => {
  if (value && value.type === 'VARIABLE_ALIAS' && depth < 6) {
    const v = await figma.variables.getVariableByIdAsync(value.id);
    return v ? resolve(v.valuesByMode[Object.keys(v.valuesByMode)[0]], depth + 1) : null;
  }
  if (value && typeof value === 'object' && 'r' in value) {
    const h = n => Math.round(n * 255).toString(16).padStart(2, '0');
    return '#' + h(value.r) + h(value.g) + h(value.b) + (value.a !== undefined && value.a < 1 ? h(value.a) : '');
  }
  return value;
};
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
for (const col of collections.values()) {
  const rows = [];
  for (const id of col.variableIds) {
    const v = await figma.variables.getVariableByIdAsync(id);
    if (!v) continue;
    // [name, key, first-mode value, how library components bind it]
    rows.push([v.name, v.key, await resolve(v.valuesByMode[col.modes[0].modeId]), used.has(id) ? [...used.get(id)].join('/') : '']);
  }
  out[`${col.name} [${col.modes.map(m => m.name).join(',')}]`] = rows;
}
const styles = [];
for (const id of styleIds) {
  const s = await figma.getStyleByIdAsync(id);
  if (s) styles.push([s.type, s.name, s.key, s.type === 'TEXT' ? `${s.fontName.family} ${s.fontName.style} ${s.fontSize}` : '']);
}
return { collections: out, styles, errors };
