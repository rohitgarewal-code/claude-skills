/* Launch Control components for video-studio. Load AFTER the Motion engine and BEFORE your timeline.
   API: map(svgId) → svg; nodesOf(svg); node(nodesOf(svg), {x,y,w,h,label,state,title,owners,kind}) → {g,l,r,b};
   link(svg, fromPt, toPt, 'charged'|'moving'|'pending'|'blocked'|'togate', particleStart) → mask path to draw on;
   enter([{n, links:[...]}], at, stagger); lanePill(nodesOf(svg), {x,y,w,h,label}); queue(svg, {x,y0,y1,start}).
   States: done progress waiting blocked gate none. Easing: Motion.EASE.settle / .camera. */
Motion.EASE.settle = Motion.bezier(0.22, 0.9, 0.24, 1);
Motion.EASE.camera = Motion.bezier(0.645, 0.045, 0.355, 1);
const NS = 'http://www.w3.org/2000/svg';
const ST = {
  done: { c: 'var(--state-done)', w: 'Done', fill: 'var(--fill-done)' },
  progress: { c: 'var(--state-progress)', w: 'In progress' },
  waiting: { c: 'var(--state-waiting)', w: 'Waiting', id: 'var(--ink-pending)', title: 'var(--ink-waiting)' },
  blocked: { c: 'var(--state-blocked)', w: 'Blocked' },
  gate: { c: 'var(--state-gate)', w: 'Not started', fill: 'var(--fill-gate)' },
  none: { c: 'var(--line-strong)', w: '', id: 'var(--ink-2)' },
};
const loops = []; // fn(t) for anything that loops: spinners, marching dashes, particles, halos
Motion.hook(t => loops.forEach(f => f(t)));
function mk(tag, attrs, parent) { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; }
function defs(svg) {
  const d = mk('defs', {}, svg);
  const f = mk('filter', { id: svg.id + '-blur', x: '-50%', y: '-50%', width: '200%', height: '200%' }, d); mk('feGaussianBlur', { stdDeviation: 18 }, f);
  const f2 = mk('filter', { id: svg.id + '-pglow', x: '-100%', y: '-100%', width: '300%', height: '300%' }, d); mk('feGaussianBlur', { stdDeviation: 5 }, f2);
  return d;
}
// Node: 3px state bar (scaled), state icon, mono ID line in the state colour, title, owner discs. Halo for active work.
const lcChecks = [];
// warn (in the render output) when a node's text is wider than the node
document.fonts.ready.then(() => setTimeout(() => lcChecks.forEach(f => f()), 0));
function node(svg, o) {
  const root = svg.ownerSVGElement || svg;
  const s = ST[o.state], h = o.h || 120, w = o.w || 520, x = o.x, y = o.y, cy = y + h / 2;
  const g = mk('g', { class: o.cls || '' }, svg);
  if (['done', 'progress', 'blocked'].includes(o.state)) {
    const halo = mk('rect', { x: x + 10, y: y + 10, width: w - 20, height: h - 20, rx: 28, fill: s.c, opacity: 0.16, filter: `url(#${root.id}-blur)` }, g);
    if (o.state === 'progress') loops.push(t => halo.setAttribute('opacity', 0.12 + 0.08 * Math.sin(t * 2 * Math.PI / 2.8)));
  }
  mk('rect', { x, y, width: w, height: h, rx: o.kind === 'gate' ? 26 : 24, fill: s.fill || 'var(--surface-card)', stroke: o.kind === 'gate' ? 'rgba(34,211,238,.35)' : 'var(--line)', 'stroke-width': 2 }, g);
  if (o.kind !== 'gate') mk('rect', { x: x + 12, y: y + 22, width: 7, height: h - 44, rx: 3.5, fill: s.c }, g);
  const ix = x + 66;
  icon(g, o.kind === 'gate' ? 'gate' : o.state, ix, cy);
  const tx = x + 112;
  const lines = String(o.title).split('\n');
  const top = cy - (lines.length * 40 + 34) / 2 + 22;
  const idT = mk('text', { x: tx, y: top, class: 'nid', fill: s.id || s.c }, g); idT.textContent = o.label + (s.w ? ' · ' + s.w : '');
  lines.forEach((ln, i) => { const tt = mk('text', { x: tx, y: top + 46 + i * 40, class: 'ntitle', fill: s.title || 'var(--ink)' }, g); tt.textContent = ln; });
  const texts = [...g.querySelectorAll('text')];
  lcChecks.push(() => {
    const need = Math.max(...texts.map(t => t.getComputedTextLength())) + (tx - x) + ((o.owners || []).length ? 30 + 40 * o.owners.length : 28);
    if (need > w + 1) console.warn(`LC node "${o.label}" needs ${Math.ceil(need)}px but is ${w}px wide: widen it or shorten the label/title`);
  });
  (o.owners || []).forEach((ini, i) => {
    const ox = x + w - 46 - i * 40;
    mk('circle', { cx: ox, cy, r: 24, fill: 'var(--surface-avatar)', stroke: 'rgba(255,255,255,.18)', 'stroke-width': 2 }, g);
    const it = mk('text', { x: ox, y: cy + 6, class: 'ini', 'text-anchor': 'middle' }, g); it.textContent = ini;
  });
  return { g, state: o.state, l: { x, y: cy }, r: { x: x + w, y: cy }, b: { x: x + w / 2, y: y + h } };
}
function icon(g, state, x, y) {
  if (state === 'done') { mk('circle', { cx: x, cy: y, r: 21, fill: 'var(--state-done)' }, g); mk('path', { d: `M ${x - 9} ${y + 1} L ${x - 3} ${y + 7} L ${x + 10} ${y - 7}`, fill: 'none', stroke: 'var(--on-done)', 'stroke-width': 4.5, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, g); }
  else if (state === 'blocked') { mk('circle', { cx: x, cy: y, r: 21, fill: 'var(--state-blocked)' }, g); mk('path', { d: `M ${x - 7} ${y - 7} L ${x + 7} ${y + 7} M ${x + 7} ${y - 7} L ${x - 7} ${y + 7}`, stroke: 'var(--on-blocked)', 'stroke-width': 4.5, 'stroke-linecap': 'round' }, g); }
  else if (state === 'progress') {
    mk('circle', { cx: x, cy: y, r: 18, fill: 'none', stroke: 'rgba(96,165,250,.25)', 'stroke-width': 4 }, g);
    const a = mk('path', { d: `M ${x} ${y - 18} A 18 18 0 0 1 ${x + 18} ${y}`, fill: 'none', stroke: 'var(--state-progress)', 'stroke-width': 4, 'stroke-linecap': 'round' }, g);
    loops.push(t => a.setAttribute('transform', `rotate(${(t / 1.1) * 360 % 360} ${x} ${y})`));
  }
  else if (state === 'waiting') mk('circle', { cx: x, cy: y, r: 18, fill: 'none', stroke: 'var(--state-waiting)', 'stroke-width': 3.5, 'stroke-dasharray': '5 5.3' }, g);
  else if (state === 'gate') { const r = 21, p = [...Array(6)].map((_, i) => { const an = Math.PI / 3 * i - Math.PI / 2; return `${x + r * Math.cos(an)},${y + r * Math.sin(an)}`; }).join(' ');
    mk('polygon', { points: p, fill: 'none', stroke: 'var(--state-gate)', 'stroke-width': 3.5, 'stroke-linejoin': 'round' }, g); }
  else mk('circle', { cx: x, cy: y, r: 18, fill: 'none', stroke: 'var(--ink-3)', 'stroke-width': 3 }, g);
}
// Link: cubic with horizontal tangents. kind: charged (particles) | moving | pending | blocked. Draws on through a mask.
let linkN = 0;
const LK = {
  charged: { c: 'var(--state-done)', o: 0.55, dash: null },
  moving: { c: 'var(--state-progress)', o: 0.75, dash: [12, 17], dur: 0.8 },
  pending: { c: 'var(--ink-pending)', o: 0.45, dash: [7, 22], dur: 1.4 },
  blocked: { c: 'var(--state-blocked)', o: 0.75, dash: [10, 19], dur: 1.4 },
  togate: { c: 'var(--state-gate)', o: 0.4, dash: null },
};
function link(svg, a, b, kind, pStart) {
  const s = LK[kind], id = svg.id + '-lk' + (linkN++);
  const off = Math.max(90, (b.x - a.x) / 2);
  const d = `M ${a.x} ${a.y} C ${a.x + off} ${a.y}, ${b.x - off} ${b.y}, ${b.x} ${b.y}`;
  const df = svg.querySelector('defs');
  const m = mk('mask', { id, maskUnits: 'userSpaceOnUse', x: 0, y: 0, width: 1920, height: 1080 }, df);
  const mp = mk('path', { d, fill: 'none', stroke: '#fff', 'stroke-width': 30, 'stroke-linecap': 'round' }, m);
  const g = mk('g', { mask: `url(#${id})` }, svg.querySelector('.links'));
  const p = mk('path', { d, fill: 'none', stroke: s.c, 'stroke-width': 4.2, opacity: s.o, 'stroke-linecap': 'round' }, g);
  if (s.dash) { p.setAttribute('stroke-dasharray', s.dash.join(' ')); const cyc = s.dash[0] + s.dash[1]; loops.push(t => p.setAttribute('stroke-dashoffset', -((t / s.dur) * cyc) % cyc)); }
  if (kind === 'charged') {
    const len = p.getTotalLength(), n = Math.max(1, Math.min(4, Math.round(len / 400)));
    const parts = [...Array(n)].map(() => { const pg = mk('g', { opacity: 0 }, svg.querySelector('.parts'));
      mk('circle', { r: 13, fill: 'var(--state-done)', opacity: 0.55, filter: `url(#${svg.id}-pglow)` }, pg); mk('circle', { r: 5.5, fill: 'var(--particle-core-done)' }, pg); return pg; });
    loops.push(t => parts.forEach((pg, k) => {
      if (t < pStart) { pg.setAttribute('opacity', 0); return; }
      const u = ((((t - pStart) * 190) / len + k / n) % 1);
      const pt = p.getPointAtLength(u * len);
      pg.setAttribute('transform', `translate(${pt.x} ${pt.y})`);
      pg.setAttribute('opacity', Math.min(1, (t - pStart) * 2) * Math.min(1, u * 8, (1 - u) * 8));
    }));
  }
  return mp;
}
function map(id) { const svg = document.getElementById(id); defs(svg); mk('g', { class: 'links' }, svg); mk('g', { class: 'parts' }, svg); mk('g', { class: 'nodes' }, svg); return svg; }
const nodesOf = svg => svg.querySelector('.nodes');
// Opening sequence: nodes rise in left to right (settle), each link draws on 160 ms after its target lands.
function enter(items, at, step = 0.09) {
  items.forEach((it, i) => {
    const t0 = at + i * step;
    Motion.tween(it.n.g, { at: t0, dur: 0.6, ease: 'settle', from: { opacity: 0, y: 22 } });
    if (it.n.state === 'done' && it.ding !== false) Motion.cue(t0 + 0.12, 'ding'); // achievement lands
    (it.links || []).forEach(mp => Motion.tween(mp, { at: t0 + 0.16, dur: 1.0, ease: 'settle', from: { draw: 0 }, to: { draw: 1 } }));
  });
}

// Lane pill: a stateless label on the map (owners, layers, teams)
function lanePill(svg, o) {
  const g = mk('g', {}, svg);
  mk('rect', { x: o.x, y: o.y, width: o.w, height: o.h, rx: o.h / 2, fill: 'var(--surface-overlay)', stroke: 'var(--line-strong)', 'stroke-width': 2 }, g);
  const t = mk('text', { x: o.x + o.w / 2, y: o.y + o.h / 2 + 8, class: 'lane', 'text-anchor': 'middle' }, g); t.textContent = o.label;
  return { g, l: { x: o.x, y: o.y + o.h / 2 }, r: { x: o.x + o.w, y: o.y + o.h / 2 } };
}
// Queue: items flow down a straight charged link and pile up against a red barrier (the "blocked" pattern).
// Returns { mask, barrier } to animate in: Motion.tween(q.mask, {draw}) and Motion.tween(q.barrier, {opacity, scale}).
function queue(svg, o) {
  const { x, y0, y1, start, count = 9, gap = 0.42, speed = 300, spacing = 22 } = o;
  const id = svg.id + '-q' + (linkN++);
  const m = mk('mask', { id, maskUnits: 'userSpaceOnUse', x: 0, y: 0, width: 1920, height: 1080 }, svg.querySelector('defs'));
  const mp = mk('path', { d: `M ${x} ${y0} L ${x} ${y1}`, stroke: '#fff', 'stroke-width': 30 }, m);
  mk('path', { d: `M ${x} ${y0} L ${x} ${y1}`, stroke: 'var(--state-done)', 'stroke-width': 4.2, opacity: 0.55, mask: `url(#${id})` }, svg.querySelector('.links'));
  const barrier = mk('rect', { x: x - 52, y: y1 - 3, width: 104, height: 7, rx: 3.5, fill: 'var(--state-blocked)' }, nodesOf(svg));
  const len = y1 - y0, P = svg.querySelector('.parts');
  const dots = [...Array(count)].map(() => { const g = mk('g', { opacity: 0 }, P);
    mk('circle', { r: 12, fill: 'var(--state-done)', opacity: 0.5, filter: `url(#${svg.id}-pglow)` }, g); mk('circle', { r: 6, fill: 'var(--particle-core-done)' }, g); return g; });
  loops.push(t => dots.forEach((d, i) => {
    const born = start + i * gap;
    if (t < born) { d.setAttribute('opacity', 0); return; }
    const yy = y0 + Math.min(len - 16 - i * spacing, (t - born) * speed);
    d.setAttribute('transform', `translate(${x} ${yy})`); d.setAttribute('opacity', Math.min(1, (t - born) * 6));
  }));
  return { mask: mp, barrier };
}
