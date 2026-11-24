"""Measure rocker and thickness along the stringer from a board STEP file and
write the shaping-guide JSON used by split36x48.py.
usage: python shaping_data.py BOARD.step L_inches OUT.json
Needs cadquery-ocp. Zone positions (rail, bottom contours) are the v5 6'6" plan,
measured from the v5 file and placed by distance from tail / nose."""
import sys, json, numpy as np
from OCP.STEPControl import STEPControl_Reader
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRep import BRep_Tool
step, L, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
r = STEPControl_Reader(); r.ReadFile(step); r.TransferRoots(); s = r.OneShape()
S = BRep_Tool.Surface_s(TopoDS.Face(TopExp_Explorer(s, TopAbs_FACE).Current()))
us = np.linspace(0, 1, 721); xs, bot, deck = [], [], []
for v in np.linspace(0, 1, 801):
    P = np.array([(lambda p: (p.X(), p.Y(), p.Z()))(S.Value(u, v)) for u in us]) / 25.4
    m = np.abs(P[:, 1]) < 0.05
    if m.sum() < 2: continue
    xs.append(P[:, 0].mean()); bot.append(P[m, 2].min()); deck.append(P[m, 2].max())
o = np.argsort(xs); xs, bot, deck = np.array(xs)[o], np.array(bot)[o], np.array(deck)[o]
low = bot.min()
rk = lambda x: float(np.interp(x, xs, bot) - low)
th = lambda x: float(np.interp(x, xs, deck) - np.interp(x, xs, bot))
# flat spot: where rocker <= 1/16"
flat = xs[(bot - low) <= 1/16 + 1e-9]
d = dict(L=L,
  rocker=[[x, rk(x)] for x in (0.5, 6, 12, 18, 24)] + [[L - n, rk(L - n)] for n in (24, 18, 12, 6, 0.5)],
  flat=[float(flat.min()), float(flat.max())],
  thick=[[x, th(x)] for x in (6, 12, 24)] + [[float(xs[np.argmax(deck - bot)]), float((deck - bot).max())]] + [[L - n, th(L - n)] for n in (24, 12, 6)],
  rail=dict(hard=[0, 14], blend=[14, 20], nose_soft=L - 12),
  bottom=dict(vee=[0, 22], vee_fade=[22, 28], concave=[28, L - 21], concave_fade=[L - 21, L - 18], nose_vee=[L - 18, L]))
json.dump(d, open(out, 'w'), indent=1); print(json.dumps(d))
