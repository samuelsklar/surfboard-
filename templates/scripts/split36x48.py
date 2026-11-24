"""Split a FULLSIZE half-outline template into two overlapping pieces laid
side by side on one 36x48in sheet (Staples engineering print), at 100% scale.
usage: python split36x48.py FULLSIZE.pdf OUT.pdf "TITLE" L_inches
Source convention (from gen.py): tail tip at x=4.5in, stringer at y=15.5in from top."""
import sys, pymupdf as fitz
src_path, out_path, title, L = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
I = 72.0
BF = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"  # embedded bold sans
TX, SY = 4.5, 15.5                  # tail tip x, stringer y (inches, source page, y down)
mid = round(L / 2)                  # overlap centred on the CENTER station
OV = 2.0
a0, a1 = mid - OV/2, mid + OV/2     # overlap zone in board inches from tail
Y0, Y1 = 4.3, 16.6                  # source strip kept (y, inches from top)
XA0, XA1 = TX - 2.0, TX + a1         # piece A: tail half
XB0, XB1 = TX + a0, TX + L + 2.5     # piece B: nose half
src = fitz.open(src_path); sp = src[0]
sp.insert_font(fontname="LSB", fontfile=BF)

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

# --- output sheet 36 x 48 portrait
out = fitz.open(); W, H = 36 * I, 48 * I; pg = out.new_page(width=W, height=H)
pg.insert_font(fontname="LSB", fontfile=BF)
sw = (Y1 - Y0)                       # strip width once rotated
pieces = [("A", "TAIL HALF", XA0, XA1, 1.0), ("B", "NOSE HALF", XB0, XB1, 1.0 + sw + 1.25)]
placed = {}
for name, desc, x0, x1, px in pieces:
    ln = x1 - x0
    py = (48 - ln) / 2 + 0.5
    r = fitz.Rect(px * I, py * I, (px + sw) * I, (py + ln) * I)
    pg.show_pdf_page(r, src, 0, clip=fitz.Rect(x0 * I, Y0 * I, x1 * I, Y1 * I), rotate=-90)
    pg.draw_rect(r, color=(0, 0, 0), width=1.5)   # cut line
    placed[name] = (r, ln)
    pg.insert_text(fitz.Point(r.x0, r.y0 - 0.55 * I), f"PIECE {name} - {desc}", fontsize=30, fontname="LSB")
    pg.insert_text(fitz.Point(r.x0, r.y0 - 0.18 * I), f"{ln:.2f}\" x {sw:.2f}\"  -  cut on the black border", fontsize=14, fontname="helv")
    pg.insert_text(fitz.Point(r.x0, r.y1 + 0.35 * I), f"PIECE {name}", fontsize=18, fontname="LSB")

# --- info column
ix = 1.0 + 2 * sw + 1.25 + 1.0; y = 3.0
def T(s, size=14, font="helv", dy=None, color=(0, 0, 0)):
    global y
    pg.insert_text(fitz.Point(ix * I, y * I), s, fontsize=size, fontname=font, color=color)
    y += dy if dy else size / 72 * 1.45
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
bx0 = 1.0 + sw + 1.25
bar(bx0, 1.1, 12, True)
pg.insert_text(fitz.Point(bx0 * I, 0.95 * I), "SCALE CHECK: this bar must measure exactly 12\" (each block 1\")", fontsize=13, fontname="LSB")
for i in (0, 6, 12): pg.insert_text(fitz.Point((bx0 + i - 0.05) * I, 1.62 * I), str(i), fontsize=10, fontname="helv")
bar(34.6, 18.0, 12, False)
pg.insert_text(fitz.Point(34.4 * I, 30.0 * I), "SCALE CHECK 12\"", fontsize=12, fontname="LSB", rotate=-90)
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
y += 0.4
T("Source: " + src_path.split('/')[-1], 9)
T(f"Overlap centred on CENTER station ({mid:.0f}\" from tail).", 9)
out.set_metadata({"title": title + " - 36x48 split template"})
out.save(out_path, garbage=3, deflate=True)
print(placed)
