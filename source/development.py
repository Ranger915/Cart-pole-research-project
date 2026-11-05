import engine as e
import numpy as np,pandas as pd,json
ALPHAS=[0.,.1,.2,.4,.6,.8,.9,.95,.98]
TASKS=[(0,5),(40,5),(60,5),(0,10),(60,10)]
def serialize(x):
 if isinstance(x,np.ndarray):return x.tolist()
 if isinstance(x,np.generic):return x.item()
 raise TypeError(type(x).__name__)
def case(c,d,p):return dict(config=c,delay=d,push=p)
def get_rows(model,configs,out,metadata):
 rows=[]
 for j,(c,extra) in enumerate(zip(configs,metadata)):
  for k,(delay,push) in enumerate(TASKS):rows.append(dict(model=model,label=c['label'],kind=c['kind'],delay_ms=delay,push_N=push,**extra,**e.summary(out,j*len(TASKS)+k)))
 return rows
def objective(rows):
 return (np.mean([r['success'] for r in rows]),np.mean([r['dwell'] for r in rows]),-np.mean([r['rms_active'] for r in rows]))
def main():
 allrows=[];selection={};audit={};configs_dump={}
 for model,rho in [('point',0.),('rod',1/3)]:
  base=e.design(rho);legacy=e.design(rho,continuous_units='legacy')
  old100=e.design(rho,scale=100,continuous_units='legacy');err=float(np.max(abs(base['H']-old100['H']))/np.max(abs(base['H'])));assert err<1e-9
  # Numerical invariants for the timestamp-aware predictor.
  a=e.config('dLQG','DKF',base);b=e.config('predictor','PRED',base)
  out,tr=e.simulate(rho,[dict(config=a,delay=0,push=5),dict(config=b,delay=0,push=5)],ntrial=8,horizon=3,record=True)
  zero=float(np.max(abs(tr[:,:8,1:]-tr[:,8:,1:])));assert zero<1e-8
  cases=[dict(config=b,delay=delay,push=0,noisy=False,uncertain=False) for delay in [0,37,60,115]]
  out,tr=e.simulate(rho,cases,ntrial=1,horizon=3,record=True,linear=True)
  perfect=max(float(np.max(abs(tr[:,0,1:]-tr[:,j,1:]))) for j in range(1,4));assert perfect<1e-8
  audit[model]=dict(unit_ratio_identity_relative_error=err,predictor_zero_delay_error=zero,predictor_perfect_model_delay_equivalence_error=perfect)
  checkpoint=e.OUT/'results'/f'development_fd_{model}.json'
  fdconfigs=[];meta=[];gainrows=[]
  for alpha in ALPHAS:
   c=e.config('FD-fixed-a'+str(alpha),'FD',base,alpha=alpha);fdconfigs.append(c);meta.append(dict(family='FD-fixed',alpha=alpha,scale=1.))
   K,opt=e.redesign_fd(base,alpha);gainrows.append(dict(alpha=alpha,K=K.tolist(),**opt))
   if opt['stable']:
    fdconfigs.append(e.config('FD-redesign-a'+str(alpha),'FD',base,alpha=alpha,K=K));meta.append(dict(family='FD-redesign',alpha=alpha,scale=1.))
  print('Develop FD sweep',model,len(fdconfigs),flush=True)
  out,_=e.simulate(rho,[case(c,d,p) for c in fdconfigs for d,p in TASKS],ntrial=200,seed=20261121)
  fdrows=get_rows(model,fdconfigs,out,meta);allrows+=fdrows
  checkpoint.write_text(json.dumps(dict(rows=fdrows,gains=gainrows),default=serialize,indent=2))
  choose={}
  for family in ['FD-fixed','FD-redesign']:
   candidates=[c for c,m in zip(fdconfigs,meta) if m['family']==family]
   choose[family]=max(candidates,key=lambda c:objective([r for r in fdrows if r['label']==c['label']]))
  # Broad covariance-ratio sweep. High-end convergence is distinguished from
  # a finite peak; no claim that a ceiling point is an unconstrained optimum.
  observer_configs=[];observer_meta=[]
  for power in range(-6,9):
   scale=10.**power;d=e.design(rho,scale=scale)
   for family,kind in [('C-causal','C-causal'),('dLQG','DKF')]:
    observer_configs.append(e.config(f'{family}-w{power}',kind,d));observer_meta.append(dict(family=family,alpha=np.nan,scale=scale))
  print('Develop covariance sweep',model,len(observer_configs),flush=True)
  out,_=e.simulate(rho,[case(c,d,p) for c in observer_configs for d,p in TASKS],ntrial=200,seed=20261121)
  obsrows=get_rows(model,observer_configs,out,observer_meta);allrows+=obsrows
  for family in ['C-causal','dLQG']:
   candidates=[c for c,m in zip(observer_configs,observer_meta) if m['family']==family]
   choose[family]=max(candidates,key=lambda c:objective([r for r in obsrows if r['label']==c['label']]))
   scores=[objective([r for r in obsrows if r['label']==c['label']]) for c in candidates]
   gainchange=float(np.linalg.norm(candidates[-1]['d']['L']-candidates[-2]['d']['L'])/np.linalg.norm(candidates[-1]['d']['L'])) if family=='dLQG' else float(np.linalg.norm(candidates[-1]['d']['H']-candidates[-2]['d']['H'])/np.linalg.norm(candidates[-1]['d']['H']))
   audit[model][family+'_sweep']=dict(selected_label=choose[family]['label'],selected_scale=choose[family]['d']['scale'],highest_power=8,high_end_gain_relative_change=gainchange,development_score_at_high_end=list(scores[-1]),best_development_score=list(max(scores)),finite_peak_bracketed=bool(max(scores[:-1])>scores[-1]),note='If the discrete gain converges and survival plateaus, the optimum is not identified as a unique finite multiplier. All settings are retained.')
  # Primary held-out boundaries plus diagnostics isolating the old unit error.
  kx,kv,ka,kw=(.1,.2,60.,12.) if model=='point' else (.1,.2,60.,18.)
  primary=[e.config('PD-reference','PD',base,K=-np.array([[ka*kx,ka*kv,ka,kw]])),e.config('LQR-oracle','STATE',base),e.config('FD-reference','FD',base),choose['FD-fixed'],choose['FD-redesign'],e.config('C-legacy-units','C-current',legacy),e.config('C-correct-units','C-current',base),e.config('C-causal-base','C-causal',base),choose['C-causal'],e.config('dLQG-base','DKF',base),choose['dLQG'],e.config('delay-aware-base','PRED',base)]
  primary.append(e.config('delay-aware-tuned','PRED',choose['dLQG']['d']))
  primary.append(e.config('KF-LQR-base','KF',base))
  # Deduplicate exact reference/tuning coincidences without losing names.
  selection[model]={family:dict(label=c['label'],alpha=c['alpha'],scale=c['d']['scale'],K=c['K'].tolist()) for family,c in choose.items()}
  configs_dump[model]=primary
  (e.OUT/'results'/f'fd_redesign_{model}.json').write_text(json.dumps(gainrows,default=serialize,indent=2))
 pd.DataFrame(allrows).to_csv(e.OUT/'results/development_sweeps.csv',index=False)
 (e.OUT/'results/selected_configurations.json').write_text(json.dumps(configs_dump,default=serialize,indent=2))
 (e.OUT/'results/selection.json').write_text(json.dumps(selection,default=serialize,indent=2));(e.OUT/'results/implementation_checks.json').write_text(json.dumps(audit,default=serialize,indent=2))
 print('Development complete',flush=True)
if __name__=='__main__':main()
