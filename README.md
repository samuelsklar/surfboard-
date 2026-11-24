# Surfboard build: Sam's 6'6" and friend's 6'8" (Hypto Krypto-style)

Winter garage build of two boards from the same design, a copy of the Haydenshapes Hypto Krypto. Boards are surfed at Rockaway, NY. Target: finish by late Dec 2026 / Jan 2027 to catch the El Niño nor'easter swell.

Carried over from Sam's private project on 2026-11-21. Edit designs in Fusion 360 and commit the new STEP file with a new version name.

## Files in this repo
- `designs/hypto_6-6_v5_narrow-tail.step`: Sam's current 6'6" design (final, v5).
- `designs/hypto_6-8_build.step`: friend's 6'8" design.
- `designs/archive/`: earlier 6'6" iterations (original, build, concave, fins, v2–v4), kept for reference.
- `templates/`: 1:1 half-outline templates for both boards.
  - `*_FULLSIZE_85x18in.pdf` / `*_87x18in.pdf`: one long sheet for a print shop plotter (24" or 36" roll). Print at 100%, no "fit to page", on heavy paper or card stock.
  - `*_STAPLES_36x48in.pdf`: the full-size template split into two pieces (tail half A, nose half B) side by side on one 36x48" sheet, for Staples-style engineering prints. Print at 100%, no fit-to-page; check the 1" square and the two 12" bars. Cut each piece on its black border, overlap the shaded 2" bands so crosses X1-X4 and the red stringer line match, tape both sides. These sheets also carry shaping marks taken from the design files: a colored line outside the rail for the rail type (red hard edge from the tail to 14", orange blend to 20", green soft round rail, blue nose), and strips under the stringer showing where the rocker starts and how high it lifts, the vee and concave zones, and thickness on the stringer. Made by `scripts/split36x48.py` from the FULLSIZE PDF, the outline DXF and `scripts/shaping/*.json` (measured by `scripts/shaping_data.py`).
  - `*_TILED_letter_18pages.pdf`: home-printable backup, 18 letter pages taped together on crosshairs.
  - `*_outline.dxf`: outline in inches, for CAD or a CNC/laser shop.
  - Each template shows the half outline (stringer to rail), inch marks from tail and nose, widths every 6", wide point, fin bases with toe/cant labels, leash plug, and two 10" scale bars to check the print.
  - `scripts/`: Python scripts used to generate the templates from the STEP files.
- Rule: always edit designs in Fusion 360, not a web viewer.

## Shared design (both boards)
- Width 20 3/4", thickness 2 7/8".
- Wide point about 2" forward of center (measured 2.8" forward on the v5 file).
- Pulled-in round pin tail, Hypto style.
- Rocker: 4 1/2" nose, 2" tail, flat through the middle.
- Bottom: rolled vee in the nose (~5/32") into a subtle single concave under the chest (~1/8"), then vee (~1/8") with a subtle double (~1/16") out the tail.
- Rails: low-apex, pinched. Tail ~0.2" thicker than nose at 12" from each end.
- 3" thick (~43 L on the 6'6") was considered and rejected so duck diving stays easy.

## Sam's board: 6'6"
- Rider: 5'9", 165 lb, intermediate, mostly cruising. This is the big-day board (4–8 ft+), so duck diving is a must. Current small-day board: Lost Puddle Jumper 5'7" x 21 x 2.5, 34 L. Reference Sam loved: rented Hypto Krypto 6'4" x 21 x 3, 43.2 L.
- Design: 6'6" x 20 3/4" x 2 7/8", ~41.4 L (`hypto_6-6_v5_narrow-tail.step`).
- Measured from the v5 file: 77.88" tip to tip, max width 20.76" at 41.8" from tail, 13.30" wide at 12" from tail, 15.23" wide at 12" from nose.
- Blank: Greenlight 66SB x 3 1/4" EPS, no stringer ($75). A wood stringer has to be glued in. Check the blank is at least ~6'7" long and ~21 1/2" wide before cutting. Gluing the stringer in yourself needs several bar clamps 24" or longer (6" clamps won't reach around a ~21" blank).

## Friend's board: 6'8"
- Design: same shape stretched to 6'8" x 20 3/4" x 2 7/8", ~43.1 L (`hypto_6-8_build.step`).
- Templates: `templates/hypto_6-8_template_FULLSIZE_87x18in.pdf`, `templates/hypto_6-8_template_TILED_letter_18pages.pdf`, `templates/hypto_6-8_outline.dxf`.
- Blank: Greenlight 7'0" x 3 1/4" EPS with a black PVC stringer already in, $68. One side is softer, less dense foam.
  - The soft side doesn't change how the board surfs once glassed; it just dents more easily. If possible, put the soft side on the bottom when shaping. If it ends up on the deck, add an extra 4 oz glass patch on the deck over it.
- Stringer thickness: the PVC stringer looked thicker than Sam's wood one. Worth measuring both with calipers (1/8"–1/4" is normal).
- Not yet recorded: the friend's height, weight, ability level and the waves this board is for. Worth adding so the 6'8" volume (~43 L) can be sanity-checked for them.
- Fins, leash, construction and tools: same as below unless you decide otherwise.

## Construction (both boards)
- EPS foam + epoxy only. Never polyester resin, it melts EPS. TotalBoat High Performance 2:1 laminating epoxy is fine.
- Glass: double 6 oz top and bottom (aiming for very durable).
- Optional: 1" carbon tape on the rails (FutureFlex look), ~10 yd, ~$50.
- Paint: water-based acrylic (brush, roller, airbrush or Posca pens) on the shaped foam right before glassing, thin coats, fully dry. Never spray cans or solvent paint, they melt EPS. Mask with painter's tape and pull it before glassing. Alternative: paint the sanded hot coat and add a gloss coat.

## Fins and leash (both boards)
- Glass-on thruster, homemade angle guides (no kit). Fins go on after lamination, before the hot coat.
- Side fins (settled 2026-11-24, drawn on all templates): 5° cant, toe-in 3/16" over the base (front points toward the stringer, ~2.5°). Front of base 11" from tail, 2 5/16" in from the rail on the 6'6" (2 3/16" on the 6'8"). Back of base 6 3/4" from tail, 3/4" in from the rail. Mark them from the templates.
- Center fin: 0°, on stringer, back of base 3 1/4" from tail (STEP file: 3 1/4"–7 11/16").
- Leash plug: deck, on stringer, 2 1/2" from tail, 1" hole.
- Note: the fin bodies in the STEP files still sit in the old spot (back end ~3/8" from the rail, 3.2° toe). The templates are the reference for fin placement.

## Tools
- Foam removal: power planer (an older Makita 1900B-style 3 1/4" planer works; put in sharp blades) or a Surform by hand.
- Measuring: tape, 4–6 ft straightedge, thickness calipers, contour gauge, the printed templates.
- Shaping: Surform, sanding blocks, drywall sanding screen, orbital sander (Sam owns one), shaping stands, low side light, optional hot-wire cutter. Small clamps are handy for templates, fins and stands.
- Template: spray-glue the full-size print to 1/8" hardboard (Masonite) or 1/4" MDF/ply, jigsaw just outside the line, sand to the line. Flip it over the stringer line to trace the second half.
- Glassing: graduated cups, squeegees, chip brushes, good scissors, tape, plastic sheeting, 80–220 grit sandpaper.
- Safety: organic-vapor respirator, N95s, nitrile gloves, glasses.

## Supplier
Greenlight Surf Supply, Manasquan, NJ. Ask for Brian.

## Open questions
1. 66SB actual length and width (Sam needs ~6'7"+ long, 21 1/2"+ wide).
2. Cost of having Greenlight glue a stringer into the 66SB vs doing it yourself.
3. Stringer thickness check (Sam's wood vs friend's PVC), and whether Sam got the stringer he paid for.
4. Friend's rider details (see friend's board section).
