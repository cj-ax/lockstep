// Lockstep follow-up for build-billing.js: label the Dialog's buttons. Inside the build
// call, edits to the Button Group nested in the Dialog's slot don't stick; the same edits in
// a separate call do. ROOTS = the Dialog frames the build returned.
const ROOTS = __ROOT_IDS__;
const PROTECTED_FILE_KEYS = __PROTECTED_FILE_KEYS__;
if (PROTECTED_FILE_KEYS.includes(figma.fileKey)) throw new Error(`Refusing to write: ${figma.fileKey} is a protected file. Use a draft.`);

const page = figma.root.children.find(p => p.name === 'Billing');
await figma.setCurrentPageAsync(page);
await figma.loadFontAsync({ family: 'Inter', style: 'Regular' });
const danger = await figma.importComponentSetByKeyAsync('3d3073170c1014cfacc5d047c23495cfed01e0a8');
const dangerPrimary = danger.children.find(c => c.name === 'Variant=Primary, State=Default, Size=Medium');
const label = (inst, text) => inst.setProperties({ [Object.keys(inst.componentProperties).find(k => k.split('#')[0] === 'Label')]: text });

const out = [];
for (const id of ROOTS) {
  const frame = await figma.getNodeByIdAsync(id);
  const group = frame.findAll(n => n.type === 'INSTANCE' && n.name === 'Button Group')[0];
  const [start, end] = group.children;
  start.setProperties({ Variant: 'Neutral' });
  label(start, 'Keep subscription');
  end.swapComponent(dangerPrimary);
  label(end, 'Cancel subscription');
  out.push({ id, buttons: group.children.map(c => ({ n: c.name, t: c.findOne(n => n.type === 'TEXT').characters })) });
}
return out;
