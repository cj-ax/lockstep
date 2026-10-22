// Lockstep build: UserSettings, one frame per call. Run through use_figma in a DRAFT file.
// WHICH = list of 'Profile' | 'Notifications' | 'Account' | 'Dialog'. Safe to retry: it
// removes any existing frame with the same name first.
// Every key below came from scripts/inventory.js or search_design_system (keys.slalom.json).
const WHICH = __WHICH__;
const VERSION = __VERSION__;
const PROTECTED_FILE_KEYS = __PROTECTED_FILE_KEYS__;
if (PROTECTED_FILE_KEYS.includes(figma.fileKey)) throw new Error(`Refusing to write: ${figma.fileKey} is a protected file. Use a draft.`);

const C = {
  header: 'a1f1f34b73b954a1533d18ac4330a5ad2d4cfaee', container: 'e33ee7e85bebeab756aab527e05c15b3a1829c6b',
  card: 'a6a89663be3c8cdf14ec4ef3660dca654051e6b4', contentSlot: '71da0a7caaabe6d4a21d0be5692ad5e899293063',
  tabs: 'ff47b6308847a0098698b9b41a16ed853ed70b6b', textField: 'ebc9ce3c2e9055e1644fa21609b4d7da1b510f48',
  listSection: 'f6cfb4f3ea42221b22b21f046cb042baf45a9966', listItem: 'e3c831409fefc1c54095f1ff73f9324fa8e33247',
  button: '3a807bad37f01ba6bcca6860fad365113c55afe2', semantic: 'f1b8e09313d2329422f09f5e0ae8f619956feab5',
  modal: 'c80e89aaf48682a718e1eae881ca70e4e9496723',
};
const ICON = { profile: '7f2d3ea4f909eceb2e83c95da8d2ef79ac32bb8b', bell: 'ffc3a92836c6b8f3dd3b96b26490a3fdae63ab87', account: 'ad95a5a137eab74fa4ef330c8bdc1ee7784f664f', eye: '23e0084d01c99251cec02bc443722427cabc8e50' };
const V = {
  pageBg: '91a116c8d0add16d8c319dc62995977f1f26973c', textRegular: '82f040093af673c7804535a216ebb111286a3872',
  textMedium: 'cd9f5777cd48ce8534a9c02326d7bd71a9206209',
  pa6: 'e7de87cb0f77390abaa76950a0539a237c88849b', ga2: '0562032ad8aec53e74320b6f7f51aff4273efa94',
  ga4: 'c39e9ab323c2317dfcadbc7fd291852d5b730be1', ga6: 'e3e6edeb7ddf385a94aa9365ab8da416f8e0d2cd',
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
const setText = (node, chars) => { node.characters = chars; };

function button(label, kind) {
  if (kind === 'negative') return setProps(variant(sets.semantic, { semantic: 'negative', variant: 'contained_button', Size: 'md', status: 'default' }), { label, 'icon left': false, 'icon right': false });
  return setProps(variant(sets.button, { variant: kind, size: 'md', status: 'enabled' }), { Text: label, 'icon-left': false, 'icon right': false });
}
function field(label, value, opts = {}) {
  // The set has no enabled+has value=true with label on; its populated default is state=input.
  const f = variant(sets.textField, { state: 'input', 'has value': 'textField', 'Label style': 'label on' });
  setProps(f, { 'field label': label, content: value, 'icon-left': false, 'icon-right': !!opts.reveal, 'Assistive Text': !!opts.help, 'is required': !!opts.required });
  if (opts.help) setProps(f, { 'assistive text': opts.help });
  if (opts.reveal) for (const i of f.findAllWithCriteria({ types: ['INSTANCE'] })) if (i.name === 'calendar-month-outline' && i.parent.visible) i.swapComponent(icons.eye);
  return f;
}
function card(title, subtitle) {
  const c = variant(sets.card, { type: 'elevated', status: 'Default', 'primary color': 'false' });
  const hdr = c.findAllWithCriteria({ types: ['INSTANCE'] }).find(i => i.name === 'card header');
  setProps(hdr, { 'left icon': false, 'right icon': false, 'title lg': true, 'Title sm': false, 'has subtitle': !!subtitle });
  // Both header text layers are named "Title"; the subtitle is the smaller one.
  const [main, ...subs] = hdr.findAllWithCriteria({ types: ['TEXT'] }).sort((a, b) => b.fontSize - a.fontSize);
  setText(main, title);
  if (subtitle) for (const t of subs) setText(t, subtitle);
  const content = slot(c, 'content Slot'); clearSlot(content);
  content.setBoundVariable('itemSpacing', vars.ga4);
  // The card ships at a fixed sample height; let it and its body grow with the content.
  content.layoutSizingVertical = 'HUG';
  c.layoutSizingVertical = 'HUG';
  const cta = slot(c, 'CTA slot'); clearSlot(cta);
  cta.primaryAxisAlignItems = 'MAX'; cta.setBoundVariable('itemSpacing', vars.ga4);
  return { c, content, cta };
}
function body(chars) {
  const b = variant(sets.contentSlot, { type: 'content-left' });
  for (const t of b.findAllWithCriteria({ types: ['TEXT'] })) setText(t, chars);
  return b;
}
function row(...children) { const r = stack('HORIZONTAL', 'Row', vars.ga4); for (const ch of children) { add(r, ch, false); ch.layoutSizingHorizontal = 'FILL'; } return r; }
function tabBar(selected) {
  const bar = stack('HORIZONTAL', 'Tab bar', null);
  for (const [label, icon] of [['Profile', icons.profile], ['Notifications', icons.bell], ['Account', icons.account]]) {
    const t = variant(sets.tabs, { State: label === selected ? 'Selected' : 'Unselected', Hover: 'No Hover' });
    setProps(t, { 'Tab Label': label, 'has icon': true, Icon: icon.id });
    add(bar, t, false);
  }
  return bar;
}

// ---- page shell ------------------------------------------------------------
// VERSION picks the row on the canvas, so earlier passes of the loop stay visible above.
const NAMES = ['Profile', 'Notifications', 'Account', 'Dialog'];
async function buildFrame(which) {
  const name = `UserSettings / ${which} / v${VERSION}`;
  for (const old of figma.currentPage.children.filter(n => n.name === name)) old.remove();
  const page = figma.createAutoLayout('VERTICAL', { name });
  page.resize(1440, 100);
  page.layoutSizingHorizontal = 'FIXED';
  page.x = NAMES.indexOf(which) * 1540; page.y = VERSION * 1400;
  page.fills = bindPaint(vars.pageBg);

  const appHeader = variant(sets.header, { Version: 'Default' });
  add(page, appHeader);

  const main = add(page, stack('VERTICAL', 'Main', vars.ga6));
  pad(main, vars.pa6);

  if (which === 'Dialog') {
    main.counterAxisAlignItems = 'CENTER';
    main.primaryAxisAlignItems = 'CENTER';
    const m = variant(sets.modal, { type: 'alert', 'rounded corner': 'true' });
    setProps(m, { close: true, 'has icon': true, 'Show CTA Section': true });
    setText(m.findAllWithCriteria({ types: ['TEXT'] }).find(t => t.name === 'Modal content'), 'Delete your account?');
    const content = slot(m, 'content slot'); clearSlot(content);
    content.setBoundVariable('itemSpacing', vars.ga4);
    add(content, text('This permanently deletes your profile, settings and data. You can’t undo this.', styles.body1, vars.textRegular, 'Message'));
    add(content, field('Type DELETE to confirm', 'DELETE', { required: true }));
    const cta = slot(m, 'CTA Section'); clearSlot(cta);
    cta.counterAxisAlignItems = 'MAX';
    const actions = stack('HORIZONTAL', 'Actions', vars.ga4);
    add(cta, actions, false);
    actions.appendChild(button('Cancel', 'neutral_outlined'));
    actions.appendChild(button('Delete Account', 'negative'));
    add(main, m, false);
  } else {
    const section = add(main, variant(sets.container, { type: 'general container' }));
    const s = slot(section, 'header'); clearSlot(s);
    s.setBoundVariable('itemSpacing', vars.ga6);
    const intro = add(s, stack('VERTICAL', 'Page title', vars.ga2));
    add(intro, text('Settings', styles.h4, vars.textRegular, 'Title'));
    add(intro, text('Manage your profile, notifications and account.', styles.body2, vars.textMedium, 'Subtitle'));
    add(s, tabBar(which));

    if (which === 'Profile') {
      const two = add(s, stack('HORIZONTAL', 'Cards', vars.ga6));
      two.counterAxisAlignItems = 'MIN';
      const info = card('Personal information', 'This is how people see you across the app.');
      add(info.content, row(field('First name', 'Jordan', { required: true }), field('Last name', 'Lee', { required: true })));
      add(info.content, row(field('Email', 'jordan.lee@example.com', { required: true }), field('Phone', '+1 206 555 0134')));
      add(info.content, field('Job title', 'Senior Consultant'));
      info.cta.appendChild(button('Cancel', 'neutral_outlined'));
      info.cta.appendChild(button('Save Changes', 'contained_button'));
      add(two, info.c);
      const pw = card('Change password', 'Use at least 12 characters.');
      add(pw.content, field('Current password', '••••••••••••', { reveal: true, required: true }));
      add(pw.content, field('New password', '••••••••••••', { reveal: true, required: true, help: 'At least 12 characters, with a number and a symbol.' }));
      add(pw.content, field('Confirm new password', '••••••••••••', { reveal: true, required: true }));
      pw.cta.appendChild(button('Update Password', 'contained_button'));
      add(two, pw.c);
    }

    if (which === 'Notifications') {
      const n = card('Notification preferences', 'Changes save as soon as you switch them.');
      setProps(n.c, { 'has CTA': false });
      const groups = [
        ['Email notifications', [['Product updates', 'News about features and improvements.', true], ['Security alerts', 'Sign-ins from new devices and password changes.', true], ['Weekly digest', 'A summary of activity every Monday.', false]]],
        ['Push notifications', [['Direct messages', 'When someone messages you.', true], ['Mentions', 'When someone mentions you.', true], ['Task assignments', 'When a task is assigned to you.', false]]],
      ];
      groups.forEach(([title, items], gi) => {
        const ls = variant(sets.listSection, { type: 'menu lists' });
        setProps(ls, { 'has title': true, divider: gi === 0 });
        setText(ls.findAllWithCriteria({ types: ['TEXT'] }).find(t => t.name === 'Label' && t.parent.name === 'header'), title);
        const list = slot(ls, 'list container slot'); clearSlot(list);
        for (const [label, desc, on] of items) {
          const li = variant(sets.listItem, { status: 'Default' });
          setProps(li, { label, 'bottom description': true, 'has icon': false, 'has toggle': true, directional: false, 'right icon': false, 'right description': false });
          setText(li.findAllWithCriteria({ types: ['TEXT'] }).find(t => t.name === 'description'), desc);
          const sw = li.findAllWithCriteria({ types: ['INSTANCE'] }).find(i => i.name === 'Switch Toggle');
          sw.setProperties({ 'Toggle Status': on ? 'On' : 'Off' });
          add(list, li);
        }
        add(n.content, ls);
      });
      add(s, n.c);
    }

    if (which === 'Account') {
      const two = add(s, stack('HORIZONTAL', 'Cards', vars.ga6));
      two.counterAxisAlignItems = 'MIN';
      const ex = card('Export your data', null);
      add(ex.content, body('Download a copy of your profile, settings and activity as a ZIP file. We email you a link when it’s ready.'));
      ex.cta.appendChild(button('Export Data', 'outlined'));
      add(two, ex.c);
      const del = card('Delete account', null);
      add(del.content, body('Permanently delete your account and all of its data. You’ll be asked to confirm.'));
      del.cta.appendChild(button('Delete Account', 'negative'));
      add(two, del.c);
    }
  }
  return { id: page.id, name: page.name, size: [page.width, Math.round(page.height)] };
}

const built = [];
for (const which of WHICH) built.push(await buildFrame(which));
return built;
