import engine as e
import numpy as np,pandas as pd,json
from development import serialize

def restore(c):
 c['K']=np.array(c['K']);c['d']={k:np.array(v) if isinstance(v,list) else v for k,v in c['d'].items()};return c

def crossing(delays,values):
 if values[0]<.5:return np.nan
 for i in range(1,len(delays)):
  if values[i]<.5:
   return delays[i-1]+(delays[i]-delays[i-1])*(values[i-1]-.5)/(values[i-1]-values[i])
 return np.nan

def main():
 configs=json.loads((e.OUT/'results/selected_configurations.json').read_text());allrows=[];bound=[]
 census=pd.read_csv(e.OUT/'results/trial_census.csv').to_dict('records') if (e.OUT/'results/trial_census.csv').exists() else []
 for model,rho in [('point',0.),('rod',1/3)]:
  cs=[restore(c) for c in configs[model]];lookup={c['label']:c for c in cs};keys=[(c['label'],p) for c in cs for p in [5,10]];cache={};archive={};metrics={}
  old=e.OUT/'results'/f'heldout_success_{model}.npz'
  if old.exists():
   data=np.load(old)
   for key in data.files:
    l,p,d=key.split('|');cache[l,int(p),int(d)]=data[key];archive[key]=data[key]
   for row in pd.read_csv(e.OUT/'results/heldout_summary.csv').to_dict('records'):
    if row['model']==model:metrics[row['label'],int(row['push_N']),int(row['delay_ms'])]={k:v for k,v in row.items() if k not in ['model','label','push_N','delay_ms']}
  partial=e.OUT/'results'/f'partial_{model}'
  if partial.with_suffix('.npz').exists():
   data=np.load(partial.with_suffix('.npz'))
   for key in data.files:
    l,p,d=key.split('|');cache[l,int(p),int(d)]=data[key];archive[key]=data[key]
   for row in json.loads(partial.with_suffix('.json').read_text()):metrics[row['label'],row['push_N'],row['delay_ms']]=row['metrics']
  def query(requests,n=500,seed=20261122,save=True):
   requests=list(dict.fromkeys(requests));requests=[r for r in requests if not save or r not in cache]
   if not save:requests=[r for r in requests if r not in locator]
   if not requests:return
   print('Boundary',model,'cases',len(requests),'N',n,'delays',sorted(set(r[2] for r in requests)),flush=True)
   # Bound memory while preserving the trial-paired random stream.
   for start in range(0,len(requests),8):
    batch=requests[start:start+8];out,_=e.simulate(rho,[dict(config=lookup[l],push=p,delay=d) for l,p,d in batch],ntrial=n,seed=seed)
    census.append(dict(model=model,cases=len(batch),trials_per_case=n,seed=seed,phase='held-out' if save else 'locator'))
    for j,r in enumerate(batch):
     if save:
      cache[r]=out['success'][j];metrics[r]=e.summary(out,j);archive['|'.join(map(str,r))]=out['success'][j]
     else:locator[r]=float(out['success'][j].mean())
    if save:
     np.savez_compressed(partial.with_suffix('.npz'),**archive)
     partial.with_suffix('.json').write_text(json.dumps([dict(label=l,push_N=p,delay_ms=d,metrics=m) for (l,p,d),m in metrics.items()],default=serialize))
    pd.DataFrame(census).to_csv(e.OUT/'results/trial_census.csv',index=False)
    print('Saved batch',model,start+len(batch),'of',len(requests),flush=True)
  locator={};grid=[0,20,40,60,80,100,150,200,300]
  oldlocator=e.OUT/'results'/f'locator_{model}.csv'
  if oldlocator.exists():
   for row in pd.read_csv(oldlocator).to_dict('records'):locator[row['label'],int(row['push_N']),int(row['delay_ms'])]=float(row['success'])
  query([(l,p,d) for l,p in keys for d in grid],n=100,seed=20261124,save=False)
  pd.DataFrame([dict(model=model,label=l,push_N=p,delay_ms=d,success=v,N=100) for (l,p,d),v in locator.items()]).to_csv(e.OUT/'results'/f'locator_{model}.csv',index=False)
  brackets={}
  for l,p in keys:
   ys=[locator[l,p,d] for d in grid];idx=next((i for i,y in enumerate(ys) if y<.5),None)
   brackets[l,p]=[0,0] if idx==0 else [grid[idx-1],grid[idx]] if idx is not None else [300,600]
  query([(l,p,d) for (l,p),(lo,hi) in brackets.items() for d in set([0,40,60,lo,hi])])
  # Verify the development bracket with held-out outcomes, then expand as needed.
  for iteration in range(12):
   requests=[];changed=False
   for (l,p),(lo,hi) in brackets.items():
    if cache[l,p,0].mean()<.5:brackets[l,p]=[0,0];continue
    if cache[l,p,lo].mean()<.5:
     hi=lo;lo=max(0,lo-20);changed=True
    elif cache[l,p,hi].mean()>=.5 and hi<1200:
     lo=hi;hi=min(1200,hi*2);changed=True
    brackets[l,p]=[lo,hi];requests += [(l,p,lo),(l,p,hi)]
   query(requests)
   if not changed:break
  for iteration in range(12):
   request=[(l,p,(lo+hi)//2) for (l,p),(lo,hi) in brackets.items() if hi-lo>1 and cache[l,p,lo].mean()>=.5 and cache[l,p,hi].mean()<.5]
   if not request:break
   query(request)
   for l,p,mid in request:
    if cache[l,p,mid].mean()>=.5:brackets[l,p][0]=mid
    else:brackets[l,p][1]=mid
  # A local grid checks recrossings and supports conditional paired bootstrap CIs.
  query([(l,p,d) for (l,p),(lo,hi) in brackets.items() for d in range(max(0,lo-6),min(1200,hi+6)+1)])
  def first_bracket(l,p):
   ds=sorted(d for ll,pp,d in cache if ll==l and pp==p)
   if cache[l,p,ds[0]].mean()<.5:return [0,0]
   idx=next((i for i in range(1,len(ds)) if cache[l,p,ds[i]].mean()<.5),None)
   return [ds[idx-1],ds[idx]] if idx is not None else [ds[-1],ds[-1]]
  # A local grid can expose an earlier dip than the root located by bisection.
  # Refine that first observed crossing, then complete its local window too.
  for iteration in range(24):
   requests=[]
   for l,p in keys:
    lo,hi=first_bracket(l,p);brackets[l,p]=[lo,hi]
    if lo==hi:continue
    if hi-lo>1:requests.append((l,p,(lo+hi)//2))
    else:requests.extend((l,p,d) for d in range(max(0,lo-6),min(1200,hi+6)+1) if (l,p,d) not in cache)
   if not requests:break
   query(requests)
  else:raise RuntimeError('First observed crossing refinement did not finish')
  for l,p in keys:
   brackets[l,p]=first_bracket(l,p)
   lo,hi=brackets[l,p];assert lo==hi or hi-lo==1
  for (l,p),(lo,hi) in brackets.items():
   ds=np.array(sorted(d for ll,pp,d in cache if ll==l and pp==p));ys=np.array([cache[l,p,int(d)].mean() for d in ds]);status='interior'
   if ys[0]<.5:status='below-half-at-zero'
   elif not np.any(ys<.5):status='above-half-at-limit'
   estimate=crossing(ds,ys);mat=np.stack([cache[l,p,int(d)] for d in ds]);rng=np.random.default_rng(20261123);boots=[]
   for k in range(2000):boots.append(crossing(ds,mat[:,rng.integers(0,500,500)].mean(axis=1)))
   finite=np.array(boots)[np.isfinite(boots)];rawci=np.quantile(finite,[.025,.975]) if len(finite) else [np.nan,np.nan]
   crossindex=next((i for i in range(1,len(ds)) if ys[i]<.5),None) if ys[0]>=.5 else None
   # Preserve statistical interpolation intervals separately; reported bounds
   # also cover the evaluated grid crossing and round outward to 1 ms.
   ci=[min(np.floor(rawci[0]),ds[crossindex-1]),max(np.ceil(rawci[1]),ds[crossindex])] if crossindex is not None and len(finite) else rawci
   recrossings=int(np.sum((ys[:-1]<.5)&(ys[1:]>=.5)));maxrise=float(np.max(np.diff(ys))) if len(ys)>1 else 0.
   bound.append(dict(model=model,label=l,push_N=p,D50_ms=estimate,low_ms=ci[0],high_ms=ci[1],interpolated_bootstrap_low_ms=rawci[0],interpolated_bootstrap_high_ms=rawci[1],status=status,bracket_low_ms=lo,bracket_high_ms=hi,bootstrap_valid=len(finite),upward_half_recrossings=recrossings,max_adjacent_rise=maxrise,N=500))
  allrows.extend(dict(model=model,label=l,push_N=p,delay_ms=d,**v) for (l,p,d),v in metrics.items())
  np.savez_compressed(e.OUT/'results'/f'heldout_success_{model}.npz',**archive)
  pd.DataFrame(allrows).to_csv(e.OUT/'results/heldout_summary.csv',index=False);pd.DataFrame(bound).to_csv(e.OUT/'results/survival_boundaries.csv',index=False);pd.DataFrame(census).to_csv(e.OUT/'results/trial_census.csv',index=False)
 print('Boundary campaign complete',flush=True)
if __name__=='__main__':main()
