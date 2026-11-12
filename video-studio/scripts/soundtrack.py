#!/usr/bin/env python3
"""Score a rendered video: a music bed plus sound effects on the page's cues, mixed and muxed (video is not re-encoded).

  soundtrack.py renders/v.mp4 --cues renders/v.cues.json --out renders/v-sound.mp4
                [--music afrohouse | path/to/track.mp3] [--bpm 122] [--key A] [--seed 7]
                [--drop 3.2] [--outro 3.6] [--music-db -20] [--sfx-db -4] [--loudness -14]
  soundtrack.py --music afrohouse --duration 40 --wav-only bed.wav          # just the bed, to audition

--music afrohouse   generate an ORIGINAL Afro house groove in the video's length: four-on-the-floor kick,
                    16th shakers, open hats, claps, tuned congas, a rolling log-drum bass, warm minor-9 chords
                    and a marimba ostinato, sidechained to the kick. Intro bars are percussion + chords;
                    drums leave `--outro` seconds before the end so the close can breathe. `--drop T` lands the
                    full groove's first downbeat at video time T (set it to the first content scene).
--music FILE        use a supplied (licensed) track instead: looped or trimmed to length, faded.
--music none        effects only.

Cue types (from Motion.cue in the page; render_html.mjs writes <out>.cues.json):
  ding    an achievement: a bell chime. Each ding steps UP the key's pentatonic scale, so a run of wins rises.
  tick    a soft marimba note: a row or count landing.
  whoosh  a filtered-noise swell for a transition (centred on the cue).
  hit     a low, soft accent.
Options on a cue: "gain" (multiplier), "note" (MIDI number) to force a pitch.
Needs numpy and scipy (pip install numpy scipy) and ffmpeg.
"""
import argparse, json, os, subprocess, sys, tempfile
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
KEYS = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}


def hz(m): return 440.0 * 2 ** ((m - 69) / 12)
def T(d): return np.arange(int(d * SR)) / SR
def filt(x, kind, f, order=2): return sosfilt(butter(order, f, kind, fs=SR, output='sos'), x)


def place(buf, sig, t, gain=1.0, pan=0.0):
    i = int(round(t * SR))
    if i < 0:
        sig, i = sig[-i:], 0
    if i >= buf.shape[1] or len(sig) == 0:
        return
    n = min(len(sig), buf.shape[1] - i)
    a = (pan + 1) * np.pi / 4
    buf[0, i:i + n] += sig[:n] * gain * np.cos(a) * 1.4142
    buf[1, i:i + n] += sig[:n] * gain * np.sin(a) * 1.4142


# ---------------------------------------------------------------- instruments (mono, peak ~1)
def kick():
    t = T(0.45); f = 46 + 92 * np.exp(-t * 30)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6.5)
    x[:240] += filt(np.random.randn(240), 'highpass', 2500) * np.exp(-t[:240] * 500) * 0.25
    return np.tanh(1.7 * x) / np.tanh(1.7)


def clap(rng):
    t = T(0.32); n = filt(rng.standard_normal(len(t)), 'bandpass', [900, 4800])
    env = np.zeros_like(t)
    for k, ti in enumerate([0, .009, .019, .028]):
        m = t >= ti; env[m] += np.exp(-(t[m] - ti) * (320 if k < 3 else 17)) * (1 if k < 3 else 0.7)
    x = n * env; return x / np.abs(x).max()


def shaker(rng):
    t = T(0.075); x = filt(filt(rng.standard_normal(len(t)), 'highpass', 5200), 'lowpass', 13000)
    env = np.minimum(1, t / 0.004) * np.exp(-t * 58); x = x * env; return x / np.abs(x).max()


def open_hat(rng):
    t = T(0.24); x = filt(rng.standard_normal(len(t)), 'highpass', 7600) * np.exp(-t * 15); return x / np.abs(x).max()


def conga(f, rng):
    t = T(0.32); ff = f * (1 + 0.16 * np.exp(-t * 60)); ph = 2 * np.pi * np.cumsum(ff) / SR
    x = np.sin(ph) * np.exp(-t * 13) + 0.28 * np.sin(1.59 * ph) * np.exp(-t * 24)
    x[:900] += filt(rng.standard_normal(900), 'bandpass', [1200, 3600]) * np.exp(-t[:900] * 110) * 0.35
    return x / np.abs(x).max()


def log_bass(f, dur):
    t = T(dur + 0.04); ff = f * (1 + 0.55 * np.exp(-t * 42)); ph = 2 * np.pi * np.cumsum(ff) / SR
    x = (np.sin(ph) + 0.22 * np.sin(2 * ph)) * np.minimum(1, t / 0.004) * np.exp(-t * 6.5)
    rel = t > dur; x[rel] *= np.exp(-(t[rel] - dur) * 120)
    x = filt(np.tanh(2.2 * x), 'lowpass', 900); return x / np.abs(x).max()


def pad(midis, dur):
    t = T(dur + 0.6); x = np.zeros_like(t)
    for m in midis:
        for c in (-7, 0, 7):
            f = hz(m + c / 100); x += 2 * ((f * t + np.random.rand()) % 1) - 1
    x = filt(filt(x, 'lowpass', 1500), 'highpass', 120)
    env = np.minimum(1, t / 0.35) * np.where(t > dur, np.exp(-(t - dur) * 6), 1.0)
    x = x * env; return x / np.abs(x).max()


def marimba(f):
    t = T(0.6)
    x = (np.sin(2 * np.pi * f * t) * np.exp(-t * 9) + 0.14 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t * 30)
         + 0.05 * np.sin(2 * np.pi * 9.9 * f * t) * np.exp(-t * 70)) * np.minimum(1, t / 0.002)
    return x / np.abs(x).max()


def bell(f):
    t = T(2.4); x = np.zeros_like(t)
    for r, a, d in [(1, 1, 1.5), (2.0, .42, 0.95), (2.76, .28, .65), (4.07, .14, .42), (5.4, .09, .28), (6.8, .05, .18)]:
        x += a * np.sin(2 * np.pi * f * r * t + r) * np.exp(-t / d)
    x *= np.minimum(1, t / 0.003)
    return x / np.abs(x).max()


def whoosh(rng, dur=0.6):
    t = T(dur); n = filt(rng.standard_normal(len(t)), 'bandpass', [600, 7000])
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2
    return n * env / np.abs(n * env).max()


def hit():
    t = T(0.9); x = np.sin(2 * np.pi * np.cumsum(60 + 40 * np.exp(-t * 25)) / SR) * np.exp(-t * 4.5)
    return np.tanh(1.5 * x) / np.tanh(1.5)


def reverb_ir(rng, sec=1.7, decay=0.38):
    t = T(sec); ir = np.zeros((2, len(t)))
    for c in range(2):
        n = filt(rng.standard_normal(len(t)), 'lowpass', 6500) * np.exp(-t / decay)
        n[:int(0.012 * SR)] = 0; ir[c] = n / np.sqrt(np.sum(n ** 2))
    return ir


def apply_reverb(bus, ir):
    out = np.zeros_like(bus)
    for c in range(2):
        out[c] = fftconvolve(bus[c], ir[c])[:bus.shape[1]]
    return out


# ---------------------------------------------------------------- the Afro house bed
def afrohouse(duration, bpm=122, key='A', seed=7, intro_bars=2, outro=4.5, drop=None):
    rng = np.random.default_rng(seed); np.random.seed(seed)
    beat = 60 / bpm; s16 = beat / 4; bar = 4 * beat
    # music time = video time + pre, so the first full-groove downbeat lands on `drop` (video seconds)
    pre = 0.0
    if drop is not None:
        intro_bars = max(1, int(np.ceil(drop / bar - 1e-6))); pre = intro_bars * bar - drop
    v_end = duration; duration = duration + pre
    N = int((duration + 2.5) * SR)
    drums, music, send = np.zeros((2, N)), np.zeros((2, N)), np.zeros((2, N))
    root = 57 + ((KEYS[key] - 9 + 6) % 12 - 6)          # minor key root near A3
    prog = [[0, 3, 7, 10, 14], [-4, 0, 3, 7, 11], [5, 8, 12, 15, 19], [7, 10, 14, 17, 21]]  # i9, VImaj7, iv9, v7(9)
    K, CL, OH = kick(), clap(rng), open_hat(rng)
    shakers = [shaker(rng) for _ in range(4)]
    hiC, loC = conga(hz(root + 7), rng), conga(hz(root), rng)
    kicks = []
    nbars = int(np.ceil(duration / bar)) + 1
    drums_out = (v_end - outro + pre) if outro > 0 else duration + 99
    drums_out = np.round(drums_out / bar) * bar if drums_out < duration else drums_out
    for b in range(nbars):
        t0 = b * bar
        if t0 > duration + 0.5:
            break
        chord = prog[(b // 2) % 4]
        full = b >= intro_bars and t0 < drums_out
        hum = lambda: rng.normal(0, 0.004)
        # shakers through everything (quieter in the outro)
        for s in range(16):
            vel = [0.42, 0.22, 0.7, 0.28][s % 4] * (1 if t0 < drums_out else 0.5) * rng.uniform(0.85, 1.1)
            place(drums, shakers[s % 4], t0 + s * s16 + hum(), 0.16 * vel, 0.35)
        if full:
            for q in range(4):
                tk = t0 + q * beat; place(drums, K, tk, 0.9); kicks.append(tk)
            for q in (1, 3):
                place(drums, CL, t0 + q * beat + hum(), 0.32, -0.05); place(send, CL, t0 + q * beat, 0.16)
            for s in (2, 6, 10, 14):
                place(drums, OH, t0 + s * s16 + hum(), 0.11, -0.2)
            hi = [2, 5, 10, 13] + ([12, 14] if b % 4 == 3 else []); lo = [7, 15] + ([11] if b % 4 == 3 else [])
            for s in hi:
                place(drums, hiC, t0 + s * s16 + hum(), 0.24 * rng.uniform(0.8, 1.05), -0.35); place(send, hiC, t0 + s * s16, 0.05)
            for s in lo:
                place(drums, loC, t0 + s * s16 + hum(), 0.26 * rng.uniform(0.8, 1.05), -0.45)
            for s, iv, v in [(3, 0, .9), (6, 0, .7), (10, 7, .8), (13, 0, .6), (15, 12, .45)]:
                place(music, log_bass(hz(root - 24 + chord[0] % 12 + iv), 0.22), t0 + s * s16, 0.4 * v)
        # chords: one pad per two bars
        if b % 2 == 0:
            p = pad([root + c for c in chord[:4]], 2 * bar)
            place(music, p, t0, 0.13, -0.25); place(music, p, t0 + 0.011, 0.13, 0.25); place(send, p, t0, 0.04)
        # marimba ostinato over chord tones, with a dotted-eighth ping-pong echo
        tones = sorted(set((root + 12 + c) for c in chord))
        for k, s in enumerate([0, 3, 6, 8, 11, 14]):
            f = hz(tones[[0, 2, 1, 3, 2, 1][k] % len(tones)])
            m = marimba(f); tt = t0 + s * s16 + hum(); g = 0.2 * [1, .7, .85, .6, .8, .65][k]
            place(music, m, tt, g, 0.2); place(music, m, tt + 3 * s16, g * 0.35, -0.6); place(music, m, tt + 6 * s16, g * 0.15, 0.6)
            place(send, m, tt, g * 0.4)
    # sidechain: pad, marimba and bass breathe with the kick
    duck = np.ones(N); tt = np.arange(N) / SR
    for tk in kicks:
        i = int(tk * SR); j = min(N, i + int(0.3 * SR))
        duck[i:j] = np.minimum(duck[i:j], 1 - 0.5 * np.exp(-(tt[i:j] - tk) / 0.11))
    mix = drums + music * duck + apply_reverb(send, reverb_ir(rng)) * 0.9
    mix = filt(mix, 'highpass', 30)
    i0 = int(pre * SR); n = int(v_end * SR); mix = mix[:, i0:i0 + n]
    duration = v_end
    fo = int(min(3.0, duration / 4) * SR); mix[:, -fo:] *= np.linspace(1, 0, fo) ** 1.5
    fi = int(0.05 * SR); mix[:, :fi] *= np.linspace(0, 1, fi)
    return mix


# ---------------------------------------------------------------- effects from cues
def effects(cues, duration, key='A', seed=7):
    rng = np.random.default_rng(seed + 1)
    N = int((duration + 3) * SR); fx, send = np.zeros((2, N)), np.zeros((2, N))
    k0 = KEYS[key]; scale = [81 + ((k0 - 9 + 6) % 12 - 6) + i for i in (0, 3, 5, 7, 10, 12)]  # minor pentatonic, octave 5–6
    step, tick_n = 0, 0
    for c in sorted(cues, key=lambda c: c['t']):
        t, g = c['t'], c.get('gain', 1.0)
        if c['type'] == 'ding':
            m = c.get('note', scale[step % len(scale)]); step += 1
            b = bell(hz(m)); pan = rng.uniform(-0.15, 0.15)
            place(fx, b, t, 0.5 * g, pan); place(fx, marimba(hz(m - 12)), t, 0.18 * g, pan); place(send, b, t, 0.22 * g)
        elif c['type'] == 'tick':
            m = c.get('note', scale[[1, 2][tick_n % 2]] - 12); tick_n += 1
            place(fx, marimba(hz(m)), t, 0.22 * g, rng.uniform(-0.2, 0.2)); place(send, marimba(hz(m)), t, 0.05 * g)
        elif c['type'] == 'whoosh':
            w = whoosh(rng); place(fx, w, t - 0.3, 0.12 * g); place(send, w, t - 0.3, 0.05 * g)
        elif c['type'] == 'hit':
            place(fx, hit(), t, 0.35 * g)
    fx = fx + apply_reverb(send, reverb_ir(rng, 2.2, 0.55)) * 1.1
    return fx[:, :int(duration * SR)]


def load_track(path, duration):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True, check=True)
    x = np.frombuffer(r.stdout, dtype=np.float32).reshape(-1, 2).T.copy()
    n = int(duration * SR)
    if x.shape[1] < n:
        x = np.tile(x, (1, int(np.ceil(n / x.shape[1]))))
    x = x[:, :n]; fo = int(min(2.5, duration / 4) * SR); x[:, -fo:] *= np.linspace(1, 0, fo)
    fi = int(0.4 * SR); x[:, :fi] *= np.linspace(0, 1, fi)
    return x


def rms_to(x, db):
    r = np.sqrt(np.mean(x ** 2)) + 1e-12
    return x * (10 ** (db / 20) / r)


def write_wav(path, x):
    x = np.clip(x, -1, 1).T.astype(np.float32)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', '-c:a', 'pcm_s24le', path],
                   input=x.tobytes(), check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('video', nargs='?')
    ap.add_argument('--cues'); ap.add_argument('--out'); ap.add_argument('--music', default='afrohouse')
    ap.add_argument('--bpm', type=float, default=122); ap.add_argument('--key', default='A'); ap.add_argument('--seed', type=int, default=7)
    ap.add_argument('--intro-bars', type=int, default=2); ap.add_argument('--outro', type=float, default=4.5)
    ap.add_argument('--drop', type=float, help='video time (s) where the full groove starts, e.g. the first content scene')
    ap.add_argument('--music-db', type=float, default=-20); ap.add_argument('--sfx-db', type=float, default=-4)
    ap.add_argument('--loudness', type=float, default=-14); ap.add_argument('--duration', type=float)
    ap.add_argument('--wav-only')
    a = ap.parse_args()

    dur = a.duration
    if a.video and not dur:
        dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', a.video],
                                   capture_output=True, text=True, check=True).stdout)
    if not dur:
        sys.exit('Give a video or --duration')
    cues = []
    cpath = a.cues or (a.video and os.path.splitext(a.video)[0] + '.cues.json')
    if cpath and os.path.exists(cpath):
        cues = json.load(open(cpath))['cues']

    mix = np.zeros((2, int(dur * SR)))
    if a.music == 'afrohouse':
        mix += rms_to(afrohouse(dur, a.bpm, a.key, a.seed, a.intro_bars, a.outro, a.drop), a.music_db)
    elif a.music != 'none':
        mix += rms_to(load_track(a.music, dur), a.music_db)
    if cues:
        fx = effects(cues, dur, a.key, a.seed)
        mix[:, :fx.shape[1]] += fx * 10 ** (a.sfx_db / 20) / max(1e-9, np.abs(fx).max())
    mix = np.tanh(mix * 1.1) / np.tanh(1.1) * 0.95          # gentle safety saturation; loudnorm sets the level

    if a.wav_only:
        write_wav(a.wav_only, mix); print(f'{a.wav_only} ({dur:.1f}s, {len(cues)} cues)'); return
    if not a.video:
        sys.exit('Give a video to mux into, or --wav-only')
    out = a.out or os.path.splitext(a.video)[0] + '-sound.mp4'
    with tempfile.TemporaryDirectory() as td:
        wav = os.path.join(td, 'mix.wav'); write_wav(wav, mix)
        tmp = out.replace('.mp4', '.tmp.mp4')
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', a.video, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                        '-af', f'loudnorm=I={a.loudness}:TP=-1.5:LRA=11,aresample={SR}', '-c:a', 'aac', '-b:a', '192k',
                        '-t', f'{dur:.3f}', '-movflags', '+faststart', tmp], check=True)
        os.replace(tmp, out)
    print(f'{out}  ({dur:.1f}s, music: {a.music}, {len(cues)} cues)')


if __name__ == '__main__':
    main()
