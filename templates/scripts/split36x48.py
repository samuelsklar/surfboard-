"""Split a FULLSIZE half-outline template into two overlapping pieces laid
side by side on one 36x48in sheet (Staples engineering print), at 100% scale.
usage: python split36x48.py FULLSIZE.pdf OUT.pdf "TITLE" L_inches [OUTLINE.dxf SHAPING.json]
With the DXF and JSON (from shaping_data.py) it also draws the shaping guide:
rail zones along the rail, and rocker / bottom shape / thickness strips under the stringer.
Source convention (from gen.py): tail tip at x=4.5in, stringer at y=15.5in from top."""
import sys, json, math, pymupdf as fitz
src_path, out_path, title, L = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
GUIDE = len(sys.argv) > 6
I = 72.0
BF = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"  # embedded bold sans
RF = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"  # embedded regular sans
TX, SY = 4.5, 15.5                  # tail tip x, stringer y (inches, source page, y down)
mid = round(L / 2)                  # overlap centred on the CENTER station
OV = 2.0
a0, a1 = mid - OV/2, mid + OV/2     # overlap zone in board inches from tail
Y0, Y1 = (3.5, 18.0) if GUIDE else (4.3, 16.6)   # source strip kept (y, inches from top)
XA0, XA1 = TX - 2.0, TX + a1         # piece A: tail half
XB0, XB1 = TX + a0, TX + L + 2.5     # piece B: nose half
src = fitz.open(src_path); sp = src[0]
sp.insert_font(fontname="LSB", fontfile=BF); sp.insert_font(fontname="LSR", fontfile=RF)

# --- add alignment marks to the source drawing (so both pieces get identical marks)
P = lambda bx, off: fitz.Point((TX + bx) * I, (SY - off) * I)
sh = sp.new_shape()
# light band showing the overlap
sh.draw_rect(fitz.Rect(P(a0, SY - Y0)[0], Y0 * I, P(a1, 0)[0], Y1 * I))
sh.finish(color=None, fill=(1, .93, .75))
sh.commit(overlay=False); sh = sp.new_shape()
for bx in (a0, a1):
    sh.draw_line(fitz.Point(P(bx, 0).x, Y0 * I), fitz.Point(P(bx, 0).x, Y1 * I))
sh.finish(color=(0.85, 0.45, 0), width=1.2, dashes="[10 6] 0")
crosses = [("1", 0.0), ("2", 3.0), ("3", 6.0), ("4", 9.0)]
for lab, off in crosses:
    c = P(mid, off); r = 0.35 * I
    sh.draw_line(fitz.Point(c.x - r, c.y), fitz.Point(c.x + r, c.y))
    sh.draw_line(fitz.Point(c.x, c.y - r), fitz.Point(c.x, c.y + r))
    sh.draw_circle(c, 0.15 * I)
sh.finish(color=(0, 0, 0), width=1.0)
sh.commit()
for lab, off in crosses:
    c = P(mid, off)
    sp.insert_text(fitz.Point(c.x + 0.2 * I, c.y - 0.2 * I), f"X{lab}", fontsize=16, fontname="LSB", color=(.8, 0, 0))
# overlap captions (read along the stringer)
sp.insert_text(fitz.Point(P(a0, 0).x + 4, Y0 * I + 0.5 * I), "OVERLAP", fontsize=12, fontname="LSB", color=(.85, .45, 0))
sp.insert_text(fitz.Point(P(a0, 0).x - 2, Y0 * I + 3.2 * I), "B ends here", fontsize=11, fontname="LSB", color=(.85, .45, 0), rotate=90)
sp.insert_text(fitz.Point(P(a1, 0).x + 13, Y0 * I + 3.2 * I), "A ends here", fontsize=11, fontname="LSB", color=(.85, .45, 0), rotate=90)

# --- shaping guide (drawn on the source so it lands on both pieces)
def frac(v):
    n = round(v * 16); w, r = divmod(n, 16)
    if r == 0: return f'{w}"'
    g = math.gcd(r, 16); return (f'{w} ' if w else '') + f'{r//g}/{16//g}"'
if GUIDE:
    import ezdxf, numpy as np
    D = json.load(open(sys.argv[6]))
    pts = [p for e in ezdxf.readfile(sys.argv[5]).modelspace().query('LWPOLYLINE[layer=="OUTLINE_HALF"]') for p in e.get_points('xy')]
    OX = np.array([p[0] for p in pts]); OY = np.array([p[1] for p in pts])
    hw = lambda x: float(np.interp(x, OX, OY))
    def txt(bx, off, s, size=9, color=(0, 0, 0), bold=False):
        p = P(bx, off); sp.insert_text(p, s, fontsize=size, fontname="LSB" if bold else "LSR", color=color)
    # rail zones: thick coloured line 0.3" outside the rail
    RED, ORA, GRN, BLU = (.85, .1, .1), (.95, .55, 0), (0, .6, .25), (.1, .35, .85)
    zones = [(D['rail']['hard'], RED), (D['rail']['blend'], ORA), ([D['rail']['blend'][1], D['rail']['nose_soft']], GRN), ([D['rail']['nose_soft'], L], BLU)]
    sh = sp.new_shape()
    for (z0, z1), col in zones:
        xs = np.linspace(max(z0, 1.0), min(z1, L - 1.0), 80)
        ys = np.array([hw(x) for x in xs])
        dy = np.gradient(ys, xs); nrm = np.sqrt(1 + dy**2)
        q = [P(x - 0.3 * d / n, y + 0.3 / n) for x, y, d, n in zip(xs, ys, dy, nrm)]
        sh.draw_polyline(q); sh.finish(color=col, width=6, closePath=False, lineCap=0)
    sh.commit()
    for x in (D['rail']['hard'][1], D['rail']['blend'][1], D['rail']['nose_soft']):   # zone boundary ticks
        sh = sp.new_shape(); sh.draw_line(P(x, hw(x) - 0.15), P(x, hw(x) + 0.9)); sh.finish(color=(0, 0, 0), width=1.2); sh.commit()
        txt(x + 0.1, hw(x) + 0.8, f'{frac(x)} from tail' if x < L / 2 else f'{frac(L - x)} from nose', 9, bold=True)
    txt(2.0, hw(7) + 1.6, 'RED = HARD RAIL EDGE (tail to 14")', 11, RED, True)
    txt(2.0, hw(7) + 1.35, 'Keep a sharp edge where bottom meets rail, rail shaped from the deck down.', 9, RED)
    txt(2.0, hw(7) + 1.15, 'Runs past the fins. Lets the tail let go of the wave in turns.', 9, RED)
    txt(15.0, hw(15) + 1.6, 'ORANGE = BLEND (14" to 20")', 11, ORA, True)
    txt(15.0, hw(15) + 1.35, 'Hard edge slowly rounds off into the soft rail.', 9, ORA)
    txt(49.0, hw(49) + 1.25, 'GREEN = SOFT, ROUND RAIL (low and tucked under)', 11, GRN, True)
    txt(49.0, hw(49) + 1.0, 'Edge tucked about 5/8" in from the outline at the widest point. Forgiving, holds in steep faces.', 9, GRN)
    txt(L - 11.5, hw(L - 11.5) + 1.6, 'BLUE = NOSE: thinner, softer rail', 11, BLU, True)
    txt(L - 11.5, hw(L - 11.5) + 1.35, 'Round it off so it does not catch.', 9, BLU)
    # strips under the stringer: rocker, bottom shape, thickness
    def band(z0, z1, top, h, fill, label, col=(0, 0, 0)):
        sh = sp.new_shape(); sh.draw_rect(fitz.Rect(P(z0, top), P(z1, top - h))); sh.finish(color=(0, 0, 0), fill=fill, width=0.6); sh.commit()
        if label: txt(z0 + 0.15, top - h + 0.07, label, 9, col, True)
    f0, f1 = D['flat']
    r_top = -1.12
    txt(-1.95, r_top - 0.2, 'ROCKER', 8, bold=True)
    band(0, f0, r_top, 0.25, (1, .85, .85), f'TAIL ROCKER: bottom starts curving up about {round(f0):.0f}" from the tail')
    band(f0, f1, r_top, 0.25, (.85, 1, .85), 'FLAT SPOT: keep the bottom dead straight here (check with a straightedge)')
    band(f1, L, r_top, 0.25, (.85, .9, 1), f'NOSE ROCKER: bottom starts curving up about {round(L - f1):.0f}" from the nose')
    for x, v in D['rocker']:
        sh = sp.new_shape(); sh.draw_line(P(x, r_top - 0.25), P(x, r_top - 0.33)); sh.finish(color=(0, 0, 0), width=1); sh.commit()
        txt(x - 0.25, r_top - 0.46, frac(v), 8, bold=True)
    txt(f0 + 0.3, r_top - 0.46, 'Rocker numbers = gap under the stringer, board bottom-down on a flat floor', 8)
    b_top = -1.7; B = D['bottom']; PUR = (.92, .85, 1); CON = (1, .95, .8); GRY = (.94, .94, .94)
    txt(-1.95, b_top - 0.2, 'BOTTOM', 8, bold=True)
    band(*B['vee'], b_top, 0.25, PUR, 'VEE about 1/8": stringer a bit lower than the rails, like a flat roof. Through the fins.')
    band(*B['vee_fade'], b_top, 0.25, GRY, 'fades to flat')
    band(*B['concave'], b_top, 0.25, CON, 'SINGLE CONCAVE about 3/32" deep: shallow scoop under your chest and front foot')
    band(*B['concave_fade'], b_top, 0.25, GRY, 'fade')
    band(*B['nose_vee'], b_top, 0.25, PUR, 'ROLLED VEE about 3/32": nose bottom slightly peaked on the stringer')
    t_top = -2.1
    txt(-1.95, t_top - 0.17, 'THICK', 8, bold=True)
    for x, v in D['thick']:
        sh = sp.new_shape(); sh.draw_line(P(x, t_top), P(x, t_top - 0.1)); sh.finish(color=(0, 0, 0), width=1); sh.commit()
        big = v == max(t for _, t in D['thick'])
        txt(x - 0.25, t_top - 0.25, (f'THICKEST {frac(v)}' if big else frac(v)), 8, bold=True)
    txt(D['thick'][2][0] + 2.5, t_top - 0.25, 'thickness on the stringer (deck to bottom) - check with calipers', 8)

# --- output sheet 36 x 48 portrait
out = fitz.open(); W, H = 36 * I, 48 * I; pg = out.new_page(width=W, height=H)
pg.insert_font(fontname="LSB", fontfile=BF); pg.insert_font(fontname="LSR", fontfile=RF)
sw = (Y1 - Y0)                       # strip width once rotated
M0, GAP = (0.6, 0.6) if GUIDE else (1.0, 1.25)
pieces = [("A", "TAIL HALF", XA0, XA1, M0), ("B", "NOSE HALF", XB0, XB1, M0 + sw + GAP)]
placed = {}
for name, desc, x0, x1, px in pieces:
    ln = x1 - x0
    py = (48 - ln) / 2 + 0.5
    r = fitz.Rect(px * I, py * I, (px + sw) * I, (py + ln) * I)
    pg.show_pdf_page(r, src, 0, clip=fitz.Rect(x0 * I, Y0 * I, x1 * I, Y1 * I), rotate=-90)
    pg.draw_rect(r, color=(0, 0, 0), width=1.5)   # cut line
    placed[name] = (r, ln)
    pg.insert_text(fitz.Point(r.x0, r.y0 - 0.55 * I), f"PIECE {name} - {desc}", fontsize=30, fontname="LSB")
    pg.insert_text(fitz.Point(r.x0, r.y0 - 0.18 * I), f"{ln:.2f}\" x {sw:.2f}\"  -  cut on the black border", fontsize=14, fontname="LSR")
    pg.insert_text(fitz.Point(r.x0, r.y1 + 0.35 * I), f"PIECE {name}", fontsize=18, fontname="LSB")

# --- info column
ix = M0 + 2 * sw + GAP + (0.5 if GUIDE else 1.0); y = 3.0
FS = 0.85 if GUIDE else 1.0
def T(s, size=14, font="LSR", dy=None, color=(0, 0, 0)):
    global y
    size = size * FS; pg.insert_text(fitz.Point(ix * I, y * I), s, fontsize=size, fontname=font, color=color)
    y += dy * FS if dy else size / 72 * 1.45
T(title, 26, "LSB"); T("Half-outline template, 2 pieces", 16)
T("FULL SIZE 1:1 on 36 x 48 in sheet", 16, "LSB", 0.6)
T("PRINT AT 100% / ACTUAL SIZE.", 18, "LSB", color=(.8, 0, 0))
T("NO fit-to-page, NO scaling.", 18, "LSB", color=(.8, 0, 0), dy=0.6)
T("Measure both bars after printing:", 14, "LSB", 0.45)
def bar(x, yy, n, horiz=True, unit=1.0):
    for i in range(n):
        rr = fitz.Rect(x * I, yy * I, (x + unit) * I, (yy + 0.3) * I) if horiz else fitz.Rect(x * I, yy * I, (x + 0.3) * I, (yy + unit) * I)
        if horiz: rr = fitz.Rect((x + i * unit) * I, yy * I, (x + (i + 1) * unit) * I, (yy + 0.3) * I)
        else: rr = fitz.Rect(x * I, (yy + i * unit) * I, (x + 0.3) * I, (yy + (i + 1) * unit) * I)
        pg.draw_rect(rr, color=(0, 0, 0), fill=(0, 0, 0) if i % 2 == 0 else (1, 1, 1), width=0.5)
# 1" square
pg.draw_rect(fitz.Rect(ix * I, y * I, (ix + 1) * I, (y + 1) * I), color=(0, 0, 0), fill=(0, 0, 0), width=0.5)
pg.insert_text(fitz.Point((ix + 1.2) * I, (y + 0.6) * I), "1\" x 1\" square", fontsize=14, fontname="LSB")
y += 1.5
T("12\" bars: top of sheet + right edge.", 13, dy=0.7)
bx0 = M0 + sw + GAP
bar(bx0, 1.1, 12, True)
pg.insert_text(fitz.Point(bx0 * I, 0.95 * I), "SCALE CHECK: this bar must measure exactly 12\" (each block 1\")", fontsize=13, fontname="LSB")
for i in (0, 6, 12): pg.insert_text(fitz.Point((bx0 + i - 0.05) * I, 1.62 * I), str(i), fontsize=10, fontname="LSR")
VX, VY = (ix + 0.2, 33.5) if GUIDE else (34.6, 18.0)
bar(VX, VY, 12, False)
pg.insert_text(fitz.Point((VX + 0.75) * I, VY * I), "SCALE CHECK: this bar must measure exactly 12\"", fontsize=12, fontname="LSB", rotate=-90)
T("HOW TO ASSEMBLE", 18, "LSB", 0.4)
steps = [
 "1. Cut both pieces out on their black border.",
 "2. Lay piece B flat. Slide piece A over it",
 "   so the OVERLAP bands stack (~2\").",
 "3. Line up the 4 crosses X1-X4 (hold up to",
 "   light). Red stringer lines must make one",
 "   straight line - check with a straightedge.",
 "4. A's end edge lands on B's \"A ends here\"",
 "   dashed line, and B's edge on \"B ends here\".",
 "5. Tape both faces along the seam.",
 f"6. Check: tail tip to nose tip = {L:.0f}\"",
 f"   ({int(L//12)}'{L%12:.0f}\") along the stringer.",
 "7. Glue to 1/8\" hardboard, cut, sand to line.",
]
for s in steps: T(s, 13, dy=0.27)
if GUIDE:
    y += 0.3
    T("SHAPING MARKS", 18, "LSB", 0.4)
    for s_ in ["Numbers come from your design file.",
               "Colored line outside the rail = rail type:",
               "  red hard edge, orange blend, green soft",
               "  round rail, blue nose.",
               "Strips under the stringer:",
               "  ROCKER = where the bottom curves up",
               "  BOTTOM = vee / concave zones",
               "  THICK = thickness on the stringer",
               "Order: outline, then rocker + thickness",
               "(planer), then bottom shape, then rails.",
               "Trace the zone ends onto the blank."]:
        T(s_, 13, dy=0.27)
y += 0.4
T("Source: " + src_path.split('/')[-1], 9)
T(f"Overlap centred on CENTER station ({mid:.0f}\" from tail).", 9)
out.set_metadata({"title": title + " - 36x48 split template"})
out.save(out_path, garbage=3, deflate=True)
print(placed)
