import engine as e
from boundaries import restore
from figures import short
import numpy as np,json,pandas as pd,cv2

def main():
 folder=e.OUT/'videos';folder.mkdir(exist_ok=True);configs=json.loads((e.OUT/'results/selected_configurations.json').read_text());audit=[];alltraces={}
 width,height,fps=1920,1440,24
 for model,rho in [('point',0.),('rod',1/3)]:
  cs=[restore(c) for c in configs[model]]
  for delay in [0,40,60]:
   for push in [5,10]:
    out,tr=e.simulate(rho,[dict(config=c,delay=delay,push=push) for c in cs],ntrial=1,seed=20261125,record=True);stem=f'{model}_d{delay}_p{push}';alltraces[stem]=tr
    writer=cv2.VideoWriter(str(folder/(stem+'.mp4')),cv2.VideoWriter_fourcc(*'mp4v'),fps,(width,height));assert writer.isOpened()
    def text(im,s,xy,size=.55,color=(35,35,35)):cv2.putText(im,s,xy,cv2.FONT_HERSHEY_SIMPLEX,size,color,1,cv2.LINE_AA)
    for frame in range(240):
     idx=min(len(tr)-1,round(frame/fps/.01));t=tr[idx,0,0];im=np.full((height,width,3),250,np.uint8)
     for j,c in enumerate(cs):
      col,row=j%4,j//4;ox,oy=col*480,row*360;x,v,theta,omega,u=tr[idx,j,1:];failed=bool(np.isfinite(out['failure_time'][j,0]) and t>=out['failure_time'][j,0]);color=(50,50,205) if failed else (150,85,25)
      cv2.rectangle(im,(ox+4,oy+4),(ox+476,oy+356),(215,215,215),1);text(im,short(c['label']).replace('α','alpha'),(ox+15,oy+27),.53)
      text(im,f'x={x:+.2f} m  theta={theta:+.3f} rad',(ox+15,oy+52),.45);text(im,f'u={u:+.2f} N'+('  FAILED' if failed else ''),(ox+15,oy+74),.45,color)
      cy=oy+245;cx=ox+240+int(45*x);cv2.line(im,(ox+105,cy+14),(ox+375,cy+14),(170,170,170),2)
      for sign in [-1,1]:cv2.line(im,(ox+240+sign*108,cy-12),(ox+240+sign*108,cy+22),(90,90,210),1)
      cv2.rectangle(im,(cx-20,cy-10),(cx+20,cy+10),color,-1)
      length=120 if model=='rod' else 60;tip=(cx+int(length*np.sin(theta)),cy-int(length*np.cos(theta)));cv2.line(im,(cx,cy),tip,color,5 if model=='rod' else 2)
      com=(cx+int(60*np.sin(theta)),cy-int(60*np.cos(theta)));cv2.circle(im,com,7,color,-1)
      cv2.arrowedLine(im,(cx,cy+32),(cx+int(u*3),cy+32),color,2,tipLength=.25)
      if 2<=t<2.1:cv2.arrowedLine(im,(cx-70,cy-23),(cx-25,cy-23),(0,100,240),3,tipLength=.3)
      # Angle trace uses the same axes and failure bounds in every panel.
      cv2.line(im,(ox+25,oy+315),(ox+450,oy+315),(200,200,200),1)
      vals=tr[:idx+1,j,3];pts=np.column_stack((ox+25+np.arange(idx+1)*425/(len(tr)-1),oy+315-np.clip(vals,-.55,.55)*55)).astype(np.int32);cv2.polylines(im,[pts],False,color,1,cv2.LINE_AA)
      text(im,'angle trace',(ox+25,oy+347),.38)
     text(im,f'{model.upper()}   delay {delay} ms   push {push} N for 0.1 s   time {t:.2f} s',(1000,1140),.52)
     text(im,'One paired illustrative trial',(1460,1175),.53);text(im,'Not an ensemble success rate',(1460,1205),.48)
     text(im,'Track limits +/-2.4 m',(1460,1255),.48);text(im,'Angle limit +/-0.5 rad',(1460,1285),.48);text(im,'Command limit +/-10 N',(1460,1315),.48)
     writer.write(im)
    writer.release();path=folder/(stem+'.mp4');cap=cv2.VideoCapture(str(path));nf=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));first,_=cap.read();cap.set(cv2.CAP_PROP_POS_FRAMES,nf-1);last,lastimage=cap.read();cap.release();assert nf==240 and first and last
    if delay==60:cv2.imwrite(str(folder/(stem+'_preview.png')),lastimage)
    audit.append(dict(model=model,delay_ms=delay,push_N=push,frames=nf,fps=fps,width=width,height=height,seed=20261125,bytes=path.stat().st_size));print('Video',stem,flush=True)
 np.savez_compressed(e.OUT/'results/illustrative_traces.npz',**alltraces);pd.DataFrame(audit).to_csv(e.OUT/'results/video_checks.csv',index=False)
if __name__=='__main__':main()
