// Ground truth for the learn fixture: run through use_figma (read-only) on the PRISTINE frames,
// before degrade.js. Records every design token and component the frames use, so later
// milestones can measure what learn recovers from the degraded copy.
// ROOT_IDS: the pristine frames.
const ROOT_IDS = __ROOT_IDS__;

const hex = c => '#' + [c.r, c.g, c.b].map(n => Math.round(n * 255).toString(16).padStart(2, '0')).join('') + (c.a !== undefined && c.a < 1 ? Math.round(c.a * 255).toString(16).padStart(2, '0') : '');
async function resolve(value, depth = 0) {
  if (value && value.type === 'VARIABLE_ALIAS' && depth < 6) {
    const v = await figma.variables.getVariableByIdAsync(value.id);
    return v ? resolve(v.valuesByMode[Object.keys(v.valuesByMode)[0]], depth + 1) : null;
  }
  if (value && typeof value === 'object' && 'r' in value) return hex(value);
  return value;
}

const varUse = new Map();      // variable id -> { props:Set, authored, internal }
const textStyles = new Map();  // style id -> count
const placements = new Map();  // "set name / variant" -> { key, count, authored }
const collections = new Map();

async function recordVars(n, authored) {
  const note = (id, prop) => {
    if (!varUse.has(id)) varUse.set(id, { props: new Set(), authored: 0, internal: 0 });
    const u = varUse.get(id); u.props.add(prop); authored ? u.authored++ : u.internal++;
  };
  for (const [prop, b] of Object.entries(n.boundVariables || {})) for (const x of [].concat(b)) if (x && x.id) note(x.id, prop.replace(/(Top|Right|Bottom|Left)$/, '').replace(/^(top|bottom)(Left|Right)Radius$/, 'radius'));
  for (const field of ['fills', 'strokes']) for (const p of Array.isArray(n[field]) ? n[field] : []) if (p.boundVariables && p.boundVariables.color) note(p.boundVariables.color.id, field);
  if (n.type === 'TEXT' && typeof n.textStyleId === 'string' && n.textStyleId) textStyles.set(n.textStyleId, (textStyles.get(n.textStyleId) || 0) + 1);
}

async function place(inst, authored) {
  const m = await inst.getMainComponentAsync();
  if (!m) return;
  const set = m.parent && m.parent.type === 'COMPONENT_SET' ? m.parent : m;
  const id = `${set.name} :: ${set === m ? '' : m.name}`;
  if (!placements.has(id)) placements.set(id, { set: set.name, variant: set === m ? null : m.name, key: set.key, authored: 0, nested: 0 });
  placements.get(id)[authored ? 'authored' : 'nested']++;
}

// authored = placed by the build (outside library internals, or inside a slot)
async function walk(n, authored) {
  if (n.visible === false) return;
  await recordVars(n, authored);
  if (n.type === 'INSTANCE') {
    await place(n, authored);
    // Every slot inside the instance, at any depth (a Dialog's nested Dialog Body has one),
    // holds authored content; skip slots that sit inside another of these slots.
    const allSlots = n.findAll(x => x.type === 'SLOT');
    const slots = allSlots.filter(s => !allSlots.some(o => o.id !== s.id && isInside(s, o)));
    // library internals: everything inside the instance except its own slots' contents
    const internals = n.findAll(x => !slots.some(s => s.id === x.id || isInside(x, s)));
    for (const x of internals) {
      if (x.visible === false) continue;
      await recordVars(x, false);
      if (x.type === 'INSTANCE') await place(x, false);
    }
    for (const s of slots) for (const c of s.children) await walk(c, true);
    return;
  }
  if ('children' in n) for (const c of n.children) await walk(c, authored);
}
function isInside(x, anc) { for (let p = x.parent; p; p = p.parent) if (p.id === anc.id) return true; return false; }

for (const id of ROOT_IDS) await walk(await figma.getNodeByIdAsync(id), true);

const used = [];
for (const [id, u] of varUse) {
  const v = await figma.variables.getVariableByIdAsync(id);
  if (!v) continue;
  if (!collections.has(v.variableCollectionId)) collections.set(v.variableCollectionId, await figma.variables.getVariableCollectionByIdAsync(v.variableCollectionId));
  const col = collections.get(v.variableCollectionId);
  used.push({ name: v.name, collection: col.name, type: v.resolvedType, key: v.key, value: await resolve(v.valuesByMode[col.modes[0].modeId]), props: [...u.props].sort(), authored: u.authored, internal: u.internal });
}
const allTokens = [];
for (const col of collections.values()) {
  for (const vid of col.variableIds) {
    const v = await figma.variables.getVariableByIdAsync(vid);
    if (v) allTokens.push({ name: v.name, collection: col.name, type: v.resolvedType, value: await resolve(v.valuesByMode[col.modes[0].modeId]) });
  }
}
const styles = [];
for (const [id, count] of textStyles) {
  const s = await figma.getStyleByIdAsync(id);
  if (s) styles.push({ name: s.name, key: s.key, font: `${s.fontName.family} ${s.fontName.style}`, size: s.fontSize, lineHeight: s.lineHeight && s.lineHeight.value, count });
}
return {
  tokensUsed: used.sort((a, b) => a.collection.localeCompare(b.collection) || a.name.localeCompare(b.name)),
  tokensAll: allTokens,
  textStyles: styles,
  components: [...placements.values()].sort((a, b) => a.set.localeCompare(b.set)),
};
