"""Check plotted cells, reference remapping and the randomized-phase extension."""
import engine as e
import numpy as np,pandas as pd,json

def main():
 d=pd.read_csv(e.OUT/'results/development_sweeps.csv');h=pd.read_csv(e.OUT/'results/heldout_summary.csv');configs=json.loads((e.OUT/'results/selected_configurations.json').read_text());rows=[]
 for model,rho in [('point',0.),('rod',1/3)]:
  base=next(c for c in configs[model] if c['label']=='dLQG-base');fresh=e.design(rho)
  error=max(float(np.max(abs(np.asarray(base['d'][k])-fresh[k]))) for k in ['Kd','F','G','Qd','L']);assert error<1e-10
  for regime,frame in [('development',d[(d.model==model)&(d.family=='dLQG')&(d.scale==1)&(d.delay_ms==60)&(d.push_N==5)]),('held-out',h[(h.model==model)&(h.label=='dLQG-base')&(h.delay_ms==60)&(h.push_N==5)])]:
   assert len(frame)==1;r=frame.iloc[0];count=round(r.N*r.success);assert abs(count/r.N-r.success)<1e-12
   rows.append(dict(model=model,regime=regime,seed=20261121 if regime=='development' else 20261122,N=int(r.N),successes=count,success=float(r.success),low=float(r.low),high=float(r.high),same_design_error=error))
 pd.DataFrame(rows).to_csv(e.OUT/'results/figure2_tableII_audit.csv',index=False)
 phase=pd.read_csv(e.OUT/'results/push_phase_summary.csv');phasecheck=json.loads((e.OUT/'results/push_phase_checks.json').read_text());assert phasecheck['all_zero_phase_matches'] and len(phasecheck['checks'])==len(phase)
 fixed=phase[phase.delay_ms==60];local=phase[phase.delay_ms!=60]
 stats=dict(cells=len(phase),trajectories=phasecheck['trajectories'],zero_phase_matches=len(phasecheck['checks']),max_absolute_change_60ms=float(fixed.difference.abs().max()),max_absolute_change_local=float(local.difference.abs().max()),half_threshold_changes=int(((phase.fixed_success>=.5)!=(phase.random_success>=.5)).sum()),point_base_60_5N=phase[(phase.model=='point')&(phase.label=='dLQG-base')&(phase.delay_ms==60)&(phase.push_N==5)].iloc[0].to_dict(),actual_maximum_delays_ms={model:int(x.delay_ms.max()) for model,x in h.groupby('model')})
 (e.OUT/'results/revision_summary.json').write_text(json.dumps(stats,indent=2));print(json.dumps(stats,indent=2),flush=True)
if __name__=='__main__':main()
