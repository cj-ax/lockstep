// Lockstep code-to-Figma: SExpansionPanels as a draft component set. Run through use_figma in the DRAFT file.
// Its panels are library Accordion Row instances (Accordion Row = SExpansionPanel in the review).
// Safe to retry: removes any existing set with the same name first.
const PROTECTED_FILE_KEYS = ['LMgKpbsEmxRpiHBKd9YGlw'];
if (PROTECTED_FILE_KEYS.includes(figma.fileKey)) throw new Error(`Refusing to write: ${figma.fileKey} is a protected file. Use a draft.`);

const V = {
  r0: '1a664bcec26cde4dae8c9eb50d6ba723e2fb0720', pa0: '60a49ef439417247dafe7583e4e7f5c08e15ea23',
  ga0: '4a127b119409919f7b3d3eb0041b34e885561a22', ga2: '0562032ad8aec53e74320b6f7f51aff4273efa94',
  ga6: 'e3e6edeb7ddf385a94aa9365ab8da416f8e0d2cd', pa8: '267fd6c72c81a443e83fb75724159e472868ba5e',
};
const vars = Object.fromEntries(await Promise.all(Object.entries(V).map(async ([k, key]) => [k, await figma.variables.importVariableByKeyAsync(key)])));
const rowSet = await figma.importComponentSetByKeyAsync('3ce647fbb205f169a5d73c0afe513e462767e9c6');

const SIDES = ['paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft'];
const pad = (f, v) => { for (const p of SIDES) f.setBoundVariable(p, v); };
const radius = (f, v) => { for (const p of ['topLeftRadius', 'topRightRadius', 'bottomLeftRadius', 'bottomRightRadius']) f.setBoundVariable(p, v); };
const variant = (set, props) => {
  const want = Object.entries(props);
  const v = set.children.find(c => { const p = Object.fromEntries(c.name.split(', ').map(x => x.split('='))); return want.every(([k, val]) => p[k] === val); });
  if (!v) throw new Error(`${set.name}: no variant ${JSON.stringify(props)}`);
  return v.createInstance();
};
const propKey = (inst, name) => Object.keys(inst.componentProperties).find(k => k.split('#')[0] === name);
const setProps = (inst, props) => { const o = {}; for (const [n, v] of Object.entries(props)) { const k = propKey(inst, n); if (!k) throw new Error(`${inst.name}: no property ${n}`); o[k] = v; } inst.setProperties(o); return inst; };
const setText = async (t, chars) => { if (t.fontName !== figma.mixed) await figma.loadFontAsync(t.fontName); else for (const s of t.getStyledTextSegments(['fontName'])) await figma.loadFontAsync(s.fontName); t.characters = chars; };
const textIn = (root, path, chars) => root.findAll(n => n.type === 'TEXT' && n.characters === chars && (!path || n.parent.name === path));

// PanelGroup.vue's four panels, in order.
const PANELS = ['Accordion Row Name', 'Project Alpha', 'Client Engagement', 'Budget Review'];

async function panel(i, expanded) {
  const r = variant(rowSet, { status: expanded ? 'Expanded' : 'Collapsed', Type: 'custom' });
  setProps(r, { 'Accordion Row Name': PANELS[i] });
  if (expanded && i === 1) {
    // Project Alpha: progress 72.3, one status row, two data rows, no notes.
    setProps(r, { 'Show Row 4': false, 'Show Comments Group': false });
    const statuses = r.findAll(n => n.type === 'FRAME' && n.name === 'Headings' && n.parent.name === 'Statuses');
    await setText(statuses[0].findOne(n => n.type === 'TEXT' && n.characters === 'Work In Progress'), 'In Review');
    statuses[1].visible = false;
    for (const t of textIn(r, null, '47.6')) await setText(t, '72.3');
    for (const e of r.findAll(n => n.type === 'ELLIPSE' && n.arcData && n.arcData.endingAngle - n.arcData.startingAngle < 2 * Math.PI * 0.99)) {
      const a = e.arcData; e.arcData = { ...a, endingAngle: a.startingAngle + 2 * Math.PI * 0.723 };
    }
    const chip = r.findOne(n => n.type === 'INSTANCE' && n.name === 'Chip');
    const chipText = chip && chip.findOne(n => n.type === 'TEXT');
    if (chipText) await setText(chipText, 'Fixed Bid');
    for (const t of textIn(r, null, 'Low Touch')) await setText(t, 'High Touch');
    for (const t of textIn(r, null, 'Northern California Office')) await setText(t, 'Seattle Office');
  }
  return r;
}

async function group(multiple) {
  const c = figma.createComponent(); c.name = `multiple=${multiple}`;
  c.layoutMode = 'VERTICAL'; c.counterAxisSizingMode = 'FIXED'; c.resize(370, 10); c.primaryAxisSizingMode = 'AUTO';
  c.fills = []; radius(c, vars.r0); pad(c, vars.pa0); c.setBoundVariable('itemSpacing', vars.ga0);
  const slot = c.createSlot(); slot.name = 'default';
  slot.layoutMode = 'VERTICAL'; slot.fills = [];
  slot.setBoundVariable('itemSpacing', vars.ga2); pad(slot, vars.pa0); radius(slot, vars.r0);
  slot.layoutSizingHorizontal = 'FILL'; slot.layoutSizingVertical = 'HUG';
  // Single mode: PanelGroup opens panel 0. Multiple mode: two panels open at once.
  const open = multiple ? [0, 1] : [0];
  for (let i = 0; i < PANELS.length; i++) {
    const p = await panel(i, open.includes(i));
    slot.appendChild(p); p.layoutSizingHorizontal = 'FILL';
  }
  return c;
}

let page = figma.root.children.find(p => p.name === 'Code components');
await figma.setCurrentPageAsync(page);
const section = page.children.find(n => n.type === 'SECTION' && n.name === 'Code components (draft)');
const skel = section.children.find(n => n.name === 'SSkeletonLoader');
for (const old of section.children.filter(n => n.name === 'SExpansionPanels')) old.remove();

const comps = [await group(false), await group(true)]; // false first: the code's default
for (const c of comps) section.appendChild(c);
const set = figma.combineAsVariants(comps, section);
set.name = 'SExpansionPanels';
set.layoutMode = 'HORIZONTAL'; set.counterAxisAlignItems = 'MIN';
set.setBoundVariable('itemSpacing', vars.ga6); pad(set, vars.pa8);
set.primaryAxisSizingMode = 'AUTO'; set.counterAxisSizingMode = 'AUTO';
set.fills = [];
set.x = skel.x; set.y = skel.y + skel.height + 120;
set.description = [
  'Draft from code: src/components/SExpansionPanels.vue in design-system-beta. Not yet reviewed or published.',
  '',
  'Properties → code props',
  '• multiple = false | true → multiple (default false). false: one panel open at a time (v-model is a number). true: any number open (v-model is an array). Shown here as one vs two panels open.',
  '• default (slot) → the default slot. Put Accordion Row instances (SExpansionPanel) in it, one per panel. Type=custom matches SExpansionPanel\'s structured body; the library says to use Type=general outside Engagement Summary.',
  '',
  'From our code: vertical column, 8px gap (gap/ga-2), width 100% with max-width 370, no padding, transparent background, 4px panel radius, Vuetify dividers and hover overlay removed, variant="accordion" + flat. Sample panels from src/pages/PanelGroup.vue.',
  'From Vuetify: only the open/close behaviour (single vs multiple). The panel look comes from the library\'s Accordion Row.',
].join('\n');

section.resizeWithoutConstraints(Math.max(section.width, set.x + set.width + 80), set.y + set.height + 80);
return { setId: set.id, variants: set.children.map(c => `${c.name} ${Math.round(c.width)}x${Math.round(c.height)} ${c.id}`), props: Object.keys(set.componentPropertyDefinitions) };
