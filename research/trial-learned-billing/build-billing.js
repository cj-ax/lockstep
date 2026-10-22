// Lockstep build: Billing on the learned SDS library (lockstep/sds-learned).
// Runs through use_figma in the learned draft itself, on a page "Billing", because the
// learned components and variables are local to that file. WHICH = list of
// 'Overview' | 'Dialog'; VERSION picks the canvas row. Safe to retry: it removes frames
// with the same name first.
const WHICH = __WHICH__;
const VERSION = __VERSION__;
const PROTECTED_FILE_KEYS = __PROTECTED_FILE_KEYS__;
if (PROTECTED_FILE_KEYS.includes(figma.fileKey)) throw new Error(`Refusing to write: ${figma.fileKey} is a protected file. Use a draft.`);

const KEYS = {
  header: 'a1f69d8fdde4a1fe8523e49d3baa3c8464ad17d2', inputField: 'c28150b04d333d34ed9d2b77abd9f2f54e1a878a',
  button: 'cc8b558dc7d9684011b6b99ce8e6509399bc836b', tab: '18aa207708b43593a2af7096b2dfd531553f3414',
  text: 'fbaca594bc38824e75467b952cbca0a976c46856', textTitlePage: 'f1e2f812cd9a9e7babb0032e88b57c4d681e8bbb',
  buttonDanger: '3d3073170c1014cfacc5d047c23495cfed01e0a8',
  textHeading: 'local:5:2', switchField: 'local:5:4', cardSlot: 'local:5:10', buttonGroup: 'local:5:12',
  tabs: 'local:5:156', dialog: 'local:5:158',
};
const V = {
  pageBg: 'local:VariableID:2:4', s200: 'local:VariableID:2:19', s400: 'local:VariableID:2:23',
  s600: 'local:VariableID:2:22', s800: 'local:VariableID:2:21',
};

// Learned (local) and published refs side by side.
const component = async (ref) => ref.startsWith('local:') ? figma.getNodeByIdAsync(ref.slice(6))
  : figma.importComponentSetByKeyAsync(ref).catch(() => figma.importComponentByKeyAsync(ref));
const variable = async (ref) => figma.variables.getVariableByIdAsync(ref.slice(6));
const L = Object.fromEntries(await Promise.all(Object.entries(KEYS).map(async ([k, r]) => [k, await component(r)])));
const vars = Object.fromEntries(await Promise.all(Object.entries(V).map(async ([k, r]) => [k, await variable(r)])));
await Promise.all(['Regular', 'Medium', 'Semi Bold', 'Bold'].map(style => figma.loadFontAsync({ family: 'Inter', style })));

let page = figma.root.children.find(p => p.name === 'Billing');
if (!page) { page = figma.createPage(); page.name = 'Billing'; }
await figma.setCurrentPageAsync(page);

// ---- helpers ------------------------------------------------------------------
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
const slotOf = (inst) => inst.findAll(n => n.type === 'SLOT').find(s => { let p = s.parent; while (p && p.type !== 'INSTANCE') p = p.parent; return p && p.id === inst.id; });
const clearSlot = (s) => { for (const c of [...s.children]) c.remove(); };
const nearestInstance = n => { let p = n.parent; while (p && p.type !== 'INSTANCE') p = p.parent; return p; };
// findAllWithCriteria misses instances nested in a slot of another instance (the Dialog's
// Button Group), so walk the tree.
const ownButtons = (g) => g.findAll(n => n.type === 'INSTANCE').filter(i => { const o = nearestInstance(i); return o && o.id === g.id && i.visible; });
// A swapped button keeps the group's old layout until Figma lays it out again.
const relayout = (g) => { const mode = g.layoutSizingHorizontal; const w = g.width; g.layoutSizingHorizontal = 'FIXED'; g.resize(w + 1, g.height); g.resize(w, g.height); g.layoutSizingHorizontal = mode; };
// The library Header ships marketing nav and a logged-out state: relabel it as app nav.
async function appHeader() {
  const h = variant(L.header, { Platform: 'Desktop', State: 'Default' });
  const list = h.findOne(n => n.type === 'INSTANCE' && n.name === 'Navigation Pill List');
  setProps(list, { 'Link 5': false, 'Link 6': false, 'Link 7': false });
  const pills = list.findAll(n => n.type === 'INSTANCE' && n.name === 'Navigation Pill' && n.visible);
  ['Dashboard', 'Projects', 'Team', 'Billing'].forEach((label, i) => { if (pills[i]) setProps(pills[i], { Label: label }).setProperties({ State: label === 'Billing' ? 'Active' : 'Default' }); });
  const auth = h.findOne(n => n.type === 'INSTANCE' && n.name === 'Header Auth');
  const states = Object.values(auth.componentProperties).find(p => p.type === 'VARIANT');
  const authSet = (await auth.getMainComponentAsync()).parent;
  const loggedIn = authSet.type === 'COMPONENT_SET' && authSet.children.map(c => c.name.split('=')[1]).find(s => s && s !== 'Logged Out');
  if (loggedIn) auth.setProperties({ State: loggedIn });
  return { h, states: states && states.value, loggedIn };
}

// Text is a library component: published Text / Text Title Page take "Text", the learned
// Text Heading takes "Heading".
const textComp = (comp, chars) => setProps(comp.createInstance(), { [comp.name === 'Text Heading' ? 'Heading' : 'Text']: chars });
const addText = (parent, inst, fill = true) => {
  add(parent, inst, fill);
  if (fill) for (const t of inst.findAll(n => n.type === 'TEXT')) {
    if (t.parent.layoutMode && t.parent.layoutMode !== 'NONE') t.layoutSizingHorizontal = 'FILL';
    t.textAutoResize = 'HEIGHT';
  }
  return inst;
};
function field(label, value) { return setProps(variant(L.inputField, { State: 'Default', 'Value Type': 'Default' }), { 'Has Label': true, Label: label, Value: value }); }
const DANGER = (variantName) => variantComponent(L.buttonDanger, { Variant: variantName, State: 'Default', Size: 'Medium' });
// Configure the visible buttons of a button group in order: [label, kind] pairs, where kind
// is a Button variant or 'danger:<Danger variant>'.
function labelButtons(g, specs) {
  const shown = ownButtons(g);
  for (const [i, inst] of shown.entries()) {
    const spec = specs[i];
    if (!spec) continue;
    const [label, kind] = spec;
    if (kind.startsWith('danger:')) inst.swapComponent(DANGER(kind.slice(7)));
    else inst.setProperties({ Variant: kind, State: 'Default', Size: 'Medium' });
    setProps(inst, { Label: label });
  }
  return g;
}
function card(title) {
  const c = L.cardSlot.createInstance();
  const s = slotOf(c); clearSlot(s);
  s.setBoundVariable('itemSpacing', vars.s600);
  addText(s, textComp(L.textHeading, title));
  return { c, s };
}
const fit = (c, s) => { for (const ch of s.children) ch.layoutSizingHorizontal = 'FILL'; s.layoutSizingHorizontal = 'FILL'; s.layoutSizingVertical = 'HUG'; c.layoutSizingVertical = 'HUG'; };
function row(...children) { const r = stack('HORIZONTAL', 'Row', vars.s400); for (const ch of children) { r.appendChild(ch); ch.layoutSizingHorizontal = 'FILL'; } return r; }
function tabBar(selected) {
  const t = L.tabs.createInstance();
  const s = slotOf(t); clearSlot(s);
  for (const label of ['Overview', 'Invoices', 'Payment']) s.appendChild(setProps(variant(L.tab, { State: 'Default', Active: label === selected ? 'On' : 'Off' }), { Label: label }));
  return t;
}

// ---- frames -------------------------------------------------------------------
const NAMES = ['Overview', 'Dialog'];
async function buildFrame(which) {
  const name = `Billing / ${which} / v${VERSION}`;
  for (const old of page.children.filter(n => n.name === name)) old.remove();
  const frame = figma.createAutoLayout('VERTICAL', { name });
  frame.resize(1440, 100);
  frame.layoutSizingHorizontal = 'FIXED';
  frame.x = NAMES.indexOf(which) * 1540; frame.y = VERSION * 1600;
  frame.fills = bindPaint(vars.pageBg);

  if (which === 'Dialog') {
    // The learned Dialog is a full-screen scrim holding a Dialog Body; it is the whole frame.
    const d = L.dialog.createInstance();
    add(frame, d);
    const body = d.findAllWithCriteria({ types: ['INSTANCE'] }).find(i => i.name === 'Dialog Body');
    setProps(body, { Heading: 'Cancel your subscription?', Body: 'Your Pro plan stays active until 1 November 2026. After that, your team moves to the Free plan and loses access to Pro features.', Dismissible: true });
    const group = d.findAll(n => n.type === 'INSTANCE' && n.name === 'Button Group')[0];
    setProps(group, { 'Button Start': true, 'Button End': true });
    labelButtons(group, [['Keep subscription', 'Neutral'], ['Cancel subscription', 'danger:Primary']]);
    relayout(group);
    return { id: frame.id, name: frame.name, size: [frame.width, Math.round(frame.height)] };
  }

  const head = await appHeader();
  add(frame, head.h);
  const main = add(frame, stack('VERTICAL', 'Main', vars.s800));
  pad(main, vars.s800);
  const intro = add(main, stack('VERTICAL', 'Page title', vars.s200));
  addText(intro, textComp(L.textTitlePage, 'Billing'));
  addText(intro, textComp(L.text, 'Manage your plan, payment method and receipts.'));
  add(main, tabBar(which), false);

  const cards = add(main, stack('HORIZONTAL', 'Cards', vars.s600));
  cards.counterAxisAlignItems = 'MIN';

  const plan = card('Current plan');
  const planRow = stack('HORIZONTAL', 'Plan and price', vars.s400);
  plan.s.appendChild(planRow);
  addText(planRow, textComp(L.text, 'Pro plan'));
  addText(planRow, textComp(L.text, '$24 per month'));
  planRow.children[1].findAll(n => n.type === 'TEXT').forEach(t => { t.textAlignHorizontal = 'RIGHT'; });
  addText(plan.s, textComp(L.text, 'Billed monthly. Your next payment is on 1 November 2026.'));
  // Swapping the first button of a learned Button Group leaves a phantom copy that takes up
  // space, so the danger button goes in the end slot.
  plan.s.appendChild(labelButtons(L.buttonGroup.createInstance(), [['Change plan', 'Primary'], ['Cancel subscription', 'danger:Subtle']]));
  add(cards, plan.c); fit(plan.c, plan.s);

  const pay = card('Payment details');
  pay.s.appendChild(row(field('Cardholder name', 'Jordan Lee'), field('Card number', '•••• •••• •••• 4242')));
  pay.s.appendChild(row(field('Expiry date', '08 / 28'), field('Billing email', 'billing@example.com')));
  pay.s.appendChild(setProps(L.switchField.createInstance(), { Label: 'Email me receipts', Description: 'We send a receipt to your billing email after each payment.' }));
  pay.s.appendChild(labelButtons(L.buttonGroup.createInstance(), [['Cancel', 'Neutral'], ['Save changes', 'Primary']]));
  add(cards, pay.c); fit(pay.c, pay.s);
  for (const g of [plan.s, pay.s].map(s => s.children[s.children.length - 1])) relayout(g);

  return { id: frame.id, name: frame.name, size: [frame.width, Math.round(frame.height)], headerAuth: head.loggedIn || 'Logged Out (no other state)' };
}

const built = [];
for (const which of WHICH) built.push(await buildFrame(which));
return { page: page.id, built };
