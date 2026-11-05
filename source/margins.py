import engine as e
from boundaries import restore
import numpy as np,pandas as pd,json,control

def lifted(c,delay):
 Ac,Bc,Cc,Dc,C=e.feedback_ss(c);F,G=c['d']['F'],c['d']['G'];q,r=divmod(delay,10);Fm,_=e.transition(c['d']['A'],c['d']['B'],-r*.001);_,Gr=e.transition(c['d']['A'],c['d']['B'],r*.001)
 ns=4*(q+1);nu=q+1;nc=len(Ac);n=ns+nu+nc;Y=np.zeros((len(C),n));Y[:,4*q:4*q+4]=C@Fm;Y[:,ns+q:ns+q+1]=-C@Fm@Gr
 U=-Dc@Y
 if nc:U[:,-nc:]-=Cc
 M=np.zeros((n,n));M[:4,:4]=F;M[:4]+=G@U
 if q:M[4:ns,:ns-4]=np.eye(ns-4)
 M[ns:ns+1]=U
 if q:M[ns+1:ns+nu,ns:ns+nu-1]=np.eye(q)
 if nc:M[-nc:]=Bc@Y;M[-nc:,-nc:]+=Ac
 return M

def main():
 configs=json.loads((e.OUT/'results/selected_configurations.json').read_text());rows=[];crossings=[];tests=[]
 for model in ['point','rod']:
  for raw in configs[model]:
   c=restore(raw);label=c['label']
   if c['kind']=='PRED':
    rows.append(dict(model=model,label=label,phase_margin_deg=np.nan,crossover_rad_s=np.nan,PM_delay_ms=np.nan,linear_boundary_ms=np.nan,note='Controller depends on delay; fixed-loop PM division is inapplicable.'));continue
   Ac,Bc,Cc,Dc,C=e.feedback_ss(c);d=c['d'];plant=control.ss(d['F'],d['G'],C,np.zeros((len(C),1)),e.TS)
   loop=control.ss(Ac,Bc,Cc,Dc,e.TS)*plant if len(Ac) else control.ss(d['F'],d['G'],Dc@C,0,e.TS)
   freq=np.geomspace(1e-4,np.pi/e.TS*.999999,10000);gm,pm,sm,wpc,wgc,wms=control.stability_margins(control.frd(loop,freq),returnall=True)
   candidates=[]
   for phi,w in zip(pm,wgc):
    val=float(np.deg2rad(phi)/w*1000);crossings.append(dict(model=model,label=label,phase_margin_deg=phi,crossover_rad_s=w,PM_delay_ms=val))
    if phi>0:candidates.append((val,phi,w))
   if candidates:pred,phi,w=min(candidates)
   else:pred=phi=w=np.nan
   radius=lambda delay:float(max(abs(np.linalg.eigvals(lifted(c,delay)))))
   rz=radius(0);stable=rz<1;closed=control.feedback(loop,1);independent=float(max(abs(control.poles(closed))));assert abs(rz-independent)<1e-5
   if stable:
    lo=0;hi=10
    while radius(hi)<1 and hi<500:lo=hi;hi+=10
    if hi<500:
     while hi-lo>1:
      mid=(lo+hi)//2
      if radius(mid)<1:lo=mid
      else:hi=mid
     exact=(lo+hi)/2
    else:exact=np.nan
   else:lo=hi=0;exact=0.
   rows.append(dict(model=model,label=label,phase_margin_deg=phi,crossover_rad_s=w,PM_delay_ms=pred,linear_boundary_ms=exact,linear_lower_ms=lo,linear_upper_ms=hi,zero_delay_radius=rz,note='Exact fractional measurement delay with held actuator input; 1 ms bracket.'))
   tests.append(dict(model=model,label=label,lifted_vs_independent_radius_error=abs(rz-independent)))
   print('Margins',model,label,'PM/w',round(pred,2),'lifted',exact,flush=True)
 pd.DataFrame(rows).to_csv(e.OUT/'results/delay_margins.csv',index=False);pd.DataFrame(crossings).to_csv(e.OUT/'results/all_gain_crossings.csv',index=False);pd.DataFrame(tests).to_csv(e.OUT/'results/margin_checks.csv',index=False)
if __name__=='__main__':main()
