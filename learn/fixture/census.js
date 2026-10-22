// Census of the DEGRADED fixture (read-only): the verified final state that ground-truth.json
// records. Node IDs logged by degrade.js can go stale when an outer instance is detached after
// an inner one, so the ground truth uses these IDs instead.
const ROOT_IDS = __ROOT_IDS__;

const isInside = (x, anc) => { for (let p = x.parent; p; p = p.parent) if (p.id === anc.id) return true; return false; };
const out = { detached: [], instances: {}, values: { paintsRaw: 0, paintsBound: 0, paintsWip: 0, numbersBound: 0, numbersWip: 0, textStyled: 0, textRaw: 0 } };
const wipIds = new Set();
for (const c of await figma.variables.getLocalVariableCollectionsAsync()) if (c.name === 'Tokens (WIP)') for (const id of c.variableIds) wipIds.add(id);

async function visit(n, frameName) {
  if (n.visible === false) return;
  if (n.type === 'INSTANCE') {
    const m = await n.getMainComponentAsync();
    const set = m && m.parent && m.parent.type === 'COMPONENT_SET' ? m.parent : m;
    const name = set ? set.name : '?';
    out.instances[name] = (out.instances[name] || 0) + 1;
    const all = n.findAll(x => x.type === 'SLOT');
    const slots = all.filter(s => !all.some(o => o.id !== s.id && isInside(s, o)));
    for (const s of slots) for (const c of s.children) await visit(c, frameName);
    return;
  }
  if (n.detachedInfo) out.detached.push({ frame: frameName, node: n.id, name: n.name, componentKey: n.detachedInfo.componentKey || null, type: n.detachedInfo.type });
  for (const field of ['fills', 'strokes']) for (const p of Array.isArray(n[field]) ? n[field] : []) {
    if (p.type !== 'SOLID' || p.visible === false) continue;
    const b = p.boundVariables && p.boundVariables.color;
    if (!b) out.values.paintsRaw++; else if (wipIds.has(b.id)) out.values.paintsWip++; else out.values.paintsBound++;
  }
  for (const [prop, b] of Object.entries(n.boundVariables || {})) for (const x of [].concat(b)) if (x && x.id && prop !== 'fills' && prop !== 'strokes') {
    if (wipIds.has(x.id)) out.values.numbersWip++; else out.values.numbersBound++;
  }
  if (n.type === 'TEXT') (typeof n.textStyleId === 'string' && n.textStyleId ? out.values.textStyled++ : out.values.textRaw++);
  if ('children' in n) for (const c of n.children) await visit(c, frameName);
}
for (const id of ROOT_IDS) { const r = await figma.getNodeByIdAsync(id); await visit(r, r.name); }
out.wipVariables = wipIds.size;
return out;
