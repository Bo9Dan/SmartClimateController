import library_io as l
def fields(a):
    return dict(p.split(b'=',1) for p in a.rstrip(b'\0').split(b'|') if b'=' in p)
s=l.setup('SmartClimateControlLibrarySNEDA/1571294-1/SmartClimate.SchDoc')
i=next(i for i,e in enumerate(s['entries']) if s['ename'](e)=='FileHeader')
rr=s['records'](s['streams'][i]); fs=[fields(a) for t,a in rr]
for j,f in enumerate(fs):
    if f.get(b'RECORD')==b'1' and f.get(b'LibReference',b'').startswith(b'R_'):
        children=[g for g in fs if g.get(b'OwnerIndex')==str(j-1).encode()]
        print(j, f.get(b'LibReference'), [(g.get(b'RECORD'),g.get(b'Name'),g.get(b'Text'),g.get(b'Designator')) for g in children if g.get(b'RECORD') in (b'2',b'34')])
