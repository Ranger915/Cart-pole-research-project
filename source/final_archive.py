"""Package only after every scientific and visual verification gate passes."""
from pathlib import Path
import csv,json,hashlib,zipfile,html,shutil,sys
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/ieee_revision'
def filehash(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def read(name):
 with open(OUT/'results'/name,encoding='utf-8') as f:return list(csv.DictReader(f))
def main():
 checks=json.loads((OUT/'results/revision_checks.json').read_text());assert checks and all(x['passed'] for x in checks)
 bounds=read('survival_boundaries.csv');assert len(bounds)==56 and all(int(x['N'])==500 for x in bounds)
 assert len(read('paired_interventions.csv'))==108
 assert len(read('development_sweeps.csv'))==480
 videos=read('video_checks.csv');assert len(videos)==12 and all(int(v['frames'])==240 for v in videos)
 encoding=read('video_encoding_checks.csv');assert len(encoding)==12 and all(v['codec']=='H.264' for v in encoding)
 qa=json.loads((OUT/'results/visual_review.json').read_text());assert qa['all_pages_reviewed'] and not qa['unresolved_layout_issues']
 docs=json.loads((OUT/'results/document_checks.json').read_text());assert len(docs)==3
 for stem in docs:
  for ext in ['docx','pdf']:assert (OUT/(stem+'.'+ext)).is_file()
  for ext in ['docx','pdf']:assert filehash(OUT/(stem+'.'+ext))==qa['documents'][stem][ext+'_sha256']
 source=OUT/'source';source.mkdir(exist_ok=True)
 for name in ['engine.py','development.py','finalize_configs.py','boundaries.py','margins.py','audit.py','figures.py','videos.py','transcode_videos.py','formatter.py','build_documents.py','render_word.ps1','qa_documents.py','final_archive.py']:
  shutil.copyfile(Path(__file__).parent/name,source/name)
 (source/'requirements.txt').write_text('numpy\nscipy\npandas\nmatplotlib\ncontrol\nopencv-python\nimageio-ffmpeg\npython-docx\nlxml\npypdf\nPillow\n',encoding='utf-8')
 (OUT/'README.md').write_text('''# Current research revision

Read revised_ieee_manuscript.docx for the editable IEEE-style article, revised_detailed_derivations.docx for the complete derivations, and methodological_response.docx for the four-point response. PDF copies are included.

The earlier architecture-only and observer-implementation interpretations are superseded. Current comparisons correct covariance units, distinguish causal timing, tune derivative filtering and gains, extend covariance-ratio sweeps, include timestamp-aware prediction, and report first observed 50% survival crossings with recrossing flags.

The boundary intervals condition on the evaluated adaptive grid. They are rounded outward to milliseconds and include the observed crossing bracket. Survival for ten seconds is distinct from terminal dwell and local asymptotic stability. The velocity oracle has privileged measurements. No new controller or universal ranking is claimed.

## Reproduce

Install source/requirements.txt in a Python environment. Scientific runs used Python 3.13; Word authoring used the bundled Python 3.12 environment. Exact package versions are recorded in results/runtime_versions.json.

Run source/development.py, source/finalize_configs.py, source/boundaries.py, source/margins.py, source/audit.py, source/videos.py, source/transcode_videos.py and source/figures.py in that order. Source paths detect this extracted layout. Boundaries reuse checkpoints/results when present; for an entirely fresh campaign use a clean copy containing source/ and results/equations_mathml.json. Start clean whenever changing designs, noise levels, seeds or protocol. The seeds and selected designs are fixed in the source and result files. Use the recorded package versions for exact replay rather than relying on the unversioned installation list.

Run source/build_documents.py for editable Word files. Native equations use Office16 MML2OMML.XSL; render_word.ps1 uses installed Microsoft Word to update fields and export PDFs. The QA helper's Poppler path is host-specific and must be adjusted on another machine. Scientific results do not require Word.

videos/ contains twelve 10-second MP4 comparisons, showing fourteen configurations for both models, delays 0/40/60 ms and pushes 5/10 N. Each is one paired illustrative realization, not an ensemble success rate. The NPZ traces and all aggregate tables are supplied. Failed states are frozen, rather than animated past the stated failure event.

figures/ includes publication PNG/PDF figures, full multi-panel sweeps and additional illustrative traces. results/ contains the development sweeps, held-out outcomes, all queried cells, boundary intervals, linear margins, intervention tests, validation checks and trial census.
''',encoding='utf-8')
 files={}
 def add_tree(folder,prefix,exclude=()):
  if not folder.exists():return
  exclude=set(exclude)|{'.git','.venv','venv','packages','node_modules','__pycache__','media_packages'}
  for p in sorted(folder.rglob('*')):
   rel=p.relative_to(folder)
   if p.is_file() and not any(part in exclude for part in rel.parts) and not p.name.startswith('~$') and p.suffix not in ['.pyc','.zip'] and not p.name.startswith('partial_'):files[str(Path(prefix)/rel).replace('\\','/')]=p
 add_tree(OUT,'current_revision',exclude=('__pycache__','mplcache','qa'))
 for name in ['cartpole_study','research_package','ieee_journal']:add_tree(ROOT/'outputs'/name,'history/'+name,exclude=('__pycache__','mplcache','qa','node_modules'))
 add_tree(ROOT/'work','history/development_sources',exclude=('journal_revision','__pycache__','mplcache','qa','packages','node_modules'))
 original=Path(r'C:/Users/Raaghav/Documents/ChatGPT/Control systems proj 1')
 add_tree(original/'cartpole_study','history/original_project',exclude=('__pycache__','packages','node_modules'))
 add_tree(original/'work','history/original_work',exclude=('__pycache__','packages','node_modules','mplcache','qa'))
 add_tree(Path(r'C:/Users/Raaghav/.codex/visualizations/2026/11/05/01a1a9e4-478a-7cb2-a7d8-4b7e92342839'),'history/inline_visualizations',exclude=('node_modules','__pycache__'))
 brief=Path(r'C:/Users/Raaghav/.codex/attachments/af969128-5eea-43c4-91c0-53f23fe8c78c/Pasted text.txt')
 if brief.exists():files['history/original_request.txt']=brief
 readme='''# Complete cart pole research project

Start with START_HERE.html after extracting this ZIP. The current_revision folder contains the corrected article, full mathematical supplement, review response, all revised results, graphs, MP4s and sources.

history preserves the original study, earlier reports/manuscripts, earlier movies and figures, inline visualization, and development sources. Historical numerical claims and architecture interpretations may be superseded; use the current revision for current conclusions. Earlier nested ZIPs and installed dependencies are omitted to avoid duplication. Their extracted project artifacts and the reproducible code are retained.

The author is RAAGHAVAN MOOKIAH BARATHKUMAR. The article follows a general IEEE journal layout. Before actual submission, choose the journal and supply affiliation/contact metadata and satisfy its submission requirements; no journal acceptance or algorithmic novelty is claimed.

CONTENTS_SHA256.json records the hash and size of every packaged file except itself. The archive has been checked for CRC integrity. Verification and visual-review records are in current_revision/results.
'''
 index='''<!doctype html><html><head><meta charset="utf-8"><title>Cart pole research project</title><style>body{font:16px/1.6 system-ui;max-width:1050px;margin:50px auto;padding:0 25px;color:#17212b;background:#f7f8fa}h1,h2{line-height:1.2}a{color:#1457a3}article{background:white;padding:25px;margin:25px 0;border:1px solid #ddd}video,img{max-width:100%}small{color:#555}table{border-collapse:collapse}td,th{padding:7px 16px;border:1px solid #ddd;text-align:left}</style></head><body><h1>Cart pole research project</h1><p>RAAGHAVAN MOOKIAH BARATHKUMAR</p><p>The current revision corrects and calibrates the baselines, adds known-delay prediction, and reports survival boundaries for both models. Earlier versions are retained in <a href="history/">history</a> and are superseded where their interpretations conflict.</p><article><h2>Read the revised work</h2><p><a href="current_revision/revised_ieee_manuscript.docx">Editable IEEE-style manuscript</a> · <a href="current_revision/revised_ieee_manuscript.pdf">PDF</a></p><p><a href="current_revision/revised_detailed_derivations.docx">Detailed mathematical supplement</a> · <a href="current_revision/revised_detailed_derivations.pdf">PDF</a></p><p><a href="current_revision/methodological_response.docx">Response to the four methodological criticisms</a> · <a href="current_revision/methodological_response.pdf">PDF</a></p><p><a href="current_revision/README.md">Reproduction guide</a> · <a href="current_revision/results/">All numerical tables and checks</a> · <a href="current_revision/source/">Source</a></p></article><article><h2>Controller comparisons in motion</h2><p>Each movie shows one paired illustrative trial across fourteen configurations. It is not an ensemble survival estimate. Choose a scenario:</p><select id="scenario">'''
 for v in videos:
  stem=f"{v['model']}_d{v['delay_ms']}_p{v['push_N']}";index+=f'<option value="{stem}">{html.escape(v["model"])} · {v["delay_ms"]} ms · {v["push_N"]} N</option>'
 first=f"{videos[0]['model']}_d{videos[0]['delay_ms']}_p{videos[0]['push_N']}";index+=f'</select><p><video id="movie" controls preload="metadata" src="current_revision/videos/{first}.mp4"></video></p><p><a id="movieLink" href="current_revision/videos/{first}.mp4">Open selected MP4</a></p></article><article><h2>Research figures</h2>'
 for cap in json.loads((OUT/'figures/captions.json').read_text()):
  name=cap['name'];index+=f'<p><a href="current_revision/figures/{name}.pdf"><img loading="lazy" src="current_revision/figures/{name}.png" alt="{html.escape(cap["caption"],quote=True)}"></a><br><small>{html.escape(cap["caption"])}</small></p>'
 index+='''</article><p>Survival, sustained terminal dwell and local stability are different outcomes. See the article and supplement for tuning, uncertainty and scope.</p><script>document.getElementById('scenario').onchange=function(){const p='current_revision/videos/'+this.value+'.mp4';const v=document.getElementById('movie');v.src=p;v.load();document.getElementById('movieLink').href=p;};</script></body></html>'''
 extras={'README.md':readme.encode(),'START_HERE.html':index.encode()};manifest={}
 for name,p in files.items():manifest[name]=dict(bytes=p.stat().st_size,sha256=filehash(p))
 for name,data in extras.items():manifest[name]=dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
 extras['CONTENTS_SHA256.json']=json.dumps(manifest,indent=2).encode()
 target=ROOT/'outputs/COMPLETE_CARTPOLE_RESEARCH_PROJECT.zip'
 # The archive is created only after all assertions and final review records.
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for name,p in files.items():z.write(p,name)
  for name,data in extras.items():z.writestr(name,data)
 with zipfile.ZipFile(target) as z:
  assert z.testzip() is None
  for name,entry in manifest.items():
   h=hashlib.sha256()
   with z.open(name) as member:
    for chunk in iter(lambda:member.read(1024*1024),b''):h.update(chunk)
   assert h.hexdigest()==entry['sha256']
 report=dict(file=str(target),bytes=target.stat().st_size,entries=len(files)+len(extras),sha256=filehash(target),crc_check=True,content_hashes_verified=len(manifest))
 (ROOT/'work/journal_revision/final_archive_check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
if __name__=='__main__':main()
