// Lockstep usage audit (read-only): what a product file actually uses, for lockstep:learn.
// ROOT_IDS are frames, or pages (their top-level frames are audited). Large files are paged:
// it audits roots from OFFSET until a node budget runs out, and returns `next` to resume.
//
// Authored layers are everything the designer placed: frames, text, shapes, detached copies,
// and the contents of instance slots. Library internals are recorded only as the variables
// they bind ("internal"), which names values the product files left raw.
//
// Returns aggregates, not every node, to stay under use_figma's 48 KB:
// - instances: per component, count, variants and overridden fields
// - detached: every detached frame with its detachedInfo (the component it came from)
// - colors / numbers / type / effects: each raw or bound value, with counts, roles, the
//   variables or styles it's bound to, and example node IDs
// - internal: variables bound inside library instances, with values and the properties they drive
// - structures: repeated subtrees (same shape, ignoring text and exact sizes), clusters of 3+
const ROOT_IDS = __ROOT_IDS__;
const OFFSET = __OFFSET__;
const NODE_BUDGET = 6000;
const EXAMPLES = 4;
const MAX_STRUCTURES = 30;

const h2 = n => Math.round(n * 255).toString(16).padStart(2, '0');
const hex = (c, opacity = 1) => { const a = (c.a === undefined ? 1 : c.a) * opacity; return '#' + h2(c.r) + h2(c.g) + h2(c.b) + (a < 0.999 ? h2(a) : ''); };
const isInside = (x, anc) => { for (let p = x.parent; p; p = p.parent) if (p.id === anc.id) return true; return false; };
const topSlots = inst => { const all = inst.findAll(x => x.type === 'SLOT'); return all.filter(s => !all.some(o => o.id !== s.id && isInside(s, o))); };
const SHAPES = new Set(['RECTANGLE', 'ELLIPSE', 'VECTOR', 'LINE', 'POLYGON', 'STAR', 'BOOLEAN_OPERATION']);
const visible = arr => (Array.isArray(arr) ? arr : []).filter(p => p.visible !== false && (p.opacity === undefined || p.opacity > 0));

const varCache = new Map();
async function varName(id) {
  if (!varCache.has(id)) {
    let name = null, collection = null, remote = null;
    try {
      const v = await figma.variables.getVariableByIdAsync(id);
      if (v) {
        name = v.name; remote = v.remote;
        try { const c = await figma.variables.getVariableCollectionByIdAsync(v.variableCollectionId); collection = c ? c.name : null; } catch (e) { /* remote collection not loaded */ }
      }
    } catch (e) { /* missing variable */ }
    varCache.set(id, { name, collection, remote });
  }
  return varCache.get(id);
}
const styleCache = new Map();
async function styleName(id) {
  if (typeof id !== 'string' || !id) return null;
  if (!styleCache.has(id)) { let s = null; try { s = await figma.getStyleByIdAsync(id); } catch (e) { /* missing */ } styleCache.set(id, s ? s.name : '(missing style)'); }
  return styleCache.get(id);
}

const out = { file: figma.fileKey, roots: [], next: null, instances: {}, detached: [], colors: {}, numbers: {}, type: {}, effects: {}, internal: {}, structures: [] };
function tally(table, key, nodeId, extra) {
  const e = table[key] || (table[key] = { n: 0, ex: [] });
  e.n++;
  if (e.ex.length < EXAMPLES) e.ex.push(nodeId);
  if (extra) for (const [k, v] of Object.entries(extra)) if (v) { e[k] = e[k] || {}; e[k][v] = (e[k][v] || 0) + 1; }
}
const wipLabel = v => v && v.name ? `${v.remote ? '' : 'local:'}${v.collection ? v.collection + '/' : ''}${v.name}` : null;

async function colors(n, role) {
  for (const field of ['fills', 'strokes']) {
    const styleId = field === 'fills' ? n.fillStyleId : n.strokeStyleId;
    for (const p of visible(n[field])) {
      if (p.type !== 'SOLID') continue;
      const b = p.boundVariables && p.boundVariables.color;
      tally(out.colors, hex(p.color, p.opacity === undefined ? 1 : p.opacity), n.id, {
        role: field === 'strokes' ? 'stroke' : role,
        bound: b ? wipLabel(await varName(b.id)) : null,
        style: await styleName(styleId),
      });
    }
  }
}

const NUMBER_PROPS = [['paddingTop', 'spacing'], ['paddingRight', 'spacing'], ['paddingBottom', 'spacing'], ['paddingLeft', 'spacing'], ['itemSpacing', 'spacing'], ['counterAxisSpacing', 'spacing'],
  ['topLeftRadius', 'radius'], ['topRightRadius', 'radius'], ['bottomLeftRadius', 'radius'], ['bottomRightRadius', 'radius'], ['strokeWeight', 'stroke']];
async function numbers(n) {
  const bv = n.boundVariables || {};
  const auto = n.layoutMode && n.layoutMode !== 'NONE';
  for (const [prop, kind] of NUMBER_PROPS) {
    if (!(prop in n) || typeof n[prop] !== 'number' || n[prop] === 0) continue;
    if (kind === 'spacing' && !auto) continue;
    if (prop === 'itemSpacing' && (n.children.length < 2 || n.primaryAxisAlignItems === 'SPACE_BETWEEN')) continue;
    if (prop === 'counterAxisSpacing' && n.layoutWrap !== 'WRAP') continue;
    if (kind === 'stroke' && !visible(n.strokes).length) continue;
    const b = bv[prop] || (kind === 'stroke' && bv.strokeTopWeight);
    tally(out.numbers, `${kind}:${Math.round(n[prop] * 100) / 100}`, n.id, { prop: prop.replace(/(Top|Right|Bottom|Left)$/, '').replace(/^(top|bottom)(Left|Right)Radius$/, 'radius'), bound: b ? wipLabel(await varName(b.id)) : null });
  }
}

async function typography(n) {
  const segs = n.getStyledTextSegments(['fontName', 'fontSize', 'lineHeight', 'letterSpacing', 'textStyleId']);
  const bv = n.boundVariables || {};
  const boundSize = [].concat(bv.fontSize || [])[0];
  for (const s of segs) {
    const lh = s.lineHeight.unit === 'AUTO' ? 'auto' : `${Math.round(s.lineHeight.value * 10) / 10}${s.lineHeight.unit === 'PERCENT' ? '%' : 'px'}`;
    const ls = s.letterSpacing.value ? `${Math.round(s.letterSpacing.value * 100) / 100}${s.letterSpacing.unit === 'PERCENT' ? '%' : 'px'}` : '0';
    tally(out.type, `${s.fontName.family}|${s.fontName.style}|${s.fontSize}|${lh}|${ls}`, n.id, {
      style: await styleName(s.textStyleId), bound: boundSize && boundSize.id ? wipLabel(await varName(boundSize.id)) : null,
    });
  }
}

async function effects(n) {
  for (const e of (n.effects || []).filter(e => e.visible !== false)) {
    const key = e.type.includes('SHADOW')
      ? `${e.type === 'DROP_SHADOW' ? 'drop' : 'inner'}:${e.offset.x},${e.offset.y},${e.radius},${e.spread || 0},${hex(e.color)}`
      : `${e.type === 'LAYER_BLUR' ? 'blur' : 'bg-blur'}:${e.radius}`;
    const bound = e.boundVariables && Object.values(e.boundVariables)[0];
    tally(out.effects, key, n.id, { style: await styleName(n.effectStyleId), bound: bound ? wipLabel(await varName(bound.id)) : null });
  }
}

async function internals(inst, slots) {
  // Variables the library binds inside this instance (not its slot contents).
  for (const x of [inst, ...inst.findAll(x => !slots.some(s => s.id === x.id || isInside(x, s)))]) {
    if (x.visible === false) continue;
    const record = async (id, value, prop) => {
      const v = await varName(id);
      if (!v.name) return;
      const key = wipLabel(v);
      const e = out.internal[key] || (out.internal[key] = { n: 0, values: {}, props: {} });
      e.n++; e.values[value] = (e.values[value] || 0) + 1; e.props[prop] = (e.props[prop] || 0) + 1;
    };
    for (const field of ['fills', 'strokes']) for (const p of visible(x[field])) if (p.type === 'SOLID' && p.boundVariables && p.boundVariables.color) await record(p.boundVariables.color.id, hex(p.color, p.opacity === undefined ? 1 : p.opacity), field === 'fills' ? (x.type === 'TEXT' ? 'text' : 'fill') : 'stroke');
    for (const e of (x.effects || []).filter(e => e.visible !== false)) for (const [field, alias] of Object.entries(e.boundVariables || {})) {
      const val = field === 'offsetX' ? e.offset.x : field === 'offsetY' ? e.offset.y : field === 'color' ? hex(e.color) : e[field];
      if (alias && alias.id) await record(alias.id, typeof val === 'number' ? Math.round(val * 100) / 100 : val, `effect.${field}`);
    }
    for (const [prop, b] of Object.entries(x.boundVariables || {})) {
      if (prop === 'fills' || prop === 'strokes' || prop === 'effects') continue;
      // Some bindable fields (fontFamily, fontStyle) aren't node properties; record those by name.
      const val = prop in x ? x[prop] : prop;
      const kind = prop.replace(/(Top|Right|Bottom|Left)(Weight)?$/, '$2').replace(/^(top|bottom)(Left|Right)Radius$/, 'radius');
      for (const one of [].concat(b)) if (one && one.id) await record(one.id, typeof val === 'number' ? Math.round(val * 100) / 100 : val && typeof val === 'object' && 'family' in val ? val.family : String(val).slice(0, 30), kind);
    }
  }
}

// Structure signature: node kinds, auto layout direction, padding and gap rounded to 4, paint
// presence and text style, to `depth` levels. Text content, sizes and sizing modes (a
// component hugs, its placed copies often stretch) are ignored. A slot
// counts as one node whatever it holds. The shallow "shell" signature (depth 1) matches
// containers whose contents differ, such as cards.
const r4 = v => Math.round((v || 0) / 4) * 4;
function sig(n, depth) {
  if (n.type === 'TEXT') return `T(${typeof n.fontName === 'object' && n.fontName.family ? n.fontName.family + ' ' + n.fontName.style : 'mixed'} ${typeof n.fontSize === 'number' ? n.fontSize : 'mixed'})`;
  if (n.type === 'INSTANCE') return `I(${n.name.split('=')[0]})`;
  if (n.type === 'SLOT') return 'S';
  if (SHAPES.has(n.type)) return n.type[0];
  if (!('children' in n)) return n.type;
  const lay = n.layoutMode && n.layoutMode !== 'NONE'
    ? `${n.layoutMode[0]}${r4(n.paddingTop)},${r4(n.paddingRight)},${r4(n.paddingBottom)},${r4(n.paddingLeft)}g${r4(n.itemSpacing)}`
    : 'abs';
  const paint = `${visible(n.fills).length ? 'f' : ''}${visible(n.strokes).length ? 's' : ''}${typeof n.cornerRadius === 'number' && n.cornerRadius > 0 ? 'r' : ''}${(n.effects || []).some(e => e.visible !== false) ? 'e' : ''}`;
  if (depth <= 0) return `F(${lay}${paint})`;
  return `F(${lay}${paint})[${n.children.filter(c => c.visible !== false).map(c => sig(c, depth - 1)).join(',')}]`;
}
const sigs = { full: new Map(), shell: new Map() };
function noteStructure(n) {
  if (!('children' in n) || n.type === 'INSTANCE' || n.children.length === 0) return;
  for (const [kind, depth] of [['full', 3], ['shell', 1]]) {
    const s = sig(n, depth);
    if (!sigs[kind].has(s)) sigs[kind].set(s, []);
    sigs[kind].get(s).push(n);
  }
}

let budget = NODE_BUDGET;
async function walk(n, frameName) {
  if (n.visible === false) return;
  budget--;
  if (n.type === 'INSTANCE') {
    const main = await n.getMainComponentAsync();
    const set = main && main.parent && main.parent.type === 'COMPONENT_SET' ? main.parent : main;
    const name = set ? set.name : '(missing component)';
    const e = out.instances[name] || (out.instances[name] = { key: set ? set.key : null, remote: main ? main.remote : null, n: 0, variants: {}, overrides: {}, ex: [] });
    e.n++;
    if (e.ex.length < EXAMPLES) e.ex.push(n.id);
    if (main && set !== main) e.variants[main.name] = (e.variants[main.name] || 0) + 1;
    for (const o of n.overrides || []) for (const f of o.overriddenFields) e.overrides[f] = (e.overrides[f] || 0) + 1;
    const slots = topSlots(n);
    await internals(n, slots);
    for (const s of slots) for (const c of s.children) await walk(c, frameName);
    return;
  }
  if (n.detachedInfo) out.detached.push({ id: n.id, name: n.name, frame: frameName, type: n.detachedInfo.type, key: n.detachedInfo.componentKey || null, componentId: n.detachedInfo.componentId || null });
  const role = n.type === 'TEXT' ? 'text' : SHAPES.has(n.type) ? 'shape' : 'frame';
  await colors(n, role);
  await numbers(n);
  await effects(n);
  if (n.type === 'TEXT') await typography(n);
  noteStructure(n);
  if ('children' in n) for (const c of n.children) await walk(c, frameName);
}

const roots = [];
for (const id of ROOT_IDS) {
  const node = await figma.getNodeByIdAsync(id);
  if (!node) throw new Error(`No node ${id}`);
  if (node.type === 'PAGE') { await node.loadAsync(); roots.push(...node.children); } else roots.push(node);
}
for (let i = OFFSET; i < roots.length; i++) {
  if (budget <= 0) { out.next = i; break; }
  out.roots.push({ id: roots[i].id, name: roots[i].name });
  await walk(roots[i], roots[i].name);
}

// Repeated structures: 3+ matches with at least two levels, outermost first. Shell clusters
// that only repeat a full cluster are dropped.
const rootIds = new Set(out.roots.map(r => r.id));
const seen = new Set();
const clusters = [];
for (const kind of ['full', 'shell']) {
  for (const [s, nodes] of sigs[kind]) {
    const members = nodes.filter(n => !rootIds.has(n.id));
    if (members.length < 3 || !s.includes('[')) continue;
    const ids = members.map(n => n.id).sort();
    const fp = ids.join(',');
    if (seen.has(fp)) continue;
    seen.add(fp);
    const names = {};
    for (const n of members) names[n.name] = (names[n.name] || 0) + 1;
    const insideDetached = members.filter(n => { for (let a = n.parent; a; a = a.parent) if (a.detachedInfo) return true; return false; }).length;
    clusters.push({ kind, n: members.length, size: s.length, names, detached: members.filter(n => n.detachedInfo).length, insideDetached, ids: ids.slice(0, 12), sig: s.slice(0, 300) });
  }
}
clusters.sort((a, b) => b.n * Math.log(b.size) - a.n * Math.log(a.size));
out.structures = clusters.slice(0, MAX_STRUCTURES);
out.structureClusters = clusters.length;
return out;
