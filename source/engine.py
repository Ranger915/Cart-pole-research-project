"""Corrected bandwidth, timestamp and delay-prediction experiments."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import sys,copy,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent if HERE.name=='source' else HERE.parents[1];OUT=ROOT if HERE.name=='source' else ROOT/'outputs/ieee_revision'
for p in ['results','figures','source']: (OUT/p).mkdir(parents=True,exist_ok=True)
import numpy as np
from scipy.linalg import solve_continuous_are,solve_discrete_are,solve_discrete_lyapunov,expm
from scipy.optimize import minimize
DT=.001;TS=.01
C=np.array([[1.,0,0,0],[0,0,1.,0]])
RMEAS=np.diag([.005**2,.002**2]);W=np.diag([1e-6,.04,1e-6,.04])
def rhs(z,u,p,rho):
 M,m,l,b=p;v,t,w=z[:,1],z[:,2],z[:,3];J=(1+rho)*m*l*l;cross=m*l*np.cos(t);den=(M+m)*J-cross*cross
 force=u-b*v+m*l*w*w*np.sin(t);grav=m*9.81*l*np.sin(t)
 return np.column_stack((v,(J*force-cross*grav)/den,w,((M+m)*grav-cross*force)/den))
def rk(z,u,p,rho,dt=DT):
 a=rhs(z,u,p,rho);b=rhs(z+dt*a/2,u,p,rho);c=rhs(z+dt*b/2,u,p,rho);d=rhs(z+dt*c,u,p,rho)
 return z+dt*(a+2*b+2*c+d)/6
def model(rho):
 M=1.;m=.1;l=.5;b=.1;J=(1+rho)*m*l*l;den=(M+m)*J-m*m*l*l
 A=np.array([[0,1,0,0],[0,-b*J/den,-m*m*9.81*l*l/den,0],[0,0,0,1],[0,b*m*l/den,(M+m)*m*9.81*l/den,0]])
 return A,np.array([[0.],[J/den],[0.],[-m*l/den]])
def transition(A,B,seconds):
 E=np.zeros((5,5));E[:4,:4]=A;E[:4,4:]=B;E=expm(E*seconds);return E[:4,:4],E[:4,4:]
def process(A,W,seconds):
 E=expm(np.block([[A,W],[np.zeros((4,4)),-A.T]])*seconds);return E[:4,4:]@E[:4,:4].T
def design(rho,scale=1.,continuous_units='correct'):
 A,B=model(rho);Q=np.diag([1.,1.,25.,1.]);R=np.array([[.01]])
 P=solve_continuous_are(A,B,Q,R);K=np.linalg.solve(R,B.T@P);F,G=transition(A,B,TS);Qd=process(A,W*scale,TS)
 # Common covariance scaling preserves the gain and avoids large DARE norms.
 normal=max(np.linalg.norm(Qd),np.linalg.norm(RMEAS));Pp=solve_discrete_are(F.T,C.T,Qd/normal,RMEAS/normal)*normal
 L=Pp@C.T@np.linalg.inv(C@Pp@C.T+RMEAS)
 Pd=solve_discrete_are(F,G,Q*TS,R*TS);Kd=np.linalg.solve(R*TS+G.T@Pd@G,G.T@Pd@F)
 rc=A.T@P+P@A-P@B@np.linalg.inv(R)@B.T@P+Q
 rd=Pd-F.T@Pd@F+F.T@Pd@G@Kd-Q*TS
 rf=Pp-F@Pp@F.T-Qd+F@Pp@C.T@np.linalg.inv(C@Pp@C.T+RMEAS)@C@Pp@F.T
 residuals=dict(control_care=float(np.linalg.norm(rc)/(np.linalg.norm(P)+np.linalg.norm(Q))),control_dare=float(np.linalg.norm(rd)/(np.linalg.norm(Pd)+np.linalg.norm(Q*TS))),filter_dare=float(np.linalg.norm(rf)/(np.linalg.norm(Pp)+np.linalg.norm(Qd))))
 assert max(residuals.values())<1e-6
 assert max(abs(np.linalg.eigvals(F-G@Kd)))<1 and max(abs(np.linalg.eigvals((np.eye(4)-L@C)@F)))<1
 V=RMEAS*(TS if continuous_units=='correct' else 1.)
 Pc=None
 for time_scale in [max(1.,np.sqrt(scale)),1.,max(1.,scale**.25)]:
  common=max(np.linalg.norm(W*scale/time_scale**2),np.linalg.norm(V))
  for balanced in [True,False]:
   try:
    candidate=solve_continuous_are(A.T/time_scale,C.T,W*scale/(time_scale**2*common),V/common,balanced=balanced)*common*time_scale
    residual=A@candidate+candidate@A.T-candidate@C.T@np.linalg.inv(V)@C@candidate+W*scale
    if np.linalg.norm(residual)/max(1e-30,np.linalg.norm(W*scale)+np.linalg.norm(A@candidate))<1e-6 and max(np.real(np.linalg.eigvals(A-candidate@C.T@np.linalg.inv(V)@C)))<0:Pc=candidate;break
   except (ValueError,np.linalg.LinAlgError):pass
  if Pc is not None:break
 if Pc is None:raise ArithmeticError(('continuous CARE failed',rho,scale))
 H=Pc@C.T@np.linalg.inv(V)
 residual=A@Pc+Pc@A.T-Pc@C.T@np.linalg.inv(V)@C@Pc+W*scale
 assert np.linalg.norm(residual)/max(1e-30,np.linalg.norm(W*scale)+np.linalg.norm(A@Pc))<1e-6
 residuals['observer_care']=float(np.linalg.norm(residual)/max(1e-30,np.linalg.norm(W*scale)+np.linalg.norm(A@Pc)))
 O=np.zeros((7,7));O[:4,:4]=A-H@C;O[:4,4:5]=B;O[:4,5:]=H;O=expm(O*TS)
 return dict(A=A,B=B,Q=Q,R=R,K=K,Kd=Kd,F=F,G=G,Qd=Qd,L=L,Pp=Pp,H=H,O=O,scale=float(scale),units=continuous_units,residuals=residuals)
def config(label,kind,d,alpha=.8,K=None):
 return dict(label=label,kind=kind,d=d,alpha=float(alpha),K=d['Kd'].copy() if kind in ['DKF','PRED'] else d['K'].copy() if K is None else np.asarray(K).reshape(1,4))
def feedback_ss(c):
 d=c['d'];K=c['K'];kind=c['kind'];a=c['alpha'];ny=4 if kind=='STATE' else 2
 if kind=='STATE':return np.empty((0,0)),np.empty((0,4)),np.empty((1,0)),K,np.eye(4)
 if kind in ['FD','PD']:
  ky=K[:,[0,2]];kv=K[:,[1,3]];beta=(1-a)/TS
  return a*np.eye(2),np.eye(2),kv*beta*(a-1),ky+kv*beta,C
 if kind in ['C-current','C-causal']:
  Ac=d['O'][:4,:4]-d['O'][:4,4:5]@K;Lc=d['O'][:4,5:]
  if kind=='C-causal':return Ac,Lc,K,np.zeros((1,2)),C
 else:Ac=(np.eye(4)-d['L']@C)@(d['F']-d['G']@K);Lc=d['L']
 return Ac,Lc,K@Ac,K@Lc,C
def redesign_fd(d,alpha):
 """Local static output-feedback H2 redesign including the actual FD filter."""
 F,G,Q,R=d['F'],d['G'],d['Q'],d['R'];b=1-alpha
 Ag=np.block([[F,np.zeros((4,2))],[b*C,alpha*np.eye(2)]]);Bg=np.vstack([G,np.zeros((2,1))]);Cy=np.block([[C,np.zeros((2,2))],[np.zeros((2,4)),np.eye(2)]])
 Qg=np.zeros((6,6));Qg[:4,:4]=Q*TS;x0=np.r_[0.,0.,.1,0.,0.,.1];base=d['K'].ravel()
 def cost(logs):
  K=(base*np.exp(logs)).reshape(1,4);ky=K[:,[0,2]]+K[:,[1,3]]*b/TS;kh=-K[:,[1,3]]*b/TS;Ko=np.hstack([ky,kh]);Acl=Ag-Bg@Ko@Cy
  radius=max(abs(np.linalg.eigvals(Acl)))
  if radius>=1:return 1e8+1e6*(radius-1)
  Qcl=Qg+(Ko@Cy).T@R@(Ko@Cy)*TS;P=solve_discrete_lyapunov(Acl.T,Qcl)
  Bn=np.vstack([-G@ky,b*np.eye(2)]);S=solve_discrete_lyapunov(Acl,Bn@RMEAS@Bn.T)
  # Regulation transient plus a 10 s stationary noise H2 surrogate.
  return float(x0@P@x0+1000*(np.trace(Qcl@S)+float((R@ky@RMEAS@ky.T)[0,0])*TS))
 rng=np.random.default_rng(20261120);starts=np.vstack([np.zeros(4),rng.uniform(-2,2,(120,4))]);scores=np.array([cost(x) for x in starts]);best=None
 for idx in np.argsort(scores)[:3]:
  opt=minimize(cost,starts[idx],method='Powell',bounds=[(-2.3,2.3)]*4,options={'maxiter':250,'xtol':1e-6,'ftol':1e-7})
  if best is None or opt.fun<best.fun:best=opt
 K=(base*np.exp(best.x)).reshape(1,4)
 return K,dict(surrogate_cost=float(best.fun),stable=bool(best.fun<1e8),optimizer_success=bool(best.success),log_gain_multipliers=best.x.tolist())
def simulate(rho,cases,ntrial=200,seed=20261121,horizon=10,record=False,linear=False,active_only=True):
 """Cases contain config, integer-ms delay and push; random draws are trial-paired
 independently of the number/order of cases or separate simulation calls."""
 nc=len(cases);n=nc*ntrial;rng=np.random.default_rng(seed);parbase=rng.uniform(.8,1.2,(4,ntrial));p=np.tile(np.array([1.,.1,.5,.1])[:,None]*parbase,(1,nc))
 for j,case in enumerate(cases):
  if not case.get('uncertain',True):p[:,j*ntrial:(j+1)*ntrial]=np.array([1.,.1,.5,.1])[:,None]
 delay=np.repeat([int(c['delay']) for c in cases],ntrial);limits=np.repeat([c.get('umax',10.) for c in cases],ntrial);push=np.repeat([c.get('push',5.) for c in cases],ntrial)
 z=np.zeros((n,4));z[:,2]=.1;z0=z.copy();est=z.copy();held=z[:,[0,2]].copy();fdprev=held.copy();vel=np.zeros((n,2));cmd=np.zeros(n)
 maxdelay=int(max(delay));hist=np.zeros((maxdelay+1,n,4));hist[0]=z;uh=np.zeros((maxdelay//10+4,n));u0=np.zeros(n)
 stale=[z0[j*ntrial:(j+1)*ntrial].copy() for j in range(nc)];cov=[c['config']['d']['Pp'].copy() for c in cases];started=np.zeros(nc,bool)
 fail=np.zeros(n,bool);ftime=np.full(n,np.nan);peak=np.full(n,.1);active=np.zeros(n);squared=np.zeros(n);sqactive=np.zeros(n);saturation=np.zeros(n);lastout=np.zeros(n);trace=[]
 coeff=[]
 for case in cases:
  d=case['config']['d'];q,r=divmod(case['delay'],10);Fr,Gr=transition(d['A'],d['B'],r*.001);Frest,Grest=transition(d['A'],d['B'],TS-r*.001)
  Ft,Gt=transition(d['A'],d['B'],case['delay']*.001);powers=[np.linalg.matrix_power(d['F'],i) for i in range(q+1)]
  coeff.append((q,r,Fr,Gr,Frest,Grest,Ft,powers,process(d['A'],W*d['scale'],r*.001)))
 steps=round(horizon/DT)
 for i in range(steps):
  t=i*DT
  if i%10==0:
   k=i//10;noise=rng.normal(size=(ntrial,2))*np.sqrt(np.diag(RMEAS));oldcmd=cmd.copy()
   state=hist[np.maximum(i-delay,0)%len(hist),np.arange(n)].copy();pos=state[:,[0,2]].copy()
   for j,case in enumerate(cases):
    sl=slice(j*ntrial,(j+1)*ntrial);c=case['config'];d=c['d'];kind=c['kind'];K=c['K'];ms=case['delay'];q,r,Fr,Gr,Frest,Grest,Ftau,powers,Qr=coeff[j]
    # No packet predates experiment initialization; hold the known initial packet.
    if i>=ms and case.get('noisy',True):pos[sl]+=noise
    state[sl,0]=pos[sl,0];state[sl,2]=pos[sl,1]
    if kind=='STATE':fb=state[sl]
    elif kind in ['FD','PD']:
     if k==0:fdprev[sl]=pos[sl]
     a=c['alpha'];vel[sl]=a*vel[sl]+(1-a)*(pos[sl]-fdprev[sl])/TS;fdprev[sl]=pos[sl]
     fb=np.column_stack((pos[sl,0],vel[sl,0],pos[sl,1],vel[sl,1]))
    elif kind in ['C-current','C-causal']:
     measurement=pos[sl] if kind=='C-current' else held[sl]
     if kind=='C-current' or k>0:est[sl]=est[sl]@d['O'][:4,:4].T+oldcmd[sl,None]*d['O'][:4,4]+measurement@d['O'][:4,5:].T
     held[sl]=pos[sl];fb=est[sl]
    elif kind in ['DKF','KF']:
     if k:est[sl]=est[sl]@d['F'].T+oldcmd[sl,None]*d['G'][:,0]
     est[sl]+=(pos[sl]-est[sl][:,[0,2]])@d['L'].T;fb=est[sl]
    elif kind=='PRED':
     def past(index):return uh[index%len(uh),sl] if index>=0 else np.zeros(ntrial)
     if i<ms:
      if k:est[sl]=est[sl]@d['F'].T+oldcmd[sl,None]*d['G'][:,0]
      fb=est[sl]
     else:
      if not started[j]:
       stamp=(i-ms)*.001;Fs,Gs=transition(d['A'],d['B'],stamp);Ps=process(d['A'],W*d['scale'],stamp)
       prior=z0[sl]@Fs.T+u0[sl,None]*Gs[:,0];Pprior=Fs@d['Pp']@Fs.T+Ps;started[j]=True
      else:
       prior=stale[j]@d['F'].T+past(k-q-2)[:,None]*(Frest@Gr)[:,0]+past(k-q-1)[:,None]*Grest[:,0]
       Pprior=d['F']@cov[j]@d['F'].T+d['Qd']
      gain=d['L'] if ms==0 else Pprior@C.T@np.linalg.inv(C@Pprior@C.T+RMEAS)
      stale[j]=prior+(pos[sl]-prior[:,[0,2]])@gain.T;cov[j]=(np.eye(4)-gain@C)@Pprior
      current=stale[j]@Ftau.T
      for h in range(q):current+=past(k-1-h)[:,None]*(powers[h]@d['G'])[:,0]
      if r:current+=past(k-q-1)[:,None]*(powers[q]@Gr)[:,0]
      est[sl]=current;fb=current
    assert np.isfinite(fb).all(),(c['label'],t)
    raw=-np.sum(fb*K,axis=1);cmd[sl]=np.clip(raw,-limits[sl],limits[sl]);cmd[sl][fail[sl]]=0
   uh[k%len(uh)]=cmd
   if k==0:u0=cmd.copy()
  force=cmd+np.where((t>=2)&(t<2.1),push,0)
  if linear:
   A,B=model(rho)
   def f(q):return q@A.T+force[:,None]*B[:,0]
   aa=f(z);bb=f(z+DT*aa/2);cc=f(z+DT*bb/2);dd=f(z+DT*cc);new=z+DT*(aa+2*bb+2*cc+dd)/6
  else:
   if active_only and np.mean(~fail)<.7:
    live=np.flatnonzero(~fail);new=z.copy()
    if len(live):new[live]=rk(z[live],force[live],p[:,live],rho)
   else:new=rk(z,force,p,rho)
  new[fail]=z[fail];z=new
  active_now=~fail;cross=active_now&((abs(z[:,2])>.5)|(abs(z[:,0])>2.4));ftime[cross]=t+DT;fail|=cross
  peak=np.maximum(peak,abs(z[:,2]));active+=active_now;squared+=cmd**2;sqactive+=cmd**2*active_now;saturation+=(abs(cmd)>=limits-1e-10)*active_now
  lastout[(abs(z[:,2])>.002)|(abs(z[:,0])>.02)]=t+DT
  hist[(i+1)%len(hist)]=z
  if record and i%10==0:trace.append(np.column_stack((np.full(n,t+DT),z,cmd)))
 dwell=(~fail)&(lastout<=horizon-1)
 return dict(success=(~fail).reshape(nc,ntrial),dwell=dwell.reshape(nc,ntrial),rms_active=np.sqrt(sqactive/np.maximum(active,1)).reshape(nc,ntrial),rms_full=np.sqrt(squared/steps).reshape(nc,ntrial),saturation_active=(saturation/np.maximum(active,1)).reshape(nc,ntrial),failure_time=ftime.reshape(nc,ntrial),peak=peak.reshape(nc,ntrial)),np.array(trace)
def summary(out,index):
 from scipy.stats import norm
 y=out['success'][index];n=len(y);p=float(y.mean());z=norm.ppf(.975);den=1+z*z/n;mid=(p+z*z/(2*n))/den;half=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
 return dict(N=n,success=p,low=0. if p==0 else mid-half,high=1. if p==1 else mid+half,dwell=float(out['dwell'][index].mean()),rms_active=float(out['rms_active'][index].mean()),rms_full=float(out['rms_full'][index].mean()),saturation=float(out['saturation_active'][index].mean()))
