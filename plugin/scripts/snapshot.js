// Lockstep snapshot (read-only): record an approved component's example layers as data, so
// rebuild.js can recreate it in a draft library. The org's files stay untouched, and the plugin
// API can't copy layers between files anyway.
// SPEC: { component name: example node id } (generate.py writes it from the approved components).
// Each node records its layout, size, paints (hex), corner radius, stroke, effects and text;
// a library instance inside records its component key and property values instead of its
// layers. A frame named like a slot ("Slot", "content slot") is marked so rebuild makes it one;
// what it holds is only counted.
const SPEC = __SPEC__;
const MAX_NODES = 400;

const h2 = n => Math.round(n * 255).toString(16).padStart(2, '0');
const hex = (c, o = 1) => { const a = (c.a === undefined ? 1 : c.a) * o; return '#' + h2(c.r) + h2(c.g) + h2(c.b) + (a < 0.999 ? h2(a) : ''); };
const paints = arr => (Array.isArray(arr) ? arr : []).filter(p => p.visible !== false && p.type === 'SOLID').map(p => hex(p.color, p.opacity === undefined ? 1 : p.opacity));
let count = 0;

async function snap(n, isRoot) {
  if (++count > MAX_NODES) return null;
  const o = { type: n.type, name: n.name, w: Math.round(n.width * 100) / 100, h: Math.round(n.height * 100) / 100 };
  if (!isRoot && n.parent && (!n.parent.layoutMode || n.parent.layoutMode === 'NONE')) { o.x = n.x; o.y = n.y; }
  if (n.visible === false) o.hidden = true;
  if ('layoutSizingHorizontal' in n && !isRoot) { o.sizeH = n.layoutSizingHorizontal; o.sizeV = n.layoutSizingVertical; }
  if (n.layoutPositioning === 'ABSOLUTE') o.absolute = true;
  for (const k of ['minWidth', 'maxWidth', 'minHeight', 'maxHeight']) if (k in n && n[k] != null) (o.limits = o.limits || {})[k] = n[k];
  if (n.type === 'INSTANCE') {
    const main = await n.getMainComponentAsync();
    o.key = main ? main.key : null;
    o.component = main ? (main.parent && main.parent.type === 'COMPONENT_SET' ? `${main.parent.name} / ${main.name}` : main.name) : null;
    o.props = {};
    for (const [k, v] of Object.entries(n.componentProperties)) if (v.type !== 'INSTANCE_SWAP') o.props[k.split('#')[0]] = v.value;
    return o;
  }
  if ('fills' in n) { const f = paints(n.fills); if (f.length) o.fills = f; }
  if ('strokes' in n) { const s = paints(n.strokes); if (s.length) { o.strokes = s; o.strokeWeight = n.strokeWeight; o.strokeAlign = n.strokeAlign; } }
  if ('effects' in n && n.effects.some(e => e.visible !== false)) o.effects = n.effects.filter(e => e.visible !== false).map(e => e.type.includes('SHADOW')
    ? { type: e.type, x: e.offset.x, y: e.offset.y, blur: e.radius, spread: e.spread || 0, color: hex(e.color) } : { type: e.type, blur: e.radius });
  if ('opacity' in n && n.opacity < 1) o.opacity = n.opacity;
  if ('topLeftRadius' in n && [n.topLeftRadius, n.topRightRadius, n.bottomRightRadius, n.bottomLeftRadius].some(r => r)) o.radius = [n.topLeftRadius, n.topRightRadius, n.bottomRightRadius, n.bottomLeftRadius];
  if (n.type === 'TEXT') {
    const font = typeof n.fontName === 'object' ? n.fontName : n.getRangeFontName(0, 1);
    o.text = { characters: n.characters, family: font.family, style: font.style, size: typeof n.fontSize === 'number' ? n.fontSize : n.getRangeFontSize(0, 1),
      lineHeight: typeof n.lineHeight === 'object' && n.lineHeight.unit ? n.lineHeight : n.getRangeLineHeight(0, 1),
      letterSpacing: typeof n.letterSpacing === 'object' && n.letterSpacing.unit ? n.letterSpacing : n.getRangeLetterSpacing(0, 1),
      textCase: typeof n.textCase === 'string' ? n.textCase : 'ORIGINAL', align: n.textAlignHorizontal, autoResize: n.textAutoResize };
    return o;
  }
  if (n.type === 'VECTOR') { o.paths = n.vectorPaths; return o; }
  if ('layoutMode' in n) {
    o.clips = n.clipsContent;
    if (n.layoutMode && n.layoutMode !== 'NONE') o.layout = { mode: n.layoutMode, pt: n.paddingTop, pr: n.paddingRight, pb: n.paddingBottom, pl: n.paddingLeft,
      gap: n.itemSpacing, primary: n.primaryAxisAlignItems, counter: n.counterAxisAlignItems, primarySizing: n.primaryAxisSizingMode,
      counterSizing: n.counterAxisSizingMode, wrap: n.layoutWrap };
  }
  if (n.type === 'SLOT' || (!isRoot && /(^|\s)slot($|\s)/i.test(n.name))) {
    // Slot content belongs to each use, not to the component: count it, don't record it.
    o.slot = true;
    o.slotContent = 'children' in n ? n.children.length : 0;
    return o;
  }
  if ('children' in n) {
    o.children = [];
    for (const c of n.children) { const s = await snap(c, false); if (s) o.children.push(s); }
  }
  return o;
}

const out = { components: {}, missing: [] };
for (const [name, id] of Object.entries(SPEC)) {
  const n = await figma.getNodeByIdAsync(id);
  if (!n) { out.missing.push(name); continue; }
  count = 0;
  out.components[name] = await snap(n, true);
  if (count > MAX_NODES) out.components[name].truncated = true;
}
return out;
