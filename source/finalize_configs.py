import engine as e,json,copy
p=e.OUT/'results/selected_configurations.json';v=json.loads(p.read_text())
for cs in v.values():
 if not any(c['label']=='delay-aware-tuned' for c in cs):cs.append(dict(copy.deepcopy(next(c for c in cs if c['label'].startswith('dLQG-w'))),label='delay-aware-tuned',kind='PRED'))
 if not any(c['label']=='KF-LQR-base' for c in cs):
  c=copy.deepcopy(next(c for c in cs if c['label']=='dLQG-base'));c.update(label='KF-LQR-base',kind='KF',K=c['d']['K']);cs.append(c)
p.write_text(json.dumps(v,indent=2));print('Primary diagnostic configurations',[(k,len(vv)) for k,vv in v.items()])
