"""Build G06_HCI_CA3_Presentation.html: a self-contained 16:9 deck for the HCI CA-3 (Raktdaan).

Usage: python capture_screens.py   (only when raktdaan.html changes)
       python build_presentation.py
Controls in the deck: → / Space / PageDown = next, ← / PageUp = previous, Home / End, F = full screen.
Arrows appear only while hovering the left/right edge; the cursor hides after 2 s of no movement.
Layout follows the group's Cyber Security CA-2 deck (../build_presentation.py); colours and fonts are Raktdaan's.
"""
import base64
import io
import re
from pathlib import Path

from PIL import Image

HERE = Path(__file__).parent
ASSETS = HERE / "presentation_assets"
OUT = HERE / "G06_HCI_CA3_Presentation.html"


def png_uri(path, max_w):
    im = Image.open(path)
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def file_uri(path, mime):
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


LOGO = png_uri(HERE.parent / "sit-logo.png", 2000)
SCREENS = sorted(p.stem for p in (ASSETS / "screens").glob("*.webp"))  # 2x phone captures (864 x 1874)
# each screen is embedded once as a CSS class and reused by the flow slides and the overview grid
SCREEN_CSS = "".join(f'.s-{s}{{background-image:url({file_uri(ASSETS / "screens" / f"{s}.webp", "image/webp")})}}'
                     for s in SCREENS)
COMPONENTS = file_uri(ASSETS / "figma" / "components.webp", "image/webp")
ICONS = file_uri(ASSETS / "figma" / "icons.webp", "image/webp")

# Design tokens are read from the prototype itself so the swatches always match the code.
SRC = (HERE / "raktdaan.html").read_text(encoding="utf-8")
TOK = dict(re.findall(r"--([a-z-]+):\s*(#[0-9A-Fa-f]{6})", SRC.split("}", 1)[0]))


def contrast(fg, bg):
    def lum(h):
        c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    hi, lo = sorted((lum(fg), lum(bg)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


TITLE = "Raktdaan: A Blood Donation and Blood Bank Mobile App — UI/UX Design in Figma with an HTML &amp; CSS Prototype"

CSS = """
@font-face{font-family:"Figtree";src:url(FIGTREE) format("woff2");font-weight:400 700;font-display:block}
@font-face{font-family:"Fraunces";src:url(FRAUNCES) format("woff2");font-weight:600 700;font-display:block}
:root{--ink:#2A1E1C;--muted:#6B5A55;--brand:#C2362F;--rt:#A82E28;--wine:#4A1D24;--line:#EADFD6;--canvas:#FBF6F1;
 --sunken:#F3EAE3;--blush:#FBE8E2;--sage:#2F6B4B;--sage-soft:#E1EEE5}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:100%;height:100%;background:#fff;overflow:hidden}
body{font-family:"Figtree","Segoe UI",Calibri,Arial,sans-serif;color:var(--ink);-webkit-font-smoothing:antialiased}
body.idle,body.idle *{cursor:none!important}
#stage{position:absolute;left:50%;top:50%;width:1600px;height:900px;transform-origin:center center}
.slide{position:absolute;inset:0;opacity:0;visibility:hidden;transition:opacity .25s ease;padding:66px 90px 64px;display:flex;flex-direction:column;background:#fff}
.content{flex:1;display:flex;flex-direction:column;justify-content:center;padding-bottom:22px}
body.static .slide{transition:none}
.slide.active{opacity:1;visibility:visible}
.frame{position:absolute;inset:18px;border:2.5px solid var(--ink);border-radius:34px;pointer-events:none}
.kicker{font-size:19px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--rt);margin-bottom:8px}
h2{font-family:"Fraunces",Georgia,serif;font-size:46px;font-weight:600;line-height:1.12;letter-spacing:-.01em;margin-bottom:10px}
h3{font-size:26px;font-weight:700;color:var(--wine);margin-bottom:10px}
p,li{font-size:27px;line-height:1.4}
ul{padding-left:28px}
li{margin-bottom:12px}
li::marker{color:var(--brand)}
b{font-weight:700}
.muted{color:var(--muted)}
.small{font-size:22px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:40px}
.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:26px}
.card{border:1.5px solid var(--line);border-radius:20px;padding:22px 24px;background:#fff}
.card.tint{background:var(--canvas)}
.card p,.card li{font-size:22px;line-height:1.38}
.card li{margin-bottom:6px}
.persona{font-size:19px;margin-bottom:10px;min-height:54px;line-height:1.4}
.chips{display:flex;gap:12px;flex-wrap:wrap}
.chip{border:1.5px solid var(--brand);color:var(--rt);border-radius:999px;padding:8px 20px;font-size:22px;font-weight:600}
.chip.sm{font-size:18px;padding:6px 15px}
.callout{border-left:6px solid var(--brand);background:var(--blush);padding:18px 24px;border-radius:0 14px 14px 0;font-size:24px;line-height:1.38}
table{border-collapse:collapse;width:100%}
th{font-size:17px;text-transform:uppercase;letter-spacing:1px;color:var(--wine);text-align:left;padding:10px 12px;border-bottom:2px solid var(--brand);background:var(--canvas)}
td{font-size:20px;padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top;line-height:1.3}
.flow{display:flex;align-items:stretch;gap:10px}
.flow .step{flex:1;border:1.5px solid var(--line);border-radius:16px;padding:14px 16px;background:var(--canvas)}
.flow .step b{display:block;color:var(--rt);font-size:16px;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px}
.flow .step span{font-size:19px;line-height:1.3;display:block}
.flow .arrow{align-self:center;color:var(--brand);font-size:26px}
.note{font-size:19px;color:var(--muted);margin-top:18px;line-height:1.35}
/* phone screens */
.phones{display:flex;gap:26px;align-items:flex-start}
.phones figure{text-align:center}
.scr{aspect-ratio:864/1874;margin:0 auto;background-size:contain;background-repeat:no-repeat;filter:drop-shadow(0 12px 16px rgba(42,30,28,.22))}
.phones figcaption{font-size:18px;font-weight:600;color:var(--muted);margin-top:14px}
.flowgrid{display:grid;grid-template-columns:auto 1fr;align-items:center;gap:44px}
.flowgrid.wide{gap:64px}
.notes{padding-left:0;list-style:none}
.notes li{font-size:21px;line-height:1.36;margin-bottom:13px;padding-left:16px;border-left:3px solid var(--blush)}
.wide .notes li{font-size:23px;margin-bottom:16px;max-width:760px}
.notes li b{color:var(--wine)}
.ptitle{font-size:15px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted);margin:20px 0 10px}
/* design system */
.sw-group{margin-bottom:14px}
.sw-label{font-size:15px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted);margin-bottom:8px}
.sw-row{display:flex;gap:12px}
.sw{width:112px}
.sw i{display:block;height:50px;border-radius:12px;border:1px solid rgba(42,30,28,.12)}
.sw span{display:block;font-size:15px;font-weight:600;margin-top:5px;line-height:1.2}
.sw small{font-size:14px;color:var(--muted)}
.spec{border:1.5px solid var(--line);border-radius:16px;padding:14px 18px;margin-bottom:12px;background:var(--canvas)}
.spec .fam{font-size:15px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted)}
.spec .serif{font-family:"Fraunces",Georgia,serif;font-weight:600;font-size:34px;line-height:1.15;margin:4px 0}
.spec .sans{font-size:22px;line-height:1.35;margin:6px 0}
.spec .styles{font-size:16px;color:var(--muted)}
.shapes{display:flex;gap:14px;align-items:flex-end}
.shapes div{width:84px;height:56px;background:var(--blush);border:1.5px solid var(--brand);display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:600;color:var(--rt)}
.shapes div.sh{background:#fff;border:0}
/* IA */
.ia{display:grid;grid-template-columns:repeat(5,1fr);gap:18px}
.ia .card{padding:18px 18px;background:var(--canvas)}
.ia .num{font-family:"Fraunces",Georgia,serif;font-size:40px;font-weight:700;color:var(--brand);line-height:1}
.ia h3{font-size:23px;margin:8px 0 10px}
.ia ol{list-style:none}
.ia li{font-size:21px;line-height:1.3;margin-bottom:7px}
.bnav{display:flex;justify-content:space-around;align-items:center;border:1.5px solid var(--line);border-radius:18px;padding:12px 20px;width:660px;background:#fff}
.bnav span{font-size:19px;font-weight:600;color:var(--muted);text-align:center}
.bnav span.req{background:var(--brand);color:#fff;border-radius:12px;padding:8px 16px}
.bnav span.on{background:var(--blush);color:var(--ink);border-radius:999px;padding:6px 16px}
.paths{font-size:22px;line-height:1.6}
.paths b{color:var(--wine)}
/* evaluation */
.pass{color:var(--sage);font-weight:700}
.nw{white-space:nowrap}
table.tight td{font-size:19px;padding:8px 10px}
table.tight th{font-size:15px;padding:8px 10px}
.aa{display:inline-block;width:40px;text-align:center;border-radius:7px;font-weight:700;font-size:17px;padding:1px 0;margin-right:10px;border:1px solid rgba(42,30,28,.12)}
/* code */
.code{background:var(--ink);color:#F6EDE6;border-radius:18px;padding:22px 26px;font-family:Consolas,"Cascadia Mono","Courier New",monospace;font-size:17.5px;line-height:1.5;white-space:pre}
.code .c{color:#C9B4AA}
.code .k{color:#F2C1AB}
.code .s{color:#9ED3B4}
.thumbs{display:grid;grid-template-columns:repeat(5,84px);gap:12px 12px}
.thumbs .scr{width:84px;filter:drop-shadow(0 4px 6px rgba(42,30,28,.2))}
.refs li{font-size:18px;line-height:1.3;margin-bottom:6px}
/* title slide (matches the group's template) */
.title-slide{text-align:center;padding:36px 110px}
.title-slide .logo{height:170px;margin:26px auto 0;display:block}
.title-slide .course{font-size:34px;font-weight:700;margin-top:28px}
.title-slide .topic{font-size:33px;font-weight:700;line-height:1.3;margin:22px auto 0;max-width:1300px}
.title-slide .group{font-size:30px;margin-top:26px}
.title-slide .names{font-size:26px;line-height:1.7;margin-top:10px}
.title-slide .guide{font-size:26px;margin-top:16px}
.title-slide .foot{position:absolute;left:0;right:0;bottom:38px;font-size:19px}
/* navigation: invisible until hovered */
.nav{position:fixed;top:0;bottom:0;width:12vw;z-index:10;display:flex;align-items:center;cursor:pointer;opacity:0;transition:opacity .2s ease}
.nav:hover{opacity:1}
.nav.left{left:0;justify-content:flex-start;padding-left:2vw}
.nav.right{right:0;justify-content:flex-end;padding-right:2vw}
.nav span{width:58px;height:58px;border-radius:50%;background:rgba(42,30,28,.55);color:#fff;font-size:30px;display:flex;align-items:center;justify-content:center;line-height:1}
/* print / PDF: one slide per 1600x900 page */
@media print{
 @page{size:1600px 900px;margin:0}
 html,body{width:1600px;height:auto;overflow:visible}
 #stage{position:static;transform:none!important;width:1600px;height:auto}
 .slide{position:relative;inset:auto;width:1600px;height:900px;opacity:1;visibility:visible;transition:none;break-after:page}
 .nav{display:none}
 *{-webkit-print-color-adjust:exact;print-color-adjust:exact}
}
"""

JS = """
const slides=[...document.querySelectorAll('.slide')];let cur=0;
function fit(){const s=Math.min(innerWidth/1600,innerHeight/900);
 document.getElementById('stage').style.transform=`translate(-50%,-50%) scale(${s})`;}
function show(i){cur=Math.max(0,Math.min(slides.length-1,i));
 slides.forEach((el,k)=>el.classList.toggle('active',k===cur));history.replaceState(null,'','#'+(cur+1));}
addEventListener('keydown',e=>{
 if(['ArrowRight','PageDown',' ','Enter'].includes(e.key)){e.preventDefault();show(cur+1);}
 else if(['ArrowLeft','PageUp','Backspace'].includes(e.key)){e.preventDefault();show(cur-1);}
 else if(e.key==='Home')show(0);else if(e.key==='End')show(slides.length-1);
 else if(e.key==='f'||e.key==='F'){document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen();}});
document.querySelector('.nav.left').onclick=()=>show(cur-1);
document.querySelector('.nav.right').onclick=()=>show(cur+1);
if(location.search.includes("static"))document.body.classList.add("static");
let idle;addEventListener('mousemove',()=>{document.body.classList.remove('idle');clearTimeout(idle);
 idle=setTimeout(()=>document.body.classList.add('idle'),2000);});
addEventListener('resize',fit);fit();
show((parseInt(location.hash.slice(1))||1)-1);
"""


def slide(body, cls=""):
    if "</h2>" in body:  # centre everything below the heading vertically
        top, rest = body.split("</h2>", 1)
        body = f'{top}</h2><div class="content">{rest}</div>'
    return f'<section class="slide {cls}"><div class="frame"></div>{body}</section>'


def head(kicker, title):
    return f'<div class="kicker">{kicker}</div><h2>{title}</h2>'


def screen(sid, height, label):
    return f'<div class="scr s-{sid}" style="height:{height}px" role="img" aria-label="{label}"></div>'


def phones(items, height):
    return '<div class="phones">' + "".join(
        f'<figure>{screen(sid, height, label)}<figcaption>{label}</figcaption></figure>'
        for sid, label in items) + "</div>"


def flow_slide(kicker, title, screens, height, notes, principles):
    items = "".join(f"<li><b>{lab}</b> — {txt}</li>" for lab, txt in notes)
    chips = "".join(f'<span class="chip sm">{p}</span>' for p in principles)
    wide = " wide" if len(screens) <= 2 else ""  # fewer phones -> more room for the notes
    return slide(head(kicker, title) + f"""
<div class="flowgrid{wide}">
 {phones(screens, height)}
 <div><ul class="notes">{items}</ul><div class="ptitle">HCI principles applied</div><div class="chips">{chips}</div></div>
</div>""")


def swatches(label, names):
    cells = "".join(f'<div class="sw"><i style="background:{TOK[n]}"></i><span>{n}</span><small>{TOK[n]}</small></div>'
                    for n in names)
    return f'<div class="sw-group"><div class="sw-label">{label}</div><div class="sw-row">{cells}</div></div>'


def contrast_rows():
    rows = [("Primary text / canvas", "text-primary", "bg-canvas", "Headings, body"),
            ("Secondary text / canvas", "text-secondary", "bg-canvas", "Supporting text"),
            ("White / brand red", "text-on-brand", "brand", "Primary buttons"),
            ("Brand text / blush", "text-brand", "bg-blush", "Critical tag"),
            ("White / wine", "text-on-brand", "bg-wine", "Matching screen"),
            ("Primary text / white", "text-primary", "bg-surface", "Cards, inputs"),
            ("Brand text / canvas", "text-brand", "bg-canvas", "Links: “Change”, “Sign in”"),
            ("Secondary text / sunken", "text-secondary", "bg-sunken", "Neutral tag")]
    out = []
    for name, fg, bg, use in rows:
        r = contrast(TOK[fg], TOK[bg])
        assert r >= 4.5, f"{name} is {r:.2f}:1 - below WCAG AA, do not label it Pass"
        verdict = '<span class="pass">Pass</span>'
        out.append(f'<tr><td><span class="aa" style="background:{TOK[bg]};color:{TOK[fg]}">Aa</span>{name}</td>'
                   f'<td>{use}</td><td class="nw"><b>{r:.1f} : 1</b></td><td>{verdict}</td></tr>')
    return "".join(out)


SLIDES = [
    # 1 — title, same layout as the group's template (+ Guided by)
    slide(f"""
<img class="logo" src="{LOGO}" alt="Symbiosis Institute of Technology, Pune">
<div class="course">Human–Computer Interaction — CA-3</div>
<div class="topic">{TITLE}</div>
<div class="group">Group Number: Group – 06</div>
<div class="names">Raghav Sonchhatra – PRN 23070122172<br>Sanidhya Awasthi – PRN 23070122192<br>Faheemuddin Sayyed – PRN 23070122196</div>
<div class="guide">Guided by: <b>Dr. Sudhanshu Gonge</b></div>
<div class="foot">HCI CA-3 — PPT · Figma Design · HTML &amp; CSS Code &nbsp;|&nbsp; Department of Computer Engineering &nbsp;|&nbsp; Academic Year 2026–27</div>
""", "title-slide"),

    # 2 — problem
    slide(head("Problem statement", "Finding blood still runs on phone calls and forwards") + """
<div class="grid2" style="grid-template-columns:1fr 1.05fr;align-items:center">
 <div style="display:grid;gap:18px">
  <div class="card"><h3>Patients’ families</h3><p>An urgent need turns into phone calls and forwarded posts. Nobody can tell who has seen the request or who is on the way.</p></div>
  <div class="card"><h3>Willing donors</h3><p>They do not know which centre needs their blood group, whether they are eligible today, or when a slot is free.</p></div>
  <div class="card"><h3>Blood centres</h3><p>Stock levels are hidden from donors, and donors rarely hear what happened to their blood — so fewer come back.</p></div>
 </div>
 <div>
  <div class="callout"><b>Our problem statement:</b> design a mobile app that lets a willing donor find a centre, check eligibility and book a slot in a few taps,
  and lets a patient’s family send an urgent request to nearby compatible donors — then follow every step live.</div>
  <h3 style="margin-top:30px">Scope of this CA-3</h3>
  <div class="chips"><span class="chip">Figma design system</span><span class="chip">15 high-fidelity screens</span>
  <span class="chip">Clickable prototype</span><span class="chip">HTML &amp; CSS build</span></div>
 </div>
</div>"""),

    # 3 — personas
    slide(head("Users", "Who we designed for: three proto-personas") + """
<div class="grid3">
 <div class="card tint"><h3>Aarav Deshpande · Donor</h3><p class="muted persona">Primary user · B+ · Kothrud, Pune · 6 donations since 2021</p>
  <ul><li><b>Wants</b> to know when he can donate again and book without paperwork.</li>
  <li><b>Wants</b> to see where his blood went.</li>
  <li><b>Frustrated by</b> forms at every centre and no news after donating.</li></ul></div>
 <div class="card tint"><h3>Meera’s family · Requester</h3><p class="muted persona">Primary user · needs 2 units of B+ at Sahyadri Hospital within 6 hours</p>
  <ul><li><b>Wants</b> to reach compatible donors fast, without knowing transfusion rules.</li>
  <li><b>Wants</b> to know who is coming and when.</li>
  <li><b>Frustrated by</b> panic, guesswork and no status updates.</li></ul></div>
 <div class="card tint"><h3>Blood-centre staff</h3><p class="muted persona">Secondary user · blood bank desk at a hospital</p>
  <ul><li><b>Wants</b> donors who arrive eligible and on time.</li>
  <li><b>Wants</b> quick check-in and verified donor details.</li>
  <li><b>Frustrated by</b> deferrals at the desk and repeated paperwork.</li></ul></div>
</div>
<p class="note">Proto-personas are assumption-based (Cooper, 1999). They guided our design decisions and should be validated with real donors and families in usability testing.</p>"""),

    # 4 — process & goals
    slide(head("Approach", "Design process and design goals") + """
<div class="flow" style="margin-bottom:30px">
 <div class="step"><b>1 · Understand</b><span>Problem, users, Indian donor rules (NBTC 2017)</span></div><div class="arrow">→</div>
 <div class="step"><b>2 · Define</b><span>Proto-personas, goals, five user flows</span></div><div class="arrow">→</div>
 <div class="step"><b>3 · Design</b><span>Figma variables, text styles, components, 15 screens</span></div><div class="arrow">→</div>
 <div class="step"><b>4 · Prototype</b><span>Figma prototype links, then HTML &amp; CSS</span></div><div class="arrow">→</div>
 <div class="step"><b>5 · Evaluate</b><span>Nielsen’s heuristics, WCAG contrast and targets</span></div>
</div>
<div class="grid3" style="gap:20px">
 <div class="card"><h3>Fast under stress</h3><p>An urgent request fits on one screen; big primary buttons sit at the bottom, in thumb reach.</p></div>
 <div class="card"><h3>Trustworthy</h3><p>Verified donors, government-licensed centres and stock that says when it was last updated.</p></div>
 <div class="card"><h3>Private by default</h3><p>A hospital sees a donor’s number only after the donor accepts the request.</p></div>
 <div class="card"><h3>Clear</h3><p>One question per screen, plain words, and “Why do we ask this?” next to medical questions.</p></div>
 <div class="card"><h3>Motivating</h3><p>A “ready to donate” countdown, an impact tracker and badges bring donors back.</p></div>
 <div class="card"><h3>Accessible</h3><p>Large touch targets, colour never used alone, visible focus states.</p></div>
</div>"""),

    # 5 — information architecture
    slide(head("Information architecture", "15 screens in 5 flows, one bottom navigation") + """
<div class="ia" style="margin-bottom:30px">
 <div class="card"><div class="num">01</div><h3>Onboarding</h3><ol><li>1.1 Welcome</li><li>1.2 Sign in</li><li>1.3 Verify OTP</li><li>1.4 Blood group</li></ol></div>
 <div class="card"><div class="num">02</div><h3>Home &amp; discover</h3><ol><li>2.1 Home</li><li>2.2 Find centres (map)</li><li>2.3 Centre details</li><li>2.4 Eligibility check</li></ol></div>
 <div class="card"><div class="num">03</div><h3>Book a donation</h3><ol><li>3.1 Choose a slot</li><li>3.2 Booking confirmed</li></ol></div>
 <div class="card"><div class="num">04</div><h3>Emergency request</h3><ol><li>4.1 Request blood</li><li>4.2 Matching donors</li><li>4.3 Request tracking</li></ol></div>
 <div class="card"><div class="num">05</div><h3>Donor card &amp; impact</h3><ol><li>5.1 Donor card</li><li>5.2 Your impact</li></ol></div>
</div>
<div class="grid2" style="grid-template-columns:1.25fr 1fr;align-items:center">
 <div class="paths">
  <div><b>Donor:</b> Home → Find → Centre details → Choose a slot → Booked</div>
  <div><b>Urgent donor:</b> Home → “I can donate” → Eligibility check → Slot</div>
  <div><b>Requester:</b> Request → Matching donors → Request tracking</div>
 </div>
 <div>
  <div class="bnav"><span class="on">Home</span><span>Find</span><span class="req">Request</span><span>Donor card</span><span>Profile</span></div>
  <p class="note" style="margin-top:12px">Request is a raised button in the centre of the bottom bar, so the emergency path is one tap from any main screen.</p>
 </div>
</div>"""),

    # 6 — design system foundations
    slide(head("Design system · Figma", "Foundations: colour, type and shape") + f"""
<div class="grid2" style="grid-template-columns:1.12fr 1fr;gap:44px">
 <div>
  {swatches("Backgrounds", ["bg-canvas", "bg-surface", "bg-sunken", "bg-blush", "bg-wine"])}
  {swatches("Text", ["text-primary", "text-secondary", "text-tertiary", "text-brand"])}
  {swatches("Brand", ["brand", "brand-pressed", "brand-soft"])}
  {swatches("Accents (status)", ["sage", "turmeric", "peach", "plum"])}
 </div>
 <div>
  <div class="spec"><div class="fam">Fraunces · display &amp; headings</div><div class="serif">Be the reason someone gets a tomorrow.</div>
   <div class="styles">Display 34/40 · Headline 26/32 · Title L 20/26 · Numeral 40/44</div></div>
  <div class="spec"><div class="fam">Figtree · body &amp; interface</div><div class="sans">Find blood centres near you and book a slot in seconds.</div>
   <div class="styles">Title 17/24 · Body L 16/24 · Body 14/20 · Label 15/20 · Caption 12/16 · Overline 11/14</div></div>
  <div class="sw-label" style="margin-top:16px">Corner radius &amp; elevation</div>
  <div class="shapes"><div style="border-radius:10px">10</div><div style="border-radius:16px">16</div><div style="border-radius:24px">24</div>
   <div style="border-radius:999px">pill</div><div class="sh" style="border-radius:16px;box-shadow:0 4px 16px rgba(92,41,28,.16)">soft</div>
   <div class="sh" style="border-radius:16px;box-shadow:0 10px 28px -4px rgba(92,41,28,.28)">raised</div></div>
 </div>
</div>
<p class="note">Warm neutrals keep the app calm; red is kept for actions and urgency. The same token names are used as Figma variables and as CSS custom properties.</p>"""),

    # 7 — components & icons
    slide(head("Design system · Figma", "Reusable components and one icon family") + f"""
<div class="grid2" style="grid-template-columns:auto 1fr;gap:48px;align-items:center">
 <img src="{COMPONENTS}" alt="Raktdaan component sheet in Figma" style="height:600px;border:1.5px solid var(--line);border-radius:16px">
 <div>
  <ul style="margin-bottom:22px">
   <li style="font-size:23px;margin-bottom:9px"><b>Button</b> — primary, secondary and outline, in 56 px and 44 px heights.</li>
   <li style="font-size:23px;margin-bottom:9px"><b>Blood-group chip</b> — default and selected; works as a radio button.</li>
   <li style="font-size:23px;margin-bottom:9px"><b>Filter chip</b> — off and on; works as a checkbox.</li>
   <li style="font-size:23px;margin-bottom:9px"><b>Status tag</b> — critical, ready, soon, neutral: a dot, a colour <i>and</i> a word.</li>
   <li style="font-size:23px;margin-bottom:9px"><b>Input field</b> — default, focused and error with helper text.</li>
   <li style="font-size:23px;margin-bottom:9px"><b>Android system bars, top app bar, bottom navigation</b> (four active states).</li>
  </ul>
  <div class="sw-label">Icons · Phosphor, Regular + Fill</div>
  <img src="{ICONS}" alt="Phosphor icon set used in Raktdaan" style="width:100%;border:1.5px solid var(--line);border-radius:14px">
  <p class="note" style="margin-top:10px">One stroke style everywhere; the filled version marks the active tab and selected states.</p>
 </div>
</div>"""),

    # 8 — onboarding
    flow_slide("Flow 01 · Onboarding", "Sign up in three short steps", [
        ("welcome", "1.1 Welcome"), ("signin", "1.2 Sign in"), ("otp", "1.3 Verify OTP"), ("bloodgroup", "1.4 Blood group")],
        470,
        [("Welcome", "one clear promise, one main button; “Skip” and “Sign in” for returning donors."),
         ("Sign in", "only a mobile number; explains up front that hospitals see it only after you accept."),
         ("OTP", "large keypad, resend timer, and “Change” if the number was wrong."),
         ("Blood group", "tap one of 8 chips instead of typing; “I don’t know” is a valid answer.")],
        ["Visibility of status: Step 1 of 3", "User control", "Recognition over recall", "Error recovery"]),

    # 9 — home & discover
    flow_slide("Flow 02 · Home & discover", "Know when you can donate, and where", [
        ("home", "2.1 Home"), ("find", "2.2 Find centres"), ("centre", "2.3 Centre details"), ("eligibility", "2.4 Eligibility")],
        470,
        [("Home", "a status card says “You’re ready to donate again”; urgent requests show only patients the donor’s group can help."),
         ("Find", "map plus list; filter chips such as “Has B+” and “Within 5 km”."),
         ("Centre", "stock for all 8 groups with a text legend and “Updated 10 min ago”."),
         ("Eligibility", "one question per screen, progress shown, and a “Why do we ask this?” note.")],
        ["Match with the real world", "Hick’s law", "Help in context", "Error prevention"]),

    # 10 — book a donation
    flow_slide("Flow 03 · Book a donation", "Booking a slot, then closure", [
        ("slot", "3.1 Choose a slot"), ("booked", "3.2 Booking confirmed")],
        560,
        [("Donation type", "a two-option segmented control shows how long each one takes (45 min vs 2 hrs)."),
         ("Day and time", "a date strip and slot grid grouped into Morning / Afternoon; full slots are struck through and cannot be picked."),
         ("Sticky summary", "the chosen slot and the Confirm button stay at the bottom, within thumb reach."),
         ("Confirmation", "token number, QR code for fast check-in, a “Before you come” checklist, Add to calendar and Directions.")],
        ["Gestalt proximity", "Fitts’s law", "Closure (Shneiderman)", "Reduce memory load"]),

    # 11 — emergency request
    flow_slide("Flow 04 · Emergency request", "From request to donor arrival, in plain sight", [
        ("request", "4.1 Request blood"), ("matching", "4.2 Matching donors"), ("tracking", "4.3 Request tracking")],
        490,
        [("Safety first", "a banner says to call 108 for an ambulance before anything else."),
         ("Compatibility done for you", "the family picks the patient’s group; the app alerts every compatible group (B+, B−, O+, O−) and says so on the button."),
         ("Live matching", "a darker screen signals urgency: 48 alerted, 31 seen, 6 said yes, nearest first."),
         ("Tracking", "“1 of 2 units arranged”, time left, and a timeline of every update.")],
        ["Visibility of system status", "Error prevention", "Emotional design", "Feedback"]),

    # 12 — donor card & impact
    flow_slide("Flow 05 · Donor card & impact", "Reasons to come back", [
        ("donorcard", "5.1 Donor card"), ("impact", "5.2 Your impact")],
        560,
        [("Digital donor card", "verified badge, QR code, eligibility, last haemoglobin and blood pressure — no paperwork at the next centre."),
         ("Impact", "“18 people may have been helped by your 6 donations”, with the reason: one unit becomes red cells, plasma and platelets."),
         ("Where your blood went", "Donated → Tested → Sent out → Used, ending with the hospital that used it."),
         ("Badges and history", "small rewards for regular donors, and a record of every donation.")],
        ["Feedback loop", "Honest wording", "Recognition", "Motivation"]),

    # 13 — heuristic evaluation
    slide(head("Evaluation · Heuristics", "Nielsen’s 10 heuristics, checked against the design") + """
<table>
 <tr><th style="width:30%">Heuristic</th><th>Where Raktdaan applies it</th></tr>
 <tr><td><b>1</b> Visibility of system status</td><td>“Step 2 of 3”, “Question 3 of 6 · about a minute left”, live request timeline, stock “updated 10 min ago”</td></tr>
 <tr><td><b>2</b> Match with the real world</td><td>+91 numbers, km, Pune hospitals, units in ml, NBTC donor rules, 108 ambulance</td></tr>
 <tr><td><b>3</b> User control and freedom</td><td>Skip, Back on every step, “Change” number or centre, pause alerts any time</td></tr>
 <tr><td><b>4</b> Consistency and standards</td><td>One component library; Android system bars and bottom navigation; main button always at the bottom</td></tr>
 <tr><td><b>5</b> Error prevention</td><td>Eligibility check before booking; app works out compatible groups; full slots cannot be picked</td></tr>
 <tr><td><b>6</b> Recognition rather than recall</td><td>Blood-group chips, date strip and slot grid, QR donor card instead of typing IDs</td></tr>
 <tr><td><b>7</b> Flexibility and efficiency</td><td>“I can donate” right on Home; filter chips; Add to calendar; Request is one tap away</td></tr>
 <tr><td><b>8</b> Aesthetic and minimalist design</td><td>One main action per screen; warm, calm palette; red only for actions and urgency</td></tr>
 <tr><td><b>9</b> Help users recover from errors</td><td>Inline error text on inputs; “I don’t know my blood group”; OTP resend timer and “Change”</td></tr>
 <tr><td><b>10</b> Help and documentation</td><td>“Why do we ask this?”, “Did you know?” tips, “Before you come” checklist</td></tr>
</table>"""),

    # 14 — accessibility
    slide(head("Evaluation · Accessibility", "Accessibility check against WCAG 2.2") + f"""
<div class="grid2" style="grid-template-columns:1.12fr 1fr;gap:48px;align-items:start">
 <div>
  <h3>Colour contrast (WCAG AA: 4.5 : 1)</h3>
  <table class="tight"><tr><th>Text / background</th><th>Used for</th><th>Ratio</th><th></th></tr>{contrast_rows()}</table>
 </div>
 <div>
  <h3>Touch targets and semantics</h3>
  <ul>
   <li class="small" style="margin-bottom:10px">Main buttons are 56 px tall, icon buttons 48 × 48 px, bottom-bar items 76 × 58 px, blood-group chips 76 px tall.</li>
   <li class="small" style="margin-bottom:10px">Status never relies on colour alone: every tag has a word, and the stock grid has a legend.</li>
   <li class="small" style="margin-bottom:10px">Choices are real radio buttons and checkboxes ({SRC.count('<input')} inputs); icon-only controls carry text labels ({SRC.count('aria-label="') - SRC.count('<section class="screen"')} aria-labels), so screen readers can announce them.</li>
   <li class="small" style="margin-bottom:10px">Visible focus ring on every control; animations switch off when “reduce motion” is on.</li>
  </ul>
 </div>
</div>
<div class="callout" style="margin-top:22px;font-size:21px;padding:14px 22px"><b>Result:</b> main text, links and buttons meet WCAG AA contrast, and every touch target is well above
the 24 px minimum (WCAG 2.5.8). Ratios are computed from the design tokens in raktdaan.html.</div>"""),

    # 15 — HTML & CSS
    slide(head("Implementation · HTML & CSS", "A clickable prototype with zero JavaScript") + f"""
<div class="grid2" style="grid-template-columns:1fr 1.02fr;gap:44px;align-items:center">
 <ul>
  <li class="small"><b>One file</b>, raktdaan.html: {len(SRC.splitlines()):,} lines of HTML and CSS, all 15 screens.</li>
  <li class="small"><b>Navigation:</b> each screen is a &lt;section id&gt;; buttons are links; CSS <b>:target</b> shows the current screen.</li>
  <li class="small"><b>State:</b> blood groups, slots, answers and filters are real inputs, styled with <b>:has(:checked)</b>.</li>
  <li class="small"><b>Tokens:</b> CSS custom properties with the same names as the Figma variables; text styles as classes.</li>
  <li class="small"><b>Icons:</b> {SRC.count('<symbol') - 1} Phosphor icons in one inline SVG sprite (&lt;symbol&gt; + &lt;use&gt;).</li>
  <li class="small"><b>Responsive:</b> on a laptop it shows a phone frame and a screen menu; on a real phone the page becomes the app.</li>
 </ul>
 <div class="code"><span class="c">/* 1 · navigation without JavaScript */</span>
<span class="k">.screen</span> {{ display: none; }}
<span class="k">.screen:target</span> {{ display: block; }}

&lt;a href=<span class="s">"#slot"</span> class=<span class="s">"btn btn--white"</span>&gt;Book a slot&lt;/a&gt;

<span class="c">/* 2 · selected state from a real radio input */</span>
<span class="k">.bg-chip:has(input:checked)</span> {{
  background: var(--brand);
  color: var(--text-on-brand);
}}

&lt;label class=<span class="s">"bg-chip"</span>&gt;
  &lt;input class=<span class="s">"sr"</span> type=<span class="s">"radio"</span> name=<span class="s">"my-group"</span> value=<span class="s">"B+"</span>&gt;
  &lt;b&gt;B+&lt;/b&gt; …
&lt;/label&gt;</div>
</div>"""),

    # 16 — Figma to code
    slide(head("Implementation · Design to code", "From Figma to code without losing the design") + f"""
<div class="grid2" style="grid-template-columns:1fr auto;gap:56px;align-items:center">
 <table>
  <tr><th style="width:38%">In Figma</th><th>In HTML &amp; CSS</th></tr>
  <tr><td>Colour and radius variables</td><td>Custom properties: <b>--brand</b>, <b>--bg-canvas</b>, <b>--radius-md</b></td></tr>
  <tr><td>Text styles</td><td>Classes: <b>.t-display</b>, <b>.t-headline</b> … <b>.t-overline</b></td></tr>
  <tr><td>Components and variants</td><td>Class + modifier: <b>.btn--primary</b>, <b>.tag--urgent</b></td></tr>
  <tr><td>Interactive states</td><td><b>:hover</b>, <b>:focus-visible</b>, <b>:has(:checked)</b></td></tr>
  <tr><td>Prototype links</td><td><b>&lt;a href="#screen"&gt;</b> + <b>:target</b></td></tr>
  <tr><td>Android frame, 412 × 917</td><td><b>.phone</b>, 412 × 917 px; full screen on a real phone</td></tr>
  <tr><td>Auto layout</td><td>Flexbox and grid helpers: <b>.row</b>, <b>.col</b>, <b>.gap-16</b></td></tr>
 </table>
 <div>
  <div class="thumbs">{"".join(f'<div class="scr s-{s}" role="img" aria-label="{s}"></div>' for s in
      ["welcome", "signin", "otp", "bloodgroup", "home", "find", "centre", "eligibility",
       "slot", "booked", "request", "matching", "tracking", "donorcard", "impact"])}</div>
  <p class="note" style="text-align:center;margin-top:14px">All 15 screens, rendered from the HTML</p>
 </div>
</div>"""),

    # 17 — conclusion
    slide(head("Conclusion", "What we built and what comes next") + """
<ul style="margin-bottom:24px">
 <li>Raktdaan covers both sides of blood donation — a donor’s routine and a family’s emergency — in <b>15 screens</b> and <b>5 flows</b>.</li>
 <li>One design system drives both the Figma file and the HTML &amp; CSS build, so the design and the code match.</li>
 <li>Our heuristic and WCAG review confirmed clear system status, error prevention, recognition over recall, <b>AA contrast</b> for text and buttons, and <b>large touch targets</b>.</li>
</ul>
<div class="grid3" style="gap:20px;margin-bottom:30px">
 <div class="card tint"><h3>PPT</h3><p>This deck: the problem, users, flows, design system and evaluation.</p></div>
 <div class="card tint"><h3>Figma design</h3><p>Variables, text styles, components, icons and 15 linked screens.</p></div>
 <div class="card tint"><h3>HTML &amp; CSS code</h3><p>raktdaan.html — opens in any browser, no install, no JavaScript.</p></div>
</div>
<h3>Future work</h3>
<div class="chips"><span class="chip">Usability tests with donors and families (task time, SUS)</span><span class="chip">Hindi and Marathi</span><span class="chip">Dark mode</span><span class="chip">Live stock from e-RaktKosh</span>
<span class="chip">Push alerts</span><span class="chip">Blood-centre staff dashboard</span></div>"""),

    # 18 — references + thanks
    slide(head("References", "Thank you") + """
<ol class="refs" style="padding-left:26px;columns:2;column-gap:46px">
 <li>J. Nielsen, “10 usability heuristics for user interface design,” Nielsen Norman Group, 1994 (updated 2024).</li>
 <li>B. Shneiderman <i>et al.</i>, <i>Designing the User Interface</i>, 6th ed. Pearson, 2016.</li>
 <li>D. A. Norman, <i>The Design of Everyday Things</i>, revised ed. Basic Books, 2013.</li>
 <li>P. M. Fitts, “The information capacity of the human motor system in controlling the amplitude of movement,” <i>J. Exp. Psychol.</i>, vol. 47, no. 6, 1954.</li>
 <li>W. E. Hick, “On the rate of gain of information,” <i>Q. J. Exp. Psychol.</i>, vol. 4, no. 1, 1952.</li>
 <li>A. Cooper, <i>The Inmates Are Running the Asylum</i>. Sams, 1999.</li>
 <li>W3C, “Web Content Accessibility Guidelines (WCAG) 2.2,” W3C Recommendation, Oct. 2023.</li>
 <li>Google, “Material Design 3,” m3.material.io.</li>
 <li>National Blood Transfusion Council, MoHFW, “Guidelines for blood donor selection &amp; blood donor referral,” 2017.</li>
 <li>MoHFW, Govt. of India, “e-RaktKosh: Centralised blood bank management system,” eraktkosh.mohfw.gov.in.</li>
 <li>H. Zhang and T. Fried, “Phosphor Icons,” phosphoricons.com.</li>
 <li>MDN Web Docs, “:target” and “:has()” CSS pseudo-classes, Mozilla.</li>
</ol>
<p class="muted small" style="margin-top:22px">Group 06 · Raghav Sonchhatra · Sanidhya Awasthi · Faheemuddin Sayyed &nbsp;·&nbsp; Guided by Dr. Sudhanshu Gonge</p>"""),
]


def main():
    fonts = ASSETS / "fonts"
    css = (CSS.replace("FIGTREE", file_uri(fonts / "Figtree-latin-var.woff2", "font/woff2"))
              .replace("FRAUNCES", file_uri(fonts / "Fraunces-latin-var.woff2", "font/woff2")))
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>G06 – HCI CA-3 – Raktdaan</title>
<style>{css}{SCREEN_CSS}</style></head>
<body>
<div id="stage">{''.join(SLIDES)}</div>
<div class="nav left" aria-label="Previous slide"><span>&#8249;</span></div>
<div class="nav right" aria-label="Next slide"><span>&#8250;</span></div>
<script>{JS}</script>
</body></html>"""
    OUT.write_text(html, encoding="utf-8")
    print(f"wrote {OUT.name}: {len(SLIDES)} slides, {len(html) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
