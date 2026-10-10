"""Build CA3_Presentation.html: a self-contained 16:9 deck for the Data Science CA-3 presentation and viva.

Usage: python3 build_presentation.py      (after analysis/prepare_data.py and analysis/make_figures.py)
Controls: → / Space / PageDown = next, ← / PageUp = previous, Home / End, F = full screen.
Arrows appear only while hovering the left/right edge; the cursor hides after 2 s without movement.

Tableau screenshots: save them as screenshots/overview.png and screenshots/network.png and re-run this script;
until then the two dashboard slides show the layout wireframe instead.
"""
import base64
import io
import json
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
FIGS = HERE / "figures"
SHOTS = HERE / "screenshots"
S = json.loads((HERE / "results" / "summary.json").read_text())


def data_uri(path, max_w=None):
    im = Image.open(path)
    if max_w and im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


LOGO = data_uri(HERE.parent / "sit-logo.png", 2000)
FIG = {p.stem: data_uri(p, 1700) for p in sorted(FIGS.glob("fig_*.png"))}
SHOT = {n: data_uri(SHOTS / f"{n}.png", 1800) for n in ("overview", "network") if (SHOTS / f"{n}.png").exists()}

TITLE = ("Enron Email Network Analytics: An Interactive Tableau Dashboard of Communication Patterns, "
         "Communities and Privacy Risks during a Corporate Collapse (1999–2002)")

P = S["periods"]
PRE, CRI, POST = (P[k] for k in sorted(P))
LOC = S["locality_whole"]
GN = S["girvan_newman"]
LOG = S["cleaning_log"]
fmt = "{:,}".format
CSV_MB = sum(f.stat().st_size for f in (HERE / "data" / "processed").glob("*.csv")) / 1e6

CSS = """
:root{--ink:#111418;--muted:#4a5160;--blue:#1F3864;--accent:#2A4DA8;--accent2:#5A97EE;--line:#d5dbe7;--tint:#eef3fc}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:100%;height:100%;background:#fff;overflow:hidden}
body{font-family:"Segoe UI",Calibri,"Helvetica Neue",-apple-system,Arial,sans-serif;color:var(--ink);-webkit-font-smoothing:antialiased}
body.idle,body.idle *{cursor:none!important}
#stage{position:absolute;left:50%;top:50%;width:1600px;height:900px;transform-origin:center center}
.slide{position:absolute;inset:0;opacity:0;visibility:hidden;transition:opacity .25s ease;padding:62px 90px 60px;display:flex;flex-direction:column}
.content{flex:1;display:flex;flex-direction:column;justify-content:center;padding-bottom:22px}
body.static .slide{transition:none}
.slide.active{opacity:1;visibility:visible}
.frame{position:absolute;inset:18px;border:2.5px solid #1b1b1b;border-radius:34px;pointer-events:none}
.kicker{font-size:19px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:var(--accent);margin-bottom:8px}
h2{font-size:44px;font-weight:700;line-height:1.12;margin-bottom:8px;color:var(--ink)}
h3{font-size:26px;font-weight:700;color:var(--blue);margin-bottom:10px}
p,li{font-size:26px;line-height:1.38}
ul{padding-left:28px}
li{margin-bottom:10px}
li::marker{color:var(--accent)}
.muted{color:var(--muted)}
.small{font-size:21px}
.src{position:absolute;left:90px;bottom:40px;font-size:16px;color:var(--muted)}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:40px}
.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}
.grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:20px}
.card{border:1.5px solid var(--line);border-radius:18px;padding:20px 22px;background:#fff}
.card.tint{background:var(--tint);border-color:#cfdaf0}
.card p,.card li{font-size:21px;line-height:1.32}
.card h3{font-size:22px;margin-bottom:6px}
.stat .v{font-size:52px;font-weight:800;color:var(--accent);line-height:1}
.stat .l{font-size:20px;color:var(--muted);margin-top:8px;line-height:1.3}
.chips{display:flex;gap:12px;flex-wrap:wrap}
.chip{border:1.5px solid var(--accent);color:var(--accent);border-radius:999px;padding:7px 18px;font-size:20px;font-weight:600}
.flow{display:flex;align-items:stretch;gap:10px}
.flow .step{flex:1;border:1.5px solid var(--line);border-radius:16px;padding:16px 14px;background:#fff}
.flow .step b{display:block;color:var(--accent);font-size:16px;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px}
.flow .step span{font-size:19px;line-height:1.3;display:block}
.flow .arrow{align-self:center;color:var(--accent);font-size:26px}
table{border-collapse:collapse;width:100%}
th{font-size:17px;text-transform:uppercase;letter-spacing:1px;color:var(--blue);text-align:left;padding:9px 12px;border-bottom:2px solid var(--accent);background:var(--tint)}
td{font-size:20px;padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top;line-height:1.28}
.figure{width:100%;display:block}
.callout{border-left:6px solid var(--accent);background:var(--tint);padding:16px 22px;border-radius:0 14px 14px 0;font-size:23px;line-height:1.35}
.refs li{font-size:16.5px;line-height:1.28;margin-bottom:5px}
.obj{counter-reset:o;list-style:none;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:22px 48px}
.obj li{counter-increment:o;font-size:25px;line-height:1.3;padding-left:52px;position:relative;margin:0}
.obj li::before{content:counter(o);position:absolute;left:0;top:-2px;width:38px;height:38px;border-radius:50%;background:var(--tint);color:var(--accent);font-weight:800;display:flex;align-items:center;justify-content:center;font-size:19px}
.funnel .row{display:grid;grid-template-columns:360px 1fr;gap:16px;align-items:center;margin-bottom:12px}
.funnel .lab{font-size:18px;line-height:1.25;color:var(--muted);text-align:right}
.funnel .bar{height:34px;background:#2a78d6;border-radius:0 6px 6px 0;color:#fff;font-weight:700;font-size:18px;display:flex;align-items:center;padding-left:12px;min-width:110px}
/* dashboard wireframes (shown until real Tableau screenshots are added) */
.wf{display:grid;gap:8px;background:#f6f8fc;border:1.5px solid var(--line);border-radius:14px;padding:10px;height:100%}
.wf div{background:#fff;border:1.5px solid #cfd6e4;border-radius:8px;padding:8px 10px;font-size:15px;line-height:1.25;color:var(--muted)}
.wf div b{display:block;color:var(--ink);font-size:16px;margin-bottom:2px}
.wf .t{background:var(--tint);border-color:#cfdaf0}
.shot{width:100%;border:1.5px solid var(--line);border-radius:12px;display:block}
/* title slide (same template as the group's earlier deck) */
.title-slide{text-align:center;padding:40px 110px}
.title-slide .logo{height:170px;margin:26px auto 0;display:block}
.title-slide .course{font-size:34px;font-weight:700;margin-top:30px}
.title-slide .topic{font-size:32px;font-weight:700;line-height:1.3;margin:24px auto 0;max-width:1320px}
.title-slide .names{font-size:27px;line-height:1.75;margin-top:30px}
.title-slide .guide{font-size:27px;margin-top:18px}
.title-slide .foot{position:absolute;left:0;right:0;bottom:38px;font-size:19px}
/* navigation: invisible until hovered */
.nav{position:fixed;top:0;bottom:0;width:12vw;z-index:10;display:flex;align-items:center;cursor:pointer;opacity:0;transition:opacity .2s ease}
.nav:hover{opacity:1}
.nav.left{left:0;justify-content:flex-start;padding-left:2vw}
.nav.right{right:0;justify-content:flex-end;padding-right:2vw}
.nav span{width:58px;height:58px;border-radius:50%;background:rgba(17,20,24,.55);color:#fff;font-size:30px;display:flex;align-items:center;justify-content:center;line-height:1}
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


def funnel():
    top = LOG[0][1]
    labels = ["Raw sender→recipient records", "Inside Jan 1999 – Jun 2002", "bcc copies removed",
              "Self-addressed copies removed", "Folder duplicates removed"]
    rows = []
    for (_, n), lab in zip(LOG, labels):
        rows.append(f'<div class="row"><div class="lab">{lab}</div>'
                    f'<div><div class="bar" style="width:{max(n / top * 100, 12):.1f}%">{fmt(n)}</div></div></div>')
    return '<div class="funnel">' + "".join(rows) + "</div>"


def overview_panel():
    if "overview" in SHOT:
        return f'<img class="shot" src="{SHOT["overview"]}" alt="Tableau dashboard 1: Overview">'
    return """<div class="wf" style="grid-template-columns:3fr 3fr 2fr;grid-template-rows:auto auto 1.5fr 1.2fr;
 grid-template-areas:'t t t' 'k k f' 'v v e' 'h l e'">
 <div class="t" style="grid-area:t"><b>Title + one-line context</b>data source, privacy note</div>
 <div style="grid-area:k"><b>KPI tiles</b>deliveries · messages · active senders · cross-community %</div>
 <div style="grid-area:f"><b>Controls</b>Period · Sender role</div>
 <div style="grid-area:v"><b>Weekly email volume</b>area chart, colour = period</div>
 <div style="grid-area:e"><b>Period legend + Key events</b>10 dated milestones of the collapse</div>
 <div style="grid-area:h"><b>Who emails whom</b>sender role × recipient role heat-map</div>
 <div style="grid-area:l"><b>Locality test by month</b>closure probability vs density</div>
</div>"""


def network_panel():
    if "network" in SHOT:
        return f'<img class="shot" src="{SHOT["network"]}" alt="Tableau dashboard 2: Network">'
    return """<div class="wf" style="grid-template-columns:3fr 2fr;grid-template-rows:auto auto 1.4fr 1fr auto">
 <div class="t" style="grid-column:1/3"><b>Title + how to use</b>click a bar to highlight that person on the map</div>
 <div style="grid-row:2/5"><b>People map</b>force-directed layout positions of all 148 people;<br>size = betweenness, colour = community</div>
 <div><b>Controls</b>Rank people by · Community</div>
 <div><b>Top 15 people</b>bar chart, metric chosen by the parameter</div>
 <div><b>Community composition</b>stacked bar by role group</div>
 <div style="grid-column:1/3"><b>Community colour legend</b></div>
</div>"""


def dash_cols(name):
    """A real screenshot gets more room than the wireframe so its labels stay readable."""
    return "2.3fr 1fr" if name in SHOT else "1.55fr 1fr"


def shot_note(name):
    return "" if name in SHOT else ('<div class="src">Layout shown as a wireframe — the live dashboard is '
                                    'demonstrated in Tableau.</div>')

SLIDES = [
    # 1 — title (group template; two members; guided by)
    slide(f"""
<img class="logo" src="{LOGO}" alt="Symbiosis Institute of Technology, Pune">
<div class="course">Data Science — CA-3 Case Study</div>
<div class="topic">{TITLE}</div>
<div class="names">Faheemuddin Sayyed – PRN 23070122196<br>Sanidhya Awasthi – PRN 23070122192</div>
<div class="guide">Guided by: <b>Dr. Deepak Dharrao</b></div>
<div class="foot">CA-3 — Case Study-Based Tableau Dashboard &nbsp;|&nbsp; Department of Computer Engineering &nbsp;|&nbsp; Academic Year 2026–27</div>
""", "title-slide"),

    # 2 — problem statement
    slide(head("Problem statement", "What happened inside Enron’s email network as the company collapsed?") + f"""
<div class="grid2" style="grid-template-columns:1.25fr 1fr;align-items:start">
 <div>
  <ul>
   <li>Enron, a top-10 US company, went bankrupt in <b>December 2001</b> after an accounting scandal.</li>
   <li>US regulators (FERC) made the <b>internal emails of about 150 employees</b> public — one of the very few real
       corporate communication datasets.</li>
   <li>The raw data is <b>noisy</b> (duplicates, aliases, bad timestamps) and <b>sensitive</b> (real people’s names).</li>
  </ul>
  <div class="callout" style="margin-top:18px">How can we turn this raw email metadata into an <b>interactive Tableau
  dashboard</b> that shows how communication volume, communities and key people changed before, during and after the
  crisis — <b>while protecting the employees’ privacy</b>?</div>
 </div>
 <div style="display:grid;gap:18px">
  <div class="card stat tint"><div class="v">{fmt(LOG[0][1])}</div><div class="l">raw sender→recipient records</div></div>
  <div class="card stat tint"><div class="v">{S['addresses']} → {S['people']}</div><div class="l">email addresses → real people after merging aliases</div></div>
  <div class="card stat tint"><div class="v">1999–2002</div><div class="l">covers the boom, the crisis and the bankruptcy</div></div>
 </div>
</div>"""),

    # 3 — objectives
    slide(head("Target objectives", "Ten objectives") + """
<ol class="obj">
 <li>Acquire a real, publicly released dataset and document its source</li>
 <li>Clean it: remove duplicate copies, merge email aliases, check timestamps</li>
 <li>Model email traffic as a social network graph (strong vs weak ties)</li>
 <li>Test whether the graph shows social-network <i>locality</i> (Unit 5)</li>
 <li>Find key people and brokers with centrality measures</li>
 <li>Detect communities with Girvan–Newman and cross-check with Louvain</li>
 <li>Compare pre-crisis, crisis and post-bankruptcy communication</li>
 <li>Build an interactive Tableau dashboard using sound visualisation principles</li>
 <li>Compare Tableau Creator and Viewer licences for this dashboard</li>
 <li>Assess privacy, security and ethics; apply privacy-by-design (Unit 6)</li>
</ol>"""),

    # 4 — dataset
    slide(head("Dataset", "The Enron email network (Johns Hopkins version)") + f"""
<div class="grid2" style="grid-template-columns:1fr 1.1fr;align-items:start">
 <div>
  <table>
   <tr><th>Part</th><th>Fields used</th></tr>
   <tr><td><b>People</b> (184 addresses)</td><td>name, job title (e.g. “Vice President”)</td></tr>
   <tr><td><b>Emails</b> (125,409 links)</td><td>sender, recipient, time, To / CC / BCC</td></tr>
   <tr><td><b>Not used</b></td><td>message text and topic labels (data minimisation)</td></tr>
  </table>
  <p class="small" style="margin-top:16px">Source: <b>igraphdata</b> R package, <i>enron</i> graph — Priebe et al. (2005),
  built from the CMU Enron corpus (Klimt &amp; Yang, 2004) that FERC released during its investigation.</p>
 </div>
 <div class="grid2" style="gap:16px">
  <div class="card stat"><div class="v">{fmt(S['messages'])}</div><div class="l">unique messages after cleaning</div></div>
  <div class="card stat"><div class="v">{fmt(S['deliveries'])}</div><div class="l">sender→recipient deliveries</div></div>
  <div class="card stat"><div class="v">{S['active_people']}</div><div class="l">active people (nodes)</div></div>
  <div class="card stat"><div class="v">{fmt(S['ties_undirected'])}</div><div class="l">person-to-person ties (edges)</div></div>
 </div>
</div>
<div class="src">Small (0.2 MB compressed), so Git LFS was not needed; processed CSVs are {CSV_MB:.0f} MB in total.</div>"""),

    # 5 — methodology
    slide(head("Methodology", "From raw records to a dashboard in six steps") + """
<div class="flow" style="height:270px">
 <div class="step"><b>1 · Acquire</b><span>Load the R <i>.rda</i> graph into Python (rdata, pandas)</span></div>
 <div class="arrow">›</div>
 <div class="step"><b>2 · Clean</b><span>Date window, drop BCC copies, merge aliases, remove self-mail and folder duplicates</span></div>
 <div class="arrow">›</div>
 <div class="step"><b>3 · Protect</b><span>Pseudonymise staff, keep coarse roles, metadata only</span></div>
 <div class="arrow">›</div>
 <div class="step"><b>4 · Model</b><span>Directed + undirected weighted graphs; strong vs weak ties (NetworkX)</span></div>
 <div class="arrow">›</div>
 <div class="step"><b>5 · Analyse</b><span>Locality test, centrality, Girvan–Newman, period comparison</span></div>
 <div class="arrow">›</div>
 <div class="step"><b>6 · Visualise</b><span>5 Tableau data sources → 11 sheets → 2 dashboards</span></div>
</div>
<div class="chips" style="margin-top:40px"><span class="chip">Python · pandas · NetworkX · scikit-learn</span>
<span class="chip">Tableau Desktop / Public 2026</span><span class="chip">Fully reproducible scripts</span></div>"""),

    # 6 — data quality
    slide(head("Data cleaning &amp; quality", "73% of raw records were duplicates or artefacts — and the clock drifted") + f"""
<div class="grid2" style="grid-template-columns:1.05fr 1fr;align-items:center">
 <div>{funnel()}
  <p class="small muted" style="margin-top:8px">{S['addresses']} email addresses merged into {S['people']} people
  (one person used three different addresses).</p></div>
 <div>
  <img class="figure" src="{FIG['fig_clock']}" alt="Start of working day by month">
  <p class="small" style="margin-top:10px">An apparent “after-hours email doubled” result was really a <b>~5 hour
  timestamp drift</b> in the corpus (Apr–Sep 2001). We dropped hour-of-day analysis: <b>validate before you visualise</b>.</p>
 </div>
</div>"""),

    # 7 — Unit 5 analysis
    slide(head("Unit 5 · Mining social-network graphs", "Is it a social network? Yes — friends of friends connect") + f"""
<div class="grid2" style="grid-template-columns:1.2fr 1fr;align-items:center">
 <img class="figure" src="{FIG['fig_locality']}" alt="Locality test by month">
 <div>
  <table>
   <tr><td>P(<i>y–z</i> tie | <i>x–y</i>, <i>x–z</i>)</td><td><b>{LOC['p_closed']:.2f}</b></td></tr>
   <tr><td>Expected at random (density)</td><td><b>{LOC['density']:.2f}</b></td></tr>
   <tr><td>Strong (two-way) / weak ties</td><td><b>{S['strong_ties']} / {S['weak_ties']}</b></td></tr>
   <tr><td>Reciprocity</td><td><b>{S['reciprocity'] * 100:.0f}%</b></td></tr>
   <tr><td>Average path length · diameter</td><td><b>{S['avg_shortest_path']:.1f} · {S['diameter']}</b></td></tr>
   <tr><td>Girvan–Newman best modularity</td><td><b>{GN['best_modularity']:.2f}</b> → {GN['communities_ge3']} communities</td></tr>
   <tr><td>Agreement with Louvain (NMI)</td><td><b>{S['gn_vs_louvain']['NMI']:.2f}</b></td></tr>
  </table>
  <p class="small" style="margin-top:12px">Closure is <b>{LOC['p_closed'] / LOC['density']:.1f}×</b> the random
  baseline overall, and higher in every month with 50+ active people — the locality test from the Unit 5 slides.</p>
 </div>
</div>"""),

    # 8 — dashboard 1
    slide(head("Tableau dashboard 1", "Overview: volume, hierarchy and locality over time") + f"""
<div class="grid2" style="grid-template-columns:{dash_cols("overview")};align-items:stretch;height:600px">
 {overview_panel()}
 <ul style="align-self:center">
  <li><b>KPI tiles</b> answer “how much?” at a glance.</li>
  <li><b>Weekly volume</b> coloured by period shows the crisis surge.</li>
  <li><b>Role × role heat-map</b>: who emails whom up and down the hierarchy.</li>
  <li><b>Locality line chart</b> repeats the Unit 5 test month by month.</li>
  <li>Period and sender-role drop-downs (parameters) drive the KPIs, volume chart and heat-map together.</li>
 </ul>
</div>{shot_note("overview")}"""),

    # 9 — dashboard 2
    slide(head("Tableau dashboard 2", "Network: communities and brokers") + f"""
<div class="grid2" style="grid-template-columns:{dash_cols("network")};align-items:stretch;height:600px">
 {network_panel()}
 <ul style="align-self:center">
  <li><b>People map</b>: everyone placed by a force-directed layout of their email ties, so communities form visible clusters.</li>
  <li><b>Parameter</b> switches the ranking: betweenness, PageRank, contacts, emails sent.</li>
  <li><b>Highlight action</b>: click a person in the bar chart to find them on the map.</li>
  <li>Community drop-down filters the map; top brokers are labelled.</li>
 </ul>
</div>{shot_note("network")}"""),

    # 10 — visualisation principles
    slide(head("Visualisation principles", "Design choices and why we made them") + """
<div class="grid3">
 <div class="card tint"><h3>Overview → detail</h3><p>KPIs first, then trends, then drop-down controls and tooltips
 (Shneiderman’s mantra).</p></div>
 <div class="card tint"><h3>Reading order</h3><p>Most important view top-left, supporting views below and right
 (Z-pattern).</p></div>
 <div class="card tint"><h3>Colour has one job</h3><p>Same period colours everywhere; one-hue scale for amounts;
 colour-blind-checked palette for communities.</p></div>
 <div class="card tint"><h3>Right chart for the task</h3><p>Lines for time, sorted bars for ranking, heat-map for a
 matrix, a positional map for network structure; no pie charts.</p></div>
 <div class="card tint"><h3>Less non-data ink</h3><p>Meaningless graph axes and gridlines hidden; titles state what
 the chart shows.</p></div>
 <div class="card tint"><h3>Context &amp; honesty</h3><p>Key-events table for context; months with too few people
 filtered out of the locality chart.</p></div>
</div>"""),

    # 11 — findings: time
    slide(head("Findings 1", "The crisis tripled email traffic and pulled in the executives") + f"""
<img class="figure" src="{FIG['fig_timeline']}" alt="Weekly email deliveries with events" style="width:88%;margin:0 auto">
<div class="grid3" style="margin-top:12px">
 <p class="small"><b>{PRE['deliveries_per_week']:.0f} → {CRI['deliveries_per_week']:.0f}</b> deliveries a week
 (pre-crisis → crisis); the peak month was October 2001, when the $618M loss was announced.</p>
 <p class="small">Share of traffic involving an executive: <b>{PRE['executive_share_of_traffic'] * 100:.0f}% →
 {CRI['executive_share_of_traffic'] * 100:.0f}% → {POST['executive_share_of_traffic'] * 100:.0f}%</b>.</p>
 <p class="small">Broadcast emails (5+ recipients): <b>{PRE['broadcast_share'] * 100:.1f}% →
 {CRI['broadcast_share'] * 100:.1f}%</b> as news had to reach many people at once.</p>
</div>"""),

    # 12 — findings: structure
    slide(head("Findings 2", "The informal network does not follow the org chart") + f"""
<div class="grid2" style="grid-template-columns:1.12fr 1fr;align-items:center;gap:30px">
 <img class="figure" src="{FIG['fig_network']}" alt="Strong-tie network with communities">
 <div>
  <img class="figure" src="{FIG['fig_brokers']}" alt="Top 10 by betweenness">
  <ul style="margin-top:12px">
   <li class="small">{GN['communities_ge3']} communities line up with real business units (leadership, gas pipeline,
   trading desks).</li>
   <li class="small">Two of the top four brokers have <b>no job title</b> in the data — informal brokers matter.</li>
   <li class="small">In the crisis, the top three brokers were all executives.</li>
  </ul>
 </div>
</div>"""),

    # 13 — licences
    slide(head("Tableau licensing", "Creator vs Viewer — and who needs which for this dashboard") + """
<table>
 <tr><th style="width:24%"></th><th>Creator</th><th>Viewer</th></tr>
 <tr><td><b>Price (Tableau Cloud, per user / month, billed yearly)</b></td><td>US$75 Standard · US$115 Enterprise</td><td>US$15 Standard · US$35 Enterprise</td></tr>
 <tr><td><b>Software</b></td><td>Tableau Desktop, Tableau Prep Builder, web authoring</td><td>Browser and mobile app only</td></tr>
 <tr><td><b>Connect to data &amp; build</b></td><td>Yes — new data sources, calculations, sheets, dashboards</td><td>No</td></tr>
 <tr><td><b>Publish / edit</b></td><td>Yes — publishes workbooks and data sources</td><td>No — cannot save or overwrite content</td></tr>
 <tr><td><b>Interact</b></td><td>Everything</td><td>Filters, highlight actions, parameter, tooltips, comments, subscriptions</td></tr>
 <tr><td><b>Download</b></td><td>Full data (if allowed)</td><td>Images, PDF, summary data — never full data</td></tr>
 <tr><td><b>In our project</b></td><td>The 2 analysts who build and update the workbook</td><td>Faculty / compliance reviewers who explore it</td></tr>
</table>
<p class="small muted" style="margin-top:12px">Every deployment needs at least one Creator; Explorer (US$42) sits in
between for users who edit existing views. We built it in free <b>Tableau Public</b> — but everything published there is
public, which is a privacy decision in itself.</p>"""),

    # 14 — ethics
    slide(head("Unit 6 · Privacy, security &amp; ethics", "“But the data is already public” is not enough") + """
<div class="grid2" style="grid-template-columns:1fr 1fr;gap:28px">
 <div>
  <h3>Issues in this dataset</h3>
  <ul class="small">
   <li><b>Consent</b>: employees never agreed to have their email published; some messages were later removed at their request.</li>
   <li><b>Secondary reuse</b>: data released for a legal investigation is reused for research and teaching.</li>
   <li><b>Re-identification</b>: names, titles and network position identify people even when names are hidden.</li>
   <li><b>Metadata reveals a lot</b>: who-whom-when exposes hierarchy, cliques and work patterns.</li>
   <li><b>Emerging risk</b>: Enron emails are part of public AI training data, where models can leak addresses.</li>
  </ul>
 </div>
 <div>
  <h3>What we did</h3>
  <ul class="small">
   <li>Metadata only — no message bodies, no topic labels, no email addresses.</li>
   <li>Real names only for 10 company officers; everyone else is a role pseudonym (e.g. VP-03).</li>
   <li>Job titles reduced to 7 coarse role groups to lower re-identification risk.</li>
   <li>On Tableau Public: turn off workbook and data download; in an organisation, use Viewer roles and least privilege.</li>
   <li>Reported data-quality limits openly (clock drift, missing titles).</li>
  </ul>
 </div>
</div>"""),

    # 15 — conclusion
    slide(head("Conclusion", "What the dashboard shows") + f"""
<ul style="margin-bottom:24px">
 <li>Cleaning mattered: <b>73%</b> of raw records were duplicates or artefacts, and a timestamp drift would have produced a false finding.</li>
 <li>The email graph passes the Unit 5 locality test (<b>{LOC['p_closed']:.2f}</b> vs <b>{LOC['density']:.2f}</b>)
     and splits into <b>{GN['communities_ge3']}</b> meaningful communities.</li>
 <li>In the crisis, traffic rose <b>{CRI['deliveries_per_week'] / PRE['deliveries_per_week']:.1f}×</b> and shifted
     towards executives, who also became the main brokers.</li>
 <li>Useful insight came from metadata alone, which is exactly why privacy-by-design was needed.</li>
</ul>
<h3>Limitations &amp; future work</h3>
<div class="chips"><span class="chip">Only ~150 mailboxes</span><span class="chip">32% of job titles missing</span>
<span class="chip">Timestamp drift</span><span class="chip">Add sentiment from text (with ethics approval)</span>
<span class="chip">Dynamic community tracking</span></div>"""),

    # 16 — references
    slide(head("References (selected)", "Thank you — questions?") + """
<ol class="refs" style="padding-left:26px;columns:2;column-gap:46px">
 <li>B. Klimt and Y. Yang, “The Enron corpus: A new dataset for email classification research,” ECML, 2004.</li>
 <li>C. E. Priebe, J. M. Conroy, D. J. Marchette and Y. Park, “Scan statistics on Enron graphs,” Comput. Math. Organ. Theory, 11(3), 2005.</li>
 <li>igraphdata R package, dataset <i>enron</i> (Enron email network).</li>
 <li>J. Leskovec, A. Rajaraman and J. D. Ullman, <i>Mining of Massive Datasets</i>, ch. 10, Cambridge Univ. Press.</li>
 <li>M. Girvan and M. E. J. Newman, “Community structure in social and biological networks,” PNAS, 99(12), 2002.</li>
 <li>L. C. Freeman, “A set of measures of centrality based on betweenness,” Sociometry, 40(1), 1977.</li>
 <li>V. D. Blondel et al., “Fast unfolding of communities in large networks,” J. Stat. Mech., 2008.</li>
 <li>B. Shneiderman, “The eyes have it: A task by data type taxonomy for information visualizations,” IEEE VL, 1996.</li>
 <li>E. R. Tufte, <i>The Visual Display of Quantitative Information</i>, 2nd ed., Graphics Press, 2001.</li>
 <li>M. Zimmer, “‘But the data is already public’: On the ethics of research in Facebook,” Ethics Inf. Technol., 12(4), 2010.</li>
 <li>A. Narayanan and V. Shmatikov, “De-anonymizing social networks,” IEEE S&amp;P, 2009.</li>
 <li>L. Sweeney, “k-anonymity: A model for protecting privacy,” IJUFKS, 10(5), 2002.</li>
 <li>d. boyd and K. Crawford, “Critical questions for big data,” Inf. Commun. Soc., 15(5), 2012.</li>
 <li>J. Huang, H. Shao and K. C.-C. Chang, “Are large pre-trained language models leaking your personal information?,” EMNLP Findings, 2022.</li>
 <li>Tableau, “Permissions, site roles, and licenses,” Tableau Help; Tableau pricing page, 2026.</li>
</ol>
<p class="muted small" style="margin-top:16px">Faheemuddin Sayyed · Sanidhya Awasthi &nbsp;|&nbsp; Guided by Dr. Deepak Dharrao</p>"""),
]


def main():
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Data Science CA-3 – Enron Email Network</title>
<style>{CSS}</style></head>
<body>
<div id="stage">{''.join(SLIDES)}</div>
<div class="nav left" aria-label="Previous slide"><span>&#8249;</span></div>
<div class="nav right" aria-label="Next slide"><span>&#8250;</span></div>
<script>{JS}</script>
</body></html>"""
    out = HERE / "CA3_Presentation.html"
    out.write_text(html)
    print(f"wrote {out.name}: {len(SLIDES)} slides, {len(html) / 1e6:.1f} MB, screenshots: {sorted(SHOT) or 'none'}")


if __name__ == "__main__":
    main()
