// Lockstep settle: run through use_figma in a DRAFT file right after a build, before scoring.
// Figma quirk: a library instance a script sizes differently from its component can keep
// drawing its insides at the component's original width (a text field whose outline stops
// halfway, a dropdown arrow floating past its box) until something makes Figma lay it out
// again. Its layers report the right size, so the score can't see it; only renders do.
// This nudges every library instance the build placed (including slot contents) one pixel and
// back, which forces that relayout without changing any size. Safe to run more than once.
const ROOT_IDS = __ROOT_IDS__;
const PROTECTED_FILE_KEYS = __PROTECTED_FILE_KEYS__;
if (PROTECTED_FILE_KEYS.includes(figma.fileKey)) throw new Error(`Refusing to write: ${figma.fileKey} is a protected file. Use a draft.`);

// This instance's own slots; findAll does not return slot contents, so walk them explicitly.
const ownSlots = inst => inst.findAll(n => n.type === 'SLOT').filter(s => {
  let p = s.parent;
  while (p && p.type !== 'INSTANCE') p = p.parent;
  return p && p.id === inst.id;
});

const nudged = [];
async function visit(n) {
  if (n.type === 'INSTANCE') {
    const main = await n.getMainComponentAsync();
    const inAutoLayout = n.parent && n.parent.layoutMode && n.parent.layoutMode !== 'NONE';
    if (main && inAutoLayout && Math.abs(main.width - n.width) >= 1) {
      const mode = n.layoutSizingHorizontal;
      const w = n.width;
      n.layoutSizingHorizontal = 'FIXED';
      n.resize(w + 1, n.height);
      n.resize(w, n.height);
      n.layoutSizingHorizontal = mode;
      nudged.push(n.id);
    }
    for (const s of ownSlots(n)) for (const c of s.children) await visit(c);
    return;
  }
  if ('children' in n) for (const c of n.children) await visit(c);
}

for (const id of ROOT_IDS) {
  const root = await figma.getNodeByIdAsync(id);
  if (!root) throw new Error(`No node ${id}`);
  await visit(root);
}
return { settled: nudged.length };
