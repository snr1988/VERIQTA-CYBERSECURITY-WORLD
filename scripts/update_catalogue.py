from pathlib import Path
import html,json,re,subprocess
from urllib.parse import quote
ROOT=Path(__file__).resolve().parents[1]
manifest=ROOT/'assets/pdf-covers/catalogue.json'
entries=json.loads(manifest.read_text())
known={e.get('pdf') for e in entries}
for p in sorted(ROOT.glob('*/*.pdf')):
 rel=p.relative_to(ROOT).as_posix()
 if rel not in known:
  entries.append({'title':p.stem,'pdf':rel,'cover':f'assets/pdf-covers/{p.parent.name.lower()}-{p.stem.lower().replace(" ","-")}.jpg'})
cells=[];available=0
for e in entries:
 pdf=ROOT/e['pdf'] if e.get('pdf') else None
 cover=ROOT/e['cover']
 if pdf and pdf.is_file():
  available+=1
  if not cover.exists() or pdf.stat().st_mtime>cover.stat().st_mtime:
   cover.parent.mkdir(parents=True,exist_ok=True)
   subprocess.run(['pdftoppm','-f','1','-singlefile','-scale-to','1000','-jpeg','-jpegopt','quality=85',str(pdf),str(cover.with_suffix(''))],check=True)
 if not cover.is_file(): raise SystemExit(f'Missing cover: {cover}')
 title=html.escape(e['title'],quote=True)
 image=f'<img src="{quote(e["cover"],safe="/")}" alt="{title}" title="{title}" width="100%" />'
 content=f'<a href="{quote(e["pdf"],safe="/")}">{image}</a>' if pdf and pdf.is_file() else image+'<br /><strong>PDF not available</strong>'
 if e.get('new_row') and len(cells)%3:
  cells.extend(['<td></td>']*(3-len(cells)%3))
 cells.append('<td align="center" valign="top" width="33%">'+content+'</td>')
rows=[]
for i in range(0,len(cells),3):
 row=cells[i:i+3];rows.append('<tr>\n'+'\n'.join(row+['<td></td>']*(3-len(row)))+'\n</tr>')
readme=ROOT/'README.md'
s=readme.read_text()
s=re.sub(r'<table width="100%">.*?</table>','<table width="100%">\n'+'\n'.join(rows)+'\n</table>',s,count=1,flags=re.S)
readme.write_text(s)
manifest.write_text(json.dumps(entries,indent=2,ensure_ascii=False)+'\n')
print(f'{available} PDFs available; {len(entries)-available} covers without a PDF')
