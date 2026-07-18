"""
MyNexus Premium Promotional Video Generator  v2
------------------------------------------------
Premium features:
  • Synthesised ambient soundtrack (piano + pad chords + soft bass)
  • Animated slide-in transitions (screenshot glides in from right)
  • Particle / floating-dot background on title & closing slides
  • Glowing accent lines & radial gradient backgrounds
  • Animated progress bar at bottom showing video progress
  • Fade-in text animations per slide
  • Ken-Burns-style subtle zoom on screenshots
  • Copyright watermark corner-logo on every frame

Output: C:/MyNexus-Release/MyNexus-Promo-Premium.mp4
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, sys, wave, struct, math, tempfile, subprocess

# ── Config ─────────────────────────────────────────────────────────────────────
ROOT     = os.path.dirname(os.path.abspath(__file__))
SS_DIR   = os.path.join(ROOT, "assets", "screenshots")
OUT_PATH = r"C:\MyNexus-Release\MyNexus-Promo-Premium.mp4"
WAV_PATH = os.path.join(tempfile.gettempdir(), "mynexus_music.wav")

W, H   = 1280, 720
FPS    = 30
SRATE  = 44100

# ── Colour palette ─────────────────────────────────────────────────────────────
BG      = (12, 15, 22)          # deep navy   BGR
BG2     = (18, 24, 36)          # slightly lighter panel
ACCENT  = (0, 185, 255)         # electric blue BGR
GOLD    = (0, 195, 255)         # same family, slightly warmer
WHITE   = (255, 255, 255)
GRAY    = (150, 158, 175)
DIM     = (70, 78, 95)
DARK    = (8, 10, 16)

# ── Fonts ──────────────────────────────────────────────────────────────────────
def _font(size, bold=False):
    for path in [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf"  if bold else "C:/Windows/Fonts/arial.ttf",
    ]:
        if os.path.exists(path):
            try: return ImageFont.truetype(path, size)
            except: pass
    return ImageFont.load_default()

F_HERO    = _font(68, bold=True)
F_TITLE   = _font(46, bold=True)
F_HEAD    = _font(28, bold=True)
F_SUB     = _font(22)
F_BODY    = _font(19)
F_SMALL   = _font(14)
F_BADGE   = _font(13, bold=True)

# ══════════════════════════════════════════════════════════════════════════════
#  MUSIC SYNTHESIS
# ══════════════════════════════════════════════════════════════════════════════

def _sine(freq, t): return math.sin(2 * math.pi * freq * t)

def _note(freq, dur, vol=0.18, env_attack=0.08, env_release=0.25):
    n = int(SRATE * dur)
    samples = []
    for i in range(n):
        t = i / SRATE
        env = 1.0
        if t < env_attack:          env = t / env_attack
        elif t > dur - env_release: env = (dur - t) / env_release
        env = max(0, env)
        s = (_sine(freq, t) * 0.7 +
             _sine(freq*2, t) * 0.15 +
             _sine(freq*3, t) * 0.07 +
             _sine(freq*0.5, t) * 0.08)
        samples.append(s * vol * env)
    return samples

def _pad(freq, dur, vol=0.06):
    """Soft synth pad — slow attack, sustained."""
    n = int(SRATE * dur)
    samples = []
    attack = 0.4
    for i in range(n):
        t = i / SRATE
        env = min(1.0, t / attack) if t < dur * 0.7 else (dur - t) / (dur * 0.3)
        env = max(0, env)
        s = (_sine(freq, t) * 0.6 +
             _sine(freq * 1.005, t) * 0.4 +   # slight detune for warmth
             _sine(freq * 2, t) * 0.1)
        samples.append(s * vol * env)
    return samples

def _mix(*tracks):
    length = max(len(t) for t in tracks)
    out = [0.0] * length
    for track in tracks:
        for i, v in enumerate(track):
            out[i] += v
    peak = max(abs(v) for v in out) or 1
    return [v / peak * 0.9 for v in out]

def _silence(secs):
    return [0.0] * int(SRATE * secs)

def build_music(total_secs: float) -> str:
    """Synthesise an ambient piano + pad soundtrack and save as WAV."""
    print("  ♪  Composing soundtrack …")

    # C major / A minor ambient progression: Am  F  C  G  (repeat)
    # Root notes (Hz): A3=220, F3=174.6, C3=130.8, G3=196
    chord_prog = [
        # (piano_root, pad_root, pad_fifth, duration_sec)
        (220.0, 220.0, 329.6, 2.5),   # Am  — A3, E4
        (174.6, 174.6, 261.6, 2.5),   # F   — F3, C4
        (130.8, 130.8, 196.0, 2.5),   # C   — C3, G3
        (196.0, 196.0, 293.7, 2.5),   # G   — G3, D4
    ]

    # Melodic right-hand arpeggio notes per chord (scale degrees)
    melodies = [
        [220.0, 261.6, 329.6, 392.0, 329.6, 261.6],   # Am
        [174.6, 220.0, 261.6, 349.2, 261.6, 220.0],   # F
        [261.6, 329.6, 392.0, 523.2, 392.0, 329.6],   # C
        [196.0, 246.9, 293.7, 392.0, 293.7, 246.9],   # G
    ]

    piano_track = []
    pad_track   = []
    bass_track  = []
    mel_track   = []

    beat_dur = 0.42  # seconds per arpeggio note

    while len(piano_track) / SRATE < total_secs:
        for idx, (pr, par, paf, dur) in enumerate(chord_prog):
            # Bass: root one octave down
            bass_track += _note(pr * 0.5, dur, vol=0.09, env_attack=0.02, env_release=0.3)
            # Piano chord (root + third + fifth)
            third = pr * 1.189   # minor third ≈ ×1.189, major ≈ ×1.26
            fifth = pr * 1.498
            chord_notes = _mix(
                _note(pr,    dur, vol=0.13),
                _note(third, dur, vol=0.10),
                _note(fifth, dur, vol=0.09),
            )
            piano_track += chord_notes
            # Pad sustain
            pad_track += _mix(
                _pad(par, dur, vol=0.07),
                _pad(paf, dur, vol=0.05),
            )
            # Melody arpeggio
            mel_notes = melodies[idx]
            mel_seq = []
            for mn in mel_notes:
                mel_seq += _note(mn * 2, beat_dur, vol=0.12, env_attack=0.02, env_release=0.12)
            # pad to chord dur
            target = int(SRATE * dur)
            if len(mel_seq) < target:
                mel_seq += _silence(dur - len(mel_seq)/SRATE)
            mel_track += mel_seq[:target]

    # Trim all to total_secs
    n = int(SRATE * total_secs)
    def trim(t): return t[:n] + [0.0]*(n-len(t)) if len(t)<n else t[:n]

    # Fade-out last 3 seconds
    fade_n = int(SRATE * 3)
    final = _mix(trim(bass_track), trim(piano_track), trim(pad_track), trim(mel_track))
    for i in range(fade_n):
        final[n - fade_n + i] *= (1 - i / fade_n)

    # Write WAV
    with wave.open(WAV_PATH, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SRATE)
        for s in final:
            wf.writeframes(struct.pack("<h", int(max(-32767, min(32767, s * 32767)))))

    print(f"     Soundtrack: {len(final)/SRATE:.1f}s @ {SRATE}Hz → {WAV_PATH}")
    return WAV_PATH

# ══════════════════════════════════════════════════════════════════════════════
#  DRAWING PRIMITIVES
# ══════════════════════════════════════════════════════════════════════════════

def empty_frame():
    f = np.zeros((H, W, 3), dtype=np.uint8)
    # Radial vignette background
    cx, cy = W//2, H//2
    Y, X = np.ogrid[:H, :W]
    dist = np.sqrt((X-cx)**2 + (Y-cy)**2) / max(cx, cy)
    for c, bv in enumerate(BG):
        f[:,:,c] = np.clip(bv * (1 - 0.35*dist**1.5), 0, 255).astype(np.uint8)
    return f

def pil2bgr(img):
    return cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)

def bgr2pil(f):
    return Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB))

def draw_txt(frame, text, xy, font, color=WHITE, anchor="lt"):
    img = bgr2pil(frame)
    ImageDraw.Draw(img).text(xy, text, font=font, fill=tuple(reversed(color)), anchor=anchor)
    return pil2bgr(img)

def draw_center(frame, text, y, font, color=WHITE):
    return draw_txt(frame, text, (W//2, y), font, color, anchor="mt")

def glow_line(frame, x1, y1, x2, y2, color=ACCENT, thickness=2, blur=8):
    overlay = frame.copy()
    cv2.line(overlay, (x1,y1), (x2,y2), color, thickness+blur)
    frame = cv2.addWeighted(frame, 1, overlay, 0.25, 0)
    cv2.line(frame, (x1,y1), (x2,y2), color, thickness)
    return frame

def top_bottom_bars(frame, h=5):
    frame = glow_line(frame, 0, h//2, W, h//2, ACCENT, h, blur=10)
    frame = glow_line(frame, 0, H-h//2, W, H-h//2, ACCENT, h, blur=10)
    return frame

def progress_bar(frame, progress: float):
    """Animated progress bar — thin glowing line at very bottom."""
    pw = int(W * progress)
    if pw > 0:
        frame = glow_line(frame, 0, H-3, pw, H-3, ACCENT, 3, blur=6)
    return frame

def watermark(frame, prog: float):
    """Bottom-right copyright badge + progress."""
    frame = draw_txt(frame, "© 2026 Sesank Koganti", (W-10, H-18), F_SMALL, DIM, anchor="rb")
    frame = progress_bar(frame, prog)
    return frame

def particles(frame, seed=0, n=55, alpha=0.55):
    """Floating ambient dots — deterministic per slide."""
    rng = np.random.default_rng(seed)
    xs = rng.integers(0, W, n)
    ys = rng.integers(0, H, n)
    rs = rng.integers(1, 4, n)
    overlay = frame.copy()
    for x, y, r in zip(xs, ys, rs):
        cv2.circle(overlay, (int(x), int(y)), int(r), ACCENT, -1)
    return cv2.addWeighted(frame, 1, overlay, alpha * 0.15, 0)

def grid_lines(frame, spacing=80, alpha=0.07):
    overlay = frame.copy()
    for x in range(0, W, spacing):
        cv2.line(overlay, (x,0), (x,H), (60,80,110), 1)
    for y in range(0, H, spacing):
        cv2.line(overlay, (0,y), (W,y), (60,80,110), 1)
    return cv2.addWeighted(frame, 1, overlay, alpha, 0)

def badge_pill(frame, text, x, y, bg=ACCENT, fg=DARK):
    img = bgr2pil(frame)
    d = ImageDraw.Draw(img)
    bbox = d.textbbox((0,0), text, font=F_BADGE)
    tw = bbox[2]-bbox[0]
    pw, ph = tw+24, 26
    d.rounded_rectangle([x, y, x+pw, y+ph], radius=13, fill=tuple(reversed(bg)))
    d.text((x+12, y+13), text, font=F_BADGE, fill=tuple(reversed(fg)), anchor="lm")
    return pil2bgr(img)


def draw_logo_cv(frame, cx, cy, size=80):
    """
    Draw the MyNexus hub-and-spoke logo (from my_nexus.svg) onto a BGR frame.
    SVG viewBox 0-64; scaled to `size` px, centred at (cx, cy).
    """
    sc = size / 64.0
    def sx(x): return int(cx + (x - 32) * sc)
    def sy(y): return int(cy + (y - 32) * sc)

    # ── Back-glow behind hub ──
    glow = frame.copy()
    cv2.circle(glow, (cx, cy), int(14*sc)+8, ACCENT, -1)
    frame = cv2.addWeighted(frame, 1, glow, 0.20, 0)

    # ── Spokes (draw behind nodes so they look connected) ──
    spokes = [(32,22,32,14),(40,27,47,23),(40,37,47,41),
              (32,42,32,50),(24,37,17,41),(24,27,17,23)]
    sw = max(1, int(sc * 2.8))
    spoke_col = (int(ACCENT[0]*0.65), int(ACCENT[1]*0.65), int(ACCENT[2]*0.65))
    for x1, y1, x2, y2 in spokes:
        cv2.line(frame, (sx(x1),sy(y1)), (sx(x2),sy(y2)), spoke_col, sw, cv2.LINE_AA)

    # ── Outer nodes ──
    nr = max(2, int(4.5 * sc))
    outer = [(32,10),(51,21),(51,43),(32,54),(13,43),(13,21)]
    for nx, ny in outer:
        og = frame.copy()
        cv2.circle(og, (sx(nx),sy(ny)), nr+4, ACCENT, -1)
        frame = cv2.addWeighted(frame, 1, og, 0.22, 0)
        cv2.circle(frame, (sx(nx),sy(ny)), nr, ACCENT, -1, cv2.LINE_AA)

    # ── Centre hub ──
    cr = max(4, int(10 * sc))
    hg = frame.copy()
    cv2.circle(hg, (cx, cy), cr+6, ACCENT, -1)
    frame = cv2.addWeighted(frame, 1, hg, 0.30, 0)
    cv2.circle(frame, (cx, cy), cr, ACCENT, -1, cv2.LINE_AA)
    # inner dark ring (opacity from SVG: 0.15)
    cr2 = max(2, int(6 * sc))
    inner_col = (int(ACCENT[0]*0.18), int(ACCENT[1]*0.18), int(ACCENT[2]*0.18))
    cv2.circle(frame, (cx, cy), cr2, inner_col, -1, cv2.LINE_AA)
    return frame


def brand_watermark(frame, small=False):
    """Small hub logo + 'MyNexus' text in top-left corner."""
    size = 28 if small else 34
    lx, ly = 20, 26
    frame = draw_logo_cv(frame, lx, ly, size=size)
    frame = draw_txt(frame, "MyNexus", (lx + size//2 + 8, ly - size//4), F_BADGE, ACCENT, anchor="lt")
    # thin separator under brand
    frame = glow_line(frame, 0, 52, W, 52, (30,40,60), 1, blur=0)
    return frame

# ── Screenshot renderer ────────────────────────────────────────────────────────

def load_screenshot(path, tw, th, zoom=1.0):
    """Load, scale-to-fit, apply rounded corners + shadow + glow border."""
    img = Image.open(path).convert("RGB")
    iw, ih = img.size
    scale = min(tw/iw, th/ih) * zoom
    nw, nh = int(iw*scale), int(ih*scale)
    img = img.resize((nw, nh), Image.LANCZOS)

    canvas = Image.new("RGB", (tw, th), tuple(reversed(BG)))
    ox, oy = (tw-nw)//2, (th-nh)//2

    # multi-layer shadow
    for d_off, d_alpha in [(12,0.5),(8,0.35),(4,0.2)]:
        sh = Image.new("RGB", (tw, th), tuple(reversed(DARK)))
        sd = ImageDraw.Draw(sh)
        sd.rectangle([ox+d_off, oy+d_off, ox+nw+d_off-1, oy+nh+d_off-1], fill=tuple(reversed(DARK)))
        canvas = Image.blend(canvas, sh, d_alpha*0.15)

    mask = Image.new("L", (nw, nh), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0,0,nw-1,nh-1], radius=12, fill=255)
    canvas.paste(img, (ox, oy), mask)

    # glow border
    bd = ImageDraw.Draw(canvas)
    for blur_w, blur_a in [(6,0.12),(3,0.25),(1,1.0)]:
        c = tuple(int(v*blur_a + (1-blur_a)*20) for v in reversed(ACCENT))
        bd.rounded_rectangle([ox-blur_w, oy-blur_w, ox+nw+blur_w-1, oy+nh+blur_w-1],
                              radius=12+blur_w, outline=c, width=1)
    return pil2bgr(canvas)

# ── Animated transitions ───────────────────────────────────────────────────────

def crossfade(writer, fa, fb, n=24, prog_a=0.0, prog_b=0.0):
    for i in range(n):
        t = (1 - math.cos(math.pi * i/n)) / 2   # smooth cosine
        blended = (fa*(1-t) + fb*t).astype(np.uint8)
        p = prog_a + (prog_b - prog_a) * t
        blended = progress_bar(blended, p)
        writer.write(blended)

def slide_in_animate(writer, bg_frame, ss_img, start_x, end_x, y, t_w, t_h,
                     text_frame, n=22, prog=0.0):
    """Screenshot glides from start_x to end_x while text fades in."""
    for i in range(n):
        t = (1 - math.cos(math.pi * i/n)) / 2
        cur_x = int(start_x + (end_x - start_x) * t)
        f = bg_frame.copy()
        # paste screenshot at animated position (clipped)
        paste_x = max(0, cur_x)
        paste_w = t_w - max(0, -cur_x)
        src_x   = max(0, -cur_x)
        if paste_w > 0:
            region = cv2.resize(ss_img, (t_w, t_h))
            clip_w = min(paste_w, W - paste_x)
            clip_h = min(t_h, H - y)
            if clip_w > 0 and clip_h > 0:
                f[y:y+clip_h, paste_x:paste_x+clip_w] = region[:clip_h, src_x:src_x+clip_w]
        # fade in text panel
        alpha = t
        f = cv2.addWeighted(f, 1, text_frame, alpha, 0)
        f = progress_bar(f, prog)
        writer.write(f)

def hold_frames(writer, frame, secs, prog_start=0.0, prog_end=0.0):
    n = int(FPS * secs)
    for i in range(n):
        p = prog_start + (prog_end - prog_start) * (i/max(n-1,1))
        f = frame.copy()
        f = progress_bar(f, p)
        writer.write(f)


def ken_burns_hold(writer, frame, secs, prog_start=0.0, prog_end=0.0, zoom_max=1.025):
    """Hold with subtle Ken Burns zoom-in (frame scales 1.0 → zoom_max)."""
    n = int(FPS * secs)
    for i in range(n):
        t = i / max(n - 1, 1)
        p = prog_start + (prog_end - prog_start) * t
        z = 1.0 + (zoom_max - 1.0) * t
        h_new, w_new = int(H * z), int(W * z)
        resized = cv2.resize(frame, (w_new, h_new), interpolation=cv2.INTER_LINEAR)
        oy, ox = (h_new - H) // 2, (w_new - W) // 2
        f = resized[oy:oy+H, ox:ox+W].copy()
        f = progress_bar(f, p)
        writer.write(f)

# ══════════════════════════════════════════════════════════════════════════════
#  SLIDE BUILDERS
# ══════════════════════════════════════════════════════════════════════════════

def slide_title():
    f = empty_frame()
    f = grid_lines(f, spacing=100, alpha=0.06)
    f = particles(f, seed=42, n=70)
    f = top_bottom_bars(f)

    # radial glow behind logo
    cx, cy = W//2, 200
    glow = f.copy()
    cv2.circle(glow, (cx, cy), 120, (30, 60, 100), -1)
    f = cv2.addWeighted(f, 1, glow, 0.35, 0)

    # ── Large hub-and-spoke logo ──────────────────────────────────
    # Decorative outer ring (thin)
    for ang in range(0, 360, 20):
        rad = math.radians(ang)
        x1 = int(cx + 95*math.cos(rad)); y1 = int(cy + 95*math.sin(rad))
        x2 = int(cx + 102*math.cos(rad)); y2 = int(cy + 102*math.sin(rad))
        cv2.line(f, (x1,y1), (x2,y2), (40,60,90), 1, cv2.LINE_AA)
    cv2.circle(f, (cx, cy), 92, (20,30,48), 1, cv2.LINE_AA)

    f = draw_logo_cv(f, cx, cy, size=150)

    # "PERSONAL HUB" label above title
    f = draw_center(f, "P E R S O N A L   H U B", 295, F_SMALL, DIM)

    # Hero title with letter-spacing effect
    f = draw_center(f, "MyNexus", 320, F_HERO, WHITE)

    # Subtitle
    f = draw_center(f, "Personal Finance & Activity Manager", 405, F_SUB, GRAY)

    # Divider with dots
    mid = W//2
    cv2.line(f, (mid-240, 445), (mid-20, 445), (*ACCENT[::-1],), 1)
    cv2.circle(f, (mid, 445), 3, ACCENT, -1)
    cv2.line(f, (mid+20, 445), (mid+240, 445), (*ACCENT[::-1],), 1)

    # Tagline pill
    img = bgr2pil(f)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([mid-310, 462, mid+310, 500], radius=20,
                        fill=(20,30,50), outline=tuple(reversed(ACCENT)), width=1)
    d.text((mid, 481), "Your life, organized — in one place.",
           font=F_SUB, fill=tuple(reversed(ACCENT)), anchor="mm")
    f = pil2bgr(img)

    # Bottom copyright
    f = draw_center(f, "Copyright © 2026 Sesank Koganti  ·  All Rights Reserved", H-28, F_SMALL, DIM)
    return f


def slide_feature(ss_path, feature_num, total, title, tagline, bullets):
    """Left: screenshot. Right: badge + title + bullets. Header bar on top."""
    # ── base
    f = empty_frame()
    f = grid_lines(f, spacing=120, alpha=0.04)
    f = top_bottom_bars(f)
    f = brand_watermark(f)

    # ── screenshot panel (left, shifted down by header)
    ss = load_screenshot(ss_path, 706, 636, zoom=1.04)
    f[60:696, 14:720] = ss

    # vertical accent separator
    f = glow_line(f, 744, 58, 744, H-22, ACCENT, 1, blur=8)

    # ── text panel (right)
    rx = 762

    # Feature badge
    badge_txt = f"FEATURE  {feature_num} / {total}"
    f = badge_pill(f, badge_txt, rx, 68)

    # Title
    f = draw_txt(f, title, (rx, 106), F_TITLE, WHITE, anchor="lt")
    f = draw_txt(f, tagline, (rx, 162), F_SUB, GRAY, anchor="lt")

    # Divider
    cv2.line(f, (rx, 196), (rx+490, 196), (40,50,70), 1)

    # Bullet points
    by = 212
    for bullet in bullets:
        # glow dot
        glow_o = f.copy()
        cv2.circle(glow_o, (rx+8, by+11), 8, ACCENT, -1)
        f = cv2.addWeighted(f, 1, glow_o, 0.22, 0)
        cv2.circle(f, (rx+8, by+11), 4, ACCENT, -1)
        f = draw_txt(f, bullet, (rx+24, by), F_BODY, (210,215,225), anchor="lt")
        by += 42

    # bottom copyright
    f = draw_center(f, "© 2026 Sesank Koganti  ·  MyNexus", H-16, F_SMALL, DIM)
    return f


def slide_two_shots(ss1_path, ss2_path, title, subtitle):
    f = empty_frame()
    f = grid_lines(f, spacing=120, alpha=0.04)
    f = top_bottom_bars(f)
    f = brand_watermark(f)

    f = draw_center(f, title,    72, F_HEAD, WHITE)
    f = draw_center(f, subtitle, 106, F_BODY, GRAY)

    cv2.line(f, (W//2-400, 128), (W//2+400, 128), (40,50,70), 1)

    s1 = load_screenshot(ss1_path, 610, 562)
    s2 = load_screenshot(ss2_path, 610, 562)
    f[132:694, 15:625]  = s1
    f[132:694, 655:1265] = s2

    f = draw_center(f, "© 2026 Sesank Koganti  ·  MyNexus", H-16, F_SMALL, DIM)
    return f


def slide_closing():
    f = empty_frame()
    f = grid_lines(f, spacing=100, alpha=0.055)
    f = particles(f, seed=99, n=80)
    f = top_bottom_bars(f)

    # large soft glow
    glow = np.zeros_like(f)
    cv2.circle(glow, (W//2, H//2), 380, (20, 45, 70), -1)
    f = cv2.addWeighted(f, 1, glow, 0.5, 0)

    # ── Logo centred near top ───────────────────────────────────────
    logo_cx, logo_cy = W//2, 72
    f = draw_logo_cv(f, logo_cx, logo_cy, size=70)
    f = draw_center(f, "MyNexus", logo_cy + 44, F_HEAD, ACCENT)

    f = draw_center(f, "G E T   S T A R T E D   T O D A Y", 168, F_SUB, WHITE)
    f = draw_center(f, "Free to install  •  All your data stays on your device", 200, F_BODY, GRAY)

    # Feature checklist
    checks = [
        ("Dashboard",       "Live stats, due-date tracking & overdue alerts"),
        ("My Activities",   "Bills, subscriptions, maintenance reminders"),
        ("Connected Apps",  "Banking, insurance, utilities in one place"),
        ("Document Vault",  "Passports, tax returns, insurance policies"),
        ("Integrations",    "Email sync & notification preferences"),
    ]
    cy = 240
    for feature, desc in checks:
        # checkmark glow
        glo = f.copy()
        cv2.circle(glo, (W//2-295, cy+13), 14, ACCENT, -1)
        f = cv2.addWeighted(f, 1, glo, 0.15, 0)
        cv2.circle(f, (W//2-295, cy+13), 10, ACCENT, -1)
        img = bgr2pil(f)
        ImageDraw.Draw(img).text((W//2-295, cy+13), "✓",
            font=_font(13,bold=True), fill=tuple(reversed(DARK)), anchor="mm")
        f = pil2bgr(img)
        f = draw_txt(f, feature, (W//2-272, cy), F_BODY, WHITE, anchor="lt")
        f = draw_txt(f, f"  —  {desc}", (W//2-271+130, cy+1), F_SMALL, GRAY, anchor="lt")
        cy += 42

    # CTA button
    btn_y = cy + 20
    img = bgr2pil(f)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([W//2-230, btn_y, W//2+230, btn_y+52], radius=26,
                        fill=tuple(reversed(ACCENT)))
    # shadow under button
    d.rounded_rectangle([W//2-228, btn_y+4, W//2+232, btn_y+56], radius=26,
                        outline=(0,100,180), width=2)
    d.text((W//2, btn_y+26), "Install  MyNexus-Setup-1.0.1.exe",
           font=_font(18,bold=True), fill=tuple(reversed(DARK)), anchor="mm")
    f = pil2bgr(img)

    f = draw_center(f, "Copyright © 2026 Sesank Koganti  ·  All Rights Reserved",
                    H-24, F_SMALL, DIM)
    return f


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════

def ss(name): return os.path.join(SS_DIR, name)

def _get_ffmpeg() -> str:
    """Return the path to ffmpeg, preferring the imageio_ffmpeg binary."""
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe and os.path.exists(exe):
            return exe
    except Exception:
        pass
    # fallback: system PATH
    return "ffmpeg"


def merge_audio(video_path, wav_path, out_path):
    """Mux WAV audio into the silent video using ffmpeg (imageio_ffmpeg)."""
    ffmpeg = _get_ffmpeg()
    try:
        cmd = [ffmpeg, "-y",
               "-i", video_path,
               "-i", wav_path,
               "-c:v", "copy",
               "-c:a", "aac", "-b:a", "192k",
               "-shortest",
               out_path]
        print(f"  ffmpeg: {os.path.basename(ffmpeg)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓  Audio merged sucessfully")
            return True
        else:
            print(f"  ✗  ffmpeg stderr:\n{result.stderr[-600:]}")
            return False
    except Exception as e:
        print(f"  ✗  merge_audio exception: {e}")
        return False


def main():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

    # ── define slides: (frame, hold_secs, label)
    slide_defs = [
        (slide_title(),                                                      4.0,  "Title"),
        (slide_feature(ss("tab_0_dashboard.png"),     1, 5,
            "Dashboard",
            "Everything at a glance",
            ["Live summary — Total, Due, Overdue, Completed",
             "Due This Week table — never miss a payment",
             "Overdue alerts highlighted in real-time",
             "One-click refresh"]),                                          4.5,  "Dashboard"),
        (slide_feature(ss("stress_activities.png"),   2, 5,
            "My Activities",
            "Recurring bills, tasks & subscriptions",
            ["Monthly, quarterly, yearly & custom recurrence",
             "Reminder days configurable per activity",
             "Bulk complete, export & import via CSV",
             "Category filter: Payment, Subscription, Health…"]),           4.5,  "Activities"),
        (slide_two_shots(
            ss("tab_3_connected.png"),
            ss("stress_apps_card.png"),
            "Connected Apps",
            "Banking · Credit Cards · Mortgage · Insurance · Utilities · Investments"), 4.0, "Apps-Both"),
        (slide_feature(ss("connected_apps_connect.png"), 3, 5,
            "Connected Apps",
            "All your accounts in one secure hub",
            ["One-click Connect opens the login page instantly",
             "Masked credentials & encrypted account numbers",
             "4 views: Cards, List, Grid, Compact",
             "Filter by category · Sort by name or status"]),                4.5,  "Apps-Detail"),
        (slide_feature(ss("tab_4_vault.png"),         4, 5,
            "Document Vault",
            "Secure storage for important documents",
            ["Passports, tax returns, insurance policies & more",
             "10 categories: Medical, Legal, Financial, Property…",
             "Expiry tracking with renewal reminders",
             "Favorites for instant access"]),                               4.5,  "Vault"),
        (slide_two_shots(
            ss("tab_2_integrations.png"),
            ss("tab_5_settings.png"),
            "Integrations & Settings",
            "Email sync  ·  Notifications  ·  Theme & display"),             3.5,  "Integrations"),
        (slide_closing(),                                                     5.0,  "Closing"),
    ]

    # ── calculate total duration for progress bar & music
    FADE_FRAMES = 28
    total_frames = sum(int(FPS*secs) for _,secs,_ in slide_defs) + FADE_FRAMES*(len(slide_defs)-1)
    total_secs   = total_frames / FPS
    print(f"\nBuilding MyNexus PREMIUM promo video …")
    print(f"  Slides   : {len(slide_defs)}")
    print(f"  Duration : {total_secs:.1f}s  ({total_frames} frames @ {FPS}fps)")

    # ── synthesise music
    wav = build_music(total_secs + 2)

    # ── render silent video first
    silent_path = OUT_PATH.replace(".mp4", "_silent.mp4")
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(silent_path, fourcc, FPS, (W, H))
    if not writer.isOpened():
        print("ERROR: VideoWriter failed"); sys.exit(1)

    frame_cursor = 0
    prev_frame = None
    prev_prog  = 0.0

    for i, (frame, hold_secs, label) in enumerate(slide_defs):
        print(f"  [{i+1}/{len(slide_defs)}] {label} …")
        hold_n = int(FPS * hold_secs)
        end_cursor = frame_cursor + (FADE_FRAMES if prev_frame is not None else 0) + hold_n

        prog_start = frame_cursor / total_frames
        prog_end   = end_cursor  / total_frames

        if prev_frame is not None:
            crossfade(writer, prev_frame, frame, FADE_FRAMES,
                      prog_a=prev_prog, prog_b=prog_start)
            frame_cursor += FADE_FRAMES

        # add particles animation (title & closing); Ken Burns on feature slides
        if label in ("Title", "Closing"):
            for fi in range(hold_n):
                p = prog_start + (prog_end - prog_start) * fi / max(hold_n-1,1)
                f = frame.copy()
                if fi % 4 == 0:
                    f = particles(f, seed=fi//4, n=12, alpha=0.3)
                f = progress_bar(f, p)
                f = draw_txt(f, "© 2026 Sesank Koganti", (W-10, H-18), F_SMALL, DIM, anchor="rb")
                writer.write(f)
        else:
            # Ken-Burns subtle zoom on all other slides
            ken_burns_hold(writer, frame, hold_secs, prog_start, prog_end, zoom_max=1.022)

        prev_frame   = frame
        prev_prog    = prog_end
        frame_cursor = end_cursor

    writer.release()
    print(f"  Silent video: {os.path.getsize(silent_path)/1024/1024:.1f} MB")

    # ── merge audio
    print("  Merging audio …")
    ok = merge_audio(silent_path, wav, OUT_PATH)
    if not ok:
        # fallback: just rename silent video
        import shutil
        shutil.copy(silent_path, OUT_PATH)
        print("  (Audio merge skipped — video saved without music)")
    else:
        os.remove(silent_path)

    final_mb = os.path.getsize(OUT_PATH) / 1024 / 1024
    print(f"\n{'='*60}")
    print(f"  ✅  MyNexus-Promo-Premium.mp4  DONE")
    print(f"  📁  {OUT_PATH}")
    print(f"  ⏱   {total_secs:.1f} seconds  |  {W}×{H}  |  {FPS}fps  |  {final_mb:.1f} MB")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

