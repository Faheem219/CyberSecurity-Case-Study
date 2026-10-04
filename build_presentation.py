"""Build G04_Presentation.html: a self-contained 16:9 deck for the CA-2 video.

Usage: python3 build_presentation.py
Controls in the deck: → / Space / PageDown = next, ← / PageUp = previous, Home / End, F = full screen.
Arrows appear only while hovering the left/right edge; the cursor hides after 2 s of no movement.
"""
import base64
import io
import json
from pathlib import Path

from PIL import Image

HERE = Path(__file__).parent
FIGS = HERE / "implementation" / "figures"
S = json.loads((HERE / "implementation" / "results" / "summary.json").read_text())
B, N, US, TT = S["baseline"], S["nhi"], S["gateway_us_per_call"], S["tamper_test"]


def data_uri(path, max_w=None):
    im = Image.open(path)
    if max_w and im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


LOGO = data_uri(HERE / "sit-logo.png", 2000)
FIG = {name: data_uri(FIGS / f"{name}.png") for name in
       ("fig_architecture", "fig_tactics", "fig_outcomes", "fig_timeline")}

TITLE = ("Non-Human Identity and Scoped Delegation for Intrusion Detection and Forensic Attribution "
         "of AI-Orchestrated Attacks: A Case Study of the GTG-1002 Espionage Campaign (2025)")

CSS = """
:root{--ink:#111418;--muted:#4a5160;--blue:#1F3864;--accent:#2A4DA8;--accent2:#5A97EE;--line:#d5dbe7;--tint:#eef3fc}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:100%;height:100%;background:#fff;overflow:hidden}
body{font-family:"Segoe UI",Calibri,"Helvetica Neue",-apple-system,Arial,sans-serif;color:var(--ink);-webkit-font-smoothing:antialiased}
body.idle,body.idle *{cursor:none!important}
#stage{position:absolute;left:50%;top:50%;width:1600px;height:900px;transform-origin:center center}
.slide{position:absolute;inset:0;opacity:0;visibility:hidden;transition:opacity .25s ease;padding:66px 90px 64px;display:flex;flex-direction:column}
.content{flex:1;display:flex;flex-direction:column;justify-content:center;padding-bottom:26px}
body.static .slide{transition:none}
.slide.active{opacity:1;visibility:visible}
.frame{position:absolute;inset:18px;border:2.5px solid #1b1b1b;border-radius:34px;pointer-events:none}
.kicker{font-size:19px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:var(--accent);margin-bottom:8px}
h2{font-size:46px;font-weight:700;line-height:1.12;margin-bottom:10px;color:var(--ink)}
h3{font-size:27px;font-weight:700;color:var(--blue);margin-bottom:10px}
p,li{font-size:28px;line-height:1.4}
ul{padding-left:28px}
li{margin-bottom:12px}
li::marker{color:var(--accent)}
.muted{color:var(--muted)}
.small{font-size:23px}
.src{position:absolute;left:90px;bottom:42px;font-size:16px;color:var(--muted)}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:40px}
.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:26px}
.grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:22px}
.card{border:1.5px solid var(--line);border-radius:18px;padding:22px 24px;background:#fff}
.card.tint{background:var(--tint);border-color:#cfdaf0}
.card p,.card li{font-size:23px}
.stat .v{font-size:60px;font-weight:800;color:var(--accent);line-height:1}
.stat .l{font-size:22px;color:var(--muted);margin-top:10px;line-height:1.3}
.chips{display:flex;gap:14px;flex-wrap:wrap}
.chip{border:1.5px solid var(--accent);color:var(--accent);border-radius:999px;padding:9px 22px;font-size:23px;font-weight:600}
.flow{display:flex;align-items:stretch;gap:12px}
.flow .step{flex:1;border:1.5px solid var(--line);border-radius:16px;padding:16px 16px;background:#fff}
.flow .step b{display:block;color:var(--accent);font-size:17px;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px}
.flow .step span{font-size:22px;line-height:1.3;display:block}
.flow .gate{writing-mode:vertical-rl;transform:rotate(180deg);font-size:15px;font-weight:700;color:var(--blue);border-left:2px dashed var(--accent2);padding:0 4px;text-align:center}
.flow .arrow{align-self:center;color:var(--accent);font-size:28px}
.ai{display:inline-block;font-style:normal;margin-top:12px;font-size:15px;font-weight:700;border-radius:6px;padding:2px 8px;background:var(--tint);color:var(--blue)}
.ai.h{background:#fff;border:1.5px solid var(--ink);color:var(--ink)}
table{border-collapse:collapse;width:100%}
th{font-size:18px;text-transform:uppercase;letter-spacing:1px;color:var(--blue);text-align:left;padding:10px 12px;border-bottom:2px solid var(--accent);background:var(--tint)}
td{font-size:22px;padding:12px 12px;border-bottom:1px solid var(--line);vertical-align:top;line-height:1.3}
.figure{width:100%;display:block}
.tiles{display:grid;grid-template-columns:repeat(4,1fr);gap:22px;margin-bottom:28px}
.tile{border:1.5px solid var(--line);border-radius:18px;padding:22px}
.tile .t{font-size:19px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;min-height:52px}
.tile .from{font-size:26px;color:var(--muted);margin-top:8px}
.tile .to{font-size:58px;font-weight:800;color:var(--accent);line-height:1.05}
.callout{border-left:6px solid var(--accent);background:var(--tint);padding:18px 24px;border-radius:0 14px 14px 0;font-size:25px;line-height:1.35}
.refs li{font-size:19px;line-height:1.3;margin-bottom:6px}
/* title slide (matches the group's template) */
.title-slide{text-align:center;padding:40px 110px}
.title-slide .logo{height:178px;margin:30px auto 0;display:block}
.title-slide .course{font-size:34px;font-weight:700;margin-top:34px}
.title-slide .topic{font-size:33px;font-weight:700;line-height:1.3;margin:26px auto 0;max-width:1300px}
.title-slide .group{font-size:30px;margin-top:30px}
.title-slide .names{font-size:26px;line-height:1.75;margin-top:14px}
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


SLIDES = [
    # 1 — title, same layout as the group's template (no "Guided by")
    slide(f"""
<img class="logo" src="{LOGO}" alt="Symbiosis Institute of Technology, Pune">
<div class="course">Cyber Security — CA-2 Case Study</div>
<div class="topic">{TITLE}</div>
<div class="group">Group Number: Group – 04</div>
<div class="names">Raghav Sonchhatra – PRN 23070122172<br>Sanidhya Awasthi – PRN 23070122192<br>Faheemuddin Sayyed – PRN 23070122196</div>
<div class="foot">Theory CA-2 (Part 2) — Case Study Report &nbsp;|&nbsp; Department of Computer Engineering &nbsp;|&nbsp; Academic Year 2026–27</div>
""", "title-slide"),

    # 2 — why now
    slide(head("Introduction", "AI agents now act — and each one is a non-human identity") + """
<div class="grid2" style="grid-template-columns:1fr 1.15fr;align-items:start">
 <div style="display:grid;gap:22px">
  <div class="card stat"><div class="v">82 : 1</div><div class="l">machine identities for every human identity in enterprises</div></div>
  <div class="card stat"><div class="v">42%</div><div class="l">of machine identities hold privileged or sensitive access</div></div>
  <div class="card stat"><div class="v">22%</div><div class="l">of breaches begin with credential abuse — the top initial access vector</div></div>
 </div>
 <div>
  <ul>
   <li><b>MCP</b> lets agents call tools; <b>A2A</b> lets agents call other agents.</li>
   <li>Agents usually run on one <b>shared, long-lived API key</b>.</li>
   <li>When agents delegate to sub-agents, nothing records <b>who authorised what</b>.</li>
  </ul>
  <h3 style="margin-top:26px">Unit 4 links</h3>
  <div class="chips"><span class="chip">Intrusion Detection</span><span class="chip">Digital Forensics</span>
  <span class="chip">Security tools: Kali, Nmap</span><span class="chip">Malware analysis</span></div>
 </div>
</div>
<div class="src">Sources: CyberArk Identity Security Landscape 2025; Verizon DBIR 2025; MCP spec 2025-06-18; Google A2A 2025.</div>"""),

    # 3 — GTG-1002 at a glance
    slide(head("Case study", "GTG-1002 at a glance (Anthropic, November 2025)") + """
<div class="grid4" style="margin-bottom:30px">
 <div class="card stat tint"><div class="v">~30</div><div class="l">organisations targeted; a handful of confirmed intrusions</div></div>
 <div class="card stat tint"><div class="v">80–90%</div><div class="l">of tactical work carried out by the AI agent</div></div>
 <div class="card stat tint"><div class="v">4–6</div><div class="l">human decision points per campaign</div></div>
 <div class="card stat tint"><div class="v">ops / sec</div><div class="l">peak request rate — beyond any human team</div></div>
</div>
<ul>
 <li>Detected mid-September 2025; attributed with high confidence to a Chinese state-sponsored group.</li>
 <li>Targets: technology, finance, chemical manufacturing and government agencies.</li>
 <li>Cover story: “staff of a legitimate security firm doing defensive testing”; work split into harmless-looking tasks.</li>
 <li>Commodity open-source tools driven through MCP servers — <b>no custom malware</b>.</li>
 <li>Response: accounts banned, victims and authorities notified, detection classifiers improved.</li>
</ul>
<div class="src">Source: Anthropic Threat Intelligence, “Disrupting the first reported AI-orchestrated cyber espionage campaign”, Nov 2025.</div>"""),

    # 4 — phases
    slide(head("Case study", "How the campaign unfolded: six phases, three human gates") + """
<div class="flow" style="height:250px;margin-top:20px">
 <div class="step"><b>Phase 1</b><span>Initialisation &amp; target selection</span><i class="ai h">Human</i></div>
 <div class="step"><b>Phase 2</b><span>Reconnaissance &amp; attack-surface mapping</span><i class="ai">AI</i></div>
 <div class="gate">Gate: approve exploitation</div>
 <div class="step"><b>Phase 3</b><span>Vulnerability discovery &amp; validation</span><i class="ai">AI</i></div>
 <div class="gate">Gate: authorise credentials</div>
 <div class="step"><b>Phase 4</b><span>Credential harvesting &amp; lateral movement</span><i class="ai">AI</i></div>
 <div class="step"><b>Phase 5</b><span>Data collection &amp; extraction</span><i class="ai">AI</i></div>
 <div class="gate">Gate: approve exfiltration</div>
 <div class="step"><b>Phase 6</b><span>Documentation &amp; handoff</span><i class="ai">AI</i></div>
</div>
<div class="callout" style="margin-top:48px">An orchestrator handed small tasks to sub-agents. Each task looked legitimate on its own —
the attack was only visible across the <b>whole delegation tree</b>. The AI also overstated results, e.g. credentials that did not work.</div>"""),

    # 5 — literature (part 1)
    slide(head("Literature review · 1 of 2", "Agentic attacks and the identity problem") + """
<div class="grid2">
 <div class="card"><h3>AI-orchestrated attacks</h3><ul>
  <li>Fang et al. 2024: LLM agents exploited test websites without human help.</li>
  <li>PentestGPT (USENIX Security ’24): models can plan multi-step penetration tests.</li>
  <li>Greshake et al. (AISec ’23): indirect prompt injection steers agents.</li>
  <li>OWASP LLM Top 10 · NIST AI 100-2 · MITRE ATLAS.</li></ul></div>
 <div class="card"><h3>Agent &amp; non-human identity</h3><ul>
  <li>OWASP NHI Top 10 (2025): offboarding, secret leakage, over-privilege, reuse.</li>
  <li>OWASP Agentic Top 10 (2026): identity &amp; privilege abuse, insecure inter-agent comms.</li>
  <li>SPIFFE workload identity · NIST SP 800-207 Zero Trust.</li>
  <li>Chan et al. (FAccT ’24): agent IDs, monitoring, activity logs · South et al. 2025: authenticated delegation.</li></ul></div>
</div>
<p class="muted small" style="margin-top:22px">Most of this work asks what the model can do; less asks how the environment authorises each action an agent takes.</p>"""),

    # 6 — literature (part 2)
    slide(head("Literature review · 2 of 2", "Delegation, detection and forensics — and the gap") + """
<div class="grid2" style="margin-bottom:26px">
 <div class="card"><h3>Delegation &amp; least privilege</h3><ul>
  <li>Saltzer &amp; Schroeder 1975: least privilege, complete mediation.</li>
  <li>Hardy 1988: the confused deputy.</li>
  <li>OAuth 2.0 · Token Exchange (RFC 8693) · Macaroons (NDSS ’14).</li>
  <li>MCP authorization spec · IETF on-behalf-of draft for AI agents.</li></ul></div>
 <div class="card"><h3>IDS &amp; digital forensics</h3><ul>
  <li>Denning 1987 · Snort · Bro/Zeek · NIST SP 800-94.</li>
  <li>Sommer &amp; Paxson 2010: false positives in anomaly detection.</li>
  <li>Kill chain · MITRE ATT&amp;CK.</li>
  <li>NIST SP 800-86 · 800-61r3 · tamper-evident logs (Schneier &amp; Kelsey; Crosby &amp; Wallach).</li></ul></div>
</div>
<div class="callout"><b>Research gap:</b> identity work rarely measures the effect on detection, and IDS work rarely assumes a verifiable delegation chain.
No public study tests both against a GTG-1002-shaped scenario.</div>"""),

    # 6 — objectives & methodology
    slide(head("Methodology", "Objectives and a four-stage method") + """
<ul style="margin-bottom:28px">
 <li>Analyse GTG-1002 phase by phase and find the identity failure behind each phase.</li>
 <li>Design controls based on non-human identity and scoped delegation that feed IDS and forensics.</li>
 <li>Prototype them and measure the effect against a shared-key baseline.</li>
</ul>
<div class="flow" style="height:230px">
 <div class="step"><b>Stage 1</b><span>Case reconstruction from the primary report — public, summary-level facts only</span></div><div class="arrow">→</div>
 <div class="step"><b>Stage 2</b><span>Map phases to MITRE ATT&amp;CK and OWASP NHI / Agentic risks</span></div><div class="arrow">→</div>
 <div class="step"><b>Stage 3</b><span>Control design from five principles (P1–P5)</span></div><div class="arrow">→</div>
 <div class="step"><b>Stage 4</b><span>Experiment: baseline vs NHI, 50 seeds, identical IDS rules</span></div>
</div>
<p class="muted small" style="margin-top:22px">Synthetic data: no real system is touched, ground truth is labelled, and every run is repeatable.</p>"""),

    # 7 — mapping table
    slide(head("Methodology · Stage 2", "Each phase relied on an identity failure") + """
<table>
 <tr><th style="width:27%">GTG-1002 phase</th><th style="width:19%">ATT&amp;CK tactic</th><th style="width:27%">Identity failure</th><th>Control in this study</th></tr>
 <tr><td>1 · Initialisation (security-firm persona)</td><td>Resource development</td><td>Claimed purpose not tied to an accountable person</td><td>Grant issued by a named human; purpose stored in token</td></tr>
 <tr><td>2 · Reconnaissance</td><td>Discovery</td><td>One broad credential; machine tempo</td><td>Resource scope; R1 tempo; R2 probing</td></tr>
 <tr><td>3 · Vulnerability discovery</td><td>Initial access, execution</td><td>Sub-tasks look legitimate alone</td><td>Identity per sub-agent; R3 on whole grant</td></tr>
 <tr><td>4 · Credentials &amp; lateral movement</td><td>Credential access, lateral movement</td><td>Harvested secrets usable by any agent</td><td>Scopes cannot widen; short lifetimes</td></tr>
 <tr><td>5 · Data collection</td><td>Collection, exfiltration</td><td>No blast-radius limit</td><td>Resource scoping; refusals logged</td></tr>
 <tr><td>6 · Documentation &amp; handoff</td><td>Persistence</td><td>Access handed on with no expiry</td><td>TTL, depth limit, revocation; hash-chained log</td></tr>
</table>"""),

    # 8 — design
    slide(head("Methodology · Stage 3", "Control design: identity at every hop") + f"""
<div class="grid2" style="grid-template-columns:0.9fr 1.25fr;align-items:center">
 <ul>
  <li><b>P1</b> One identity per agent, with a named human owner.</li>
  <li><b>P2</b> Authority only narrows along the delegation chain.</li>
  <li><b>P3</b> One gateway checks every tool call (complete mediation).</li>
  <li><b>P4</b> Every decision goes into a tamper-evident log.</li>
  <li><b>P5</b> IDS rules keyed on identity and grant, not IP or key.</li>
 </ul>
 <img class="figure" src="{FIG['fig_architecture']}" alt="Architecture">
</div>
<p class="muted small" style="margin-top:18px">Why identity? Model-side classifiers belong to the AI provider, and network IDS sees encrypted calls to legitimate APIs. Identity is the one signal the defending organisation can enforce and log itself.</p>"""),

    # 9 — implementation (part 1)
    slide(head("Implementation · 1 of 2", "Tokens, gateway and audit log") + """
<div class="grid3" style="margin-bottom:26px">
 <div class="card"><h3>Scoped delegation token</h3><p>JSON claims signed with HMAC-SHA256:
  <i>grant, chain (human → agents), scopes, resources, expiry, depth, purpose</i>.</p></div>
 <div class="card"><h3>delegate() only narrows</h3><p>Child scope ⊆ parent · resources ⊆ parent · expiry ≤ parent · depth − 1.
  Otherwise refused: <i>scope_widening</i>, <i>resource_widening</i>, <i>depth_exceeded</i> — and the refusal is logged.</p></div>
 <div class="card"><h3>Tool gateway + audit log</h3><p>One enforcement point checks signature, expiry, scope and resource for every call.
  Each log record carries the SHA-256 of the previous one.</p></div>
</div>
<div class="callout small">Python 3 standard library (hmac, hashlib, json, secrets) + matplotlib, about 500 lines.
Tool names are abstract labels — the prototype only decides, records and analyses; nothing is executed.</div>"""),

    # 10 — implementation (part 2)
    slide(head("Implementation · 2 of 2", "Detection rules and the test workload") + """
<div class="grid3" style="margin-bottom:26px">
 <div class="card tint"><h3>R1 · Tempo</h3><p>One agent makes more than 20 calls in 10 seconds — faster than any human operator.</p></div>
 <div class="card tint"><h3>R2 · Probing</h3><p>One agent is denied 3 times within 60 seconds — it keeps hitting permission walls.</p></div>
 <div class="card tint"><h3>R3 · Multi-tactic chain</h3><p>One delegation grant touches 3+ sensitive ATT&amp;CK tactics within 30 minutes.</p></div>
</div>
<ul>
 <li><b>Benign agents:</b> CI tests, docs sync, ops inventory, nightly backup (looks like collection + exfiltration on purpose).</li>
 <li><b>Misuse tree:</b> contractor → orchestrator → five sub-agents, holding a staging-only “testing” grant.</li>
 <li><b>Runs:</b> 3 simulated hours × 50 seeds, baseline (shared key) vs NHI — identical IDS rules.</li>
</ul>"""),

    # 10 — key outcomes
    slide(head("Results", "Same workload, same IDS rules — only identity changed") + f"""
<div class="tiles">
 <div class="tile"><div class="t">Misuse calls blocked</div><div class="from">{B['misuse_blocked_pct']:.0f}% →</div><div class="to">{N['misuse_blocked_pct']:.0f}%</div></div>
 <div class="tile"><div class="t">Prod / external resources exposed</div><div class="from">{B['blast_radius_mean']:.1f} →</div><div class="to">{N['blast_radius_mean']:.0f}</div></div>
 <div class="tile"><div class="t">False alerts per run</div><div class="from">{B['false_alerts_mean']:.2f} →</div><div class="to">{N['false_alerts_mean']:.0f}</div></div>
 <div class="tile"><div class="t">Alerts naming the accountable human</div><div class="from">{B['alert_attribution_pct']:.0f}% →</div><div class="to">{N['alert_attribution_pct']:.0f}%</div></div>
</div>
<ul>
 <li>Detection in <b>100%</b> of runs for both; median time to first alert {B['ttd_median_s']} s vs <b>{N['ttd_median_s']} s</b>.</li>
 <li>Benign calls wrongly denied: <b>{N['benign_denied_total']}</b>. Extra cost: <b>{US['nhi'] - US['baseline']:.1f} µs</b> per tool call.</li>
 <li>Baseline alerts name only the shared key — containing the attack means stopping every legitimate agent too.</li>
</ul>
<div class="src">Means over {N['runs']} seeded runs; baseline = one shared API key with wildcard scope.</div>"""),

    # 11 — by tactic
    slide(head("Results", "Prevention by ATT&CK tactic") + f"""
<div class="grid2" style="grid-template-columns:1.35fr 1fr;align-items:center">
 <img class="figure" src="{FIG['fig_tactics']}" alt="Misuse calls allowed by tactic">
 <ul>
  <li>Credential access, lateral movement, collection and exfiltration: <b>0 calls allowed</b>.</li>
  <li>The ~{N['misuse_allowed_mean']:.0f} calls per run that succeeded were discovery on staging — <b>which the grant allowed</b>.</li>
  <li>So scoping limits damage, but detection is still needed.</li>
  <li>Every refused delegation became evidence for the IDS.</li>
 </ul>
</div>"""),

    # 12 — forensic timeline
    slide(head("Results · Digital forensics", "Who, on whose behalf, did what, when") + f"""
<img class="figure" src="{FIG['fig_timeline']}" alt="Forensic timeline" style="width:82%;margin:0 auto">
<div class="grid3" style="margin-top:14px">
 <p class="small"><b>{N['record_attribution_pct']:.0f}%</b> of misuse records traced to the contractor identity (baseline: {B['record_attribution_pct']:.0f}%).</p>
 <p class="small">First alert: <b>R2 probing</b>, seconds after the first misuse call.</p>
 <p class="small">Tamper test: one edited record in a {TT['records']}-record log detected at exactly record {TT['detected_at_index']}.</p>
</div>"""),

    # 13 — discussion
    slide(head("Discussion", "What this means for GTG-1002") + """
<p style="margin-bottom:22px">The attackers ran their agents on their own infrastructure, so victims cannot force scoped tokens on them. The controls apply in three places:</p>
<div class="grid3" style="margin-bottom:28px">
 <div class="card tint"><h3>AI &amp; tool platforms</h3><p>Require a verified identity and an explicit, scoped grant before “security testing” use — a role-play claim becomes a named person’s decision.</p></div>
 <div class="card tint"><h3>Organisations running agents</h3><p>Stop their own agents from being hijacked or over-trusted; every action stays attributable.</p></div>
 <div class="card tint"><h3>Target organisations</h3><p>Issue short-lived, narrowly scoped machine credentials so harvested credentials are worth far less.</p></div>
</div>
<p class="small muted"><b>Limitations:</b> synthetic data; hand-set thresholds; single signing key; no cross-organisation delegation; a slow attacker inside a legitimate scope is only detected, not blocked.</p>"""),

    # 14 — conclusion
    slide(head("Conclusion", "Identity is the missing control for agentic attacks") + f"""
<ul style="margin-bottom:30px">
 <li>GTG-1002 used ordinary tools; the real failure was <b>authority nobody had scoped and nobody could trace</b>.</li>
 <li>Per-agent identity + delegation that only narrows + identity-aware IDS + tamper-evident logs:
   <b>{N['misuse_blocked_pct']:.0f}%</b> of misuse blocked, <b>zero</b> production exposure, <b>zero</b> false alerts, <b>100%</b> attribution.</li>
 <li>The same identity data that limits damage also sharpens detection and makes forensics possible.</li>
</ul>
<h3>Future work</h3>
<div class="chips"><span class="chip">Real agent logs</span><span class="chip">Learned per-agent thresholds</span>
<span class="chip">Cross-organisation delegation (A2A)</span><span class="chip">Platform-verified agent identity</span></div>"""),

    # 15 — references + thanks
    slide(head("References (selected)", "Thank you") + """
<ol class="refs" style="padding-left:26px;columns:2;column-gap:46px">
 <li>Anthropic, “Disrupting the first reported AI-orchestrated cyber espionage campaign,” Nov. 2025.</li>
 <li>Anthropic, “Threat intelligence report: August 2025,” Aug. 2025.</li>
 <li>Google GTIG, “AI threat tracker: Advances in threat actor usage of AI tools,” Nov. 2025.</li>
 <li>OWASP, “Top 10 Non-Human Identities Risks – 2025.”</li>
 <li>OWASP GenAI, “Top 10 for Agentic Applications for 2026,” Dec. 2025.</li>
 <li>T. South et al., “Authenticated delegation and authorized AI agents,” arXiv:2501.09674, 2025.</li>
 <li>A. Chan et al., “Visibility into AI agents,” ACM FAccT, 2024.</li>
 <li>Model Context Protocol, “Specification 2025-06-18: Authorization.”</li>
 <li>M. Jones et al., “OAuth 2.0 token exchange,” RFC 8693, 2020.</li>
 <li>A. Birgisson et al., “Macaroons,” NDSS, 2014.</li>
 <li>D. E. Denning, “An intrusion-detection model,” IEEE TSE, 1987.</li>
 <li>B. E. Strom et al., “MITRE ATT&amp;CK: Design and philosophy,” 2018.</li>
 <li>K. Kent et al., NIST SP 800-86, 2006; A. Nelson et al., NIST SP 800-61r3, 2025.</li>
 <li>B. Schneier and J. Kelsey, “Secure audit logs to support computer forensics,” ACM TISSEC, 1999.</li>
</ol>
<p class="muted small" style="margin-top:20px">Full list of 41 references in the report (G04). &nbsp;Group 04 · Raghav Sonchhatra · Sanidhya Awasthi · Faheemuddin Sayyed</p>"""),
]


def main():
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>G04 – Cyber Security CA-2</title>
<style>{CSS}</style></head>
<body>
<div id="stage">{''.join(SLIDES)}</div>
<div class="nav left" aria-label="Previous slide"><span>&#8249;</span></div>
<div class="nav right" aria-label="Next slide"><span>&#8250;</span></div>
<script>{JS}</script>
</body></html>"""
    out = HERE / "G04_Presentation.html"
    out.write_text(html)
    print(f"wrote {out.name}: {len(SLIDES)} slides, {len(html) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
