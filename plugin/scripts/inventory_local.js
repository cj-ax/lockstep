// Lockstep local inventory (read-only): a library's own components and tokens, read in place.
// For half-built or unpublished libraries, where importing by key fails. Run through use_figma
// in the library file itself; the write guard lets this script through even when the file is
// protected, because it changes nothing.
// - PART 'components': every component and component set on PAGE_IDS (all pages when empty):
//   properties, default variant, size, description, publish status, how many instances this
//   file has, and the structure signature audit.js uses, so learn can match a local component
//   to the detached copies and repeated structures it duplicates.
// - PART 'variables': every local variable collection with modes, values (aliases by name)
//   and scopes, plus local text, colour and effect styles.
const PART = __PART__;
const PAGE_IDS = __PAGE_IDS__;
const MAX_DESCRIPTION = 600;
const MAX_COMPONENTS = 150;

const h2 = n => Math.round(n * 255).toString(16).padStart(2, '0');
const hex = c => '#' + h2(c.r) + h2(c.g) + h2(c.b) + (c.a !== undefined && c.a < 0.999 ? h2(c.a) : '');

if (PART === 'variables') {
  const collections = [];
  for (const col of await figma.variables.getLocalVariableCollectionsAsync()) {
    const rows = [];
    for (const id of col.variableIds) {
      const v = await figma.variables.getVariableByIdAsync(id);
      if (!v) continue;
      const values = [];
      for (const m of col.modes) {
        const val = v.valuesByMode[m.modeId];
        if (val && val.type === 'VARIABLE_ALIAS') { const a = await figma.variables.getVariableByIdAsync(val.id); values.push(`→${a ? a.name : val.id}`); }
        else values.push(val && typeof val === 'object' && 'r' in val ? hex(val) : val);
      }
      // [name, type, values per mode, scopes, hidden from publishing]
      rows.push([v.name, v.resolvedType, values, v.scopes.join(','), v.hiddenFromPublishing || undefined]);
    }
    collections.push({ name: col.name, id: col.id, modes: col.modes.map(m => m.name), hidden: col.hiddenFromPublishing || undefined, variables: rows });
  }
  const styles = [];
  for (const s of await figma.getLocalTextStylesAsync()) styles.push(['TEXT', s.name, `${s.fontName.family} ${s.fontName.style} ${s.fontSize} ${s.lineHeight.unit === 'AUTO' ? 'auto' : s.lineHeight.value + (s.lineHeight.unit === 'PERCENT' ? '%' : 'px')}`]);
  for (const s of await figma.getLocalPaintStylesAsync()) styles.push(['PAINT', s.name, s.paints.map(p => p.type === 'SOLID' ? hex({ ...p.color, a: p.opacity }) : p.type).join(' ')]);
  for (const s of await figma.getLocalEffectStylesAsync()) styles.push(['EFFECT', s.name, s.effects.map(e => e.type).join(' ')]);
  return { file: figma.fileKey, collections, styles };
}

// Same signature as audit.js; keep the two in step.
const SHAPES = new Set(['RECTANGLE', 'ELLIPSE', 'VECTOR', 'LINE', 'POLYGON', 'STAR', 'BOOLEAN_OPERATION']);
const visible = arr => (Array.isArray(arr) ? arr : []).filter(p => p.visible !== false && (p.opacity === undefined || p.opacity > 0));
const r4 = v => Math.round((v || 0) / 4) * 4;
function sig(n, depth) {
  if (n.type === 'TEXT') return `T(${typeof n.fontName === 'object' && n.fontName.family ? n.fontName.family + ' ' + n.fontName.style : 'mixed'} ${typeof n.fontSize === 'number' ? n.fontSize : 'mixed'})`;
  if (n.type === 'INSTANCE') return `I(${n.name.split('=')[0]})`;
  if (n.type === 'SLOT') return 'S';
  if (SHAPES.has(n.type)) return n.type[0];
  if (!('children' in n)) return n.type;
  const lay = n.layoutMode && n.layoutMode !== 'NONE'
    ? `${n.layoutMode[0]}${r4(n.paddingTop)},${r4(n.paddingRight)},${r4(n.paddingBottom)},${r4(n.paddingLeft)}g${r4(n.itemSpacing)}`
    : 'abs';
  const paint = `${visible(n.fills).length ? 'f' : ''}${visible(n.strokes).length ? 's' : ''}${typeof n.cornerRadius === 'number' && n.cornerRadius > 0 ? 'r' : ''}${(n.effects || []).some(e => e.visible !== false) ? 'e' : ''}`;
  if (depth <= 0) return `F(${lay}${paint})`;
  return `F(${lay}${paint})[${n.children.filter(c => c.visible !== false).map(c => sig(c, depth - 1)).join(',')}]`;
}

const pages = PAGE_IDS.length ? await Promise.all(PAGE_IDS.map(id => figma.getNodeByIdAsync(id))) : figma.root.children;
const components = [];
let truncated = false;
for (const page of pages) {
  if (!page || page.type !== 'PAGE') continue;
  await page.loadAsync();
  for (const node of page.findAllWithCriteria({ types: ['COMPONENT_SET', 'COMPONENT'] })) {
    if (node.type === 'COMPONENT' && node.parent && node.parent.type === 'COMPONENT_SET') continue;
    if (components.length >= MAX_COMPONENTS) { truncated = true; break; }
    const props = {};
    for (const [k, v] of Object.entries(node.componentPropertyDefinitions)) {
      props[k.split('#')[0]] = v.type === 'VARIANT' ? v.variantOptions : v.type === 'SLOT' ? 'SLOT' : `${v.type}=${JSON.stringify(v.defaultValue)}`;
    }
    const d = node.type === 'COMPONENT_SET' ? node.defaultVariant : node;
    let instances = 0;
    for (const c of node.type === 'COMPONENT_SET' ? node.children : [node]) instances += (await c.getInstancesAsync()).length;
    components.push({
      name: node.name, id: node.id, page: page.name, type: node.type, key: node.key,
      status: await node.getPublishStatusAsync(), variants: node.type === 'COMPONENT_SET' ? node.children.length : 1,
      props, default: d.name, size: [Math.round(d.width), Math.round(d.height)], instancesInFile: instances,
      detachedFrom: d.detachedInfo ? (d.detachedInfo.componentKey || d.detachedInfo.componentId) : undefined,
      description: (node.description || '').slice(0, MAX_DESCRIPTION) || undefined,
      sig: { full: sig(d, 3), shell: sig(d, 1) },
    });
  }
}
return { file: figma.fileKey, components, truncated, note: truncated ? `Stopped at ${MAX_COMPONENTS}; pass fewer PAGE_IDS per call.` : undefined };
