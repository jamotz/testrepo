from PIL import Image
import base64, io, pathlib, re
root=pathlib.Path("site"); ref=pathlib.Path("reference/oxfam")
sp=pathlib.Path("/tmp/claude-0/-home-user-testrepo/ddda76a0-85c4-5287-b8c8-caa7c709d458/scratchpad")
src=(sp/"oxfam-hifi.src.html").read_text()

def embed(relpath, maxw, q=82):
    im=Image.open(ref/relpath)
    if im.mode in ("RGBA","P","LA"): im=im.convert("RGB")
    elif im.mode!="RGB": im=im.convert("RGB")
    if im.width>maxw: im=im.resize((maxw,round(im.height*maxw/im.width)), Image.LANCZOS)
    b=io.BytesIO(); im.save(b,"JPEG",quality=q,optimize=True)
    return "data:image/jpeg;base64,"+base64.b64encode(b.getvalue()).decode()

M={
 "IMG_HERO":("process/hill.webp",1500,80),
 "IMG_PERSONA":("process/Screen Shot 2023-10-06 at 12.48.30 PM.png",1200,84),
 "IMG_WF_IA":("process/Screen Shot 2023-09-30 at 2.48.04 PM.png",1100,86),
 "IMG_WF_LANDING":("process/Screen Shot 2023-09-30 at 2.52.45 PM.png",1100,86),
 "IMG_WF_PORTAL":("process/Screen Shot 2023-11-07 at 2.18.07 PM.png",1100,86),
 "IMG_ANNOTATED":("process/Screen Shot 2022-12-18 at 7.08.08 PM.png",1200,84),
 "IMG_FINAL_LANDING":("page-00-landing/Landing Page 2022-12-18 at 6.00.15 PM.png",1200,82),
 "IMG_FINAL_FAQ":("page-01/FAQ 2022-12-18 at 6.14.15 PM.png",1000,82),
 "IMG_FINAL_FEEDBACK":("page-02/Feedback 2022-12-18 at 6.21.18 PM.png",1000,82),
 "IMG_FINAL_MYOXFAM":("page-03/MyOxfam 2022-12-18 at 6.21.52 PM.png",1000,82),
 "IMG_FINAL_PORTAL":("page-03/MyOxfam Portal 2022-12-18 at 6.23.43 PM.png",1200,82),
 "IMG_FINAL_FUNDRAISING":("page-04/Fundraising 2022-12-18 at 7.19.09 PM.png",1000,82),
 "IMG_FINAL_MEDIA":("page-05/Media 2022-12-18 at 7.20.00 PM.png",1000,82),
 "IMG_FINAL_REPORT":("page-06/Report 2022-12-18 at 6.25.48 PM.png",1000,82),
}
for k,(f,w,q) in M.items():
    src=src.replace("%%"+k+"%%", embed(f,w,q))
    print("embedded",k)

# fonts
faces=[("Space Grotesk",400,"space-grotesk-400"),("Space Grotesk",500,"space-grotesk-500"),("Space Grotesk",700,"space-grotesk-700"),
       ("IBM Plex Sans",400,"ibm-plex-sans-400"),("IBM Plex Sans",500,"ibm-plex-sans-500"),("IBM Plex Sans",600,"ibm-plex-sans-600"),
       ("IBM Plex Mono",400,"ibm-plex-mono-400"),("IBM Plex Mono",500,"ibm-plex-mono-500")]
fcss=[]
for fam,wt,fn in faces:
    b=base64.b64encode((root/"public/fonts"/f"{fn}.woff2").read_bytes()).decode()
    fcss.append(f'@font-face{{font-family:"{fam}";font-style:normal;font-weight:{wt};font-display:swap;src:url(data:font/woff2;base64,{b}) format("woff2")}}')
src=src.replace("/*FONTS*/","\n".join(fcss))
logo=(root/"public/brand/motz-white.svg").read_text()
logo=re.sub(r'fill="#[0-9A-Fa-f]{6}"','fill="currentColor"',logo)
logo=re.sub(r'<svg ','<svg style="display:block;width:100%;height:100%" ',logo,count=1)
src=src.replace("<!--LOGO-->",logo)

out=sp/"oxfam-hifi.html"; out.write_text(src)
left=re.findall(r"%%[A-Z0-9_]+%%",src)
print("wrote",len(src)//1024,"KB; unresolved:",left,"| FONTS/LOGO left:",src.count("/*FONTS*/")+src.count("<!--LOGO-->"))
