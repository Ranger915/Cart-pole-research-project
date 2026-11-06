import formatter as f

def main():
 b=f.Builder(False);body=b.p('Evidence [3], a range [1]–[2], then [3].');b.eq('care',True)
 b.doc.add_picture(str(f.OUT/'figures/fd_sweep.png'),width=f.Inches(1))
 for i,name in [(1,'A'),(2,'B'),(3,'C')]:b.reference(f'[{i}] {name}')
 math=b.doc._element.xml.count('<m:oMath>');images=len(b.doc.inline_shapes)
 assert b.renumber_references()==[3,1,2]
 assert body.text=='Evidence [1], a range [2], [3], then [1].'
 assert b.doc._element.xml.count('<m:oMath>')==math and len(b.doc.inline_shapes)==images
 assert [p.text for p in b.doc.paragraphs if p.text in ['[1] C','[2] A','[3] B']]==['[1] C','[2] A','[3] B']
 print('First-citation ordering, ranges, native equations and images verified')
if __name__=='__main__':main()
