"""
MyNexus Premium Glass Icon Generator
=====================================
Creates a pixel-perfect RGBA .ico with sizes: 16, 24, 32, 40, 48, 64, 96, 128, 256
Glass design:
  • Deep navy radial-gradient circle background
  • Frosted glass inner disc with top-reflection highlight
  • Subtle outer ring (glow border)
  • Hub-and-spoke logo (matching my_nexus.svg) in electric-blue/white
  • Full transparency outside the circle
"""

import math
from PIL import Image, ImageDraw, ImageFilter
import os

OUT = r"c:\ProJ_connect\development\MyNexus\assets\icons\my_nexus_setup.ico"
SIZES = [16, 24, 32, 40, 48, 64, 96, 128, 256]


# ── helpers ──────────────────────────────────────────────────────────────────

def lerp(a, b, t):
    return a + (b - a) * t

def clamp(v, lo=0, hi=255):
    return max(lo, min(hi, int(v)))

def hsv_to_rgb(h, s, v):
    i = int(h * 6)
    f = h * 6 - i
    p, q, t_ = v*(1-s), v*(1-s*f), v*(1-s*(1-f))
    parts = [(v,t_,p),(q,v,p),(p,v,t_),(p,q,v),(t_,p,v),(v,p,q)]
    r, g, b = parts[i % 6]
    return clamp(r*255), clamp(g*255), clamp(b*255)


def make_icon(size: int) -> Image.Image:
    N = size
    img = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    pix = img.load()

    cx = cy = N / 2
    R = N / 2 - 1            # outer circle radius
    spoke_w = max(0.7, N / 64 * 1.8)

    # ── SVG node positions (original viewBox 64×64, scaled to N) ─────────────
    sc = N / 64.0

    def sp(x, y):
        return (x * sc, y * sc)

    hub_c   = sp(32, 32)
    hub_r   = 10 * sc
    inner_r = 6  * sc
    node_r  = 4.5 * sc
    nodes   = [sp(32,10), sp(51,21), sp(51,43),
               sp(32,54), sp(13,43), sp(13,21)]
    spokes  = [(sp(32,22), sp(32,14)),
               (sp(40,27), sp(47,23)),
               (sp(40,37), sp(47,41)),
               (sp(32,42), sp(32,50)),
               (sp(24,37), sp(17,41)),
               (sp(24,27), sp(17,23))]

    # Accent colour (electric cyan-blue)
    ACCENT = (0, 185, 255)
    ACCENT2 = (80, 220, 255)

    for py in range(N):
        for px in range(N):
            dx = px - cx + 0.5
            dy = py - cy + 0.5
            dist = math.hypot(dx, dy)

            # ── outside circle → fully transparent ──────────────────────────
            if dist > R + 0.5:
                continue

            # ── Anti-alias edge band ────────────────────────────────────────
            edge_alpha = 1.0
            if dist > R - 0.5:
                edge_alpha = (R + 0.5 - dist)

            # ── Background gradient (deep navy → slightly lighter navy) ─────
            t_bg = (dist / R) ** 1.2
            bg_r = clamp(lerp(14, 8,  t_bg))
            bg_g = clamp(lerp(22, 12, t_bg))
            bg_b = clamp(lerp(38, 20, t_bg))

            # ── Glass outer ring glow ───────────────────────────────────────
            ring_glow = 0.0
            ring_t = dist / R
            if ring_t > 0.90:
                ring_glow = (ring_t - 0.90) / 0.10
                ring_glow = ring_glow ** 1.5 * 0.5

            outer_r = clamp(bg_r + ring_glow * ACCENT[0])
            outer_g = clamp(bg_g + ring_glow * ACCENT[1])
            outer_b = clamp(bg_b + ring_glow * ACCENT[2])

            # ── Glass mid-disc (frosted inner area) ─────────────────────────
            mid_r_ = R * 0.82
            glass = 0.0
            if dist < mid_r_:
                gt = 1 - (dist / mid_r_) ** 2
                glass = gt * 0.12

            # ── Top-left reflection highlight ───────────────────────────────
            refl_cx, refl_cy = cx - R * 0.28, cy - R * 0.30
            refl_r  = R * 0.45
            refl_dist = math.hypot(px - refl_cx + 0.5, py - refl_cy + 0.5)
            refl = 0.0
            if refl_dist < refl_r:
                rt = 1 - refl_dist / refl_r
                refl = rt ** 2.5 * 0.55       # white highlight intensity

            # ── Compose background pixel ────────────────────────────────────
            base_r = clamp(outer_r + glass * 50 + refl * 255)
            base_g = clamp(outer_g + glass * 60 + refl * 255)
            base_b = clamp(outer_b + glass * 80 + refl * 255)

            # ── Logo: spokes ─────────────────────────────────────────────────
            logo_contrib = 0.0
            logo_col = ACCENT

            for (x1, y1), (x2, y2) in spokes:
                # distance from point to line segment
                lx, ly = x2 - x1, y2 - y1
                llen2  = lx*lx + ly*ly
                if llen2 == 0:
                    dL = math.hypot(px+.5-x1, py+.5-y1)
                else:
                    t_l = max(0, min(1, ((px+.5-x1)*lx + (py+.5-y1)*ly) / llen2))
                    dL  = math.hypot(px+.5 - (x1+t_l*lx), py+.5 - (y1+t_l*ly))
                if dL < spoke_w + 0.8:
                    fade = max(0, 1 - (dL - spoke_w + 0.8) / 0.8)
                    contrib = fade * 0.72
                    if contrib > logo_contrib:
                        logo_contrib = contrib
                        logo_col = ACCENT

            # ── Logo: outer nodes ────────────────────────────────────────────
            for nx, ny in nodes:
                dn = math.hypot(px+.5-nx, py+.5-ny)
                if dn < node_r + 1.0:
                    fade = max(0, 1 - (dn - node_r + 1.0) / 1.0)
                    contrib = fade * 0.92
                    if contrib > logo_contrib:
                        logo_contrib = contrib
                        logo_col = ACCENT2

            # ── Logo: hub circle ─────────────────────────────────────────────
            dh = dist if (abs(px+.5-hub_c[0]) > hub_r*2 or abs(py+.5-hub_c[1]) > hub_r*2) else \
                 math.hypot(px+.5-hub_c[0], py+.5-hub_c[1])
            dh = math.hypot(px+.5-hub_c[0], py+.5-hub_c[1])
            if dh < hub_r + 1.2:
                fade = max(0, 1 - (dh - hub_r + 1.2) / 1.2)
                contrib = fade * 0.98
                if contrib > logo_contrib:
                    logo_contrib = contrib
                    logo_col = (255, 255, 255)   # hub is white

            # ── Logo: inner hub ring (dark cutout) ───────────────────────────
            if dh < inner_r + 0.8 and dh > inner_r - 0.8:
                fade = 1 - abs(dh - inner_r) / 0.8
                logo_col = (int(ACCENT[0]*0.15), int(ACCENT[1]*0.15), int(ACCENT[2]*0.15))
                logo_contrib = max(logo_contrib, fade * 0.45)

            # ── Composite logo onto background ───────────────────────────────
            lr, lg, lb = logo_col
            fr = clamp(base_r * (1 - logo_contrib) + lr * logo_contrib)
            fg = clamp(base_g * (1 - logo_contrib) + lg * logo_contrib)
            fb = clamp(base_b * (1 - logo_contrib) + lb * logo_contrib)

            alpha = clamp(edge_alpha * 255)
            pix[px, py] = (fr, fg, fb, alpha)

    return img


def main():
    print("Generating premium glass icon …")
    frames = []
    for size in SIZES:
        print(f"  Rendering {size}×{size} …", end=" ", flush=True)
        frame = make_icon(size)
        frames.append(frame)
        print("done")

    # Save as ICO — PIL will embed each frame at its native size
    base = frames[-1]   # largest first
    base.save(
        OUT,
        format="ICO",
        sizes=[(s, s) for s in SIZES],
        append_images=frames[:-1],
    )

    from pathlib import Path
    kb = Path(OUT).stat().st_size / 1024
    print(f"\n✅  Saved: {OUT}")
    print(f"   Sizes : {SIZES}")
    print(f"   File  : {kb:.1f} KB")
    print(f"   Mode  : RGBA with full transparency")


if __name__ == "__main__":
    main()
