import sys, json, math, numpy as np
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color, black, red, white
import ezdxf
rfile, ffile, L, name, out, fname = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4], sys.argv[5], sys.argv[6]
R=np.load(rfile); x=R[:,1]/25.4; y=R[:,2]/25.4; o=np.argsort(x); x,y=x[o],y[o]
F=json.load(open(ffile))
# shift so tail tip = 0 (STEP tips are trimmed flats 0.06" in from each end)
def bez(p0,p1,p2,n=12):
    t=np.linspace(0,1,n)[:,None]; return (1-t)**2*p0+2*(1-t)*t*p1+t**2*p2
# close tail: tangent from first points
s0=(y[3]-y[0])/(x[3]-x[0]); c0=np.array([0, max(0,y[0]-x[0]*s0)])
tail=np.array([[x[0],0.]])
s1=(y[-1]-y[-4])/(x[-1]-x[-4]); c1=np.array([L, max(0,y[-1]+(L-x[-1])*s1)])
nose=np.array([[x[-1],0.]])
# decimate main curve to ~0.02" spacing
main=np.c_[x,y]; keep=[0]
for i in range(1,len(main)):
    if np.hypot(*(main[i]-main[keep[-1]]))>0.05: keep.append(i)
keep.append(len(main)-1); main=main[sorted(set(keep))]
OUT=np.vstack([tail,main,nose])
hw=lambda X: float(np.interp(X,OUT[:,0],OUT[:,1]))
iw=int(np.argmax(OUT[:,1])); wpx, wpw = OUT[iw,0], 2*OUT[iw,1]
def frac(v):
    n=round(v*16); w,r=divmod(n,16)
    if r==0: return f'{w}"'
    g=math.gcd(r,16); return (f'{w} ' if w else '')+f'{r//g}/{16//g}"'
fins=F["fins"]; side=[p for p in fins if np.mean([q[1] for q in p])>1][0]; ctr=[p for p in fins if abs(np.mean([q[1] for q in p]))<1][0]
def mid(pts, fx):
    P=sorted(pts,key=lambda p:p[0]); a=np.mean(P[:2],0); b=np.mean(P[2:],0); return a,b  # back, front
sb,sf=mid(side,0); toe=math.degrees(math.atan2(sb[1]-sf[1], sf[0]-sb[0]))
def order(pts):
    c=np.mean(pts,0); return sorted(pts,key=lambda p:math.atan2(p[1]-c[1],p[0]-c[0]))
side_o=order(side); ctr_o=order(ctr); ls=F["leash"]
_RX=np.linspace(0,30,6000); _RL=np.c_[_RX,np.interp(_RX,OUT[:,0],OUT[:,1])]
clr=lambda p: float(np.min(np.hypot(*(_RL-np.asarray(p)).T)))
info=dict(L=L,wpx=wpx,wpw=wpw,tail12=2*hw(12),nose12=2*hw(L-12),center=2*hw(L/2),
  side_front=sf.tolist(), side_back=sb.tolist(), toe=toe, side_front_from_rail=clr(sf), side_back_from_rail=clr(sb),
  ctr=[min(p[0] for p in ctr), max(p[0] for p in ctr)], leash=ls)
print(json.dumps(info,indent=1))
stations=sorted(set([s for s in np.arange(6,L,6) if s<L-1]+[L-12, L/2]))
GRAY=Color(.45,.45,.45); LG=Color(.88,.88,.88); BLUE=Color(0,.25,.7)

def drawing(c, title=True):
    # c is scaled so 1 unit = 1 inch, origin at tail tip on stringer
    c.setLineCap(1); c.setLineJoin(1)
    # stations
    c.setDash([0.08,0.06]); c.setLineWidth(0.008); c.setStrokeColor(GRAY)
    for s in stations: c.line(s,0,s,hw(s))
    c.setDash([])
    # wide point
    c.setStrokeColor(BLUE); c.setLineWidth(0.012); c.line(wpx,0,wpx,wpw/2+0.6)
    # stringer
    c.setStrokeColor(red); c.setLineWidth(0.015); c.setDash([0.5,0.1,0.06,0.1]); c.line(-1.5,0,L+1.5,0); c.setDash([])
    # ticks
    c.setStrokeColor(black); c.setFillColor(black)
    for i in range(0,int(L)+1):
        h=0.7 if i%12==0 else 0.4 if i%6==0 else 0.2
        c.setLineWidth(0.012 if i%6 else 0.018); c.line(i,0,i,h)
        if i%6==0 and 0<i<L:
            c.setFont("Helvetica-Bold",0.16); c.drawCentredString(i,h+0.05,f'{i}')
    # nose-measured labels below the line
    c.setFillColor(GRAY); c.setFont("Helvetica",0.12)
    for i in range(0,int(L)+1,6):
        c.drawCentredString(L-i, -0.25, f'{i} from nose' if i else 'NOSE TIP')
    c.drawCentredString(0,-0.25,'TAIL TIP') if L%6 else None
    for i in range(6,int(L),6): c.drawCentredString(i,-0.45,'')
    c.setFillColor(black); c.setFont("Helvetica",0.12)
    c.drawString(1.0,-0.6,'Numbers above the line = inches from TAIL tip.  Gray numbers below = inches from NOSE tip.')
    c.setFillColor(red); c.setFont("Helvetica-Bold",0.14)
    c.drawString(L/2-14, -0.95, 'STRINGER / CENTERLINE  - lay this line exactly on the stringer, trace, then flip the template over and trace the other side')
    # station labels
    c.setFillColor(black)
    for s in stations:
        w=2*hw(s); lab=f'W {frac(w)}'
        tag = 'NOSE 12"  ' if abs(s-(L-12))<1e-6 else 'TAIL 12"  ' if abs(s-12)<1e-6 else 'CENTER  ' if abs(s-L/2)<1e-6 else ''
        c.saveState(); c.translate(s-0.06, 1.0); c.rotate(90); c.setFont("Helvetica-Bold" if tag else "Helvetica",0.14)
        c.drawString(0,0,f'{tag}{lab}   (half {frac(w/2)})'); c.restoreState()
    c.setFillColor(BLUE); c.setFont("Helvetica-Bold",0.15)
    c.drawString(wpx+0.08, wpw/2+0.35, f'WIDE POINT {frac(wpw)} @ {wpx:.1f}" from tail ({wpx-L/2:+.1f}" from center)')
    # leash plug
    c.setStrokeColor(black); c.setLineWidth(0.012); c.circle(ls["x"],ls["y"],ls["r"]); c.line(ls["x"]-0.15,0,ls["x"]+0.15,0); c.line(ls["x"],-0.15,ls["x"],0.15)
    c.setFont("Helvetica",0.11); c.drawString(ls["x"]-0.45, 0.62+0.35, 'LEASH PLUG (deck)'); c.drawString(ls["x"]-0.45,0.82+0.35,f'1" hole, {frac(ls["x"])} from tail')
    # fins
    def poly(pts, fill):
        p=c.beginPath(); p.moveTo(*pts[0])
        for q in pts[1:]: p.lineTo(*q)
        p.close(); c.setFillColor(fill); c.setStrokeColor(black); c.setLineWidth(0.012); c.drawPath(p,fill=1,stroke=1)
    poly(side_o, LG); poly(ctr_o, LG)
    d=(sf-sb)/np.linalg.norm(sf-sb); c.setStrokeColor(black); c.setDash([0.1,0.05]); c.setLineWidth(0.01)
    a=sb-d*0.6; b=sf+d*0.9; c.line(*a,*b); c.setDash([])
    for pnt in (sf,sb): c.circle(pnt[0],pnt[1],0.04,fill=1,stroke=0)
    c.setFillColor(black); c.setFont("Helvetica-Bold",0.12)
    tx, ty = sf[0]+1.6, sf[1]+0.9
    lines=['SIDE FIN BASE (mark both sides - mirror)', f'front of base {frac(sf[0])} from tail, {frac(info["side_front_from_rail"])} in from rail edge',
           f'back of base {frac(sb[0])} from tail, {frac(info["side_back_from_rail"])} in from rail edge', 'toe-in 3/16" over the base (front points toward stringer)',
           'cant 5 deg (fin tip leans out toward rail)', f'use side fins with a base {frac(np.linalg.norm(sf-sb))} long or shorter']
    for k,t in enumerate(lines): c.setFont("Helvetica-Bold" if k==0 else "Helvetica",0.12); c.drawString(tx,ty-k*0.17,t)
    c.setLineWidth(0.008); c.line(tx-0.05, ty-0.3, sf[0]+0.05, sf[1]+0.1)
    c.setFont("Helvetica-Bold",0.12); cx0,cx1=info["ctr"]
    c.drawString(cx1+0.9, 1.65, 'CENTER FIN BASE (on stringer, 0 deg)')
    c.setFont("Helvetica",0.12); c.drawString(cx1+0.9,1.48,f'{frac(cx0)} to {frac(cx1)} from tail')
    c.setLineWidth(0.008); c.line(cx1+0.85,1.6,(cx0+cx1)/2,0.25)
    # outline (on top)
    c.setStrokeColor(black); c.setLineWidth(0.025)
    p=c.beginPath(); p.moveTo(*OUT[0])
    for q in OUT[1:]: p.lineTo(*q)
    c.drawPath(p,stroke=1,fill=0)
    c.setFont("Helvetica-Bold",0.2); c.setFillColor(black)
    c.drawString(0.15, hw(1)+0.35, 'TAIL'); c.drawRightString(L-0.15, hw(L-1)+0.35,'NOSE')
    c.setFont("Helvetica",0.13); c.drawCentredString(L*0.42, hw(L*0.42)+0.25, 'RAIL OUTLINE - trace / cut on the OUTSIDE edge of this line')

def checkbars(c, X, Y, n=10, vertical=True):
    c.setStrokeColor(black); c.setFillColor(black); c.setLineWidth(0.01)
    for i in range(n):
        if i%2==0: c.rect(X+i,Y,1,0.25,fill=1,stroke=0)
    c.rect(X,Y,n,0.25,fill=0,stroke=1)
    c.setFont("Helvetica-Bold",0.16); c.drawString(X,Y+0.35,f'SCALE CHECK: this bar must measure exactly {n}"')
    for i in range(n+1): c.setFont("Helvetica",0.11); c.drawCentredString(X+i,Y-0.17,str(i))
    if vertical:
        VX=X-4.2; VY=Y-n-0.5
        for i in range(n):
            if i%2==0: c.rect(VX,VY+i,0.25,1,fill=1,stroke=0)
        c.rect(VX,VY,0.25,n,fill=0,stroke=1)
        c.saveState(); c.translate(VX-0.1,VY); c.rotate(90); c.setFont("Helvetica-Bold",0.16); c.drawString(0,0,f'SCALE CHECK: must measure exactly {n}"'); c.restoreState()

# ---------- full-size PDF ----------
ML, MB = 4.5, 2.5; W=L+ML+2.5; H=18
c=canvas.Canvas(f'{out}/{fname}_template_FULLSIZE_{int(W)}x{H}in.pdf', pagesize=(W*72,H*72))
c.setTitle(f'{name} - 1:1 half outline template'); c.scale(72,72)
c.saveState(); c.translate(ML,MB); drawing(c)
checkbars(c, 1.5, 12.8)
c.setFont('Helvetica',0.12); c.setFillColor(GRAY); c.drawString(0.1,-0.85,'Tips end in a small flat exactly as in the CAD file (tail ~3/4", nose ~9/16" wide, 1/16" short of the nominal tip) - round them off by hand.')
# title block
TX=L-31; TY=H-MB-0.8
c.setFillColor(black); c.setFont("Helvetica-Bold",0.45); c.drawString(TX,TY,f'{name}  -  HALF OUTLINE TEMPLATE  -  FULL SIZE 1:1')
c.setFont("Helvetica",0.2)
txt=[f'Length {frac(L)} ({int(L//12)}\'{frac(L%12)}) tip to tip   |   Max width {frac(wpw)}   |   Tail @12" {frac(info["tail12"])}   |   Nose @12" {frac(info["nose12"])}',
     f'Sheet {W:.0f}" x {H}" - fits a 24" or 36" plotter roll.  Units: inches.  Source: {sys.argv[7]} (side fins repositioned 2026-11-24)',
     'PRINT SHOP: print at 100% / ACTUAL SIZE. NO "fit to page", NO scaling. Check both 10" scale bars after printing.',
     'Use: cut out along the rail line and the stringer line, trace onto 1/8" hardboard, cut and sand that to the line.',
     'On the blank: snap the stringer line, mark stations from the tail tip, trace one side, flip and trace the other.']
for k,t in enumerate(txt):
    c.setFont("Helvetica-Bold" if k==2 else "Helvetica",0.2); c.drawString(TX,TY-0.4-k*0.3,t)
c.restoreState(); c.showPage(); c.save()

# ---------- tiled letter ----------
PW,PH=11,8.5; m=0.4; ov=0.5; cw,ch=PW-2*m,PH-2*m
X0,X1,Y0,Y1=-2.2,L+1.6,-1.2,11.6
nx=math.ceil((X1-X0-ov)/(cw-ov)); ny=math.ceil((Y1-Y0-ov)/(ch-ov))
c=canvas.Canvas(f'{out}/{fname}_template_TILED_letter_{nx*ny}pages.pdf', pagesize=(PW*72,PH*72)); c.setTitle(f'{name} - tiled template')
rows='ABCDEFG'
for j in range(ny-1,-1,-1):
    for i in range(nx):
        c.saveState(); c.scale(72,72)
        x0=X0+i*(cw-ov); y0=Y0+j*(ch-ov)
        c.saveState(); p=c.beginPath(); p.rect(m,m,cw,ch); c.clipPath(p,stroke=0,fill=0)
        c.translate(m-x0, m-y0); drawing(c)
        if i==0 and j==ny-1: checkbars(c, x0+0.6, y0+ch-1.6, n=5, vertical=False)
        # registration crosshairs on the overlap band
        c.setStrokeColor(black); c.setLineWidth(0.01)
        for gx in [X0+k*(cw-ov)+ov/2 for k in range(nx+1)]:
            for gy in [Y0+k*(ch-ov)+ov/2 for k in range(ny+1)]:
                for ax in (gx,):
                    c.line(ax-0.2,gy,ax+0.2,gy); c.line(ax,gy-0.2,ax,gy+0.2); c.circle(ax,gy,0.08)
        c.restoreState()
        c.setStrokeColor(GRAY); c.setLineWidth(0.005); c.setDash([0.05,0.05]); c.rect(m,m,cw,ch); c.setDash([])
        c.setFillColor(black); c.setFont("Helvetica-Bold",0.14)
        c.drawString(m, PH-m+0.12, f'{name} tiled template  -  page {rows[ny-1-j]}{i+1}  (row {rows[ny-1-j]} of {rows[ny-1]}, column {i+1} of {nx})')
        c.setFont("Helvetica",0.11)
        c.drawString(m, 0.15, f'Print at 100% / actual size (no fit-to-page). Trim, overlap 1/2" with neighbours so the crosshairs line up, tape. Row A = rail side, columns run tail to nose.')
        c.restoreState(); c.showPage()
c.save()

# ---------- DXF ----------
doc=ezdxf.new('R2010'); doc.header['$INSUNITS']=1; msp=doc.modelspace()
for ln,col in [('OUTLINE_HALF',7),('OUTLINE_FULL',8),('STRINGER',1),('STATIONS',9),('FINS',5),('LEASH',3),('TEXT',7)]: doc.layers.add(ln,color=col)
msp.add_lwpolyline([tuple(p) for p in OUT],dxfattribs={'layer':'OUTLINE_HALF'})
full=np.vstack([OUT, OUT[::-1][1:-1]*[1,-1]]); msp.add_lwpolyline([tuple(p) for p in full],close=True,dxfattribs={'layer':'OUTLINE_FULL'})
msp.add_line((0,0),(L,0),dxfattribs={'layer':'STRINGER'})
for s in stations+[wpx]:
    msp.add_line((s,0),(s,hw(s)),dxfattribs={'layer':'STATIONS'}); msp.add_text(f'{s:.2f} W {2*hw(s):.3f}',height=0.15,dxfattribs={'layer':'TEXT'}).set_placement((s+0.05,0.3))
for i in range(int(L)+1): msp.add_line((i,0),(i,0.7 if i%12==0 else 0.4 if i%6==0 else 0.2),dxfattribs={'layer':'STRINGER'})
for pts in (side_o, [(p[0],-p[1]) for p in side_o], ctr_o): msp.add_lwpolyline([tuple(p) for p in pts],close=True,dxfattribs={'layer':'FINS'})
msp.add_circle((ls["x"],ls["y"]),ls["r"],dxfattribs={'layer':'LEASH'})
doc.saveas(f'{out}/{fname}_outline.dxf')
json.dump(info,open(f'{out}/{fname}_info.json','w'))
