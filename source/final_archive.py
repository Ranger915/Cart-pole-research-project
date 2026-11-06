"""Package verified current artifacts, optionally retaining an earlier ZIP's history."""
from pathlib import Path
import argparse, csv, hashlib, html, json, zipfile
ROOT = Path(__file__).resolve().parent.parent

def digest(data):
    return hashlib.sha256(data).hexdigest()

def current_files():
    for p in sorted(ROOT.rglob('*')):
        rel=p.relative_to(ROOT)
        if p.is_file() and p.name not in {'START_HERE.html','CONTENTS_SHA256.json'} and not any(x in {'qa','__pycache__','mplcache','.git'} for x in rel.parts) and not p.name.startswith(('~$','phase_checkpoint_')) and p.suffix not in {'.pyc','.zip'}:
            yield rel.as_posix(),p

def gates():
    checks=json.loads((ROOT/'results/revision_checks.json').read_text())
    assert checks and all(x['passed'] for x in checks)
    phase=json.loads((ROOT/'results/push_phase_checks.json').read_text())
    assert phase['all_zero_phase_matches'] and len(phase['checks'])==269
    qa=json.loads((ROOT/'results/visual_review.json').read_text())
    assert qa['all_pages_reviewed'] and not qa['unresolved_layout_issues']
    for stem,entry in qa['documents'].items():
        for ext in ('docx','pdf'):
            assert digest((ROOT/(stem+'.'+ext)).read_bytes())==entry[ext+'_sha256']
    with (ROOT/'results/video_encoding_checks.csv').open() as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==12 and all(r['codec']=='H.264' for r in rows)
    assert (ROOT/'manuscript_with_supplement.pdf').is_file() and (ROOT/'LICENSE.md').is_file()

def start_page(prefix):
    body='<!doctype html><html><head><meta charset="utf-8"><title>Cart-pole research</title><style>body{font:16px/1.6 system-ui;max-width:1000px;margin:40px auto;padding:20px;background:#f6f8fa;color:#17212b}a{color:#1457a3}article{background:white;padding:24px;margin:20px 0}video,img{max-width:100%}</style></head><body><h1>Tuning and Delay-Aware State Prediction in Cart-Pole Survival Boundaries</h1><p>RAAGHAVAN MOOKIAH BARATHKUMAR · Version 1.0.0 · All rights reserved</p><p><a href="https://github.com/Ranger915/Cart-pole-research-project">Repository</a> · <a href="https://doi.org/10.5281/zenodo.24017779">Zenodo DOI</a></p><article><h2>Read the work</h2>'
    for stem,label in [('revised_ieee_manuscript','IEEE-style manuscript'),('revised_detailed_derivations','Supplement S1: detailed derivations'),('methodological_response','Response to methodological review')]:
        body+=f'<p>{label}: <a href="{prefix}{stem}.pdf">PDF</a> · <a href="{prefix}{stem}.docx">Editable Word</a></p>'
    body+=f'<p><a href="{prefix}manuscript_with_supplement.pdf">Manuscript with attached S1</a> · <a href="{prefix}README.md">Reproduction guide</a></p></article><article><h2>Controllers in motion</h2><p>Each movie is one illustrative paired trial across fourteen configurations, not an ensemble success estimate. Movies use the fixed 2 s push onset.</p><select id="scenario">'
    with (ROOT/'results/video_checks.csv').open() as f:
        rows=list(csv.DictReader(f))
    for r in rows:
        stem=f"{r['model']}_d{r['delay_ms']}_p{r['push_N']}"
        body+=f'<option value="{stem}">{r["model"]} · {r["delay_ms"]} ms · {r["push_N"]} N</option>'
    r=rows[0];first=f"{r['model']}_d{r['delay_ms']}_p{r['push_N']}"
    body+=f'</select><video id="movie" controls preload="metadata" src="{prefix}videos/{first}.mp4"></video></article><article><h2>Research figures</h2>'
    for cap in json.loads((ROOT/'figures/captions.json').read_text()):
        body+=f'<p><a href="{prefix}figures/{cap["name"]}.pdf"><img loading="lazy" src="{prefix}figures/{cap["name"]}.png" alt="{html.escape(cap["caption"],quote=True)}"></a><br>{html.escape(cap["caption"])}</p>'
    body+=f'</article><p>Simulation study; no hardware validation or journal acceptance. Earlier interpretations are superseded by the current manuscript. Historical drafts, when included, are in history/.</p><script>document.getElementById("scenario").onchange=function(){{const v=document.getElementById("movie");v.src="{prefix}videos/"+this.value+".mp4";v.load();}};</script></body></html>'
    return body.encode()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--target',required=True,type=Path);ap.add_argument('--history',type=Path);ap.add_argument('--publication-proof',type=Path);args=ap.parse_args()
    gates()
    if args.history:
        assert args.publication_proof
        proof=json.loads(args.publication_proof.read_text())
        assert proof['zenodo_published'] and proof['github_release_published']
    assert not args.target.exists(),'Refusing to overwrite an archive'
    prefix='current_revision/' if args.history else '';manifest={}
    with zipfile.ZipFile(args.target,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        def add(name,data):
            assert name not in manifest and '..' not in Path(name).parts
            z.writestr(name,data);manifest[name]={'bytes':len(data),'sha256':digest(data)}
        if args.history:
            with zipfile.ZipFile(args.history) as old:
                assert old.testzip() is None
                for name in old.namelist():
                    if name.startswith('history/') and not name.endswith('/'):
                        add(name,old.read(name))
            add('publication_verification.json',args.publication_proof.read_bytes())
        for name,p in current_files():add(prefix+name,p.read_bytes())
        add('START_HERE.html',start_page(prefix))
        if args.history:
            add('README.md',b'Extract this ZIP and open START_HERE.html. current_revision contains the latest manuscript, attached supplement, editable Word files, figures, videos, sources and results. history retains earlier drafts and development artifacts; their claims may be superseded. All rights reserved for original material; third-party rights remain unchanged. CONTENTS_SHA256.json lists hashes.\n')
        z.writestr('CONTENTS_SHA256.json',json.dumps(manifest,indent=2).encode())
    with zipfile.ZipFile(args.target) as z:
        assert z.testzip() is None
        for name,entry in manifest.items():
            data=z.read(name);assert len(data)==entry['bytes'] and digest(data)==entry['sha256']
    report={'file':str(args.target),'bytes':args.target.stat().st_size,'entries':len(manifest)+1,'sha256':digest(args.target.read_bytes()),'crc_check':True,'content_hashes_verified':len(manifest)}
    args.target.with_suffix('.verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)

if __name__=='__main__':main()
