// Lockstep inventory: run through use_figma in a DRAFT file (never the library).
// Imports each library component set by key, then reports its variant/boolean/text
// properties, description length, and every variable its variants bind, with values.
// Then expands each collection it found into a full list of variables.
// COMPONENT_KEYS is filled in by the caller.
const COMPONENT_KEYS = __COMPONENT_KEYS__;

const resolve = async (value, modeId, depth = 0) => {
  if (value && value.type === 'VARIABLE_ALIAS' && depth < 6) {
    const v = await figma.variables.getVariableByIdAsync(value.id);
    if (!v) return null;
    const m = Object.keys(v.valuesByMode)[0];
    return resolve(v.valuesByMode[m], m, depth + 1);
  }
  if (value && typeof value === 'object' && 'r' in value) {
    const h = n => Math.round(n * 255).toString(16).padStart(2, '0');
    return '#' + h(value.r) + h(value.g) + h(value.b) + (value.a !== undefined && value.a < 1 ? h(value.a) : '');
  }
  return value;
};

const components = [];
const varIds = new Set();
for (const [label, key] of Object.entries(COMPONENT_KEYS)) {
  let set;
  try { set = await figma.importComponentSetByKeyAsync(key); }
  catch (e) {
    try { set = await figma.importComponentByKeyAsync(key); }
    catch (e2) { components.push({ label, error: String(e2) }); continue; }
  }
  const defs = set.type === 'COMPONENT_SET' || !(set.parent && set.parent.type === 'COMPONENT_SET') ? set.componentPropertyDefinitions : {};
  const props = {};
  for (const [k, v] of Object.entries(defs)) props[k] = v.type === 'VARIANT' ? v.variantOptions : `${v.type}=${JSON.stringify(v.defaultValue)}`;
  for (const n of [set, ...set.findAll(() => true)]) {
    for (const b of Object.values(n.boundVariables || {})) for (const x of [].concat(b)) if (x && x.id) varIds.add(x.id);
    for (const p of [...(Array.isArray(n.fills) ? n.fills : []), ...(Array.isArray(n.strokes) ? n.strokes : [])])
      if (p.boundVariables && p.boundVariables.color) varIds.add(p.boundVariables.color.id);
  }
  components.push({ label, name: set.name, type: set.type, key, variants: set.type === 'COMPONENT_SET' ? set.children.length : 1, props, description: set.description || '' });
}

const collections = {};
for (const id of varIds) {
  const v = await figma.variables.getVariableByIdAsync(id);
  if (!v) continue;
  const col = await figma.variables.getVariableCollectionByIdAsync(v.variableCollectionId);
  if (col && !collections[col.id]) collections[col.id] = col;
}
const variables = [];
for (const col of Object.values(collections)) {
  const mode = col.modes[0].modeId;
  for (const id of col.variableIds) {
    const v = await figma.variables.getVariableByIdAsync(id);
    if (!v) continue;
    variables.push({ collection: col.name, name: v.name, type: v.resolvedType, key: v.key, scopes: v.scopes, value: await resolve(v.valuesByMode[mode], mode), usedByComponents: varIds.has(id) });
  }
}
return { components, collections: Object.values(collections).map(c => ({ name: c.name, key: c.key, modes: c.modes.map(m => m.name), count: c.variableIds.length })), variables };
