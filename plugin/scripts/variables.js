// Lockstep learned variables: run through use_figma in a DRAFT file (never the org's library).
// Turns the approved tokens (generate.py's tokens.figma.json) into a local variable collection,
// "Learned tokens", with one mode per theme, and the approved type styles into local text styles.
// Running it again updates the same variables and styles by name, so it's safe to repeat.
// - Scopes follow the token's kind, so Figma only offers spacing for gaps and padding.
// - Each description records the kind and the drift values the token absorbed
//   ("lockstep kind=spacing absorbs=25,23"); rebuild.js reads it to snap drift back.
const TOKENS = __TOKENS__;
const PROTECTED_FILE_KEYS = __PROTECTED_FILE_KEYS__;
if (PROTECTED_FILE_KEYS.includes(figma.fileKey)) throw new Error(`Refusing to write: ${figma.fileKey} is a protected file. Use a draft.`);
const COLLECTION = 'Learned tokens';

const rgba = hex => {
  const n = hex.replace('#', '');
  const c = i => parseInt(n.slice(i, i + 2), 16) / 255;
  return { r: c(0), g: c(2), b: c(4), a: n.length === 8 ? c(6) : 1 };
};
const words = name => name.toLowerCase().split(/[^a-z0-9]+/);
function scopes(t) {
  const w = words(t.name);
  switch (t.kind) {
    case 'color':
      if (w.includes('text') || w.includes('font')) return ['TEXT_FILL'];
      if (w.includes('border') || w.includes('stroke')) return ['STROKE_COLOR'];
      if (w.includes('background') || w.includes('bg') || w.includes('surface')) return ['FRAME_FILL', 'SHAPE_FILL'];
      if (w.includes('icon')) return ['SHAPE_FILL', 'STROKE_COLOR'];
      return ['ALL_FILLS', 'STROKE_COLOR', 'EFFECT_COLOR'];
    case 'spacing': return ['GAP'];
    case 'radius': return ['CORNER_RADIUS'];
    case 'stroke': return ['STROKE_FLOAT'];
    case 'fontSize': return ['FONT_SIZE'];
    case 'fontWeight': return ['FONT_WEIGHT'];
    case 'lineHeight': return ['LINE_HEIGHT'];
    case 'letterSpacing': return ['LETTER_SPACING'];
    case 'fontFamily': return ['FONT_FAMILY'];
    case 'effect': return ['EFFECT_FLOAT'];
    default: return ['ALL_SCOPES'];
  }
}
const typeOf = t => (t.kind === 'color' ? 'COLOR' : t.kind === 'fontFamily' ? 'STRING' : 'FLOAT');
const valueOf = (t, v) => (t.kind === 'color' ? rgba(v) : t.kind === 'fontFamily' ? String(v) : Number(typeof v === 'object' && v ? v.value : v));

// Themes: light first, then the rest in the order tokens name them.
const themes = ['light'];
for (const t of TOKENS.tokens) for (const m of Object.keys(t.values)) if (!themes.includes(m)) themes.push(m);

let col = (await figma.variables.getLocalVariableCollectionsAsync()).find(c => c.name === COLLECTION);
if (!col) col = figma.variables.createVariableCollection(COLLECTION);
col.renameMode(col.modes[0].modeId, themes[0]);
const modeId = {};
for (const m of col.modes) modeId[m.name] = m.modeId;
for (const th of themes) if (!modeId[th]) modeId[th] = col.addMode(th);

const existing = {};
for (const id of col.variableIds) { const v = await figma.variables.getVariableByIdAsync(id); if (v) existing[v.name] = v; }
const out = { collection: col.id, modes: themes, variables: {}, styles: {}, skipped: [] };
for (const t of TOKENS.tokens) {
  const light = t.values.light !== undefined ? t.values.light : Object.values(t.values)[0];
  if (typeof light === 'string' && t.kind !== 'color' && t.kind !== 'fontFamily') { out.skipped.push(`${t.name}: ${light} has no Figma variable type`); continue; }
  let v = existing[t.name];
  if (v && v.resolvedType !== typeOf(t)) { v.remove(); v = null; }
  if (!v) v = figma.variables.createVariable(t.name, col, typeOf(t));
  for (const th of themes) v.setValueForMode(modeId[th], valueOf(t, t.values[th] !== undefined ? t.values[th] : light));
  v.scopes = scopes(t);
  v.description = `lockstep kind=${t.kind}` + (t.absorbs && t.absorbs.length ? ` absorbs=${t.absorbs.join(',')}` : '');
  out.variables[t.name] = { id: v.id, kind: t.kind };
}

// Text styles. Weight maps to the usual style names; a family without that style keeps Regular.
const STYLE = { 100: 'Thin', 200: 'Extra Light', 300: 'Light', 400: 'Regular', 500: 'Medium', 600: 'Semi Bold', 700: 'Bold', 800: 'Extra Bold', 900: 'Black' };
const textStyles = {};
for (const s of await figma.getLocalTextStylesAsync()) textStyles[s.name] = s;
for (const s of TOKENS.typeStyles || []) {
  let fontName = { family: s.fontFamily || 'Inter', style: STYLE[s.fontWeight] || 'Regular' };
  try { await figma.loadFontAsync(fontName); } catch (e) { fontName = { family: fontName.family, style: 'Regular' }; await figma.loadFontAsync(fontName); }
  const st = textStyles[s.name] || figma.createTextStyle();
  st.name = s.name;
  st.fontName = fontName;
  st.fontSize = s.fontSize;
  if (s.lineHeight) st.lineHeight = { unit: 'PIXELS', value: s.lineHeight };
  st.letterSpacing = { unit: 'PIXELS', value: s.letterSpacing || 0 };
  out.styles[s.name] = st.id;
}
return out;
