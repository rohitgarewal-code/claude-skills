#!/usr/bin/env node
// Render a seekable HTML animation to video (MP4, or ProRes 4444 with alpha) using Playwright + ffmpeg.
//
// The page must be deterministic in time: the renderer pauses it and, for every frame, calls
// window.seek(t) if defined, and also seeks every CSS/Web animation to t. templates/scene.html does this.
//
// Usage:
//   node render_html.mjs page.html --out out.mp4 [--fps 30] [--width 1920 --height 1080]
//        [--from 0 --to 12.5] [--workers 4] [--audio vo.wav] [--crf 18] [--preset veryfast]
//        [--scale 4/3]   draw the same layout at a higher pixel density: 1920x1080 at 4/3 = 2560x1440 output
//   node render_html.mjs page.html --alpha --out overlay.mov        # transparent overlay for vlog edits
//   node render_html.mjs page.html --stills 2.5,9,31 --out stills/  # PNG checks before a full render
//   node render_html.mjs page.html --cues-only --out out.mp4          # just write out.cues.json (sound moments)
// When the page declares sound cues (Motion.cue), a full render also writes <out>.cues.json for soundtrack.py.
//
// Duration defaults to window.DURATION. Needs ffmpeg on PATH and the playwright npm package
// (npm i -D playwright && npx playwright install chromium), or Chrome via --chrome / CHROME_PATH.

import { spawn, execSync } from 'node:child_process';
import { createRequire } from 'node:module';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

function parseArgs(argv) {
  const o = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const k = a.slice(2);
      const next = argv[i + 1];
      if (next === undefined || next.startsWith('--')) o[k] = true;
      else { o[k] = next; i++; }
    } else o._.push(a);
  }
  return o;
}

function loadPlaywright() {
  const tries = [
    () => createRequire(path.join(process.cwd(), 'x.js'))('playwright'),
    () => createRequire(import.meta.url)('playwright'),
    () => createRequire(path.join(execSync('npm root -g').toString().trim(), 'x.js'))('playwright'),
  ];
  for (const t of tries) { try { return t(); } catch {} }
  console.error('playwright not found. In the project folder run: npm i -D playwright && npx playwright install chromium');
  process.exit(2);
}

async function launch(chromium, chromePath) {
  const opts = { args: ['--force-color-profile=srgb', '--hide-scrollbars', '--font-render-hinting=none'] };
  const exe = chromePath || process.env.CHROME_PATH;
  if (exe) return chromium.launch({ ...opts, executablePath: exe });
  try { return await chromium.launch(opts); } catch (e) {
    try { return await chromium.launch({ ...opts, channel: 'chrome' }); } catch { throw e; }
  }
}

function run(cmd, args) {
  return new Promise((res, rej) => {
    const p = spawn(cmd, args, { stdio: ['ignore', 'ignore', 'pipe'] });
    let err = '';
    p.stderr.on('data', d => { err += d; });
    p.on('close', c => (c === 0 ? res() : rej(new Error(`${cmd} exited ${c}\n${err.slice(-2000)}`))));
  });
}

const A = parseArgs(process.argv.slice(2));
const input = A._[0];
if (!input) { console.error('usage: render_html.mjs page.html --out out.mp4 [options]'); process.exit(1); }
const fps = Number(A.fps || 30);
const W = Number(A.width || 1920), H = Number(A.height || 1080);
const SCALE = (v => (v.includes('/') ? v.split('/').map(Number).reduce((a, b) => a / b) : Number(v)))(String(A.scale || '1'));
if (!(SCALE >= 1)) { console.error('--scale must be 1 or more (e.g. 4/3)'); process.exit(1); }
const OW = Math.round(W * SCALE / 2) * 2, OH = Math.round(H * SCALE / 2) * 2;
const alpha = !!A.alpha;
const crf = String(A.crf || 18), preset = String(A.preset || 'veryfast');
const out = path.resolve(A.out || (alpha ? 'overlay.mov' : 'out.mp4'));
const url = pathToFileURL(path.resolve(input)).href + `?render=1${alpha ? '&alpha=1' : ''}`;

const { chromium } = loadPlaywright();
const browser = await launch(chromium, A.chrome);

async function openPage() {
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: SCALE });
  page.on('pageerror', e => console.error('[page error]', e.message));
  page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') console.error('[page]', m.text()); });
  await page.goto(url, { waitUntil: 'load' });
  await page.evaluate(async () => {
    await document.fonts.ready;
    if (window.READY && typeof window.READY.then === 'function') await window.READY;
    await Promise.all([...document.images].map(i => (i.complete ? null : new Promise(r => { i.onload = i.onerror = r; }))));
  });
  return page;
}

async function seek(page, t) {
  await page.evaluate(async t => {
    if (typeof window.seek === 'function') await window.seek(t);
    for (const a of document.getAnimations()) { a.pause(); a.currentTime = t * 1000; }
  }, t);
}

async function shot(page, type) {
  return type === 'png'
    ? page.screenshot({ type: 'png', omitBackground: alpha })
    : page.screenshot({ type: 'jpeg', quality: 92 });
}

// --- stills mode: draw a few frames at full size and look at them before a full render
if (A.stills) {
  const dir = out.endsWith('.mp4') || out.endsWith('.mov') ? path.dirname(out) : out;
  fs.mkdirSync(dir, { recursive: true });
  const page = await openPage();
  for (const t of String(A.stills).split(',').map(Number)) {
    await seek(page, t);
    const f = path.join(dir, `still_${t.toFixed(2)}s.png`);
    fs.writeFileSync(f, await shot(page, 'png'));
    console.log(f);
  }
  await browser.close();
  process.exit(0);
}

// --- full render
const probe = await openPage();
const duration = Number(A.duration || (await probe.evaluate(() => window.DURATION)));
const cues = await probe.evaluate(() => window.CUES || []);
await probe.close();
const cuesFile = out.replace(/\.(mp4|mov)$/i, '') + '.cues.json';
if (cues.length) fs.writeFileSync(cuesFile, JSON.stringify({ duration, cues: [...cues].sort((a, b) => a.t - b.t) }, null, 1));
if (A['cues-only']) { await browser.close(); console.log(cues.length ? `${cuesFile} (${cues.length} cues)` : 'page declares no cues'); process.exit(0); }
if (!duration || !isFinite(duration)) { console.error('No duration: set window.DURATION in the page or pass --duration'); process.exit(1); }
const from = Number(A.from || 0), to = Math.min(Number(A.to || duration), duration);
const total = Math.round((to - from) * fps);
const workers = Math.max(1, Math.min(Number(A.workers || Math.max(1, Math.floor(os.cpus().length / 2))), 8, total));
const ext = alpha ? '.mov' : '.mp4';
const base = out.replace(/\.(mp4|mov)$/i, '');
const t0 = Date.now();

function encoderArgs(tmp) {
  // Screenshots arrive as full-range JPEG. Convert to TV range (what players and YouTube expect) and to the
  // exact output size, instead of only tagging the range, which leaves full-range values in a TV-range file.
  const inArgs = ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', alpha ? 'png' : 'mjpeg', '-i', '-',
    ...(alpha ? [] : ['-vf', `scale=${OW}:${OH}:flags=lanczos+accurate_rnd+full_chroma_int:in_range=pc:out_range=tv,format=yuv420p`])];
  const enc = alpha
    ? ['-c:v', 'prores_ks', '-profile:v', '4444', '-pix_fmt', 'yuva444p10le', '-vendor', 'apl0']
    : ['-c:v', 'libx264', '-preset', preset, '-crf', crf, '-pix_fmt', 'yuv420p', '-color_range', 'tv', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-movflags', '+faststart'];
  return [...inArgs, ...enc, '-r', String(fps), tmp];
}

let done = 0;
async function renderChunk(idx, f0, f1) {
  const tmp = `${base}.part${idx}.tmp${ext}`;
  const final = `${base}.part${idx}${ext}`;
  const page = await openPage();
  const ff = spawn('ffmpeg', encoderArgs(tmp), { stdio: ['pipe', 'ignore', 'pipe'] });
  let err = '';
  ff.stderr.on('data', d => { err += d; });
  const closed = new Promise((res, rej) => ff.on('close', c => (c === 0 ? res() : rej(new Error(`ffmpeg exited ${c}: ${err.slice(-1500)}`)))));
  for (let i = f0; i < f1; i++) {
    await seek(page, from + i / fps);
    const buf = await shot(page, alpha ? 'png' : 'jpeg');
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    done++;
    if (done % (fps * 2) === 0) process.stderr.write(`\r${done}/${total} frames  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  ff.stdin.end();
  await closed;
  await page.close();
  fs.renameSync(tmp, final); // a stopped render never leaves a playable-but-short file under the final name
  return final;
}

const per = Math.ceil(total / workers);
const jobs = [];
for (let w = 0; w < workers; w++) {
  const f0 = w * per, f1 = Math.min(total, f0 + per);
  if (f0 < f1) jobs.push(renderChunk(w, f0, f1));
}
const parts = await Promise.all(jobs);
await browser.close();
process.stderr.write(`\r${total}/${total} frames  ${((Date.now() - t0) / 1000).toFixed(0)}s\n`);

// join parts losslessly (same size, rate and encoder settings), then add sound without re-encoding video
const list = `${base}.parts.txt`;
fs.writeFileSync(list, parts.map(p => `file '${p.replace(/'/g, "'\\''")}'`).join('\n'));
const joined = A.audio ? `${base}.silent.tmp${ext}` : `${base}.tmp${ext}`;
await run('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy', joined]);
if (A.audio) {
  const dur = (to - from).toFixed(3);
  await run('ffmpeg', ['-y', '-loglevel', 'error', '-i', joined, '-i', A.audio, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
    '-c:a', alpha ? 'pcm_s16le' : 'aac', '-b:a', '192k', '-t', dur, `${base}.tmp${ext}`]);
  fs.unlinkSync(joined);
}
fs.renameSync(`${base}.tmp${ext}`, out);
for (const p of parts) fs.unlinkSync(p);
fs.unlinkSync(list);
console.log(`${out}  (${(to - from).toFixed(2)}s, ${total} frames @ ${fps}fps, ${OW}x${OH}, ${workers} workers, ${((Date.now() - t0) / 1000).toFixed(0)}s)`);
