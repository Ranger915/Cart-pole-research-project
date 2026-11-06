"""Trial-paired sensitivity to uniformly randomized 0--9 ms push onset phase."""
import engine as e
from boundaries import restore
import numpy as np,pandas as pd,json

def main():
 n=500;seed=20261122;phase_seed=20261106
 phases=np.random.default_rng(phase_seed).integers(0,10,n)
 pd.DataFrame(dict(trial=np.arange(n),push_phase_ms=phases)).to_csv(e.OUT/'results/push_phase_assignments.csv',index=False)
 # Changing the pulse to integer time must preserve every original zero-phase step.
 assert all((2<=i*e.DT<2.1)==(2000<=i<2100) for i in range(10000))
 configs=json.loads((e.OUT/'results/selected_configurations.json').read_text());bd=pd.read_csv(e.OUT/'results/survival_boundaries.csv');summaries=[];raw={};checks=[]
 oldsummary=pd.read_csv(e.OUT/'results/heldout_summary.csv')
 for model,rho in [('point',0.),('rod',1/3)]:
  cs={c['label']:restore(c) for c in configs[model]};archive=np.load(e.OUT/'results'/f'heldout_success_{model}.npz');specs=[]
  for row in bd[bd.model==model].itertuples():
   lo,hi=int(row.bracket_low_ms),int(row.bracket_high_ms)
   for delay in sorted(set([max(0,lo-3),lo,hi,hi+3,60])):specs.append((row.label,int(row.push_N),delay))
  checkpoint=e.OUT/'results'/f'phase_checkpoint_{model}.npz';cache=dict(np.load(checkpoint)) if checkpoint.exists() else {}
  for start in range(0,len(specs),4):
   batch=[s for s in specs[start:start+4] if f'{s[0]}|{s[1]}|{s[2]}|fixed' not in cache]
   if not batch:continue
   cases=[dict(config=cs[label],push=push,delay=delay,push_phase_ms=phase) for label,push,delay in batch for phase in [np.zeros(n,int),phases]]
   out,_=e.simulate(rho,cases,ntrial=n,seed=seed)
   for j,(label,push,delay) in enumerate(batch):
    for index,phase in [(2*j,'fixed'),(2*j+1,'random')]:
     key=f'{label}|{push}|{delay}|{phase}'
     for metric in ['success','dwell','rms_active','rms_full','saturation_active']:cache[key+'|'+metric]=out[metric][index]
     cache[key]=out['success'][index]
   np.savez_compressed(checkpoint,**cache);print(model,'phase cases completed',min(start+4,len(specs)),'of',len(specs),flush=True)
  for label,push,delay in specs:
   key=f'{label}|{push}|{delay}';a=cache[key+'|fixed'];b=cache[key+'|random']
   if key in archive.files:
    assert np.array_equal(a,archive[key]),key
    checks.append(dict(model=model,label=label,push_N=push,delay_ms=delay,zero_phase_matches_original=True))
   diff=b.astype(float)-a.astype(float);rng=np.random.default_rng(20261107);bs=[np.mean(diff[rng.integers(0,n,n)]) for _ in range(2000)];low,high=np.quantile(bs,[.025,.975])
   item=dict(model=model,label=label,push_N=push,delay_ms=delay,N=n,fixed_success=float(a.mean()),random_success=float(b.mean()),difference=float(diff.mean()),low=float(low),high=float(high),original_bracket=bool(delay in [int(bd[(bd.model==model)&(bd.label==label)&(bd.push_N==push)].iloc[0].bracket_low_ms),int(bd[(bd.model==model)&(bd.label==label)&(bd.push_N==push)].iloc[0].bracket_high_ms)]))
   for phase in ['fixed','random']:
    for metric in ['dwell','rms_active','rms_full','saturation_active']:item[phase+'_'+metric]=float(cache[key+'|'+phase+'|'+metric].mean())
   summaries.append(item)
  raw.update({model+'|'+k:v for k,v in cache.items()})
 pd.DataFrame(summaries).to_csv(e.OUT/'results/push_phase_summary.csv',index=False);np.savez_compressed(e.OUT/'results/push_phase_trials.npz',**raw)
 report=dict(trials_per_cell=n,measurement_parameter_seed=seed,phase_seed=phase_seed,bootstrap_seed=20261107,cells=len(summaries),trajectories=2*n*len(summaries),phase_counts=np.bincount(phases,minlength=10).tolist(),checks=checks,all_zero_phase_matches=True)
 (e.OUT/'results/push_phase_checks.json').write_text(json.dumps(report,indent=2));print('Phase sensitivity complete',report['trajectories'],'trajectories',flush=True)
if __name__=='__main__':main()
