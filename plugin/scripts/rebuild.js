// Lockstep rebuild: run through use_figma in the DRAFT learned library, after variables.js.
// Recreates each approved component from snapshot.js's record as a local component on the
// "Learned library" page, bound to the "Learned tokens" variables:
// - colours, padding, gap, radius and stroke width bind to the variable with that value and a
//   scope that fits the use (text colour to a text token); drift values bind to the token that
//   absorbed them (its description says "absorbs=...")
// - text takes the matching local text style, and becomes a text property named after its layer,
//   so a build sets it through the instance instead of editing layers
// - library instances inside are imported by key, with their property values
// - frames that were slots become real slots, empty: slot content belongs to each use
// A component that already exists on the page is left alone; delete it to rebuild it.
// SPEC: snapshot.js's result.
const SPEC = __SPEC__;
const PROTECTED_FILE_KEYS = __PROTECTED_FILE_KEYS__;
if (PROTECTED_FILE_KEYS.includes(figma.fileKey)) throw new Error(`Refusing to write: ${figma.fileKey} is a protected file. Use a draft.`);
const PAGE = 'Learned library';

const rgba = hex => { const n = hex.replace('#', ''); const c = i => parseInt(n.slice(i, i + 2), 16) / 255; return { r: c(0), g: c(2), b: c(4), a: n.length === 8 ? c(6) : 1 }; };
const h2 = n => Math.round(n * 255).toString(16).padStart(2, '0');
const hexOf = c => '#' + h2(c.r) + h2(c.g) + h2(c.b) + (c.a !== undefined && c.a < 0.999 ? h2(c.a) : '');

// Index the learned variables by value: colours by hex, numbers by kind and value.
const col = (await figma.variables.getLocalVariableCollectionsAsync()).find(c => c.name === 'Learned tokens');
if (!col) throw new Error('No "Learned tokens" collection in this file. Run variables.js first.');
const mode = col.modes[0].modeId;
const colors = new Map();
const numbers = new Map();
const add = (m, k, v) => { if (!m.has(k)) m.set(k, []); m.get(k).push(v); };
for (const id of col.variableIds) {
  const v = await figma.variables.getVariableByIdAsync(id);
  const kind = (v.description.match(/kind=(\w+)/) || [])[1];
  const absorbs = ((v.description.match(/absorbs=([^\s]+)/) || [])[1] || '').split(',').filter(Boolean);
  const val = v.valuesByMode[mode];
  if (v.resolvedType === 'COLOR') for (const hx of [hexOf(val), ...absorbs.map(a => a.toLowerCase())]) add(colors, hx, v);
  else if (v.resolvedType === 'FLOAT') for (const n of [val, ...absorbs.map(Number)]) add(numbers, `${kind}:${Math.round(n * 100) / 100}`, v);
}
const ROLE_SCOPE = { text: 'TEXT_FILL', fill: 'FRAME_FILL', shape: 'SHAPE_FILL', stroke: 'STROKE_COLOR' };
const unbound = [];
function colorVar(hex, role, where) {
  const c = colors.get(hex.toLowerCase()) || [];
  const fit = c.find(v => v.scopes.includes(ROLE_SCOPE[role])) || c.find(v => v.scopes.includes('ALL_FILLS') || v.scopes.includes('ALL_SCOPES')) || c[0];
  if (!fit) unbound.push(`${where}: ${role} ${hex}`);
  return fit;
}
function numVar(kind, n, where, prefer) {
  const c = numbers.get(`${kind}:${Math.round(n * 100) / 100}`) || [];
  const v = (prefer && c.find(x => x.name.toLowerCase().includes(prefer))) || c[0];
  if (!v && n) unbound.push(`${where}: ${kind} ${n}`);
  return v;
}
const paint = (hex, role, where) => {
  const p = { type: 'SOLID', color: (({ r, g, b }) => ({ r, g, b }))(rgba(hex)), opacity: rgba(hex).a };
  const v = colorVar(hex, role, where);
  return v ? figma.variables.setBoundVariableForPaint(p, 'color', v) : p;
};

const textStyles = await figma.getLocalTextStylesAsync();
const lh = t => (t.lineHeight.unit === 'PERCENT' ? { unit: 'PIXELS', value: Math.round(t.lineHeight.value * t.size) / 100 } : t.lineHeight);
const ls = t => (t.letterSpacing.unit === 'PERCENT' ? { unit: 'PIXELS', value: Math.round(t.letterSpacing.value * t.size) / 100 } : t.letterSpacing);
function styleFor(t) {
  const want = lh(t);
  return textStyles.find(s => s.fontName.family === t.family && s.fontName.style === t.style && s.fontSize === t.size &&
    (want.unit === 'AUTO' ? s.lineHeight.unit === 'AUTO' : s.lineHeight.unit === 'PIXELS' && Math.abs(s.lineHeight.value - want.value) < 0.6));
}

async function make(spec, parent, comp, path) {
  const where = `${path}/${spec.name}`;
  let n;
  if (spec.type === 'INSTANCE') {
    let main = null;
    try { main = await figma.importComponentByKeyAsync(spec.key); } catch (e) { unbound.push(`${where}: library component ${spec.component} not importable`); return null; }
    n = main.createInstance();
    const keys = Object.keys(n.componentProperties);
    const props = {};
    for (const [base, val] of Object.entries(spec.props || {})) {
      const k = keys.find(x => x.split('#')[0] === base);
      if (k && n.componentProperties[k].type !== 'VARIANT') props[k] = val;
    }
    if (Object.keys(props).length) n.setProperties(props);
  } else if (spec.type === 'TEXT') {
    const t = spec.text;
    await figma.loadFontAsync({ family: t.family, style: t.style });
    n = figma.createText();
    n.fontName = { family: t.family, style: t.style };
    n.characters = t.characters;
    const st = styleFor(t);
    if (st) await n.setTextStyleIdAsync(st.id);
    else { n.fontSize = t.size; n.lineHeight = lh(t); n.letterSpacing = ls(t); unbound.push(`${where}: no text style for ${t.family} ${t.style} ${t.size}`); }
    if (t.textCase && t.textCase !== 'ORIGINAL') n.textCase = t.textCase;
    n.textAlignHorizontal = t.align;
    if (spec.fills) n.fills = spec.fills.map(h => paint(h, 'text', where));
  } else if (spec.type === 'VECTOR') {
    n = figma.createVector();
    n.vectorPaths = spec.paths;
    if (spec.fills) n.fills = spec.fills.map(h => paint(h, 'shape', where));
  } else if (spec.slot && comp && parent.id === comp.id) {
    n = comp.createSlot();
  } else {
    n = parent ? figma.createFrame() : figma.createComponent();
  }
  n.name = spec.name;
  if (parent && n.parent?.id !== parent.id) parent.appendChild(n);
  if (spec.hidden) n.visible = false;
  if (spec.type === 'TEXT' || spec.type === 'INSTANCE') { /* sized below */ }
  else {
    if ('layoutMode' in n && spec.layout) {
      const L = spec.layout;
      n.layoutMode = L.mode;
      n.primaryAxisAlignItems = L.primary; n.counterAxisAlignItems = L.counter;
      n.primaryAxisSizingMode = L.primarySizing; n.counterAxisSizingMode = L.counterSizing;
      n.layoutWrap = L.wrap || 'NO_WRAP';
      for (const [prop, val] of [['paddingTop', L.pt], ['paddingRight', L.pr], ['paddingBottom', L.pb], ['paddingLeft', L.pl]]) {
        n[prop] = val; const v = numVar('spacing', val, where); if (v) n.setBoundVariable(prop, v);
      }
      n.itemSpacing = L.gap;
      if (L.primary !== 'SPACE_BETWEEN') { const v = numVar('spacing', L.gap, where); if (v) n.setBoundVariable('itemSpacing', v); }
    }
    if ('clipsContent' in n && spec.clips !== undefined) n.clipsContent = spec.clips;
    if ('fills' in n && spec.type !== 'VECTOR') n.fills = (spec.fills || []).map(h => paint(h, 'fill', where));
    if (spec.strokes) {
      n.strokes = spec.strokes.map(h => paint(h, 'stroke', where));
      n.strokeAlign = spec.strokeAlign || 'INSIDE';
      const w = spec.strokeWeight || 1;
      const v = numVar('stroke', w, where);
      for (const p of ['strokeTopWeight', 'strokeRightWeight', 'strokeBottomWeight', 'strokeLeftWeight']) { n[p] = w; if (v) n.setBoundVariable(p, v); }
    }
    if (spec.radius && 'topLeftRadius' in n) {
      ['topLeftRadius', 'topRightRadius', 'bottomRightRadius', 'bottomLeftRadius'].forEach((p, i) => {
        n[p] = spec.radius[i]; const v = numVar('radius', spec.radius[i], where); if (v) n.setBoundVariable(p, v);
      });
    }
    if (spec.effects) n.effects = spec.effects.map(e => {
      if (!e.type.includes('SHADOW')) {
        const eff = { type: e.type, radius: e.blur, visible: true, ...(e.type === 'BACKGROUND_BLUR' ? {} : { blurType: 'NORMAL' }) };
        const v = numVar('effect', e.blur, where, 'blur');
        return v ? figma.variables.setBoundVariableForEffect(eff, 'radius', v) : eff;
      }
      return { type: e.type, color: rgba(e.color), offset: { x: e.x, y: e.y }, radius: e.blur, spread: e.spread, visible: true, blendMode: 'NORMAL' };
    });
    if (spec.opacity !== undefined) n.opacity = spec.opacity;
    if (!spec.slot) for (const c of spec.children || []) await make(c, n, comp || n, where);
  }
  // Size: fixed sizes first, then the sizing modes, which only work inside auto layout.
  if (spec.type !== 'TEXT' && !(spec.type === 'INSTANCE')) {
    // an empty slot starts short; the example's height came from its content
    n.resize(Math.max(1, spec.w), spec.slot ? 40 : Math.max(1, spec.h));
    // resize() fixes both axes; put back hugging where the original hugged
    if (spec.layout) { n.primaryAxisSizingMode = spec.layout.primarySizing; n.counterAxisSizingMode = spec.layout.counterSizing; }
  }
  if (spec.type === 'TEXT') { n.resize(Math.max(1, spec.w), Math.max(1, spec.h)); n.textAutoResize = spec.text.autoResize; }
  if (spec.x !== undefined) { n.x = spec.x; n.y = spec.y; }
  const inAuto = parent && parent.layoutMode && parent.layoutMode !== 'NONE';
  if (inAuto && spec.sizeH) { n.layoutSizingHorizontal = spec.sizeH; n.layoutSizingVertical = spec.sizeV; }
  if (spec.absolute && inAuto) n.layoutPositioning = 'ABSOLUTE';
  for (const [k, v] of Object.entries(spec.limits || {})) if (k in n) n[k] = v;
  return n;
}

const ownLayers = (comp, test) => comp.findAll(x => {
  if (!test(x)) return false;
  for (let p = x.parent; p && p.id !== comp.id; p = p.parent) if (p.type === 'INSTANCE') return false;
  return true;
});
async function textProps(comp) {
  // Text layers in a detached copy are named after what they say ("Personal information"), so
  // name each property by role: the text style when it's the only text, else Label,
  // Description, Text 3...
  const texts = ownLayers(comp, x => x.type === 'TEXT');
  const used = new Set();
  for (const [i, t] of texts.entries()) {
    const style = typeof t.textStyleId === 'string' && t.textStyleId ? (await figma.getStyleByIdAsync(t.textStyleId)).name.split('/').pop() : null;
    let name = t.name !== t.characters ? t.name : texts.length === 1 && style ? style : (['Label', 'Description'][i] || `Text ${i + 1}`);
    for (let k = 2; used.has(name); k++) name = `${name.replace(/ \d+$/, '')} ${k}`;
    used.add(name);
    t.componentPropertyReferences = { characters: comp.addComponentProperty(name, 'TEXT', t.characters) };
  }
  // Library instances inside (a button group's buttons, a dialog's body) are exposed, so a
  // build sets their properties and slots through this component's instances.
  for (const inst of ownLayers(comp, x => x.type === 'INSTANCE')) inst.isExposedInstance = true;
}

let page = figma.root.children.find(p => p.name === PAGE);
if (!page) { page = figma.createPage(); page.name = PAGE; }
await page.loadAsync();
const out = { page: page.id, components: {}, skipped: [], unbound };
let x = 0;
for (const c of page.children) x = Math.max(x, c.x + c.width + 80);
for (const [name, spec] of Object.entries(SPEC.components)) {
  const existing = page.children.find(c => c.type === 'COMPONENT' && c.name === name);
  if (existing) { out.skipped.push(name); out.components[name] = { id: existing.id, key: existing.key }; continue; }
  const comp = await make({ ...spec, name }, null, null, name);
  page.appendChild(comp);
  comp.x = x; comp.y = 0; x += comp.width + 80;
  await textProps(comp);
  comp.description = `Rebuilt by Lockstep from an approved example ("${spec.name}"). Text and slots are set per use.`;
  out.components[name] = { id: comp.id, key: comp.key, props: Object.keys(comp.componentPropertyDefinitions).map(k => k.split('#')[0]) };
}
return out;
