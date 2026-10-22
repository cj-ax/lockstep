// Lockstep code-to-Figma: SSkeletonLoader as a draft component set. Run through use_figma in the DRAFT file.
// Safe to retry: removes any existing set with the same name first.
const PROTECTED_FILE_KEYS = ['LMgKpbsEmxRpiHBKd9YGlw'];
if (PROTECTED_FILE_KEYS.includes(figma.fileKey)) throw new Error(`Refusing to write: ${figma.fileKey} is a protected file. Use a draft.`);

const V = {
  bone: '816ab613e4f1e090169fa632ad1aaa58f943841f',     // Primary Colors/background-disable-field (nearest to Vuetify's rgba(on-surface, .12))
  surface: '9aa251a20d0aec20bd2db28c4e62ce5adb7a3c7b',  // Primary Colors/background-surface (Vuetify: rgb(var(--v-theme-surface)))
  r0: '1a664bcec26cde4dae8c9eb50d6ba723e2fb0720', rM: 'cc8c1aa474202f648958851ad7002a9e3dabb369',
  rL: '1564ab3e4c5e49f92472f47707f92d3eb51a245b', pill: '073cbfc72fb979e12180fb4cec7c2737bbcf6707',
  pa0: '60a49ef439417247dafe7583e4e7f5c08e15ea23', pa4: '87fe317f560bbeeb8ef93d02cbd4a17a352c6be3',
  px4: 'f4a99f4a38e5163f77ccc788e091edd5d4feda9b', ga0: '4a127b119409919f7b3d3eb0041b34e885561a22',
  ga2: '0562032ad8aec53e74320b6f7f51aff4273efa94', ga4: 'c39e9ab323c2317dfcadbc7fd291852d5b730be1',
  ga6: 'e3e6edeb7ddf385a94aa9365ab8da416f8e0d2cd', pa8: '267fd6c72c81a443e83fb75724159e472868ba5e',
};
const vars = Object.fromEntries(await Promise.all(Object.entries(V).map(async ([k, key]) => [k, await figma.variables.importVariableByKeyAsync(key)])));

// ---- helpers -------------------------------------------------------------
const paint = (v) => [figma.variables.setBoundVariableForPaint({ type: 'SOLID', color: { r: 0, g: 0, b: 0 } }, 'color', v)];
const SIDES = ['paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft'];
const pad = (f, v) => { for (const p of SIDES) f.setBoundVariable(p, v); };
const radius = (f, v) => { for (const p of ['topLeftRadius', 'topRightRadius', 'bottomLeftRadius', 'bottomRightRadius']) f.setBoundVariable(p, v); };
const stack = (dir, name, { gap = vars.ga0, padding = vars.pa0 } = {}) => {
  const f = figma.createAutoLayout(dir, { name }); f.fills = [];
  f.setBoundVariable('itemSpacing', gap); pad(f, padding); radius(f, vars.r0); return f;
};
// A bone is an auto-layout frame (so the score counts it) with a fixed size and the bone colour.
const bone = (parent, name, w, h, r = vars.pill, fill = false) => {
  const b = stack('HORIZONTAL', name); b.resize(w, h);
  b.primaryAxisSizingMode = 'FIXED'; b.counterAxisSizingMode = 'FIXED';
  b.fills = paint(vars.bone); radius(b, r);
  parent.appendChild(b);
  if (fill) b.layoutSizingHorizontal = 'FILL';
  return b;
};
const add = (parent, child, fill = true) => { parent.appendChild(child); if (fill) child.layoutSizingHorizontal = 'FILL'; return child; };
const root = (type, width, r) => {
  const c = figma.createComponent(); c.name = `type=${type}`;
  c.layoutMode = 'VERTICAL'; c.primaryAxisSizingMode = 'AUTO'; c.counterAxisSizingMode = 'FIXED';
  c.resize(width, 10); c.primaryAxisSizingMode = 'AUTO';
  c.fills = paint(vars.surface); radius(c, r); c.clipsContent = true;
  c.setBoundVariable('itemSpacing', vars.ga0); pad(c, vars.pa0);
  return c;
};
// Vuetify 'heading': 24px pill, 16px margin, max-width 50%.
const heading = (parent, w) => { const h = add(parent, stack('HORIZONTAL', 'heading', { padding: vars.pa4 })); bone(h, 'heading bone', w, 24); return h; };
// Vuetify 'text': 12px pill, 16px margin; text + text gets margin-top -8 (so 8px between lines), 2nd max 50%, 3rd max 70%.
const lines = (parent, name, count, contentW, padding) => {
  const p = add(parent, stack('VERTICAL', name, { gap: vars.ga2, padding }));
  const widths = [1, 0.5, 0.7];
  for (let i = 0; i < count; i++) {
    if (i === 0) bone(p, 'text', contentW, 12, vars.pill, true);
    else bone(p, 'text', Math.round(contentW * widths[i]), 12);
  }
  return p;
};

// ---- variants ------------------------------------------------------------
const W = 452; // showcase surface is max 500px with 24px padding; the component is width:100%
function text() { // 'article' = heading, paragraph(text@3)
  const c = root('text', W, vars.rM);
  heading(c, W / 2);
  lines(c, 'paragraph', 3, W - 32, vars.pa4);
  return c;
}
function card() { // 'card' = image, heading; code: max-width 340, radius 8, overflow hidden
  const c = root('card', 340, vars.rL);
  bone(c, 'image', 340, 150, vars.r0, true);
  heading(c, 170);
  return c;
}
function list() { // three 'list-item-avatar-two-line' = avatar, sentences(text@2); 72px rows
  const c = root('list', W, vars.rM);
  for (let i = 0; i < 3; i++) {
    const row = add(c, stack('HORIZONTAL', 'list-item-avatar-two-line', { gap: vars.ga4 }));
    for (const p of ['paddingLeft', 'paddingRight']) row.setBoundVariable(p, vars.px4);
    row.counterAxisAlignItems = 'CENTER'; row.resize(W, 72); row.counterAxisSizingMode = 'FIXED';
    radius(row, vars.rM);
    bone(row, 'avatar', 48, 48);
    const s = stack('VERTICAL', 'sentences', { gap: vars.ga2 });
    row.appendChild(s); s.layoutSizingHorizontal = 'FILL';
    const sw = W - 16 - 48 - 16 - 16;
    bone(s, 'text', sw, 12, vars.pill, true);
    bone(s, 'text', Math.round(sw / 2), 12);
  }
  return c;
}
function table() { // 'table' = table-heading, table-thead, table-tbody, table-tfoot
  const c = root('table', W, vars.rM);
  const th = add(c, stack('HORIZONTAL', 'table-heading', { padding: vars.pa4 }));
  th.primaryAxisAlignItems = 'SPACE_BETWEEN'; th.counterAxisAlignItems = 'CENTER';
  bone(th, 'chip', 96, 32);
  bone(th, 'text', Math.round((W - 32) * 0.3), 12);
  const thead = add(c, stack('HORIZONTAL', 'table-thead', { padding: vars.pa4 }));
  thead.primaryAxisAlignItems = 'SPACE_BETWEEN';
  for (let i = 0; i < 6; i++) bone(thead, 'heading', 16, 24);
  const tbody = add(c, stack('VERTICAL', 'table-tbody'));
  for (let r = 0; r < 6; r++) {
    const row = add(tbody, stack('HORIZONTAL', 'table-row'));
    row.counterAxisAlignItems = 'CENTER'; row.resize(W, 48); row.counterAxisSizingMode = 'FIXED';
    for (let i = 0; i < 6; i++) {
      const cell = stack('HORIZONTAL', 'cell', { padding: vars.pa4 });
      row.appendChild(cell); cell.layoutSizingHorizontal = 'FILL';
      bone(cell, 'text', 10, 12, vars.pill, true);
    }
    bone(tbody, 'divider', W, 2, vars.r0, true);
  }
  const tf = add(c, stack('HORIZONTAL', 'table-tfoot', { gap: vars.ga4, padding: vars.pa4 }));
  tf.counterAxisAlignItems = 'CENTER';
  bone(tf, 'text', 100, 12, vars.pill, true);
  bone(tf, 'text', 100, 12, vars.pill, true);
  bone(tf, 'avatar', 40, 40);
  bone(tf, 'avatar', 40, 40);
  return c;
}

// ---- page, section, set --------------------------------------------------
let page = figma.root.children.find(p => p.name === 'Code components');
if (!page) { page = figma.root.children.length === 1 && figma.root.children[0].children.length === 0 ? figma.root.children[0] : figma.createPage(); page.name = 'Code components'; }
await figma.setCurrentPageAsync(page);
let section = page.children.find(n => n.type === 'SECTION' && n.name === 'Code components (draft)');
if (!section) { section = figma.createSection(); section.name = 'Code components (draft)'; section.x = 100; section.y = 100; }
for (const old of section.children.filter(n => n.name === 'SSkeletonLoader')) old.remove();

const comps = [text(), card(), list(), table()]; // text first: the code's default
for (const c of comps) section.appendChild(c);
const set = figma.combineAsVariants(comps, section);
set.name = 'SSkeletonLoader';
set.layoutMode = 'HORIZONTAL'; set.counterAxisAlignItems = 'MIN';
set.setBoundVariable('itemSpacing', vars.ga6); pad(set, vars.pa8);
set.primaryAxisSizingMode = 'AUTO'; set.counterAxisSizingMode = 'AUTO';
set.fills = [];
set.x = 80; set.y = 120;
set.description = [
  'Draft from code: src/components/SSkeletonLoader.vue in design-system-beta. Not yet reviewed or published.',
  '',
  'Properties → code props',
  '• type = text | card | list | table → type (default text). Maps to Vuetify loader types: text = "article", card = "card", list = three "list-item-avatar-two-line", table = "table".',
  '• ariaLabel (default "Loading content") is not a Figma property: it is never visible. Hand it to developers: role="status", aria-busy="true".',
  '',
  'From our code: the four types and their Vuetify mapping; width 100%; card max-width 340 and 8px radius; bone colour via --slm-skeleton-bone (inherit in Light, so Vuetify default).',
  'From Vuetify defaults (v-skeleton-loader 3.x, not this repo): every inner layout and size — 24px heading at 50% width, 12px text lines (100/50/70%), 16px margins, 8px between lines, 150px image, 48px avatars in 72px rows, table heading/thead/6 rows/tfoot, 4px loader radius, surface background.',
  'Not modelled: the shimmer animation; Build theme (no Build mode in the library colour collection). Partial-width bars are fixed at the default width.',
  'Bone colour token: Primary Colors/background-disable-field is the nearest library variable (#e0e0e0 = 12% black on white). Proposed: a dedicated skeleton-bone token.',
].join('\n');

// Size the section to fit.
section.resizeWithoutConstraints(Math.max(section.width, set.x + set.width + 80), Math.max(section.height, set.y + set.height + 80));
return { pageId: page.id, sectionId: section.id, setId: set.id, variants: set.children.map(c => `${c.name} ${Math.round(c.width)}x${Math.round(c.height)} ${c.id}`) };
