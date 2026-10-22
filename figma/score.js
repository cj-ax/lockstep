// Lockstep faithfulness score. Run through use_figma (read-only) with ROOT_IDS set to the
// frames to score. Org-agnostic: "library" means any component whose main component is
// remote (published from another file); nothing here knows about Slalom.
//
// What counts:
// - Authored nodes: everything under ROOT that the builder placed. Library instance
//   internals are the library's business and are skipped, except SLOT contents (authored)
//   and paints the builder overrode on an instance (instance.overrides).
// - Content nodes: instances, text, shapes, and frames that paint something
//   (fill, stroke or effect). Pure layout frames are structure, not content.
// - Bindable properties on authored nodes: each visible solid paint (fill/stroke),
//   stroke weight, corner radius, padding and gap on auto layout frames, and text
//   typography (text style or bound font size).
const ROOT_IDS = __ROOT_IDS__;
const MAX_OFFENDERS = 60;

let offenders = [];
const flag = (node, rule, detail) => offenders.push({ id: node.id, name: node.name, rule, detail });

const zero = () => ({
  contentNodes: 0, libraryInstances: 0, localInstances: 0, textNodes: 0, shapes: 0, paintedFrames: 0,
  bindable: 0, bound: 0,
  instancesTotal: 0, detached: 0,
  paints: 0, hardcodedPaints: 0,
  layoutFrames: 0, autoLayoutFrames: 0,
  integrityIssues: 0,
});
let counts = zero();

const SHAPES = new Set(['RECTANGLE', 'ELLIPSE', 'VECTOR', 'LINE', 'POLYGON', 'STAR', 'BOOLEAN_OPERATION']);
const visiblePaints = arr => (Array.isArray(arr) ? arr : []).filter(p => p.visible !== false && (p.opacity === undefined || p.opacity > 0));
const hex = c => '#' + [c.r, c.g, c.b].map(n => Math.round(n * 255).toString(16).padStart(2, '0')).join('');

function checkPaints(node, field, isAuthored) {
  const paints = visiblePaints(node[field]);
  const styleId = field === 'fills' ? node.fillStyleId : node.strokeStyleId;
  for (const p of paints) {
    counts.paints++;
    if (isAuthored && p.type === 'SOLID') counts.bindable++;
    const bound = p.type === 'SOLID' && p.boundVariables && p.boundVariables.color;
    const styled = typeof styleId === 'string' && styleId !== '';
    if (bound || styled) { if (isAuthored && p.type === 'SOLID') counts.bound++; continue; }
    if (p.type === 'IMAGE' || p.type === 'VIDEO') continue;
    counts.hardcodedPaints++;
    flag(node, 'hardcoded-colour', `${field}: ${p.type === 'SOLID' ? hex(p.color) : p.type}`);
  }
}

function checkNumber(node, prop, label) {
  if (!(prop in node)) return;
  const v = node[prop];
  if (typeof v !== 'number' || v === 0) return;
  counts.bindable++;
  const b = node.boundVariables && node.boundVariables[prop];
  if (b) counts.bound++;
  else flag(node, 'unbound-' + label, `${prop}=${v}`);
}

function checkRadius(node) {
  if (!('cornerRadius' in node)) return;
  const props = ['topLeftRadius', 'topRightRadius', 'bottomLeftRadius', 'bottomRightRadius'];
  const vals = props.map(p => node[p]).filter(v => typeof v === 'number');
  if (!vals.some(v => v > 0)) return;
  counts.bindable++;
  const bv = node.boundVariables || {};
  if (props.every(p => !node[p] || bv[p])) counts.bound++;
  else flag(node, 'unbound-radius', `radius=${vals.join('/')}`);
}

function checkText(node) {
  counts.bindable++;
  const styled = typeof node.textStyleId === 'string' && node.textStyleId !== '';
  const boundSize = node.boundVariables && node.boundVariables.fontSize;
  if (styled || boundSize) counts.bound++;
  else flag(node, 'untyped-text', `${typeof node.fontSize === 'number' ? node.fontSize : 'mixed'}px "${node.characters.slice(0, 30)}"`);
}

// Integrity checks. They don't change the faithfulness percentages, but a frame with any
// integrity issue is not done: the library was used, yet the result is visibly wrong.
function checkClipped(node) {
  if (!node.clipsContent || !('children' in node)) return;
  for (const c of node.children) {
    if (c.visible === false || c.layoutPositioning === 'ABSOLUTE') continue;
    if (c.y + c.height > node.height + 1 || c.x + c.width > node.width + 1) {
      counts.integrityIssues++;
      flag(node, 'clipped-content', `"${c.name}" overflows ${Math.round(node.width)}x${Math.round(node.height)}`);
      return;
    }
  }
}

function checkDefaultText(inst, main) {
  // A visible text property still showing the library's sample text ("Button", "Label").
  const owner = main && main.parent && main.parent.type === 'COMPONENT_SET' ? main.parent : main;
  if (!owner) return;
  const defs = owner.componentPropertyDefinitions;
  for (const [key, p] of Object.entries(inst.componentProperties)) {
    if (p.type !== 'TEXT' || !defs[key] || p.value !== defs[key].defaultValue) continue;
    const shown = inst.findAll(n => n.type === 'TEXT' && n.componentPropertyReferences && n.componentPropertyReferences.characters === key)
      .some(n => { for (let a = n; a && a !== inst; a = a.parent) if (a.visible === false) return false; return true; });
    if (shown) { counts.integrityIssues++; flag(inst, 'sample-text', `${key.split('#')[0]} = "${p.value}"`); }
  }
}

async function checkInstanceOverrides(inst) {
  // Paints the builder overrode inside a library instance must still be variables.
  for (const o of inst.overrides || []) {
    if (!o.overriddenFields.some(f => f === 'fills' || f === 'strokes')) continue;
    const n = await figma.getNodeByIdAsync(o.id);
    if (!n) continue;
    for (const field of ['fills', 'strokes']) if (o.overriddenFields.includes(field)) checkPaints(n, field, false);
  }
}

async function walk(node, isRoot) {
  if (node.visible === false) return;
  const t = node.type;

  if (t === 'INSTANCE') {
    counts.instancesTotal++;
    counts.contentNodes++;
    const main = await node.getMainComponentAsync();
    if (main && main.remote) counts.libraryInstances++;
    else { counts.localInstances++; flag(node, 'not-library-instance', main ? `local component "${main.name}"` : 'missing main component'); }
    await checkInstanceOverrides(node);
    checkDefaultText(node, main);
    // Descend only into this instance's own slots: their contents are authored.
    const ownerOf = n => { let p = n.parent; while (p && p.type !== 'INSTANCE') p = p.parent; return p; };
    for (const slot of node.findAllWithCriteria({ types: ['SLOT'] })) {
      if (ownerOf(slot) !== node) continue;
      checkClipped(slot);
      for (const c of slot.children) await walk(c, false);
    }
    return;
  }

  if ('detachedInfo' in node && node.detachedInfo) {
    counts.detached++;
    counts.instancesTotal++;
    flag(node, 'detached-instance', `from ${node.detachedInfo.type} component`);
  }

  if (t === 'TEXT') {
    counts.contentNodes++; counts.textNodes++;
    flag(node, 'not-library-instance', 'raw text');
    checkText(node);
    checkPaints(node, 'fills', true);
    return;
  }

  if (SHAPES.has(t)) {
    counts.contentNodes++; counts.shapes++;
    flag(node, 'not-library-instance', `raw ${t.toLowerCase()}`);
    checkPaints(node, 'fills', true);
    checkPaints(node, 'strokes', true);
    checkRadius(node);
    return;
  }

  if (t === 'FRAME' || t === 'COMPONENT' || t === 'SECTION' || t === 'GROUP' || t === 'SLOT') {
    const paints = visiblePaints(node.fills).length + visiblePaints(node.strokes).length + (node.effects || []).filter(e => e.visible).length;
    if (paints > 0 && !isRoot) { counts.contentNodes++; counts.paintedFrames++; flag(node, 'not-library-instance', 'painted frame'); }
    if (t === 'FRAME' || t === 'COMPONENT') {
      counts.layoutFrames++;
      if (node.layoutMode && node.layoutMode !== 'NONE') {
        counts.autoLayoutFrames++;
        for (const p of ['paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft']) checkNumber(node, p, 'spacing');
        if (node.children.length > 1 && node.primaryAxisAlignItems !== 'SPACE_BETWEEN') checkNumber(node, 'itemSpacing', 'spacing');
      } else if (node.children.length > 0) flag(node, 'no-auto-layout', `${node.children.length} children positioned by x/y`);
    }
    checkPaints(node, 'fills', true);
    checkPaints(node, 'strokes', true);
    if (visiblePaints(node.strokes).length) checkNumber(node, 'strokeWeight', 'stroke-weight');
    checkRadius(node);
    checkClipped(node);
    if ('children' in node) for (const c of node.children) await walk(c, false);
  }
}

const pct = (a, b) => (b === 0 ? 100 : Math.round((1000 * a) / b) / 10);
function score(c) {
  const sc = {
    libraryInstancePct: pct(c.libraryInstances, c.contentNodes),
    boundPropertyPct: pct(c.bound, c.bindable),
    detachedPct: pct(c.detached, c.instancesTotal),
    hardcodedColourPct: pct(c.hardcodedPaints, c.paints),
    autoLayoutPct: pct(c.autoLayoutFrames, c.layoutFrames),
  };
  // One headline number: the mean of the five, with the two "lower is better" ones inverted.
  sc.faithfulness = Math.round((sc.libraryInstancePct + sc.boundPropertyPct + (100 - sc.detachedPct) + (100 - sc.hardcodedColourPct) + sc.autoLayoutPct) / 5);
  sc.integrityIssues = c.integrityIssues;
  return sc;
}

const total = zero();
const frames = [];
const allOffenders = [];
for (const id of ROOT_IDS) {
  const root = await figma.getNodeByIdAsync(id);
  if (!root) throw new Error(`No node ${id}`);
  counts = zero(); offenders = [];
  await walk(root, true);
  for (const k of Object.keys(total)) total[k] += counts[k];
  frames.push({ id, name: root.name, ...score(counts) });
  allOffenders.push(...offenders.map(o => ({ frame: root.name, ...o })));
}
const byRule = {};
for (const o of allOffenders) byRule[o.rule] = (byRule[o.rule] || 0) + 1;
// Most actionable first: visible breakage, then broken links to the library, then raw values.
const RANK = ['clipped-content', 'sample-text', 'detached-instance', 'hardcoded-colour', 'not-library-instance'];
const rank = r => (RANK.includes(r) ? RANK.indexOf(r) : RANK.length);
allOffenders.sort((a, b) => rank(a.rule) - rank(b.rule));
return { scores: score(total), frames, counts: total, offendersByRule: byRule, offenders: allOffenders.slice(0, MAX_OFFENDERS), offenderCount: allOffenders.length };
