// Lockstep build: UserSettings on Figma's Simple Design System (second test library).
// Same page as build-settings.js; only the library mapping differs. Run through use_figma
// in a DRAFT file. WHICH = list of 'Profile' | 'Notifications' | 'Account' | 'Dialog';
// VERSION picks the canvas row. Safe to retry: it removes frames with the same name first.
// Keys came from search_design_system and scripts/inventory.js (keys.sds.json).
const WHICH = __WHICH__;
const VERSION = __VERSION__;
const PROTECTED_FILE_KEYS = __PROTECTED_FILE_KEYS__;
if (PROTECTED_FILE_KEYS.includes(figma.fileKey)) throw new Error(`Refusing to write: ${figma.fileKey} is a protected file. Use a draft.`);

const SETS = {
  header: 'a1f69d8fdde4a1fe8523e49d3baa3c8464ad17d2', tab: '18aa207708b43593a2af7096b2dfd531553f3414',
  input: 'c28150b04d333d34ed9d2b77abd9f2f54e1a878a', switchField: '7a8dc511d7173ec44c06ef0e8b1a5a6947c4a19c',
  button: 'cc8b558dc7d9684011b6b99ce8e6509399bc836b', danger: '3d3073170c1014cfacc5d047c23495cfed01e0a8',
  buttonGroup: '97bcba06a0df2ebfe08cd2efa567d04536ace541', dialogBody: '629a55849475c74b3aeea85d7de846e271cf504f',
};
const COMPONENTS = {
  titlePage: 'f1e2f812cd9a9e7babb0032e88b57c4d681e8bbb', heading: '035ac61042305c533b39b786ff35ab1164bdd068',
  text: 'fbaca594bc38824e75467b952cbca0a976c46856', tabs: 'b839f8a495ef7b0ef0a47ad1aefd6e05438825b5',
  cardSlot: '938ddbc1add07bdc6bbec6388327aa27d9d04868', dialog: '050bf5b28eb08c43b117646b3e4b00c9db55c540',
};
const V = {
  pageBg: 'a4865545b526a5b3399a512667f40c9efe0c2fc4', s200: '15bb1c0f339146e931cf0dc15f89ed57dcbd907e',
  s400: '16bc6f84b6e7e20e4234ef79030ee580ec0f4505', s600: 'be3115966ea99eef888c9f25751b54695c7e88d2',
  s800: '9acadea8b7c7c9884455b896e21c88b8bc62d6da',
};

const sets = Object.fromEntries(await Promise.all(Object.entries(SETS).map(async ([k, key]) => [k, await figma.importComponentSetByKeyAsync(key)])));
const comps = Object.fromEntries(await Promise.all(Object.entries(COMPONENTS).map(async ([k, key]) => [k, await figma.importComponentByKeyAsync(key)])));
const vars = Object.fromEntries(await Promise.all(Object.entries(V).map(async ([k, key]) => [k, await figma.variables.importVariableByKeyAsync(key)])));
await Promise.all(['Regular', 'Semi Bold', 'Bold'].map(style => figma.loadFontAsync({ family: 'Inter', style })));

// ---- helpers (same shape as the Slalom build) ---------------------------------
const variantComponent = (set, props) => {
  const want = Object.entries(props);
  const v = set.children.find(c => { const p = Object.fromEntries(c.name.split(', ').map(x => x.split('='))); return want.every(([k, val]) => p[k] === val); });
  if (!v) throw new Error(`${set.name}: no variant ${JSON.stringify(props)}`);
  return v;
};
const variant = (set, props) => variantComponent(set, props).createInstance();
const propKey = (inst, name) => Object.keys(inst.componentProperties).find(k => k.split('#')[0] === name);
const setProps = (inst, props) => { const o = {}; for (const [n, v] of Object.entries(props)) { const k = propKey(inst, n); if (!k) throw new Error(`${inst.name}: no property ${n}`); o[k] = v; } inst.setProperties(o); return inst; };
const bindPaint = (v) => [figma.variables.setBoundVariableForPaint({ type: 'SOLID', color: { r: 1, g: 1, b: 1 } }, 'color', v)];
const pad = (f, v) => { for (const p of ['paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft']) f.setBoundVariable(p, v); };
const stack = (dir, name, gap) => { const f = figma.createAutoLayout(dir, { name }); f.fills = []; if (gap) f.setBoundVariable('itemSpacing', gap); return f; };
const add = (parent, child, fill = true) => { parent.appendChild(child); if (fill) child.layoutSizingHorizontal = 'FILL'; return child; };
// findAllWithCriteria({ types: ['SLOT'] }) misses slots of an instance nested in another
// instance (the Dialog's Dialog Body), so walk the tree instead.
const slotOf = (inst) => inst.findAll(n => n.type === 'SLOT').find(s => { let p = s.parent; while (p && p.type !== 'INSTANCE') p = p.parent; return p && p.id === inst.id; });
const clearSlot = (s) => { for (const c of [...s.children]) c.remove(); };

// Text is a library component here, not a styled text layer.
const textComp = (comp, chars) => setProps(comp.createInstance(), { Text: chars });
// A text component set to FILL still keeps an auto-width text layer inside, which runs past
// the card and gets cut off. Make the inner layer fill and wrap.
const addText = (parent, inst) => {
  add(parent, inst);
  for (const t of inst.findAll(n => n.type === 'TEXT')) {
    if (t.parent.layoutMode && t.parent.layoutMode !== 'NONE') t.layoutSizingHorizontal = 'FILL';
    t.textAutoResize = 'HEIGHT';
  }
  return inst;
};
function field(label, value) { return setProps(variant(sets.input, { State: 'Default', 'Value Type': 'Default' }), { Label: label, Value: value }); }
function button(label, kind) {
  if (kind === 'danger') return setProps(variant(sets.danger, { Variant: 'Primary', State: 'Default', Size: 'Medium' }), { Label: label });
  return setProps(variant(sets.button, { Variant: kind, State: 'Default', Size: 'Medium' }), { Label: label });
}
// A Button Group, aligned end, with its two nested buttons configured: [label, kind] pairs.
function actions(start, end) {
  const g = variant(sets.buttonGroup, { Align: 'End' });
  setProps(g, { 'Button Start': !!start, 'Button End': !!end });
  const nearestInstance = n => { let p = n.parent; while (p && p.type !== 'INSTANCE') p = p.parent; return p; };
  // Label the buttons that are still visible, in order: which nested button the "Button
  // Start" / "Button End" booleans hide is the library's business, not ours.
  const shown = g.findAllWithCriteria({ types: ['INSTANCE'] }).filter(i => { const o = nearestInstance(i); return o && o.id === g.id && i.visible; });
  const specs = [start, end].filter(Boolean);
  for (const [i, inst] of shown.entries()) {
    const spec = specs[i];
    if (!spec) continue;
    const [label, kind] = spec;
    if (kind === 'danger') inst.swapComponent(variantComponent(sets.danger, { Variant: 'Primary', State: 'Default', Size: 'Medium' }));
    else inst.setProperties({ Variant: kind });
    setProps(inst, { Label: label });
  }
  return g;
}
// Card (Slot): a generic card whose slot takes any content. Grow with the content.
function card(title, subtitle) {
  const c = comps.cardSlot.createInstance();
  const s = slotOf(c); clearSlot(s);
  s.setBoundVariable('itemSpacing', vars.s600);
  const head = stack('VERTICAL', 'Card title', vars.s200);
  s.appendChild(head); head.layoutSizingHorizontal = 'FILL';
  addText(head, textComp(comps.heading, title));
  if (subtitle) addText(head, textComp(comps.text, subtitle));
  return { c, s };
}
const fit = (c, s) => { s.layoutSizingHorizontal = 'FILL'; s.layoutSizingVertical = 'HUG'; c.layoutSizingVertical = 'HUG'; };
function row(...children) { const r = stack('HORIZONTAL', 'Row', vars.s400); for (const ch of children) { r.appendChild(ch); ch.layoutSizingHorizontal = 'FILL'; } return r; }
function tabBar(selected) {
  const t = comps.tabs.createInstance();
  const s = slotOf(t); clearSlot(s);
  for (const label of ['Profile', 'Notifications', 'Account']) s.appendChild(setProps(variant(sets.tab, { State: 'Default', Active: label === selected ? 'On' : 'Off' }), { Label: label }));
  return t;
}

// ---- page shell ---------------------------------------------------------------
const NAMES = ['Profile', 'Notifications', 'Account', 'Dialog'];
async function buildFrame(which) {
  const name = `SDS UserSettings / ${which} / v${VERSION}`;
  for (const old of figma.currentPage.children.filter(n => n.name === name)) old.remove();
  const page = figma.createAutoLayout('VERTICAL', { name });
  page.resize(1440, 100);
  page.layoutSizingHorizontal = 'FIXED';
  page.x = NAMES.indexOf(which) * 1540; page.y = VERSION * 1400;
  page.fills = bindPaint(vars.pageBg);

  if (which === 'Dialog') {
    // The library's Dialog is a full-screen scrim with a Dialog Body; it is the whole frame.
    const d = comps.dialog.createInstance();
    add(page, d);
    const body = d.findAllWithCriteria({ types: ['INSTANCE'] }).find(i => i.name === 'Dialog Body');
    setProps(body, { Heading: 'Delete your account?', Body: 'This permanently deletes your profile, settings and data. You can’t undo this.', Dismissible: true });
    const s = slotOf(body);
    const group = s.findAllWithCriteria({ types: ['INSTANCE'] }).find(i => i.name === 'Button Group');
    const replacement = actions(['Cancel', 'Neutral'], ['Delete account', 'danger']);
    s.insertChild(s.children.findIndex(c => c.id === group.id), field('Type DELETE to confirm', 'DELETE'));
    s.appendChild(replacement); replacement.layoutSizingHorizontal = 'FILL';
    group.remove();
    s.children[s.children.length - 2].layoutSizingHorizontal = 'FILL';
    return { id: page.id, name: page.name, size: [page.width, Math.round(page.height)] };
  }

  add(page, variant(sets.header, { Platform: 'Desktop', State: 'Default' }));
  const main = add(page, stack('VERTICAL', 'Main', vars.s800));
  pad(main, vars.s800);
  const intro = add(main, stack('VERTICAL', 'Page title', vars.s200));
  addText(intro, textComp(comps.titlePage, 'Settings'));
  addText(intro, textComp(comps.text, 'Manage your profile, notifications and account.'));
  add(main, tabBar(which), false);

  if (which === 'Profile') {
    const two = add(main, stack('HORIZONTAL', 'Cards', vars.s600));
    two.counterAxisAlignItems = 'MIN';
    const info = card('Personal information', 'This is how people see you across the app.');
    info.s.appendChild(row(field('First name', 'Jordan'), field('Last name', 'Lee')));
    info.s.appendChild(row(field('Email', 'jordan.lee@example.com'), field('Phone', '+1 206 555 0134')));
    info.s.appendChild(field('Job title', 'Senior Consultant'));
    info.s.appendChild(actions(['Cancel', 'Neutral'], ['Save changes', 'Primary']));
    for (const ch of info.s.children) ch.layoutSizingHorizontal = 'FILL';
    add(two, info.c); fit(info.c, info.s);
    const pw = card('Change password', 'Use at least 12 characters.');
    for (const l of ['Current password', 'New password', 'Confirm new password']) pw.s.appendChild(field(l, '••••••••••••'));
    pw.s.appendChild(actions(null, ['Update password', 'Primary']));
    for (const ch of pw.s.children) ch.layoutSizingHorizontal = 'FILL';
    add(two, pw.c); fit(pw.c, pw.s);
  }

  if (which === 'Notifications') {
    const n = card('Notification preferences', 'Changes save as soon as you switch them.');
    const groups = [
      ['Email notifications', [['Product updates', 'News about features and improvements.', true], ['Security alerts', 'Sign-ins from new devices and password changes.', true], ['Weekly digest', 'A summary of activity every Monday.', false]]],
      ['Push notifications', [['Direct messages', 'When someone messages you.', true], ['Mentions', 'When someone mentions you.', true], ['Task assignments', 'When a task is assigned to you.', false]]],
    ];
    for (const [title, items] of groups) {
      const g = stack('VERTICAL', title, vars.s400);
      n.s.appendChild(g); g.layoutSizingHorizontal = 'FILL';
      addText(g, textComp(comps.heading, title));
      for (const [label, desc, on] of items) add(g, setProps(variant(sets.switchField, { State: 'Default', 'Value Type': on ? 'Checked' : 'Unchecked' }), { Label: label, Description: desc, 'Has Description': true }));
    }
    add(main, n.c); fit(n.c, n.s);
  }

  if (which === 'Account') {
    const two = add(main, stack('HORIZONTAL', 'Cards', vars.s600));
    two.counterAxisAlignItems = 'MIN';
    const ex = card('Export your data', 'Download a copy of your profile, settings and activity as a ZIP file. We email you a link when it’s ready.');
    ex.s.appendChild(actions(null, ['Export data', 'Neutral']));
    for (const ch of ex.s.children) ch.layoutSizingHorizontal = 'FILL';
    add(two, ex.c); fit(ex.c, ex.s);
    const del = card('Delete account', 'Permanently delete your account and all of its data. You’ll be asked to confirm.');
    del.s.appendChild(actions(null, ['Delete account', 'danger']));
    for (const ch of del.s.children) ch.layoutSizingHorizontal = 'FILL';
    add(two, del.c); fit(del.c, del.s);
  }
  return { id: page.id, name: page.name, size: [page.width, Math.round(page.height)] };
}

const built = [];
for (const which of WHICH) built.push(await buildFrame(which));
return built;
