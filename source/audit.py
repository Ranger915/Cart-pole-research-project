import engine as e
from boundaries import restore,crossing
from margins import lifted
import numpy as np,pandas as pd,json
from scipy.stats import binomtest

def main():
 checks=[]
 def check(name,value,limit):
  assert np.isfinite(value) and value<=limit,(name,value,limit)
  checks.append(dict(name=name,value=float(value),limit=float(limit),passed=True))
 configs=json.loads((e.OUT/'results/selected_configurations.json').read_text())
 boundaries=pd.read_csv(e.OUT/'results/survival_boundaries.csv')
 assert len(boundaries)==56
 for model in ['point','rod']:
  archive=np.load(e.OUT/'results'/f'heldout_success_{model}.npz')
  for row in boundaries[boundaries.model==model].itertuples():
   if row.status!='interior':continue
   lo,hi=int(row.bracket_low_ms),int(row.bracket_high_ms);assert hi-lo==1
   assert archive[f'{row.label}|{row.push_N}|{lo}'].mean()>=.5 and archive[f'{row.label}|{row.push_N}|{hi}'].mean()<.5
   assert lo-1e-12<=row.D50_ms<=hi+1e-12
   ds=sorted(int(k.split('|')[2]) for k in archive.files if k.startswith(f'{row.label}|{row.push_N}|'))
   first=next(d for d in ds if archive[f'{row.label}|{row.push_N}|{d}'].mean()<.5);assert first==hi
   check(model+' '+row.label+f' {row.push_N}N first crossing bracket width',hi-lo,1.)
 for model,rho in [('point',0.),('rod',1/3)]:
  for power in range(-6,9):
   sweep=e.design(rho,10.**power);check(model+f' all Riccati residuals sigma 1e{power}',max(sweep['residuals'].values()),1e-6)
  d=e.design(rho);z=np.zeros((1,4));p=np.array([[1.],[.1],[.5],[.1]])
  eps=1e-6;A=np.column_stack([(e.rhs(z+np.eye(4)[j]*eps,0,p,rho)-e.rhs(z-np.eye(4)[j]*eps,0,p,rho))[0]/(2*eps) for j in range(4)]);B=((e.rhs(z,eps,p,rho)-e.rhs(z,-eps,p,rho))/(2*eps)).T
  check(model+' nonlinear Jacobian A',np.max(abs(A-d['A'])),1e-8);check(model+' nonlinear Jacobian B',np.max(abs(B-d['B'])),1e-8)
  def integrate(dt):
   zz=np.array([[0.,0.,.1,0.]]);u=0.
   for i in range(round(4/dt)):
    if i%round(e.TS/dt)==0:u=float(np.clip(-(zz@d['Kd'].T)[0,0],-10,10))
    zz=e.rk(zz,u+(5 if 2<=i*dt<2.1 else 0),p,rho,dt)
   return zz
  check(model+' RK4 step halving',np.max(abs(integrate(.001)-integrate(.0005))),1e-7)
  correct=e.design(rho);old=e.design(rho,100,'legacy');check(model+' covariance units ratio identity',np.max(abs(correct['H']-old['H']))/np.max(abs(correct['H'])),1e-9)
  a=e.config('a','DKF',d);b=e.config('b','PRED',d)
  _,tr=e.simulate(rho,[dict(config=a,delay=0,push=5),dict(config=b,delay=0,push=5)],8,horizon=3,record=True)
  check(model+' predictor zero delay equality',np.max(abs(tr[:,:8,1:]-tr[:,8:,1:])),1e-8)
  cases=[dict(config=b,delay=delay,push=0,noisy=False,uncertain=False) for delay in [0,1,9,10,37,60,115]]
  _,tr=e.simulate(rho,cases,1,horizon=3,record=True,linear=True)
  check(model+' predictor fractional perfect model equality',max(np.max(abs(tr[:,0,1:]-tr[:,j,1:])) for j in range(1,len(cases))),1e-8)
  # Random command history independently integrated in chronological order.
  rng=np.random.default_rng(20261127);commands=rng.normal(size=20);x=rng.normal(size=4)
  for delay in [1,9,10,37,60,115]:
   q,r=divmod(delay,10);tau=delay*.001;Fr,Gr=e.transition(d['A'],d['B'],r*.001);Ft,_=e.transition(d['A'],d['B'],tau);chron=x.copy()
   if r:chron=Fr@chron+Gr[:,0]*commands[-q-1]
   for h in range(q,0,-1):chron=d['F']@chron+d['G'][:,0]*commands[-h]
   conv=Ft@x
   for h in range(q):conv+=np.linalg.matrix_power(d['F'],h)@d['G'][:,0]*commands[-1-h]
   if r:conv+=np.linalg.matrix_power(d['F'],q)@Gr[:,0]*commands[-q-1]
   check(model+f' fractional input convolution {delay} ms',max(abs(conv-chron)),1e-10)
  for raw in configs[model]:
   c=restore(raw)
   if c['kind']=='PRED':continue
   check(model+' '+c['label']+' nominal closed loop radius',max(abs(np.linalg.eigvals(lifted(c,0)))),1.)
  # Case order and batch size must not change common random numbers.
  c=restore(configs[model][9]);one,_=e.simulate(rho,[dict(config=c,delay=37,push=5)],8,horizon=1)
  two,_=e.simulate(rho,[dict(config=c,delay=60,push=10),dict(config=c,delay=37,push=5)],8,horizon=1)
  for key in ['success','dwell','rms_active','rms_full','peak']:check(model+' CRN batch invariance '+key,np.max(abs(one[key][0].astype(float)-two[key][1].astype(float))),1e-10)
  stopped=[dict(config=restore(configs[model][2]),delay=200,push=10)]
  aa,_=e.simulate(rho,stopped,8,horizon=3,active_only=False);bb,_=e.simulate(rho,stopped,8,horizon=3,active_only=True)
  for key in ['success','dwell','rms_active','rms_full','peak','failure_time']:check(model+' inactive trajectory optimization '+key,np.max(abs(np.nan_to_num(aa[key].astype(float))-np.nan_to_num(bb[key].astype(float)))),1e-12)
 check('crossing interpolation',abs(crossing(np.array([0,1,2]),np.array([1.,.6,.4]))-1.5),1e-12)
 margins=pd.read_csv(e.OUT/'results/delay_margins.csv');v=margins.dropna(subset=['PM_delay_ms','linear_boundary_ms']);checks.append(dict(name='PM over crossover versus exact fractional lift maximum difference ms',value=float(max(abs(v.PM_delay_ms-v.linear_boundary_ms))),limit=None,passed=True))
 from scipy.stats import spearmanr
 comparison=pd.read_csv(e.OUT/'results/survival_boundaries.csv').merge(margins,on=['model','label']);validation=[]
 for (model,push),part in comparison.groupby(['model','push_N']):
  for key in ['PM_delay_ms','linear_boundary_ms']:
   z=part.dropna(subset=[key,'D50_ms']);validation.append(dict(model=model,push_N=push,prediction=key,configurations=len(z),median_absolute_error_ms=float(np.median(abs(z[key]-z.D50_ms))),spearman_rho=float(spearmanr(z[key],z.D50_ms).statistic),note='Descriptive association across correlated listed configurations; no independence-based significance claim.'))
 pd.DataFrame(validation).to_csv(e.OUT/'results/margin_survival_validation.csv',index=False)
 # Fixed reference cells support paired intervention effects, not retuning.
 pairs=[('FD-reference','FD-fixed'),('FD-fixed','FD-redesign'),('C-legacy-units','C-correct-units'),('C-correct-units','C-causal-base'),('C-causal-base','KF-LQR-base'),('KF-LQR-base','dLQG-base'),('dLQG-base','dLQG-w'),('dLQG-base','delay-aware-base'),('dLQG-w','delay-aware-tuned')];rows=[]
 for model in ['point','rod']:
  data=np.load(e.OUT/'results'/f'heldout_success_{model}.npz');labels=[c['label'] for c in configs[model]]
  for pa,pb in pairs:
   la=next(l for l in labels if l.startswith(pa));lb=next(l for l in labels if l.startswith(pb))
   for push in [5,10]:
    for delay in [0,40,60]:
     a=data[f'{la}|{push}|{delay}'];b=data[f'{lb}|{push}|{delay}'];diff=b.astype(float)-a.astype(float);rng=np.random.default_rng(20261128);bs=[np.mean(diff[rng.integers(0,len(a),len(a))]) for _ in range(2000)];lo,hi=np.quantile(bs,[.025,.975]);up=int(np.sum(~a&b));down=int(np.sum(a&~b));pv=binomtest(up,up+down,.5).pvalue if up+down else 1.
     rows.append(dict(model=model,a=la,b=lb,push_N=push,delay_ms=delay,difference=float(diff.mean()),low=lo,high=hi,pvalue=pv,improved=up,worsened=down,N=len(a)))
 order=np.argsort([r['pvalue'] for r in rows]);running=0.
 for rank,j in enumerate(order):running=max(running,(len(rows)-rank)*rows[j]['pvalue']);rows[j]['holm_pvalue']=min(1.,running)
 pd.DataFrame(rows).to_csv(e.OUT/'results/paired_interventions.csv',index=False)
 (e.OUT/'results/revision_checks.json').write_text(json.dumps(checks,indent=2));print('Revision checks passed',len(checks),flush=True)
if __name__=='__main__':main()
