// Degrade the pristine SDS settings frames into a half-built design system, deterministically,
// and log every change. Run through use_figma in the FIXTURE DRAFT after capture_truth.js.
// ROOT_IDS: the pristine frames. Re-running on already-degraded frames is not supported:
// rebuild the pristine frames first.
const ROOT_IDS = __ROOT_IDS__;
const PROTECTED_FILE_KEYS = __PROTECTED_FILE_KEYS__;
if (PROTECTED_FILE_KEYS.includes(figma.fileKey)) throw new Error(`Refusing to write: ${figma.fileKey} is a protected file. Use a draft.`);

// Seeded PRNG (mulberry32), so the same pristine frames always degrade the same way.
let seed = 20261022;
const rand = () => { seed |= 0; seed = (seed + 0x6D2B79F5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };

// Components the org "never published": every authored instance is detached.
const UNPUBLISHED = new Set(['Card (Slot)', 'Button Group', 'Switch Field', 'Text Heading', 'Tabs']);
// Components still in the library: about half of their authored instances are detached anyway.
const DETACH_SHARE = 0.5;
// Bindings on authored layers replaced by raw values; the rest go to the WIP collection.
const UNBIND_SHARE = 0.8;
// The half-built token collection: SDS token -> local WIP name. Two extra tokens are noise.
const WIP = {
  'Background/Default/Default': 'bg/white', 'Text/Default/Default': 'text/primary',
  'Border/Default/Default': 'border/light', 'Background/Brand/Default': 'brand/dark',
  'Space/200': 'spacing-xs', 'Space/400': 'spacing-m', 'Space/600': 'spacing-l', 'Space/800': 'spacing-xl',
  'Radius/200': 'radius-md', 'Stroke/Border': 'border-w',
};
const WIP_NOISE = [['blue-accent', 'COLOR', { r: 0.231, g: 0.51, b: 0.965 }], ['spacing-s', 'FLOAT', 6]];

const hex = c => '#' + [c.r, c.g, c.b].map(n => Math.round(n * 255).toString(16).padStart(2, '0')).join('');
const isInside = (x, anc) => { for (let p = x.parent; p; p = p.parent) if (p.id === anc.id) return true; return false; };
async function setName(inst) { const m = await inst.getMainComponentAsync(); return m ? (m.parent && m.parent.type === 'COMPONENT_SET' ? m.parent.name : m.name) : '?'; }
await Promise.all(['Regular', 'Medium', 'Semi Bold', 'Bold'].map(style => figma.loadFontAsync({ family: 'Inter', style })));

const roots = [];
for (const id of ROOT_IDS) roots.push(await figma.getNodeByIdAsync(id));

// Authored instances: outside library internals, or inside any slot.
async function authoredInstances(root) {
  const out = [];
  async function walk(n) {
    if (n.type === 'INSTANCE') {
      out.push(n);
      const all = n.findAll(x => x.type === 'SLOT');
      const slots = all.filter(s => !all.some(o => o.id !== s.id && isInside(s, o)));
      for (const s of slots) for (const c of s.children) await walk(c);
      return;
    }
    if ('children' in n) for (const c of n.children) await walk(c);
  }
  await walk(root);
  return out;
}

// 1. Detach. Innermost first: detaching an outer instance can renumber the instances inside
// its slots, but detaching an inner one never renumbers its parent.
const detached = [];
for (const root of roots) {
  const insts = await authoredInstances(root);
  const plan = [];
  for (const inst of insts) {
    const name = await setName(inst);
    if (name === 'Navigation Pill') continue; // the Header's own sample navigation
    if (UNPUBLISHED.has(name) || rand() < DETACH_SHARE) plan.push([inst.id, name]);
  }
  for (const [id, name] of plan.reverse()) {
    const inst = await figma.getNodeByIdAsync(id);
    if (!inst || inst.type !== 'INSTANCE') continue;
    const frame = inst.detachInstance();
    detached.push({ frame: root.name, node: frame.id, from: name, unpublished: UNPUBLISHED.has(name) });
  }
}

// 2. The WIP token collection.
const wipCol = figma.variables.createVariableCollection('Tokens (WIP)');
const mode = wipCol.modes[0].modeId;
const wipBySds = new Map();
const wipLog = [];
async function sdsValue(v) {
  let val = v.valuesByMode[Object.keys(v.valuesByMode)[0]];
  for (let i = 0; i < 6 && val && val.type === 'VARIABLE_ALIAS'; i++) {
    const a = await figma.variables.getVariableByIdAsync(val.id);
    val = a.valuesByMode[Object.keys(a.valuesByMode)[0]];
  }
  return val;
}

// 3. Unbind or rebind every binding on authored layers (now including detached frames).
const counts = { paintsRaw: 0, paintsWip: 0, numbersRaw: 0, numbersWip: 0, effectsRaw: 0, textStylesRemoved: 0, textStylesKept: 0 };
const rawPaints = []; // candidates for drift: [node id, field, index]
const rawNumbers = [];
const NUM_PROPS = ['paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft', 'itemSpacing', 'counterAxisSpacing', 'topLeftRadius', 'topRightRadius', 'bottomLeftRadius', 'bottomRightRadius', 'strokeTopWeight', 'strokeRightWeight', 'strokeBottomWeight', 'strokeLeftWeight', 'fontSize', 'fontWeight', 'fontFamily', 'lineHeight', 'letterSpacing', 'paragraphSpacing', 'width', 'height', 'minWidth', 'maxWidth', 'minHeight', 'maxHeight'];

async function wipVarFor(sdsVar) {
  const wipName = WIP[sdsVar.name];
  if (!wipName) return null;
  if (!wipBySds.has(sdsVar.name)) {
    const v = figma.variables.createVariable(wipName, wipCol, sdsVar.resolvedType);
    v.setValueForMode(mode, await sdsValue(sdsVar));
    v.scopes = ['ALL_SCOPES'];
    wipBySds.set(sdsVar.name, v);
    wipLog.push({ wip: wipName, sds: sdsVar.name });
  }
  return wipBySds.get(sdsVar.name);
}

async function degradeNode(n) {
  for (const field of ['fills', 'strokes']) {
    if (!Array.isArray(n[field]) || !n[field].length) continue;
    let changed = false;
    const next = [];
    for (const [i, p] of n[field].entries()) {
      const b = p.boundVariables && p.boundVariables.color;
      if (!b) { next.push(p); if (p.type === 'SOLID') rawPaints.push([n.id, field, i]); continue; }
      const v = await figma.variables.getVariableByIdAsync(b.id);
      const raw = { type: 'SOLID', color: { ...p.color }, opacity: p.opacity, visible: p.visible, blendMode: p.blendMode };
      const wip = rand() >= UNBIND_SHARE && v ? await wipVarFor(v) : null;
      if (wip) { next.push(figma.variables.setBoundVariableForPaint(raw, 'color', wip)); counts.paintsWip++; }
      else { next.push(raw); counts.paintsRaw++; rawPaints.push([n.id, field, i]); }
      changed = true;
    }
    if (changed) n[field] = next;
  }
  const bv = n.boundVariables || {};
  for (const prop of NUM_PROPS) {
    const b = bv[prop];
    if (!b || Array.isArray(b)) continue;
    const v = await figma.variables.getVariableByIdAsync(b.id);
    const wip = rand() >= UNBIND_SHARE && v ? await wipVarFor(v) : null;
    try {
      if (wip) { n.setBoundVariable(prop, wip); counts.numbersWip++; }
      else { n.setBoundVariable(prop, null); counts.numbersRaw++; if (/padding|Spacing/.test(prop)) rawNumbers.push([n.id, prop]); }
    } catch (e) { /* some text properties can't be rebound per node; leave them */ }
  }
  if (Array.isArray(n.effects) && n.effects.some(e => e.boundVariables && Object.keys(e.boundVariables).length)) {
    n.effects = n.effects.map(e => { const c = { ...e }; delete c.boundVariables; return c; });
    counts.effectsRaw++;
  }
  if (n.type === 'TEXT' && typeof n.textStyleId === 'string' && n.textStyleId) {
    if (rand() < UNBIND_SHARE) { await n.setTextStyleIdAsync(''); counts.textStylesRemoved++; } else counts.textStylesKept++;
  }
}

async function walkAuthored(n) {
  if (n.visible === false) return;
  if (n.type === 'INSTANCE') {
    // Library internals stay as the library made them; only slot contents are authored.
    const all = n.findAll(x => x.type === 'SLOT');
    const slots = all.filter(s => !all.some(o => o.id !== s.id && isInside(s, o)));
    for (const s of slots) for (const c of s.children) await walkAuthored(c);
    return;
  }
  await degradeNode(n);
  if ('children' in n) for (const c of n.children) await walkAuthored(c);
}
for (const root of roots) await walkAuthored(root);

for (const [name, type, value] of WIP_NOISE) {
  const v = figma.variables.createVariable(name, wipCol, type);
  v.setValueForMode(mode, value);
  wipLog.push({ wip: name, sds: null, noise: true });
}

// 4. Drift: nudge a few raw values by a hair, as people do when they eyedrop or type by hand.
const drift = [];
const pick = (arr, k) => { const a = [...arr]; const out = []; while (a.length && out.length < k) out.push(a.splice(Math.floor(rand() * a.length), 1)[0]); return out; };
for (const [id, field, i] of pick(rawPaints, 6)) {
  const n = await figma.getNodeByIdAsync(id);
  const paints = [...n[field]]; const p = paints[i];
  if (!p || p.type !== 'SOLID' || (p.boundVariables && p.boundVariables.color)) continue;
  const from = hex(p.color);
  const c = { ...p.color, r: Math.min(1, Math.max(0, p.color.r + (p.color.r > 0.5 ? -2 : 2) / 255)) };
  paints[i] = { ...p, color: c };
  n[field] = paints;
  drift.push({ node: id, name: n.name, prop: field, from, to: hex(c) });
}
for (const [id, prop] of pick(rawNumbers, 4)) {
  const n = await figma.getNodeByIdAsync(id);
  if (!n || typeof n[prop] !== 'number' || n[prop] === 0) continue;
  const from = n[prop];
  n[prop] = from + (rand() < 0.5 ? -1 : 1);
  drift.push({ node: id, name: n.name, prop, from, to: n[prop] });
}

// 5. A half-started local library nobody uses yet: three deleted parts rebuilt as local components.
const libPage = figma.createPage();
libPage.name = 'Library (WIP)';
const local = [];
const LOCAL = [['938ddbc1add07bdc6bbec6388327aa27d9d04868', 'Card / Base', false], ['035ac61042305c533b39b786ff35ab1164bdd068', 'Section Heading', false], ['7a8dc511d7173ec44c06ef0e8b1a5a6947c4a19c', 'Toggle row', true]];
let x = 0;
for (const [key, name, isSet] of LOCAL) {
  const src = isSet ? (await figma.importComponentSetByKeyAsync(key)).defaultVariant : await figma.importComponentByKeyAsync(key);
  const frame = src.createInstance().detachInstance();
  const comp = figma.createComponentFromNode(frame);
  comp.name = name;
  libPage.appendChild(comp);
  comp.x = x; comp.y = 0; x += comp.width + 80;
  local.push({ id: comp.id, name, from: src.parent && src.parent.type === 'COMPONENT_SET' ? src.parent.name : src.name });
}

for (const root of roots) root.name = root.name.replace(/^SDS UserSettings \/ (.*) \/ v0$/, 'Settings / $1');
return { frames: roots.map(r => ({ id: r.id, name: r.name })), detached, wip: wipLog, counts, drift, local };
