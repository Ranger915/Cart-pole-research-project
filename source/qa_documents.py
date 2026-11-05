from pathlib import Path
import json,subprocess,zipfile
from pypdf import PdfReader
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent if HERE.name=='source' else HERE.parents[1];OUT=ROOT if HERE.name=='source' else ROOT/'outputs/ieee_revision';qa=HERE/'qa';qa.mkdir(exist_ok=True)
poppler=r'C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1030-493-0_26.1030.493.0_x64__3k8sg7r9htsxt/dependencies/native/poppler/Library/bin/pdftoppm.exe'
audit={}
for stem in ['revised_ieee_manuscript','revised_detailed_derivations','methodological_response']:
 folder=qa/stem;folder.mkdir(exist_ok=True)
 for old in folder.glob('page-*.png'):
  assert old.resolve().parent==folder.resolve();old.unlink()
 subprocess.run([poppler,'-r','100','-png',str(OUT/(stem+'.pdf')),str(folder/'page')],check=True,capture_output=True)
 reader=PdfReader(str(OUT/(stem+'.pdf')));text='\n'.join(p.extract_text() for p in reader.pages)
 assert 'RAAGHAVAN MOOKIAH BARATHKUMAR' in text
 assert 'AI assistance' not in text and 'AI credit' not in text
 if stem=='revised_ieee_manuscript':
  for i in range(1,8):assert 'Fig. '+str(i)+'.' in text
 with zipfile.ZipFile(OUT/(stem+'.docx')) as z:
  xml=z.read('word/document.xml').decode();native=xml.count('<m:oMath>');images=xml.count('<w:drawing>')
  if stem!='methodological_response':assert native>=5
 audit[stem]=dict(pages=len(reader.pages),native_equations=native,embedded_figures=images)
 files=sorted(folder.glob('page-*.png'))
 for b in range(0,len(files),6):
  sheet=Image.new('RGB',(1080,930),'#dddddd');draw=ImageDraw.Draw(sheet)
  for j,path in enumerate(files[b:b+6]):
   im=Image.open(path);im.thumbnail((350,435));x=(j%3)*360+(360-im.width)//2;y=(j//3)*465+20;sheet.paste(im,(x,y));draw.text(((j%3)*360+10,(j//3)*465+3),path.stem,fill='black')
  sheet.save(folder/f'contact-{b//6+1}.png')
(OUT/'results/document_checks.json').write_text(json.dumps(audit,indent=2));print(json.dumps(audit))
