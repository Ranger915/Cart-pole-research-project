"""Editable IEEE-style article and complete mathematical supplement."""
from pathlib import Path
import csv,json,math,copy,re,zipfile
from lxml import etree
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.section import WD_SECTION_START
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent if HERE.name=='source' else HERE.parents[1];OUT=ROOT if HERE.name=='source' else ROOT/'outputs/ieee_revision'
def read(name):
 with open(OUT/'results'/name,encoding='utf-8') as f:return list(csv.DictReader(f))
MATH=json.loads((OUT/'results/equations_mathml.json').read_text())
AUTHOR='RAAGHAVAN MOOKIAH BARATHKUMAR'
TITLE='Tuning and Delay Prediction in Cart Pole Survival Boundaries'
XSL=etree.XSLT(etree.parse(r'C:/Program Files/Microsoft Office/root/Office16/MML2OMML.XSL'))
def esc(t):return __import__('html').escape(str(t))
def tag(t,s):return '<'+t+'>'+s+'</'+t+'>'
def V(s):return tag('mi',esc(s))
def N(s):return tag('mn',str(s))
def O(s):return tag('mo',esc(s))
def R(*s):return tag('mrow',''.join(s))
def sub(a,b):return tag('msub',a+b)
def sup(a,b):return tag('msup',a+b)
def frac(a,b):return tag('mfrac',a+b)
def inv(a):return sup(a,R(O('−'),N(1)))
def tr(a):return sup(a,V('T'))
def hat(a):return tag('mover',a+O('^'))
def numeric(s):
 s=str(s)
 if 'e' in s.lower():
  mant,expo=s.lower().split('e');power=int(expo);exponent=R(O('−'),N(abs(power))) if power<0 else N(power)
  return R(numeric(mant),O('×'),sup(N(10),exponent))
 return R(O('−'),N(s[1:])) if s.startswith('-') else N(s)
def mat(a):return R(O('['),tag('mtable',''.join(tag('mtr',''.join(tag('mtd',numeric(x)) for x in row)) for row in a)),O(']'))
def wrap(body):return '<math xmlns="http://www.w3.org/1998/Math/MathML">'+body+'</math>'
Q,Rm,A,B,P,K,C,F,G,L,S=[V(v) for v in ['Q','R','A','B','P','K','C','F','G','L','Σ']]
TS=sub(V('T'),V('s'));Z=hat(V('z'))
CUSTOM={
 'law':wrap(R(V('u'),O('='),O('−'),K,Z)),
 'care':wrap(R(tr(A),P,O('+'),P,A,O('−'),P,B,inv(Rm),tr(B),P,O('+'),Q,O('='),N(0))),
 'gain':wrap(R(K,O('='),inv(Rm),tr(B),P)),
 'discrete':wrap(R(F,O('='),sup(V('e'),R(A,TS)),O(','),G,O('='),tag('msubsup',O('∫')+N(0)+TS),sup(V('e'),R(A,V('τ'))),B,V('dτ'))),
 'update':wrap(R(Z,sub(O('|'),V('k')),O('='),sub(Z,V('p')),O('+'),L,O('('),V('y'),O('−'),C,sub(Z,V('p')),O(')'))),
 'kfgain':wrap(R(L,O('='),S,tr(C),inv(R(O('('),C,S,tr(C),O('+'),Rm,O(')'))))),
 'fd':wrap(R(sub(V('H'),V('v')),O('('),V('z'),O(')'),O('='),frac(R(O('('),N(1),O('−'),V('α'),O(')'),O('('),N(1),O('−'),inv(V('z')),O(')')),R(TS,O('('),N(1),O('−'),V('α'),inv(V('z')),O(')'))))),
 'dare':wrap(R(P,O('='),tr(F),P,F,O('−'),tr(F),P,G,inv(R(O('('),Rm,TS,O('+'),tr(G),P,G,O(')'))),tr(G),P,F,O('+'),Q,TS)),
 'kd':wrap(R(sub(K,V('d')),O('='),inv(R(O('('),Rm,TS,O('+'),tr(G),P,G,O(')'))),tr(G),P,F)),
 'covariance':wrap(R(sub(Q,V('d')),O('='),tag('msubsup',O('∫')+N(0)+TS),sup(V('e'),R(A,V('τ'))),V('W'),sup(V('e'),R(tr(A),V('τ'))),V('dτ'))),
 'posterior':wrap(R(sub(S,O('+')),O('='),O('('),V('I'),O('−'),L,C,O(')'),sub(S,O('−')))),
 'compensator':wrap(R(sub(V('D'),V('KF')),O('('),V('z'),O(')'),O('='),K,inv(R(O('('),V('I'),O('−'),sub(A,V('c')),inv(V('z')),O(')'))),L)),
 'ac':wrap(R(sub(A,V('c')),O('='),O('('),V('I'),O('−'),L,C,O(')'),O('('),F,O('−'),G,K,O(')'))),
 'delta':wrap(R(V('Δp'),O('='),frac(N(1),V('n')),tag('munderover',O('∑')+R(V('i'),O('='),N(1))+V('n')),O('('),sub(V('Y'),V('Ai')),O('−'),sub(V('Y'),V('Bi')),O(')'))),
 'nees':wrap(R(V('NEES'),O('='),tr(V('e')),inv(sub(P,V('post'))),V('e'))),
 'nis':wrap(R(V('NIS'),O('='),tr(V('ν')),inv(R(O('('),C,sub(P,V('prior')),tr(C),O('+'),Rm,O(')'))),V('ν')))
}
CUSTOM['dualcare']=wrap(R(A,S,O('+'),S,tr(A),O('−'),S,tr(C),inv(V('V')),C,S,O('+'),V('W'),O('='),N(0)))
CUSTOM['observergain']=wrap(R(V('H'),O('='),S,tr(C),inv(V('V'))))
CUSTOM['kfprior']=wrap(R(S,O('='),F,S,tr(F),O('+'),sub(Q,V('d')),O('−'),F,S,tr(C),inv(R(O('('),C,S,tr(C),O('+'),Rm,O(')'))),C,S,tr(F)))
ph=hat(V('p'));zz=sup(V('ζ'),N(2));nn=V('n')
CUSTOM['wilson']=wrap(frac(R(ph,O('+'),frac(zz,R(N(2),nn)),O('±'),V('ζ'),tag('msqrt',R(frac(R(ph,O('('),N(1),O('−'),ph,O(')')),nn),O('+'),frac(zz,R(N(4),sup(nn,N(2))))))),R(N(1),O('+'),frac(zz,nn))))
for name in ['kfgain','nis','kfprior']:
 CUSTOM[name]=CUSTOM[name].replace(V('R'),sub(V('R'),V('m')))
refs=[
 '[1] K. J. Åström and R. M. Murray, Feedback Systems: An Introduction for Scientists and Engineers. Princeton University Press, 2008. https://authors.library.caltech.edu/records/yzs24-xsx88',
 '[2] J. C. Doyle, “Guaranteed margins for LQG regulators,” IEEE Trans. Autom. Control, vol. 23, no. 4, pp. 756–757, 1978, doi: 10.1109/TAC.1978.1101812.',
 '[3] M. Rani and S. S. Kamlu, “Optimal LQG controller design for inverted pendulum systems using a comprehensive approach,” Scientific Reports, vol. 15, art. 4692, 2025, doi: 10.1038/s41598-025-85581-3.',
 '[4] S. Irfan, L. Zhao, S. Ullah, A. Mehmood, and M. F. U. Butt, “Control strategies for inverted pendulum: A comparative analysis of linear, nonlinear, and artificial intelligence approaches,” PLOS ONE, vol. 19, no. 3, e0298093, 2024, doi: 10.1371/journal.pone.0298093.',
 '[5] Z. Yuan et al., “safe-control-gym: A unified benchmark suite for safe learning-based control and reinforcement learning in robotics,” arXiv:2109.06325v4, 2022. https://arxiv.org/abs/2109.06325',
 '[6] Y. Duan, X. Chen, R. Houthooft, J. Schulman, and P. Abbeel, “Benchmarking deep reinforcement learning for continuous control,” Proc. ICML, PMLR, vol. 48, pp. 1329–1338, 2016. https://proceedings.mlr.press/v48/duan16.html',
 '[7] C. F. Van Loan, “Computing integrals involving the matrix exponential,” IEEE Trans. Autom. Control, vol. 23, no. 3, pp. 395–404, 1978, doi: 10.1109/TAC.1978.1101743.',
 '[8] E. B. Wilson, “Probable inference, the law of succession, and statistical inference,” J. Amer. Stat. Assoc., vol. 22, no. 158, pp. 209–212, 1927, doi: 10.1080/01621459.1927.10502953.',
 '[9] Q. McNemar, “Note on the sampling error of the difference between correlated proportions or percentages,” Psychometrika, vol. 12, no. 2, pp. 153–157, 1947. https://pubmed.ncbi.nlm.nih.gov/20254758/',
 '[10] S. Holm, “A simple sequentially rejective multiple test procedure,” Scandinavian J. Stat., vol. 6, no. 2, pp. 65–70, 1979. https://sci2s.ugr.es/keel/pdf/specific/articulo/0052_001.pdf'
]
def row(model,kind,scene):return next(r for r in summary if r['model']==model and r['controller']==kind and r['scenario']==scene)
def val(model,kind,scene,key='success_rate'):return float(row(model,kind,scene)[key])
def pct(x):return f'{100*float(x):.1f}%'
def fm(x,n=3):
 try:return f'{float(x):.{n}g}' if math.isfinite(float(x)) else 'NA'
 except:return 'NA'
def pairedrow(model,a,b):return next(r for r in paired if r['model']==model and r['scenario']=='joint_d60_p5' and r['controller_a']==a and r['controller_b']==b)
class Builder:
 def __init__(self,main):
  self.doc=Document();self.main=main;self.eqcount=0;self.lines=[]
  sec=self.doc.sections[0];sec.page_width=Inches(8.5);sec.page_height=Inches(11);sec.top_margin=Inches(.65);sec.bottom_margin=Inches(.7);sec.left_margin=sec.right_margin=Inches(.7)
  for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Caption']:
   st=self.doc.styles[name];st.font.name='Times New Roman';st.font.color.rgb=RGBColor(0,0,0);st._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'Times New Roman')
  normal=self.doc.styles['Normal'];normal.font.size=Pt(10 if main else 10.5);normal.paragraph_format.space_after=Pt(3 if main else 6);normal.paragraph_format.line_spacing=1
  normal.paragraph_format.widow_control=True
  self.doc.styles['Title'].font.size=Pt(22 if main else 20);self.doc.styles['Title'].font.bold=False
  for hn,size in [('Heading 1',10 if main else 13),('Heading 2',10 if main else 11)]:
   st=self.doc.styles[hn];st.font.size=Pt(size);st.font.bold=True;st.paragraph_format.space_before=Pt(9);st.paragraph_format.space_after=Pt(4);st.paragraph_format.keep_with_next=True
  self.doc.styles['Caption'].font.size=Pt(8 if main else 9);self.doc.styles['Caption'].font.italic=False
  self.doc.core_properties.author=AUTHOR;self.doc.core_properties.title=TITLE if main else TITLE+' Mathematical Supplement'
  self.title(TITLE if main else 'Detailed Derivations and Reproducibility Supplement')
  p=self.doc.add_paragraph(AUTHOR);p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_after=Pt(12)
  for r in p.runs:r.font.size=Pt(11)
  if main:
   sec=self.doc.add_section(WD_SECTION_START.CONTINUOUS);cols=sec._sectPr.find(qn('w:cols'));cols.set(qn('w:num'),'2');cols.set(qn('w:space'),'360')
  foot=self.doc.sections[0].footer.paragraphs[0];foot.alignment=WD_ALIGN_PARAGRAPH.CENTER;f=OxmlElement('w:fldSimple');f.set(qn('w:instr'),'PAGE');foot._p.append(f)
 def title(self,text):
  p=self.doc.add_paragraph(text,'Title');p.alignment=WD_ALIGN_PARAGRAPH.CENTER;self.lines.append('# '+text)
 def h(self,text,level=1):
  p=self.doc.add_paragraph(text,'Heading '+str(level));p.alignment=WD_ALIGN_PARAGRAPH.CENTER if self.main and level==1 else WD_ALIGN_PARAGRAPH.LEFT;self.lines.append('## '+text)
 def p(self,text,boldlead=None):
  p=self.doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
  if boldlead and text.startswith(boldlead):p.add_run(boldlead).bold=True;p.add_run(text[len(boldlead):])
  else:p.add_run(text)
  p.paragraph_format.first_line_indent=Inches(.12) if self.main and not boldlead else 0
  if text.startswith('TABLE '):
   p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.first_line_indent=0;p.paragraph_format.keep_with_next=True
   for r in p.runs:r.font.size=Pt(8.5)
  self.lines.append(text);return p
 def reference(self,text):
  p=self.p(text);p.alignment=WD_ALIGN_PARAGRAPH.LEFT;p.paragraph_format.left_indent=Inches(.16);p.paragraph_format.first_line_indent=Inches(-.16);p.paragraph_format.space_after=Pt(2)
  for r in p.runs:r.font.size=Pt(8.5)
 def eq(self,key,custom=False):
  mathml=CUSTOM[key] if custom else __import__('html').unescape(MATH[key]);result=XSL(etree.fromstring(mathml.encode()));nodes=result.xpath('//*[local-name()="oMath"]');assert nodes
  p=self.doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_before=Pt(3);p.paragraph_format.space_after=Pt(5)
  p._p.append(copy.deepcopy(nodes[0]));self.eqcount+=1;p.add_run('  ('+('' if self.main else 'S')+str(self.eqcount)+')').font.size=Pt(9)
  self.lines.append('[Editable equation '+str(self.eqcount)+': '+key+']')
 def matrix(self,name,data):
  mm=wrap(R(V(name),O('='),mat([[fm(x,5) for x in r] for r in data])))
  result=XSL(etree.fromstring(mm.encode()));p=self.doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p._p.append(copy.deepcopy(result.xpath('//*[local-name()="oMath"]')[0]));self.eqcount+=1;p.add_run('  (S'+str(self.eqcount)+')').font.size=Pt(9)
 def figure(self,i):
  cap=captions[i-1];p=self.doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.keep_with_next=True
  from PIL import Image
  im=Image.open(OUT/'figures'/(cap['name']+'.png'));w=3.38 if self.main else 7.0;h=w*im.height/im.width
  if h>(4.25 if self.main else 4.7):w*=((4.25 if self.main else 4.7)/h)
  p.add_run().add_picture(str(OUT/'figures'/(cap['name']+'.png')),width=Inches(w))
  number=i if self.main else 'S'+str({10:1,11:2,8:3,9:4}.get(i,i))
  p=self.doc.add_paragraph('Fig. '+str(number)+'. '+cap['caption'],'Caption');p.paragraph_format.keep_together=True
  self.lines.append('Fig. '+str(number)+'. '+cap['caption'])
 def table(self,headers,rows,widths=None):
  t=self.doc.add_table(rows=1,cols=len(headers));t.autofit=False
  width=3.4 if self.main else 7.1;widths=widths or [width/len(headers)]*len(headers)
  for c,w in zip(t.columns,widths):c.width=Inches(w)
  for idx,rr in enumerate([headers]+rows):
   cells=t.rows[0].cells if idx==0 else t.add_row().cells
   for j,(cell,text) in enumerate(zip(cells,rr)):
    cell.width=Inches(widths[j]);cell.vertical_alignment=1;p=cell.paragraphs[0];p.paragraph_format.space_after=Pt(0);p.paragraph_format.line_spacing=1
    p.paragraph_format.keep_with_next=(idx<len(rows)) if len(rows)<=16 else idx==0
    run=p.add_run(str(text));run.font.size=Pt(7.5 if self.main else 8.5);run.font.bold=idx==0
    tcPr=cell._tc.get_or_add_tcPr();borders=OxmlElement('w:tcBorders')
    for edge in ['top','bottom','left','right']:
     x=OxmlElement('w:'+edge);x.set(qn('w:val'),'single');x.set(qn('w:sz'),'4');x.set(qn('w:color'),'D9D9D9');borders.append(x)
    tcPr.append(borders);mar=OxmlElement('w:tcMar')
    for edge in ['top','bottom','left','right']:
     x=OxmlElement('w:'+edge);x.set(qn('w:w'),'35' if edge in ['top','bottom'] else '55');x.set(qn('w:type'),'dxa');mar.append(x)
    tcPr.append(mar)
    if idx==0 or idx%2==0:
     shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'E7EDF1' if idx==0 else 'F6F7F8');tcPr.append(shade)
   trpr=t.rows[idx]._tr.get_or_add_trPr();cant=OxmlElement('w:cantSplit');trpr.append(cant)
   if idx==0:repeat=OxmlElement('w:tblHeader');trpr.append(repeat)
  self.doc.add_paragraph().paragraph_format.space_after=Pt(3)
 def save(self,name):
  if self.main:
   # A terminal continuous section balances the journal's final text columns.
   tail=self.doc.add_section(WD_SECTION_START.CONTINUOUS)
   cols=tail._sectPr.find(qn('w:cols'));cols.set(qn('w:num'),'1')
  # Remove inherited Office theme rules and paragraph borders, including the
  # default Title underline that can otherwise reappear in native Word.
  for tree in [self.doc._element,self.doc.styles._element]:
   for node in list(tree.iter(qn('w:pBdr'))):node.getparent().remove(node)
   for node in tree.iter(qn('w:rFonts')):
    for attr in ['asciiTheme','hAnsiTheme','eastAsiaTheme','cstheme','csTheme']:
     node.attrib.pop(qn('w:'+attr),None)
    for attr in ['ascii','hAnsi','eastAsia','cs']:node.set(qn('w:'+attr),'Times New Roman')
  for style_name in ['Title','Heading 1','Heading 2','Normal','Caption']:
   st=self.doc.styles[style_name];st.font.color.rgb=RGBColor(0,0,0)
   for node in st._element.iter(qn('w:color')):
    for attr in ['themeColor','themeTint','themeShade']:node.attrib.pop(qn('w:'+attr),None)
  settings=self.doc.settings.element
  for node in list(settings.iter(qn('w:updateStyles'))):node.getparent().remove(node)
  flag=OxmlElement('w:updateStyles');flag.set(qn('w:val'),'false');settings.append(flag)
  self.doc.core_properties.last_modified_by=AUTHOR
  path=OUT/(name+'.docx');self.doc.save(path);(OUT/(name+'.md')).write_text('\n\n'.join(self.lines),encoding='utf-8')
  with zipfile.ZipFile(path) as z:
   xml=z.read('word/document.xml').decode();assert '<m:oMath' in xml;assert AUTHOR in xml;assert 'AI assistance' not in xml and 'AI credit' not in xml
  print(name,'native equations',self.eqcount,flush=True)

