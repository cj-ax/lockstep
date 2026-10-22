// Lockstep build: NewProject, one frame per screen. Run through use_figma in a DRAFT file.
// WHICH = list of 'Form' | 'Discard dialog'. Safe to retry: it removes any existing frame with
// the same name first. Every key below came from lockstep/business-slalom/ (init, 2026-10-22).
const WHICH = __WHICH__;
const VERSION = __VERSION__;
const PROTECTED_FILE_KEYS = __PROTECTED_FILE_KEYS__;
if (PROTECTED_FILE_KEYS.includes(figma.fileKey)) throw new Error(`Refusing to write: ${figma.fileKey} is a protected file. Use a draft.`);

const C = {
  header: 'a1f1f34b73b954a1533d18ac4330a5ad2d4cfaee', container: 'e33ee7e85bebeab756aab527e05c15b3a1829c6b',
  button: '3a807bad37f01ba6bcca6860fad365113c55afe2', semantic: 'f1b8e09313d2329422f09f5e0ae8f619956feab5',
  textField: 'ebc9ce3c2e9055e1644fa21609b4d7da1b510f48', textArea: '26506985a5eccfaa4aa8d160fe2b1cdf5d7a5334',
  autocomplete: 'fb08dd45e21b7710d0fc1ec9ce9ea20ecb90a704', radio: '192db613fcc97940397990aabc350bcaeacea11c',
  listSection: 'f6cfb4f3ea42221b22b21f046cb042baf45a9966', listItem: 'e3c831409fefc1c54095f1ff73f9324fa8e33247',
  modal: 'c80e89aaf48682a718e1eae881ca70e4e9496723',
};
const V = {
  pageBg: '91a116c8d0add16d8c319dc62995977f1f26973c', textRegular: '82f040093af673c7804535a216ebb111286a3872',
  textMedium: 'cd9f5777cd48ce8534a9c02326d7bd71a9206209',
  pa8: '267fd6c72c81a443e83fb75724159e472868ba5e',
  ga1: '2a9b7e507c68e545738e0d37021faaeab6f689ba', ga2: '0562032ad8aec53e74320b6f7f51aff4273efa94',
  ga4: 'c39e9ab323c2317dfcadbc7fd291852d5b730be1', ga6: 'e3e6edeb7ddf385a94aa9365ab8da416f8e0d2cd',
};
const S = { h4: '75041c6b21a453b35bba16dc950f6dba732d1c7e', h6: '394c402ae3847698d62cd546133a4207cc789e78', body1: 'bc04f5a9ac30e8f94d13610c13160f8b0f33870e', body2: 'a505c525b8cbe17ddbf33d75d84cbb0e7a2a6d1c' };

const sets = Object.fromEntries(await Promise.all(Object.entries(C).map(async ([k, key]) => [k, await figma.importComponentSetByKeyAsync(key)])));
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
const wrapText = (parent, t) => { add(parent, t); t.textAutoResize = 'HEIGHT'; return t; };
// findAllWithCriteria({ types: ['SLOT'] }) misses slots of nested instances, so walk the tree.
const slot = (inst, name) => inst.findAll(n => n.type === 'SLOT').find(s => s.name === name);
const clearSlot = (s) => { for (const c of [...s.children]) c.remove(); };

function button(label, kind) {
  if (kind === 'negative') return setProps(variant(sets.semantic, { semantic: 'negative', variant: 'outlined', Size: 'md', status: 'default' }), { label, 'icon left': false, 'icon right': false });
  return setProps(variant(sets.button, { variant: kind, size: 'md', status: 'enabled' }), { Text: label, 'icon-left': false, 'icon right': false });
}
// Empty fields: the set only has has value=false with label on, state=enabled.
function field(label, placeholder, opts = {}) {
  const f = variant(sets.textField, { state: 'enabled', 'has value': 'false', 'Label style': 'label on' });
  return setProps(f, { 'field label': label, content: placeholder, 'icon-left': false, 'icon-right': !!opts.date, 'Assistive Text': false, 'is required': !!opts.required, 'has user guidance': false });
}
function textArea(label, placeholder) {
  const a = variant(sets.textArea, { type: 'label on', status: 'enable', 'has value': 'false' });
  return setProps(a, { 'label text': label, content: placeholder, 'assistive text': false, 'error text': false, 'is required': false, 'user guidance': false });
}
function personPicker(label, person) {
  const p = variant(sets.autocomplete, { status: 'enable', type: 'label on', 'has value': 'true' });
  return setProps(p, { 'label content': label, content: person, 'is required': true, 'assistive text': true, 'assistive content': 'Defaults to you. Search to pick someone else.', 'error text': false, 'has icon': false, 'has arrow': true, 'clear icon': false, 'text response': true, chips: false, 'left icon': false, 'user guidance': false });
}
function radioGroup(label, help, options) {
  const g = stack('VERTICAL', `Radio group: ${label}`, vars.ga1);
  wrapText(g, text(label, styles.body2, vars.textRegular, 'Group label'));
  const r = add(g, stack('HORIZONTAL', 'Options', vars.ga6));
  for (const o of options) {
    const b = variant(sets.radio, { status: 'default', Size: 'md' });
    // The radio has no label property; its label is a plain text layer.
    b.findAllWithCriteria({ types: ['TEXT'] })[0].characters = o;
    add(r, b, false);
  }
  wrapText(g, text(help, styles.body2, vars.textMedium, 'Group help'));
  return g;
}
function toggleRow(label, desc) {
  const li = variant(sets.listItem, { status: 'Default' });
  setProps(li, { label, 'bottom description': true, 'has icon': false, 'has toggle': true, directional: false, 'right icon': false, 'right description': false, 'has chip': false, 'info icon': false });
  li.findAllWithCriteria({ types: ['TEXT'] }).find(t => t.name === 'description').characters = desc;
  li.findAllWithCriteria({ types: ['INSTANCE'] }).find(i => i.name === 'Switch Toggle').setProperties({ 'Toggle Status': 'Off', State: 'Enabled' });
  return li;
}

// ---- page shell ------------------------------------------------------------
const NAMES = ['Form', 'Discard dialog'];
async function buildFrame(which) {
  const name = `NewProject / ${which} / v${VERSION}`;
  for (const old of figma.currentPage.children.filter(n => n.name === name)) old.remove();
  const page = figma.createAutoLayout('VERTICAL', { name });
  page.resize(1440, 100);
  page.layoutSizingHorizontal = 'FIXED';
  page.x = NAMES.indexOf(which) * 1540; page.y = (VERSION - 1) * 1600;
  page.fills = bindPaint(vars.pageBg);

  add(page, variant(sets.header, { Version: 'Default' }));
  const main = add(page, stack('VERTICAL', 'Main', vars.ga6));
  pad(main, vars.pa8);
  main.counterAxisAlignItems = 'CENTER';

  if (which === 'Discard dialog') {
    main.primaryAxisAlignItems = 'CENTER';
    main.layoutSizingVertical = 'FIXED';
    main.resize(1440, 900);
    const m = variant(sets.modal, { type: 'alert', 'rounded corner': 'true' });
    setProps(m, { close: true, 'has icon': true, 'Show CTA Section': true });
    m.findAllWithCriteria({ types: ['TEXT'] }).find(t => t.name === 'Modal content').characters = 'Discard this project?';
    const content = slot(m, 'content slot'); clearSlot(content);
    wrapText(content, text('You have changes that aren’t saved. If you discard, the project isn’t created and your changes are lost.', styles.body1, vars.textRegular, 'Message'));
    const cta = slot(m, 'CTA Section'); clearSlot(cta);
    cta.counterAxisAlignItems = 'MAX';
    const actions = add(cta, stack('HORIZONTAL', 'Actions', vars.ga4), false);
    actions.appendChild(button('Keep Editing', 'neutral_outlined'));
    actions.appendChild(button('Discard', 'negative'));
    add(main, m, false);
  } else {
    const section = add(main, variant(sets.container, { type: 'general container' }), false);
    section.layoutSizingHorizontal = 'FIXED';
    section.resize(880, section.height);
    const s = slot(section, 'header'); clearSlot(s);
    s.setBoundVariable('itemSpacing', vars.ga6);

    const intro = add(s, stack('VERTICAL', 'Page title', vars.ga2));
    wrapText(intro, text('New project', styles.h4, vars.textRegular, 'Title'));
    wrapText(intro, text('Name the project, choose who owns it and who can see it. You can change any of this later.', styles.body2, vars.textMedium, 'Guidance'));

    // Fields go straight into the slot: inside a vertical frame of ours, the library fields
    // render at their default width even though the layers report FILL (seen in passes 1 and 2).
    const form = s;
    add(form, field('Project name', 'For example, Client onboarding portal', { required: true }));
    const desc = add(form, textArea('Description', 'What is the project for, and what does done look like?'));
    desc.layoutSizingVertical = 'HUG';
    add(form, personPicker('Owner', 'Chris Axelson'));
    const dates = add(form, stack('HORIZONTAL', 'Dates', vars.ga6));
    for (const label of ['Start date', 'End date']) add(dates, field(label, 'MM/DD/YYYY', { date: true }));
    add(form, radioGroup('Visibility', 'Private: only you and people you add. Team: everyone on your team. Organization: everyone at Slalom.', ['Private', 'Team', 'Organization']));

    const notify = variant(sets.listSection, { type: 'menu lists' });
    setProps(notify, { 'has title': true, divider: false });
    notify.findAllWithCriteria({ types: ['TEXT'] }).find(t => t.name === 'Label' && t.parent.name === 'header').characters = 'Notify the team';
    const list = slot(notify, 'list container slot'); clearSlot(list);
    add(list, toggleRow('Email the team', 'Send everyone on the team an email when the project is created.'));
    add(list, toggleRow('Post in the team channel', 'Share a link to the new project in the team’s channel.'));
    add(s, notify);

    const actions = add(s, stack('HORIZONTAL', 'Actions', vars.ga4));
    actions.primaryAxisAlignItems = 'MAX';
    actions.appendChild(button('Cancel', 'neutral_outlined'));
    actions.appendChild(button('Create Project', 'contained_button'));
    s.layoutSizingVertical = 'HUG';
    section.layoutSizingVertical = 'HUG';
  }
  return { id: page.id, name: page.name, size: [page.width, Math.round(page.height)] };
}

const built = [];
for (const which of WHICH) built.push(await buildFrame(which));
return built;
