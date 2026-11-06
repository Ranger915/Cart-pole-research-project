import engine as e
from boundaries import restore
import json,shutil,numpy as np,pandas as pd,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':300})
CAP=[]
def save(fig,name,caption):
 fig.savefig(e.OUT/'figures'/f'{name}.png',bbox_inches='tight');fig.savefig(e.OUT/'figures'/f'{name}.pdf',bbox_inches='tight')
 if name in ['fd_sweep','covariance_sweep','margin_validation','local_crossings']:
  for ext in ['png','pdf']:shutil.copyfile(e.OUT/'figures'/f'{name}.{ext}',e.OUT/'figures'/f'{name}_full.{ext}')
 plt.close(fig);CAP.append(dict(name=name,caption=caption))
def short(label):
 if label.startswith('FD-fixed'):return 'FD α selected'
 if label.startswith('FD-redesign'):return 'FD gain redesigned'
 if label.startswith('C-causal-w'):return 'cKF selected'
 if label.startswith('dLQG-w'):return 'dKF selected'
 return {'PD-reference':'PD reference','LQR-oracle':'Velocity oracle','FD-reference':'FD α = 0.8','C-legacy-units':'cKF old units','C-correct-units':'cKF units fixed','C-causal-base':'cKF causal base','dLQG-base':'dKF base','KF-LQR-base':'dKF continuous K','delay-aware-base':'Predictor base','delay-aware-tuned':'Predictor selected'}.get(label,label)

def main():
 dev=pd.read_csv(e.OUT/'results/development_sweeps.csv');sel=json.loads((e.OUT/'results/selection.json').read_text());bd=pd.read_csv(e.OUT/'results/survival_boundaries.csv');held=pd.read_csv(e.OUT/'results/heldout_summary.csv');marg=pd.read_csv(e.OUT/'results/delay_margins.csv')
 fig,axs=plt.subplots(2,3,figsize=(7.1,4.3),sharex=True)
 for i,model in enumerate(['point','rod']):
  for fam,col in [('FD-fixed','#225ea8'),('FD-redesign','#c0392b')]:
   sub=dev[(dev.model==model)&(dev.family==fam)].groupby('alpha')[['success','dwell','rms_active']].mean()
   for j,key in enumerate(['success','dwell','rms_active']):axs[i,j].plot(sub.index,sub[key],'.-',label=fam,color=col)
  for j,key in enumerate(['Mean survival','Mean terminal dwell','Mean active RMS (N)']):axs[i,j].set_title(model.capitalize()+'  '+key,fontsize=8);axs[i,j].grid(alpha=.2)
  axs[i,0].set_ylim(-.03,1.03);axs[i,1].set_ylim(-.03,1.03)
 for ax in axs[-1]:ax.set_xlabel('Filter coefficient α')
 axs[0,0].legend(fontsize=7);fig.tight_layout()
 save(fig,'fd_sweep','Development sweep over nine finite-difference filter coefficients, with fixed continuous LQR gains and a local filter-aware gain redesign. Each point averages five declared tasks and 200 paired trials per task. Tuning uses development data only; no global optimality is asserted.')
 fig,axs=plt.subplots(2,3,figsize=(7.1,4.5),sharex=True)
 for i,model in enumerate(['point','rod']):
  for fam,col in [('C-causal','#c0392b'),('dLQG','#225ea8')]:
   z=dev[(dev.model==model)&(dev.family==fam)]
   for j,(delay,push,key) in enumerate([(60,5,'success'),(0,5,'dwell'),(0,5,'rms_active')]):
    sub=z[(z.delay_ms==delay)&(z.push_N==push)].sort_values('scale');axs[i,j].semilogx(sub.scale,sub[key],'.-',color=col,label=fam)
   for ax in axs[i]:ax.grid(alpha=.2)
  for j,title in enumerate(['60 ms 5 N survival','0 ms 5 N dwell','0 ms 5 N RMS (N)']):axs[i,j].set_title(model.capitalize()+'  '+title,fontsize=8)
  axs[i,0].set_ylim(-.03,1.03);axs[i,1].set_ylim(-.03,1.03)
 axs[0,0].legend(fontsize=7)
 for ax in axs[-1]:ax.set_xlabel('Process covariance multiplier σ')
 fig.tight_layout();save(fig,'covariance_sweep','The unit-correct causal continuous observer and discrete filter are swept from σ = 10⁻⁶ through 10⁸. Survival, dwell and effort expose different preferred noise-versus-lag operating points. High-end survival plateaus do not identify a unique finite optimum.')
 for model in ['point','rod']:
  sub=bd[bd.model==model];labels=list(dict.fromkeys(sub.label));fig,ax=plt.subplots(figsize=(3.55,3.8));yy=np.arange(len(labels))
  for p,off,col in [(5,-.15,'#225ea8'),(10,.15,'#c0392b')]:
   z=sub[sub.push_N==p].set_index('label').loc[labels];v=z.D50_ms.to_numpy();lo=z.low_ms.to_numpy();hi=z.high_ms.to_numpy();ax.errorbar(v,yy+off,xerr=np.vstack([np.maximum(0,v-lo),np.maximum(0,hi-v)]),fmt='o',ms=3,capsize=2,color=col,label=f'{p} N')
   for j,r in enumerate(z.itertuples()):
    if r.status=='below-half-at-zero':ax.plot(0,j+off,'x',color=col)
  ax.set_yticks(yy,[short(l) for l in labels],fontsize=8);ax.invert_yaxis();ax.set_xlabel('First observed crossing (ms)');ax.grid(axis='x',alpha=.2);ax.legend(fontsize=7);ax.set_title(model.capitalize()+' model');fig.tight_layout()
  save(fig,'boundary_'+model,'Held-out '+model+' model first observed downward crossings of 50% ten-second survival for 5 N and 10 N pushes. Bars are 95% trial-paired bootstrap intervals conditional on evaluated delays; local numerical crossing brackets are 1 ms. A cross at zero denotes survival below 50% without added delay. These are not monotone delay limits or stability certificates.')
 fig,axs=plt.subplots(1,2,figsize=(7.1,3.1));joined=bd.merge(marg,on=['model','label'])
 for ax,key,title in zip(axs,['PM_delay_ms','linear_boundary_ms'],['Phase margin divided by crossover','Exact lifted linear boundary']):
  for model,col in [('point','#225ea8'),('rod','#c0392b')]:
   for p,mark in [(5,'o'),(10,'^')]:
    z=joined[(joined.model==model)&(joined.push_N==p)];ax.scatter(z[key],z.D50_ms,s=20,color=col,marker=mark,label=f'{model} {p} N',alpha=.7)
  lim=max(100,float(joined[key].max()),float(joined.D50_ms.max()))*1.05;ax.plot([0,lim],[0,lim],':',color='.4');ax.set_xlim(0,lim);ax.set_ylim(0,lim);ax.set_xlabel(title+' (ms)',fontsize=8);ax.set_ylabel('Nonlinear 50% survival delay (ms)');ax.grid(alpha=.2)
 axs[0].legend(fontsize=7);fig.tight_layout();save(fig,'margin_validation','Local linear delay predictions versus nonlinear ten-second survival boundaries. The diagonal is equality. Delay-aware predictors are omitted because their compensators change with delay. Saturation, uncertainty, push magnitude and finite observation time can separate linear instability from 50% survival.')
 fig,axs=plt.subplots(2,1,figsize=(3.5,4.1),sharey=True)
 names=['C-legacy-units','C-correct-units','C-causal-base','dLQG-base','delay-aware-base']
 for ax,model in zip(axs,['point','rod']):
  for label in names:
   z=held[(held.model==model)&(held.label==label)&(held.push_N==5)&(held.delay_ms.isin([0,40,60]))].sort_values('delay_ms');ax.errorbar(z.delay_ms,z.success,yerr=[z.success-z.low,z.high-z.success],marker='o',ms=3,capsize=2,label=short(label))
  ax.set_title(model.capitalize());ax.set_xlabel('Measurement delay (ms)');ax.grid(alpha=.2);ax.set_ylim(-.03,1.03)
 axs[0].set_ylabel('Survival probability');axs[1].set_ylabel('Survival probability');axs[1].legend(fontsize=6.5,ncol=2);fig.tight_layout();save(fig,'unit_ablation','Paired held-out checks isolate the covariance-unit correction within the legacy update, then enforce causal observer timing and compare delay-unaware and timestamp-aware discrete estimators. Each cell has 500 trials and pointwise Wilson intervals.')
 fig,axs=plt.subplots(2,3,figsize=(7.1,4.2))
 for i,model in enumerate(['point','rod']):
  for j,prefix in enumerate(['FD-reference','dLQG-base','dLQG-w']):
   lab=next(l for l in bd[bd.model==model].label if l.startswith(prefix));ax=axs[i,j]
   for push,col in [(5,'#225ea8'),(10,'#c0392b')]:
    mid=float(bd[(bd.model==model)&(bd.label==lab)&(bd.push_N==push)].iloc[0].D50_ms);z=held[(held.model==model)&(held.label==lab)&(held.push_N==push)&(abs(held.delay_ms-mid)<=7)].sort_values('delay_ms');ax.plot(z.delay_ms-mid,z.success,'.-',color=col,label=f'{push} N');ax.fill_between(z.delay_ms-mid,z.low,z.high,color=col,alpha=.1)
   ax.axhline(.5,color='.4',ls=':');ax.axvline(0,color='.6',ls=':');ax.set_title(model+' '+short(lab),fontsize=8);ax.set_ylim(-.03,1.03);ax.grid(alpha=.15)
 for ax in axs[-1]:ax.set_xlabel('Delay relative to first D50 (ms)')
 for ax in axs[:,0]:ax.set_ylabel('Survival probability')
 axs[0,0].legend(fontsize=7);fig.tight_layout();save(fig,'local_crossings','Local one-millisecond held-out survival curves around each first observed half-survival crossing. Bands are pointwise Wilson intervals. Recrossings are retained: a single monotone collapse is not assumed, and reported boundary intervals condition on the evaluated delay grid.')
 traces=np.load(e.OUT/'results/illustrative_traces.npz');configs=json.loads((e.OUT/'results/selected_configurations.json').read_text())
 additional=e.OUT/'figures/additional_traces';additional.mkdir(exist_ok=True)
 for model in ['point','rod']:
  labels=[c['label'] for c in configs[model]];prefixes=['FD-reference','FD-fixed','FD-redesign','C-causal-w','dLQG-w','delay-aware-base'];indices=[next(j for j,l in enumerate(labels) if l.startswith(pre)) for pre in prefixes]
  for delay in [0,40,60]:
   for push in [5,10]:
    stem=f'{model}_d{delay}_p{push}';tr=traces[stem];fig,axs=plt.subplots(3,1,figsize=(7.1,4.8),sharex=True)
    for ax,col,title,limit in zip(axs,[3,1,5],['Angle (rad)','Cart position (m)','Command (N)'],[.5,2.4,10.]):
     for j,style in zip(indices,[':','--','-.','-',(0,(5,2)),(0,(2,1))]):ax.plot(tr[:,j,0],tr[:,j,col],label=short(labels[j]),ls=style,lw=.9)
     ax.axhline(limit,color='.6',ls=':',lw=.7);ax.axhline(-limit,color='.6',ls=':',lw=.7);ax.axvspan(2,2.1,color='.8',alpha=.6);ax.set_ylabel(title);ax.grid(alpha=.15)
    axs[0].set_ylim(-.55,.55);axs[1].set_ylim(-2.5,2.5);axs[2].set_ylim(-10.5,10.5);axs[-1].set_xlabel('Time (s)');axs[0].legend(fontsize=7,ncol=3,loc='upper center',bbox_to_anchor=(.5,1.45));fig.tight_layout()
    if delay==60 and push==10:save(fig,'traces_'+model,'One paired illustrative '+model+' realization at 60 ms/10 N, seed 20261125. Gray shading marks the unknown push and dotted horizontal lines mark failure or actuator limits. Failed states are frozen and commands are zeroed at the next control update. These trajectories illustrate behavior and do not estimate ensemble survival.')
    else:
     fig.savefig(additional/(stem+'.png'),bbox_inches='tight');fig.savefig(additional/(stem+'.pdf'),bbox_inches='tight');plt.close(fig)
 # Compact single-column article figures retain readable eight-point labels.
 def replace(fig,name):
  fig.tight_layout()
  for ext in ['png','pdf']:fig.savefig(e.OUT/'figures'/f'{name}.{ext}',bbox_inches='tight')
  plt.close(fig)
 fig,ax=plt.subplots(figsize=(3.5,2.7))
 for model,col in [('point','#225ea8'),('rod','#c0392b')]:
  for fam,ls in [('FD-fixed','--'),('FD-redesign','-')]:
   z=dev[(dev.model==model)&(dev.family==fam)].groupby('alpha').success.mean();ax.plot(z.index,z.values,'.',ls=ls,color=col,label=model+' '+fam.replace('FD-',''))
 ax.set(xlabel='Filter coefficient α',ylabel='Mean development survival',ylim=(-.03,1.03));ax.grid(alpha=.2);ax.legend(fontsize=7);replace(fig,'fd_sweep')
 fig,ax=plt.subplots(figsize=(3.5,2.7))
 for model,col in [('point','#225ea8'),('rod','#c0392b')]:
  for fam,ls in [('C-causal','--'),('dLQG','-')]:
   z=dev[(dev.model==model)&(dev.family==fam)&(dev.delay_ms==60)&(dev.push_N==5)].sort_values('scale');ax.semilogx(z.scale,z.success,'.',ls=ls,color=col,label=model+' '+('causal cKF' if fam=='C-causal' else 'dKF'))
   if fam=='dLQG':ax.scatter([1],[float(z[z.scale==1].iloc[0].success)],marker='s',s=20,color=col,zorder=5)
 ax.axvline(1,color='.6',ls=':',lw=.7)
 ax.set(xlabel='Covariance multiplier σ',ylabel='60 ms 5 N survival',ylim=(-.03,1.03));ax.grid(alpha=.2);ax.legend(fontsize=7);replace(fig,'covariance_sweep')
 audit=pd.read_csv(e.OUT/'results/figure2_tableII_audit.csv');details=[]
 for model in ['point','rod']:
  devrow=audit[(audit.model==model)&(audit.regime=='development')].iloc[0];holdrow=audit[(audit.model==model)&(audit.regime=='held-out')].iloc[0]
  details.append(f'{model} dKF {int(devrow.successes)}/{int(devrow.N)} ({100*devrow.success:.1f}%) versus held-out {int(holdrow.successes)}/{int(holdrow.N)} ({100*holdrow.success:.1f}%)')
 CAP[1]['caption']='Development survival at 60 ms/5 N over σ = 10⁻⁶ through 10⁸. Squares mark dKF at σ = 1: '+'; '.join(details)+'. Fig. 2 uses seed 20261121 and 200 trials per point; Table II/Fig. 6 use seed 20261122 and 500. Solid curves are dKF; dashed curves are causal cKF. The selection objective averages all five declared tasks.'
 fig,ax=plt.subplots(figsize=(3.5,2.8))
 for model,col in [('point','#225ea8'),('rod','#c0392b')]:
  for push,mark in [(5,'o'),(10,'^')]:
   z=joined[(joined.model==model)&(joined.push_N==push)];ax.scatter(z.PM_delay_ms,z.D50_ms,s=20,color=col,marker=mark,label=f'{model} {push} N',alpha=.7)
 ax.plot([0,100],[0,100],':',color='.4');ax.set(xlim=(0,100),ylim=(0,100),xlabel='Phase margin / crossover (ms)',ylabel='Nonlinear 50% survival delay (ms)');ax.grid(alpha=.2);ax.legend(fontsize=7);replace(fig,'margin_validation')
 CAP[4]['caption']='Phase-based nominal delay estimates versus nonlinear ten-second survival boundaries. The diagonal is equality. Exact lifted linear predictions, tabulated in the supplement, closely match the phase-based values. Predictors are omitted because their compensators depend on delay.'
 fig,axs=plt.subplots(2,1,figsize=(3.5,4.1))
 for ax,model in zip(axs,['point','rod']):
  lab=next(l for l in bd[bd.model==model].label if l.startswith('dLQG-w'))
  for push,col in [(5,'#225ea8'),(10,'#c0392b')]:
   mid=float(bd[(bd.model==model)&(bd.label==lab)&(bd.push_N==push)].iloc[0].D50_ms);z=held[(held.model==model)&(held.label==lab)&(held.push_N==push)&(abs(held.delay_ms-mid)<=7)].sort_values('delay_ms');ax.plot(z.delay_ms-mid,z.success,'.-',color=col,label=f'{push} N');ax.fill_between(z.delay_ms-mid,z.low,z.high,color=col,alpha=.1)
  ax.set(title=model+' selected dKF',ylabel='Survival probability',ylim=(-.03,1.03));ax.axhline(.5,color='.4',ls=':');ax.axvline(0,color='.6',ls=':');ax.grid(alpha=.15)
 axs[0].legend(fontsize=7);axs[-1].set_xlabel('Delay relative to first D50 (ms)');replace(fig,'local_crossings')
 CAP.append(dict(name='fd_sweep_full',caption='Full development α sweep: mean survival, terminal dwell and active-time RMS across the five declared tasks, for fixed and filter-aware redesigned gains. Each setting uses 200 paired trials per task.'))
 CAP.append(dict(name='covariance_sweep_full',caption='Full covariance-ratio trade-off: 60 ms/5 N survival and zero-delay/5 N terminal dwell and active RMS, across both models and both corrected observer families. The full tested multiplier range extends fourteen orders of magnitude.'))
 phase=pd.read_csv(e.OUT/'results/push_phase_summary.csv');fig,axs=plt.subplots(2,2,figsize=(7.1,4.6),sharex=True,sharey=True)
 family={'PD':'Derivative / PD','FD':'Derivative / PD','STATE':'Velocity oracle','C-current':'Continuous KF','C-causal':'Continuous KF','DKF':'Discrete KF','KF':'Discrete KF','PRED':'Delay-aware predictor'}
 colors={'Derivative / PD':'#225ea8','Velocity oracle':'#777777','Continuous KF':'#c0392b','Discrete KF':'#19865f','Delay-aware predictor':'#8a5295'}
 for i,model in enumerate(['point','rod']):
  kinds={c['label']:family[c['kind']] for c in configs[model]}
  for j,push in enumerate([5,10]):
   ax=axs[i,j];sub=phase[(phase.model==model)&(phase.push_N==push)].copy();sub['family']=sub.label.map(kinds)
   for name,col in colors.items():
    points=sub[sub.family==name];ax.scatter(points.fixed_success,points.random_success,color=col,s=12,alpha=.7,label=name)
   ax.plot([0,1],[0,1],':',color='.4');ax.axhline(.5,ls=':',lw=.5,color='.7');ax.axvline(.5,ls=':',lw=.5,color='.7');ax.set(title=model.capitalize()+f' {push} N',xlim=(-.03,1.03),ylim=(-.03,1.03));ax.grid(alpha=.15)
 for ax in axs[-1]:ax.set_xlabel('Fixed-phase survival')
 for ax in axs[:,0]:ax.set_ylabel('Randomized-phase survival')
 handles,labels=axs[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='upper center',ncol=3,fontsize=7);fig.tight_layout(rect=[0,0,1,.87]);save(fig,'push_phase_sensitivity','Randomized-minus-fixed push-phase sensitivity across all fourteen configurations, both push magnitudes and the queried local-crossing/60 ms cells. Each point compares 500 trial-paired realizations per regime; the diagonal is equality. The push starts at 2 s plus an independent uniform integer 0,…,9 ms and lasts 100 ms. This local sensitivity check does not re-estimate a full phase-averaged D50 curve.')
 (e.OUT/'figures/captions.json').write_text(json.dumps(CAP,indent=2));print('Figures complete',len(CAP),flush=True)
if __name__=='__main__':main()
