// Lockstep build: TeamMembers, run through use_figma in a DRAFT file.
// WHICH = list of 'List' | 'Dialog'. Safe to retry: it removes any existing frame with the
// same name first. Every key below came from lockstep/slalom/keys.json or the inventory.
const WHICH = __WHICH__;
const VERSION = __VERSION__;
const PROTECTED_FILE_KEYS = __PROTECTED_FILE_KEYS__;
if (PROTECTED_FILE_KEYS.includes(figma.fileKey)) throw new Error(`Refusing to write: ${figma.fileKey} is a protected file. Use a draft.`);

const C = {
  header: 'a1f1f34b73b954a1533d18ac4330a5ad2d4cfaee', container: 'e33ee7e85bebeab756aab527e05c15b3a1829c6b',
  button: '3a807bad37f01ba6bcca6860fad365113c55afe2', semantic: 'f1b8e09313d2329422f09f5e0ae8f619956feab5',
  textField: 'ebc9ce3c2e9055e1644fa21609b4d7da1b510f48', select: 'c712b2f664e7e1a0a882a607926f6770a36bfe2b',
  chip: '9696389b124a34c473e8540c420cc6cf29aa7982', cell: '04a6e7460ed2de25298e611804aeadd37d23c807',
  modal: 'c80e89aaf48682a718e1eae881ca70e4e9496723',
};
const ICON = { search: 'bde46cd529a37161def963b09aefcf45edb5b487', plus: '66c88db9cdf6da87b5e9f1dcf9a252cb3397ef50' };
const V = {
  pageBg: '91a116c8d0add16d8c319dc62995977f1f26973c', textRegular: '82f040093af673c7804535a216ebb111286a3872',
  textMedium: 'cd9f5777cd48ce8534a9c02326d7bd71a9206209',
  pa6: 'e7de87cb0f77390abaa76950a0539a237c88849b', ga0: '4a127b119409919f7b3d3eb0041b34e885561a22',
  ga2: '0562032ad8aec53e74320b6f7f51aff4273efa94', ga4: 'c39e9ab323c2317dfcadbc7fd291852d5b730be1',
  ga6: 'e3e6edeb7ddf385a94aa9365ab8da416f8e0d2cd',
};
const S = { h4: '75041c6b21a453b35bba16dc950f6dba732d1c7e', body1: 'bc04f5a9ac30e8f94d13610c13160f8b0f33870e', body2: 'a505c525b8cbe17ddbf33d75d84cbb0e7a2a6d1c' };

const sets = Object.fromEntries(await Promise.all(Object.entries(C).map(async ([k, key]) => [k, await figma.importComponentSetByKeyAsync(key)])));
const icons = Object.fromEntries(await Promise.all(Object.entries(ICON).map(async ([k, key]) => [k, await figma.importComponentByKeyAsync(key)])));
const vars = Object.fromEntries(await Promise.all(Object.entries(V).map(async ([k, key]) => [k, await figma.variables.importVariableByKeyAsync(key)])));
const styles = Object.fromEntries(await Promise.all(Object.entries(S).map(async ([k, key]) => [k, await figma.importStyleByKeyAsync(key)])));
await Promise.all([{ family: 'Slalom Sans', style: 'Regular' }, { family: 'Slalom Sans', style: 'Bold' }].map(f => figma.loadFontAsync(f)));

// ---- helpers -------------------------------------------------------------
const variant = (set, props) => {
  const want = Object.entries(props);
  const v = set.children.find(c => { const p = Object.fromEntries(c.name.split(', ').map(x => x.split('='))); return want.every(([k, val]) => p[k] === val); });
  if (!v) throw new Error(`${set.name}: no variant ${JSON.stringify(props)}`);
  return v.createInstance();
};
const propKey = (inst, name) => Object.keys(inst.componentProperties).find(k => k.split('#')[0] === name);
const setProps = (inst, props) => { const o = {}; for (const [n, v] of Object.entries(props)) { const k = propKey(inst, n); if (!k) throw new Error(`${inst.name}: no property ${n}`); o[k] = v; } inst.setProperties(o); return inst; };
const bindPaint = (v) => [figma.variables.setBoundVariableForPaint({ type: 'SOLID', color: { r: 0, g: 0, b: 0 } }, 'color', v)];
const pad = (f, v) => { for (const p of ['paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft']) f.setBoundVariable(p, v); };
const stack = (dir, name, gap) => { const f = figma.createAutoLayout(dir, { name }); f.fills = []; if (gap) f.setBoundVariable('itemSpacing', gap); return f; };
const add = (parent, child, fill = true) => { parent.appendChild(child); if (fill) child.layoutSizingHorizontal = 'FILL'; return child; };
const text = (chars, style, colour, name) => { const t = figma.createText(); t.name = name || chars.slice(0, 24); t.textStyleId = style.id; t.characters = chars; t.fills = bindPaint(colour); return t; };
// findAllWithCriteria({ types: ['SLOT'] }) misses slots of nested instances, so walk the tree.
const slot = (inst, name) => inst.findAll(n => n.type === 'SLOT').find(s => s.name === name);
const clearSlot = (s) => { for (const c of [...s.children]) c.remove(); };
// Plain text layers inside instances (chip label, modal title) can use fonts we haven't loaded.
async function setText(node, chars) {
  for (const seg of node.getStyledTextSegments(['fontName'])) await figma.loadFontAsync(seg.fontName);
  node.characters = chars;
}

function button(label, kind, size = 'md') {
  return setProps(variant(sets.button, { variant: kind, size, status: 'enabled' }), { Text: label, 'icon-left': false, 'icon right': false });
}
function field(label, value, opts = {}) {
  // Empty fields exist only as enabled + has value=false + label on.
  const f = variant(sets.textField, { state: 'enabled', 'has value': 'false', 'Label style': 'label on' });
  setProps(f, { 'field label': label, content: value, 'icon-left': !!opts.icon, 'icon-right': false, 'Assistive Text': !!opts.help, 'is required': !!opts.required });
  if (opts.help) setProps(f, { 'assistive text': opts.help });
  // Both icon frames are named icon-right; the leading one is first in the input box.
  if (opts.icon) { const i = f.findAllWithCriteria({ types: ['INSTANCE'] }).find(n => n.name === 'calendar-month-outline' && n.parent.visible); if (i) i.swapComponent(opts.icon); }
  return f;
}
function select(label, value, opts = {}) {
  const s = variant(sets.select, { status: 'enable', 'has value': 'true', type: 'label on' });
  setProps(s, { 'label text': label, 'dropdown text': value, 'is Required': !!opts.required, 'assistive text': !!opts.help, 'error text': false, 'left icon': false });
  if (opts.help) setProps(s, { 'select assistive text': opts.help });
  return s;
}

// ---- table -----------------------------------------------------------------
// [heading, width (null = fill), alignment]. The cells centre content by default; text columns read better left-aligned.
const COLS = [['Member', null, 'MIN'], ['Role', 200, 'MIN'], ['Status', 180, 'MIN'], ['Actions', 160, 'MAX']];
const MEMBERS = [
  ['Priya Natarajan', 'priya.natarajan@example.com', 'Admin', 'Active'],
  ['Marcus Bell', 'marcus.bell@example.com', 'Editor', 'Active'],
  ['Sofia Alvarez', 'sofia.alvarez@example.com', 'Editor', 'Active'],
  ['Daniel Okafor', 'daniel.okafor@example.com', 'Viewer', 'Active'],
  ['Hannah Kim', 'hannah.kim@example.com', 'Viewer', 'Invited'],
  ['Tomás Reyes', 'tomas.reyes@example.com', 'Editor', 'Invited'],
];
function sizeCell(row, cell, [, width, align]) {
  add(row, cell, false);
  if (width) { cell.resize(width, cell.height); cell.layoutSizingHorizontal = 'FIXED'; } else cell.layoutSizingHorizontal = 'FILL';
  cell.primaryAxisAlignItems = align;
  const lines = cell.findOne(n => n.name === 'Content' && n.type === 'FRAME');
  if (lines) lines.counterAxisAlignItems = align;
}
function headerRow() {
  const row = stack('HORIZONTAL', 'Header row', vars.ga0);
  for (const col of COLS) {
    const c = variant(sets.cell, { Size: '56 Clean Table Cell', 'Table Cell Type': 'Clean Heading' });
    setProps(c, { 'Clean Heading Text': col[0], 'Show Heading Content 2': false, 'Has Right Icon': false, 'Has Left Icon': false, 'Show Info Mark': false, 'Show Avatar': false });
    sizeCell(row, c, col);
  }
  return row;
}
async function slotCell(size, child) {
  const c = variant(sets.cell, { Size: size, 'Table Cell Type': 'Regular' });
  setProps(c, { 'Show Label Group': false, 'Has Right Icon': false, 'Has Left Icon': false, 'Show Avatar': false, 'has slot': true });
  const s = slot(c, 'Slot'); clearSlot(s);
  s.appendChild(child);
  return c;
}
async function memberRow([name, email, role, status], last) {
  const size = last ? '56 Clean Table Last' : '56 Clean Table Cell';
  const row = stack('HORIZONTAL', `Row / ${name}`, vars.ga0);
  const initials = name.split(' ').map(w => w[0]).join('');
  const who = variant(sets.cell, { Size: size, 'Table Cell Type': 'Regular' });
  setProps(who, { 'Show Avatar': true, 'Avatar Initials': initials, 'Cell Content': name, 'Show Content 2': true, 'Cell Content 2': email, 'Has Right Icon': false, 'Has Left Icon': false, 'Show Info Mark': false });
  sizeCell(row, who, COLS[0]);
  const r = variant(sets.cell, { Size: size, 'Table Cell Type': 'Regular' });
  setProps(r, { 'Show Avatar': false, 'Cell Content': role, 'Show Content 2': false, 'Has Right Icon': false, 'Has Left Icon': false, 'Show Info Mark': false });
  sizeCell(row, r, COLS[1]);
  const chip = variant(sets.chip, { 'Chip Type': status === 'Active' ? 'Traditional' : 'Traditional Neutral', Size: 'Small', Density: 'Default' });
  setProps(chip, { 'Show Close Icon': false, 'Show Left Icon': false, 'Show Color Tag': false, 'right icon': false });
  for (const t of chip.findAllWithCriteria({ types: ['TEXT'] })) if (t.visible) await setText(t, status);
  sizeCell(row, await slotCell(size, chip), COLS[2]);
  const remove = setProps(variant(sets.semantic, { semantic: 'negative', variant: 'outlined', Size: 'sm', status: 'default' }), { label: 'Remove', 'icon left': false, 'icon right': false });
  sizeCell(row, await slotCell(size, remove), COLS[3]);
  return row;
}

// ---- page shell ------------------------------------------------------------
const NAMES = ['List', 'Dialog'];
async function buildFrame(which) {
  const name = `TeamMembers / ${which} / v${VERSION}`;
  for (const old of figma.currentPage.children.filter(n => n.name === name)) old.remove();
  const page = figma.createAutoLayout('VERTICAL', { name });
  page.resize(1440, 100);
  page.layoutSizingHorizontal = 'FIXED';
  page.x = NAMES.indexOf(which) * 1540; page.y = VERSION * 1400;
  page.fills = bindPaint(vars.pageBg);

  add(page, variant(sets.header, { Version: 'Default' }));
  const main = add(page, stack('VERTICAL', 'Main', vars.ga6));
  pad(main, vars.pa6);

  if (which === 'List') {
    const section = add(main, variant(sets.container, { type: 'table container' }));
    const s = slot(section, 'header'); clearSlot(s);
    s.setBoundVariable('itemSpacing', vars.ga6);
    const intro = add(s, stack('VERTICAL', 'Page title', vars.ga2));
    add(intro, text('Team members', styles.h4, vars.textRegular, 'Title'));
    add(intro, text('Invite people to this workspace, set what they can do, and remove access when they leave.', styles.body1, vars.textMedium, 'Description'));
    const bar = add(s, stack('HORIZONTAL', 'Toolbar', vars.ga4));
    bar.counterAxisAlignItems = 'MAX';
    add(bar, field('Search', 'Search by name or email', { icon: icons.search }));
    const role = select('Role', 'All roles');
    add(bar, role, false); role.resize(240, role.height); role.layoutSizingHorizontal = 'FIXED';
    // lg is the size the library allows beside a field.
    add(bar, button('Invite member', 'contained_button', 'lg'), false);

    const t = slot(section, 'Table slot'); clearSlot(t);
    const table = add(t, stack('VERTICAL', 'Members table', vars.ga0));
    add(table, headerRow());
    for (const [i, m] of MEMBERS.entries()) add(table, await memberRow(m, i === MEMBERS.length - 1));
    for (const sl of [s, t]) sl.layoutSizingVertical = 'HUG';
    section.layoutSizingVertical = 'HUG';
  }

  if (which === 'Dialog') {
    main.counterAxisAlignItems = 'CENTER';
    main.primaryAxisAlignItems = 'CENTER';
    main.layoutSizingVertical = 'HUG';
    // data is the modal type for data entry; its sample ships 1200 wide, so size it to the form.
    const m = variant(sets.modal, { type: 'data', 'rounded corner': 'true' });
    add(main, m, false);
    m.resize(640, m.height);
    setProps(m, { close: true, 'has icon': false, 'Show CTA Section': true, 'Sentence Case': true });
    await setText(m.findAllWithCriteria({ types: ['TEXT'] }).find(t => t.name === 'Modal content'), 'Invite member');
    const content = slot(m, 'content slot'); clearSlot(content);
    content.setBoundVariable('itemSpacing', vars.ga4);
    add(content, text('We’ll email them a link to join this workspace.', styles.body1, vars.textMedium, 'Message'));
    add(content, field('Email address', 'name@example.com', { required: true }));
    add(content, select('Role', 'Viewer', { required: true, help: 'Viewers can see content, Editors can change it, Admins also manage members.' }));
    content.layoutSizingVertical = 'HUG';
    const cta = slot(m, 'CTA Section'); clearSlot(cta);
    cta.primaryAxisAlignItems = 'MAX';
    cta.setBoundVariable('itemSpacing', vars.ga4);
    cta.appendChild(button('Cancel', 'neutral_outlined'));
    cta.appendChild(button('Send invite', 'contained_button'));
    m.layoutSizingVertical = 'HUG';
  }
  return { id: page.id, name: page.name, size: [page.width, Math.round(page.height)] };
}

const built = [];
for (const which of WHICH) built.push(await buildFrame(which));
return built;
