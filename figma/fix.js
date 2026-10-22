// Lockstep auto-fix. Run through use_figma in a DRAFT file with ROOT_IDS set.
// Org-agnostic: it learns the library's tokens from the library instances already in the
// frames (their bound variables and those variables' collections), then binds raw values
// on authored nodes to a library variable with exactly the same value. It never changes how
// anything looks: values with no exact token are reported as decisions, not snapped.
const ROOT_IDS = __ROOT_IDS__;
if (figma.fileKey === 'LMgKpbsEmxRpiHBKd9YGlw') throw new Error('Refusing to write to the production library');

// 1. Learn the token table from the library components in use.
const seenMains = new Set();
const varIds = new Set();
const roots = [];
for (const id of ROOT_IDS) roots.push(await figma.getNodeByIdAsync(id));
for (const root of roots) for (const inst of root.findAllWithCriteria({ types: ['INSTANCE'] })) {
  const main = await inst.getMainComponentAsync();
  if (!main || !main.remote) continue;
  const owner = main.parent && main.parent.type === 'COMPONENT_SET' ? main.parent : main;
  if (seenMains.has(owner.id)) continue;
  seenMains.add(owner.id);
  for (const n of [owner, ...owner.findAll(() => true)]) {
    for (const b of Object.values(n.boundVariables || {})) for (const x of [].concat(b)) if (x && x.id) varIds.add(x.id);
  }
}
const collections = new Map();
for (const id of varIds) {
  const v = await figma.variables.getVariableByIdAsync(id);
  if (v && !collections.has(v.variableCollectionId)) collections.set(v.variableCollectionId, await figma.variables.getVariableCollectionByIdAsync(v.variableCollectionId));
}
const resolve = async (value, depth = 0) => {
  if (value && value.type === 'VARIABLE_ALIAS' && depth < 6) {
    const v = await figma.variables.getVariableByIdAsync(value.id);
    return v ? resolve(v.valuesByMode[Object.keys(v.valuesByMode)[0]], depth + 1) : null;
  }
  return value;
};
const hex = c => '#' + [c.r, c.g, c.b].map(n => Math.round(n * 255).toString(16).padStart(2, '0')).join('');
const floats = []; // { v, value, scopes }
const colours = []; // { v, hex, scopes }
for (const col of collections.values()) {
  const mode = col.modes[0].modeId;
  for (const id of col.variableIds) {
    const v = await figma.variables.getVariableByIdAsync(id);
    if (!v) continue;
    const val = await resolve(v.valuesByMode[mode]);
    if (v.resolvedType === 'FLOAT' && typeof val === 'number') floats.push({ v, value: val });
    if (v.resolvedType === 'COLOR' && val && typeof val === 'object' && 'r' in val && (val.a === undefined || val.a === 1)) colours.push({ v, hex: hex(val) });
  }
}
// Prefer a variable scoped to the property, then the shortest (most generic) name.
const SCOPE = { itemSpacing: 'GAP', paddingTop: 'GAP', paddingRight: 'GAP', paddingBottom: 'GAP', paddingLeft: 'GAP', topLeftRadius: 'CORNER_RADIUS', topRightRadius: 'CORNER_RADIUS', bottomLeftRadius: 'CORNER_RADIUS', bottomRightRadius: 'CORNER_RADIUS', strokeWeight: 'STROKE_FLOAT' };
const NAME_HINT = { itemSpacing: /gap|space|spacing/i, paddingTop: /pad|space|spacing/i, paddingRight: /pad|space|spacing/i, paddingBottom: /pad|space|spacing/i, paddingLeft: /pad|space|spacing/i, topLeftRadius: /radius|corner/i, topRightRadius: /radius|corner/i, bottomLeftRadius: /radius|corner/i, bottomRightRadius: /radius|corner/i, strokeWeight: /border|stroke/i };
function pickFloat(prop, value) {
  const c = floats.filter(f => f.value === value && NAME_HINT[prop].test(f.v.name) && !/elevation/i.test(f.v.name));
  c.sort((a, b) => (b.v.scopes.includes(SCOPE[prop]) - a.v.scopes.includes(SCOPE[prop])) || (/uniform|gap|ga-/.test(b.v.name) - /uniform|gap|ga-/.test(a.v.name)) || a.v.name.length - b.v.name.length);
  return c[0] && c[0].v;
}
function pickColour(h, field, isText) {
  const want = isText ? /font|text/i : field === 'strokes' ? /border|stroke/i : /background|surface|bg|fill/i;
  const c = colours.filter(x => x.hex === h);
  c.sort((a, b) => want.test(b.v.name) - want.test(a.v.name) || a.v.name.length - b.v.name.length);
  return c[0] && c[0].v;
}

// 2. Walk authored nodes (skip library instance internals, enter their slots).
const fixed = [];
const decisions = [];
const ownerOf = n => { let p = n.parent; while (p && p.type !== 'INSTANCE') p = p.parent; return p; };
function fixNumber(node, prop) {
  if (!(prop in node) || typeof node[prop] !== 'number' || node[prop] === 0) return;
  if (node.boundVariables && node.boundVariables[prop]) return;
  const v = pickFloat(prop, node[prop]);
  if (v) { node.setBoundVariable(prop, v); fixed.push(`${node.name}: ${prop} ${node[prop]} → ${v.name}`); }
  else decisions.push(`${node.name}: ${prop}=${node[prop]} has no library token`);
}
function fixPaints(node, field) {
  if (!Array.isArray(node[field])) return;
  let changed = false;
  const next = node[field].map(p => {
    if (p.type !== 'SOLID' || p.visible === false || (p.boundVariables && p.boundVariables.color)) return p;
    if (p.opacity !== undefined && p.opacity < 1) { decisions.push(`${node.name}: ${field} ${hex(p.color)} at ${Math.round(p.opacity * 100)}% has no library token`); return p; }
    const v = pickColour(hex(p.color), field, node.type === 'TEXT');
    if (!v) { decisions.push(`${node.name}: ${field} ${hex(p.color)} has no library token`); return p; }
    changed = true; fixed.push(`${node.name}: ${field} ${hex(p.color)} → ${v.name}`);
    return figma.variables.setBoundVariableForPaint(p, 'color', v);
  });
  if (changed) node[field] = next;
}
async function walk(node) {
  if (node.visible === false) return;
  if (node.type === 'INSTANCE') {
    for (const slot of node.findAllWithCriteria({ types: ['SLOT'] })) if (ownerOf(slot) === node) for (const c of slot.children) await walk(c);
    return;
  }
  if (node.type === 'TEXT') {
    await Promise.all(node.getRangeAllFontNames(0, node.characters.length).map(f => figma.loadFontAsync(f)));
    fixPaints(node, 'fills');
    return;
  }
  fixPaints(node, 'fills');
  fixPaints(node, 'strokes');
  if (node.layoutMode && node.layoutMode !== 'NONE') {
    for (const p of ['paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft']) fixNumber(node, p);
    if (node.children.length > 1) fixNumber(node, 'itemSpacing');
  }
  if ('topLeftRadius' in node) for (const p of ['topLeftRadius', 'topRightRadius', 'bottomLeftRadius', 'bottomRightRadius']) fixNumber(node, p);
  if (Array.isArray(node.strokes) && node.strokes.some(s => s.visible !== false) && typeof node.strokeWeight === 'number') fixNumber(node, 'strokeWeight');
  if ('children' in node) for (const c of node.children) await walk(c);
}
for (const root of roots) await walk(root);

const tally = list => { const m = {}; for (const s of list) { const k = s.replace(/^[^:]*: /, ''); m[k] = (m[k] || 0) + 1; } return m; };
return { tokensLearned: { floats: floats.length, colours: colours.length, collections: [...collections.values()].map(c => c.name) }, fixedCount: fixed.length, fixed: tally(fixed), decisionCount: decisions.length, decisions: tally(decisions) };
