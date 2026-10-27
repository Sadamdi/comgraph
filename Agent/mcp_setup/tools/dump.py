import bpy, sys, json
out=sys.argv[-1]; d={}
for o in bpy.data.objects:
    if o.type=='MESH':
        d[o.name]={"verts":[tuple(round(c,4) for c in v.co) for v in o.data.vertices],
                   "faces":[list(p.vertices) for p in o.data.polygons],
                   "mods":[(m.type,getattr(m,'use_clip',None)) for m in o.modifiers],
                   "loc":tuple(o.location),"scale":tuple(o.scale)}
json.dump(d,open(out,"w"))
