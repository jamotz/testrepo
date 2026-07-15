from PIL import Image, ImageDraw, ImageFont
import pathlib
SP=pathlib.Path("/tmp/claude-0/-home-user-testrepo/ddda76a0-85c4-5287-b8c8-caa7c709d458/scratchpad")
try: font=ImageFont.load_default(size=15)
except: font=ImageFont.load_default()

def sheet(files, out, cols=4, cw=330, th=210):
    lh=30; ch=th+lh
    rows=(len(files)+cols-1)//cols
    W=cols*cw; H=rows*ch
    sheet=Image.new("RGB",(W,H),(24,24,28))
    d=ImageDraw.Draw(sheet)
    for i,f in enumerate(files):
        cx=(i%cols)*cw; cy=(i//cols)*ch
        try:
            im=Image.open(f).convert("RGB")
            im.thumbnail((cw-16,th-16))
            ox=cx+(cw-im.width)//2; oy=cy+lh+(th-im.height)//2
            sheet.paste(im,(ox,oy))
        except Exception as e:
            d.text((cx+8,cy+lh+20),f"[err]",fill=(255,120,120),font=font)
        d.rectangle([cx,cy,cx+cw-1,cy+ch-1],outline=(70,70,78))
        name=pathlib.Path(f).name
        label=f"{i+1}. "+(name if len(name)<=34 else name[:31]+"...")
        d.rectangle([cx,cy,cx+cw-1,cy+lh],fill=(15,15,18))
        d.text((cx+6,cy+8),label,fill=(230,230,235),font=font)
    sheet.save(out)
    print(out.name, sheet.size, len(files),"imgs")

base=pathlib.Path("reference/oxfam")
final=[str(base/"page-00-landing/Landing Page 2022-12-18 at 6.00.15 PM.png"),
 str(base/"page-01/FAQ 2022-12-18 at 6.14.15 PM.png"),
 str(base/"page-02/Feedback 2022-12-18 at 6.21.18 PM.png"),
 str(base/"page-03/MyOxfam 2022-12-18 at 6.21.52 PM.png"),
 str(base/"page-03/MyOxfam Portal 2022-12-18 at 6.23.43 PM.png"),
 str(base/"page-04/Fundraising 2022-12-18 at 7.19.09 PM.png"),
 str(base/"page-05/Media 2022-12-18 at 7.20.00 PM.png"),
 str(base/"page-06/Report 2022-12-18 at 6.25.48 PM.png")]
sheet(final, SP/"sheet_final.png", cols=4, cw=330, th=230)
proc=sorted(str(p) for p in (base/"process").iterdir() if p.suffix.lower() in (".png",".jpg",".jpeg",".webp"))
sheet(proc, SP/"sheet_process.png", cols=4, cw=330, th=210)
# save the ordered process list so I can map indices later
(SP/"proc_list.txt").write_text("\n".join(f"{i+1}\t{pathlib.Path(p).name}" for i,p in enumerate(proc)))
