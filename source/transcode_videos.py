import engine as e
import sys,subprocess,os,json
sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parent/'media_packages'))
import imageio_ffmpeg,cv2,pandas as pd
encoder=imageio_ffmpeg.get_ffmpeg_exe();rows=[]
for path in sorted((e.OUT/'videos').glob('*.mp4')):
 temp=path.with_name(path.stem+'_h264.tmp.mp4')
 subprocess.run([encoder,'-hide_banner','-loglevel','error','-y','-i',str(path),'-an','-c:v','libx264','-threads','2','-preset','fast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(temp)],check=True)
 cap=cv2.VideoCapture(str(temp));n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));fps=cap.get(cv2.CAP_PROP_FPS);first,_=cap.read();cap.set(cv2.CAP_PROP_POS_FRAMES,n-1);last,_=cap.read();cap.release();assert first and last and n==240 and abs(fps-24)<1e-8
 os.replace(temp,path);rows.append(dict(file=path.name,frames=n,fps=fps,codec='H.264',pixel_format='yuv420p',bytes=path.stat().st_size));print('H264 verified',path.name,flush=True)
pd.DataFrame(rows).to_csv(e.OUT/'results/video_encoding_checks.csv',index=False)
checks=pd.read_csv(e.OUT/'results/video_checks.csv')
checks['codec']='H.264';checks['bytes']=[(e.OUT/'videos'/f'{r.model}_d{r.delay_ms}_p{r.push_N}.mp4').stat().st_size for r in checks.itertuples()];checks.to_csv(e.OUT/'results/video_checks.csv',index=False)
v=json.loads((e.OUT/'results/runtime_versions.json').read_text());v['media_encoder']=imageio_ffmpeg.get_ffmpeg_version();v['imageio_ffmpeg']=imageio_ffmpeg.__version__;(e.OUT/'results/runtime_versions.json').write_text(json.dumps(v,indent=2))
