import json, sys, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
def load(f):
    m=list(json.load(open(f)).values())[0]; V=np.array(m["verts"]); F=m["faces"]
    n=len(V); V2=V.copy(); V2[:,0]*=-1; return np.vstack([V,V2]), F+[[i+n for i in f[::-1]] for f in F]
def draw(ax,V,F,view,title,ylim):
    ax.set_title(title,fontsize=10); ax.set_aspect("equal"); ax.axis("off")
    ang={"front":0,"persp":30,"side":90,"back":180}[view]; a=np.radians(ang)
    R=np.array([[np.cos(a),np.sin(a),0],[-np.sin(a),np.cos(a),0],[0,0,1]]); W=V@R.T
    P=W[:,[0,2]]; depth=-W[:,1]; vv=np.array([0,-1,0])
    L=np.array([0.3,-0.8,0.5]);L/=np.linalg.norm(L); polys=[];cols=[];ds=[]
    for f in F:
        p=W[f]; n=np.cross(p[1]-p[0],p[2]-p[0]); nn=np.linalg.norm(n)
        if nn==0 or n.dot(vv)/nn<=0: continue
        n/=nn; polys.append(P[f]); ds.append(depth[f].mean()); s=0.35+0.6*max(0,n.dot(L)); cols.append((s,s,s))
    o=np.argsort(ds); ax.add_collection(PolyCollection([polys[i] for i in o],facecolors=[cols[i] for i in o],edgecolors="k",linewidths=0.5))
    ax.set_xlim(-4.5,4.5); ax.set_ylim(*ylim)
A,B,out,ylo=sys.argv[1],sys.argv[2],sys.argv[3],float(sys.argv[4])
a=load(A); b=load(B); views=sys.argv[5].split(",")
fig,axs=plt.subplots(2,len(views),figsize=(4.7*len(views),11))
for j,v in enumerate(views):
    draw(axs[0,j],*a,v,"Backup awal - "+v,(ylo,2.2)); draw(axs[1,j],*b,v,"Versi 3 - "+v,(ylo,2.2))
plt.tight_layout(); plt.savefig(out,dpi=70)
