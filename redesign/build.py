#!/usr/bin/env python3
"""Build the Orion TerraMetrics corporate site into redesign/dist.

  BASE=/company/ PREVIEW=1 python3 redesign/build.py   # preview at orionterrametrics.com/company/
  BASE=/ python3 redesign/build.py                     # production at orionterrametrics.co.ke

No dependencies beyond the Python standard library.
"""
import json, os, re, shutil, urllib.parse, html as H
from pathlib import Path
from data import COM, PROJECTS, SOLUTIONS, INDUSTRIES, PRODUCTS, CLIENTS, COURSES, ON_ORIONGIS

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
BASE = os.environ.get("BASE", "/company/")
PREVIEW = os.environ.get("PREVIEW", "1") == "1"
SITE = "https://orionterrametrics.co.ke/"
ENDPOINT = "/api/contact" if BASE == "/company/" else COM + "/api/contact"
EMAIL, PHONE1, PHONE2 = "info@orionterrametrics.co.ke", "+254 799 882 124", "+254 729 212 061"
ADDRESS = "GMC Mansion, 1st Floor, Mukhtar Dadah Street, Nairobi, Kenya"
PAGES = []   # (path, title, desc, category, html)

def e(s): return H.escape(str(s), quote=True)
def u(p): return BASE + p
def img(name, alt, cls="", eager=False, sizes=""):
    return f'<img src="{u("assets/img/"+name+".webp")}" alt="{e(alt)}"{" class=%s" % chr(34)+cls+chr(34) if cls else ""} {"fetchpriority=high" if eager else "loading=lazy"} decoding="async">'
def logo(name, alt, h=""):
    return f'<img src="{u("assets/logos/"+name)}" alt="{e(alt)}" loading="lazy">'

ICON = {
 "survey":'<path d="M12 2v8m0 0l-5 11m5-11l5 11M8 14h8"/>',
 "map":'<path d="M9 4L3 6v14l6-2 6 2 6-2V4l-6 2-6-2zM9 4v14m6-12v14"/>',
 "sat":'<path d="M5 19l4-4m-1-8l3 3-4 4-3-3 4-4zm8 0l3 3-4 4-3-3 4-4zM14 21a7 7 0 0 0 7-7"/>',
 "flow":'<path d="M4 6h6v5H4zM14 13h6v5h-6zM7 11v4h7M17 13V8h-7"/>',
 "db":'<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
 "compass":'<circle cx="12" cy="12" r="9"/><path d="M15.5 8.5l-2 5-5 2 2-5z"/>',
 "shield":'<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
 "spark":'<path d="M12 3v4m0 10v4M3 12h4m10 0h4M6 6l2.5 2.5m7 7L18 18M6 18l2.5-2.5m7-7L18 6"/>',
 "people":'<circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.5"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6M15 14.5c3 0 6 1.8 6 5"/>',
 "search":'<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>',
 "menu":'<path d="M4 7h16M4 12h16M4 17h16"/>',
 "globe":'<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/>',
 "book":'<path d="M4 5c3-1 6-1 8 1 2-2 5-2 8-1v14c-3-1-6-1-8 1-2-2-5-2-8-1z"/><path d="M12 6v14"/>',
 "hand":'<path d="M7 11l3-3 4 1 4-3 3 3-6 6-3-1-3 3-4-4z"/>',
}
def ico(k): return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICON[k]}</svg>'
SOL_ICON = {"surveying":"survey","gis":"map","remote-sensing":"sat","transformation":"flow","data-infrastructure":"db","consulting":"compass"}

# ------------------------------------------------------------------ navigation
NAV = [
 ("Solutions","Field data, analysis and platforms, delivered end to end.","solutions.html",[("Services",[(s["name"],s["short"],s["file"]) for s in SOLUTIONS.values()])]),
 ("Industries","Any organisation whose decisions depend on place.","industries.html",[("Public sector and infrastructure",[(i["name"],i["short"],i["file"]) for i in INDUSTRIES.values() if i["group"]=="public"]),("Enterprise and markets",[(i["name"],i["short"],i["file"]) for i in INDUSTRIES.values() if i["group"]=="commercial"])]),
 ("Technology","OrionGIS: the AI-powered geospatial workspace.","technology.html",[("Platform",[("OrionGIS workspace","Ask, map, collect and report in one AI-powered workspace.","technology.html"),("OrionAI and GeoAI","Plain-language questions, finished and explained answers.","technology.html#orionai"),("Spatial data infrastructure","Geoportals, registries and open data at scale.","data-infrastructure.html")]),("Engineering",[("Integration","QGIS, OGC services, APIs and Orion Collect.","technology.html#integration"),("Research and innovation","What our R&D team is working on.","research.html"),("Visit OrionGIS ↗","Sign in or start free at orionterrametrics.com.",COM)])]),
 ("Our work","Projects delivered for governments, utilities, health networks and businesses.","portfolio.html",[("Evidence",[("Project portfolio","Every published project, filterable by service and sector.","portfolio.html"),("Case study: national water agency","Asset registry and network model for 5 dams and 12 treatment plants.","projects/water-agency-asset-registry.html"),("Case study: county health services","178 facilities mapped into live executive dashboards.","projects/county-health-intelligence-platform.html")]),("Relationships",[("Clients and partners","Institutions we work with.","clients.html"),("Partner with us","Technology, delivery and institutional partnerships.","partners.html")])]),
 ("Insights","News, perspectives, research and events from Orion.","insights.html",[("Read",[("Newsroom","Company and product news.","newsroom.html"),("Blog","Articles from the people who do the work.","blog/"),("Research and publications","Published research by our people.","research.html#publications")]),("Learn",[("Orion Academy","Professional and corporate geospatial training.","courses.html"),("Events and webinars","Where to meet our team.","insights.html#events")])]),
 ("Company","Who we are, how we work and where we are going.","about.html",[("Who we are",[("About Orion TerraMetrics","Our story, mission and values.","about.html"),("Leadership","The people accountable for our work.","leadership.html"),("Locations","Nairobi head office and where we work.","contact.html#office")]),("Beyond business",[("Careers","Build technology that shapes Africa's future.","careers.html"),("Corporate responsibility","Open data, skills and public-interest work.","responsibility.html"),("Trust and governance","Security, privacy, ethics and policies.","trust.html")])]),
]

def mega(i, label, intro, hub, groups):
    cols = ""
    for g, items in groups:
        cols += f'<div><div class="mega-group">{e(g)}</div>' + "".join(
            f'<a href="{it[2] if it[2].startswith("http") else u(it[2])}"{" target=_blank rel=noopener" if it[2].startswith("http") else ""}><b>{e(it[0])}</b><span>{e(it[1])}</span></a>' for it in items) + "</div>"
    return f'''<li><button class="nav-top" aria-expanded="false" aria-controls="mega{i}">{e(label)}</button>
<div class="mega" id="mega{i}"><div class="wrap"><div class="mega-intro"><h3>{e(label)}</h3><p>{e(intro)}</p><a class="arrow-link" href="{u(hub)}">{e(label)} overview</a></div><div class="mega-cols">{cols}</div></div></div></li>'''

def header():
    menus = "".join(mega(i, *n) for i, n in enumerate(NAV))
    return f'''<a class="skip" href="#main">Skip to content</a>
<div class="utility"><div class="wrap"><a href="{u('careers.html')}">Careers</a><a href="{u('newsroom.html')}" class="hide-sm">Newsroom</a><a href="{u('partners.html')}" class="hide-sm">Partners</a><a href="{u('contact.html')}">Contact</a><a class="ext" href="{COM}" target="_blank" rel="noopener">OrionGIS ↗</a></div></div>
<header class="site-header"><div class="wrap">
<a class="brand" href="{u('')}" aria-label="Orion TerraMetrics home"><img src="{u('assets/OrionLogo.svg')}" alt="Orion TerraMetrics" width="104" height="40"></a>
<nav aria-label="Main"><ul class="nav">{menus}<li class="mobile-only"><a class="btn btn-primary" href="{u('contact.html')}">Talk to an expert</a></li></ul></nav>
<div class="header-actions"><button class="icon-btn" data-search aria-label="Search the site">{ico('search')}</button><a class="btn btn-primary btn-sm" href="{u('contact.html')}">Talk to an expert</a><button class="icon-btn menu-toggle" aria-label="Menu" aria-expanded="false">{ico('menu')}</button></div>
</div></header>
<div class="search-panel" role="dialog" aria-modal="true" aria-label="Search"><div class="search-box"><label for="q" class="eyebrow">Search Orion TerraMetrics</label><input id="q" type="search" placeholder="Services, sectors, projects, careers…" autocomplete="off"><ul class="search-results"></ul></div></div>'''

def footer():
    col = lambda t, items: f'<div><h4>{t}</h4><ul>' + "".join(f'<li><a href="{x if x.startswith("http") else u(x)}">{e(l)}</a></li>' for l, x in items) + "</ul></div>"
    return f'''<footer class="site-footer"><div class="wrap"><div class="foot-top">
<div class="foot-brand"><img src="{u('assets/OrionLogo.svg')}" alt="Orion TerraMetrics" width="110" height="42"><p>Orion TerraMetrics Africa Limited is an AI-native geospatial engineering and technology company in Nairobi, and the maker of OrionGIS, the AI-powered geospatial workspace.</p><p>{e(ADDRESS)}<br><a href="tel:+254799882124">{PHONE1}</a> · <a href="tel:+254729212061">{PHONE2}</a><br><a href="mailto:{EMAIL}">{EMAIL}</a></p>
<a class="foot-oriongis" href="{COM}" target="_blank" rel="noopener"><img src="{u('assets/logos/oriongis-icon.png')}" alt="" width="30" height="30"><span><b style="color:#fff">OrionGIS</b><br>The AI-powered geospatial workspace ↗</span></a></div>
{col("Solutions",[(s["name"].split(" and ")[0] if len(s["name"])>30 else s["name"],s["file"]) for s in SOLUTIONS.values()])}
{col("Industries",[(INDUSTRIES[k]["name"],INDUSTRIES[k]["file"]) for k in ["government","banking","retail","insurance","energy","health","agriculture"]]+[("All industries","industries.html")])}
{col("Our work",[("Project portfolio","portfolio.html"),("Clients and partners","clients.html"),("Technology","technology.html"),("Research","research.html"),("Blog","blog/"),("Newsroom","newsroom.html")])}
{col("Company",[("About us","about.html"),("Leadership","leadership.html"),("Careers","careers.html"),("Internships","internships.html"),("Academy","courses.html"),("Responsibility","responsibility.html")])}
{col("Get in touch",[("Discuss a project","contact.html?type=project"),("Request a proposal","contact.html?type=proposal"),("Become a partner","partners.html#become"),("Training enquiries","courses.html#enquire"),("Media enquiries","newsroom.html#media"),("Site directory","directory.html")])}
</div><div class="foot-bottom"><span>© 2026 Orion TerraMetrics Africa Limited. All rights reserved.</span><ul><li><a href="{u('privacy.html')}">Privacy</a></li><li><a href="{u('cookies.html')}">Cookies</a></li><li><a href="{u('terms.html')}">Terms</a></li><li><a href="{u('accessibility.html')}">Accessibility</a></li><li><a href="{u('security.html')}">Security</a></li><li><a href="{u('ethics.html')}">Ethics</a></li></ul></div></div></footer>'''

def page(path, title, desc, body, cat="Page", featured=False, keywords=""):
    canonical = SITE + ("" if path == "index.html" else (path[:-10] if path.endswith("/index.html") else path))
    full = title if path == "index.html" else f"{title} | Orion TerraMetrics"
    ld = {"@context":"https://schema.org","@type":"Organization","name":"Orion TerraMetrics Africa Limited","url":SITE,"logo":SITE+"assets/OrionLogo.png","email":EMAIL,"telephone":PHONE1,"address":{"@type":"PostalAddress","streetAddress":"GMC Mansion, 1st Floor, Mukhtar Dadah Street","addressLocality":"Nairobi","addressCountry":"KE"},"sameAs":[COM]} if path=="index.html" else {"@context":"https://schema.org","@type":"WebPage","name":title,"description":desc,"url":canonical,"isPartOf":{"@type":"WebSite","name":"Orion TerraMetrics","url":SITE}}
    doc = f'''<!doctype html><html lang="en-KE" data-base="{BASE}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(full)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{canonical}">
{'<meta name="robots" content="noindex,nofollow">' if PREVIEW else ''}<meta property="og:title" content="{e(full)}"><meta property="og:description" content="{e(desc)}"><meta property="og:type" content="website"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{SITE}assets/img/lidar.webp">
<link rel="icon" href="{u('assets/favicon.png')}"><link rel="apple-touch-icon" href="{u('assets/apple-touch-icon.png')}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@600;700;800&family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{u('assets/site.css')}"><script type="application/ld+json">{json.dumps(ld)}</script></head>
<body>{header()}<main id="main">{body}</main>{footer()}{contact_launcher()}{'<a class="preview-flag" href="'+u('proposal.html')+'">Preview · read the proposal</a>' if PREVIEW else ''}<script src="{u('assets/site.js')}" defer></script></body></html>'''
    PAGES.append((path, title, desc, cat, featured, keywords, doc))

# ------------------------------------------------------------------ components
def crumbs(items): return '<nav class="crumbs" aria-label="Breadcrumb"><a href="'+u('')+'">Home</a>' + "".join(f' / <a href="{u(h)}">{e(t)}</a>' if h else f' / <span>{e(t)}</span>' for t, h in items) + "</nav>"
def phero(eyebrow, title, lead, trail, image=None, actions=""):
    media = f'<div class="hero-media">{img(image, "", eager=True)}</div>' if image else ""
    return f'<section class="page-hero{" has-img" if image else ""}">{media}<div class="wrap">{crumbs(trail)}<span class="eyebrow">{e(eyebrow)}</span><h1>{e(title)}</h1><p class="lead">{e(lead)}</p>{actions}</div></section>'
def cta(title="Have a project in mind?", text="Tell us what you need, from a single survey to a national programme. A specialist replies within two working days.", primary=("Discuss a project","contact.html?type=project"), secondary=("Request a proposal","contact.html?type=proposal")):
    return f'<section class="cta-band"><div class="wrap"><div><h2>{e(title)}</h2><p>{e(text)}</p>{channels()}</div><div class="hero-actions" style="margin:0"><a class="btn btn-primary" href="{u(primary[1])}">{e(primary[0])}</a><a class="btn btn-ghost" href="{u(secondary[1])}">{e(secondary[0])}</a></div></div></section>'
P = {p[0]: p for p in PROJECTS}
def pcard(p):
    slug,title,tag,svc,ind,image,summary,m,ml = p
    return f'<a class="pcard" href="{u("projects/"+slug+".html")}" data-tags="{"|".join(svc+ind)}"><figure>{img(image, title)}</figure><div class="body"><span class="tag">{e(tag)}</span><h3>{e(title)}</h3><p>{e(summary[:150].rsplit(" ",1)[0])}…</p><div class="metric"><b>{e(m)}</b><span>{e(ml)}</span></div></div></a>'
def projects_for(key, field):
    i = 3 if field == "svc" else 4
    return [p for p in PROJECTS if key in p[i]]
def logos_strip():
    return '<div class="logos">' + "".join(f'<figure>{logo(f, n)}</figure>' for f, n in CLIENTS) + '</div>'

def enquiry_form(default="project", heading=None, types=None, extra=""):
    types = types or [("project","Discuss a project"),("proposal","Request a proposal"),("consultation","Book a consultation"),("partnership","Become a partner"),("training","Training enquiry"),("media","Media enquiry"),("careers","Careers"),("general","General enquiry")]
    radios = "".join(f'<label><input type="radio" name="type" value="{e(l)}"{" checked" if k==default else ""} data-k="{k}"> {e(l)}</label>' for k, l in types)
    return f'''<form class="form" data-enquiry="Enquiry" data-endpoint="{ENDPOINT}" novalidate>
{f'<h3 class="full">{e(heading)}</h3>' if heading else ''}
<fieldset class="full" style="border:0;padding:0;margin:0"><legend class="eyebrow" style="padding:0">What can we help with?</legend><div class="choice">{radios}</div></fieldset>
<div class="field"><label for="f-name">Full name *</label><input id="f-name" name="name" required autocomplete="name"><div class="err">Enter your name.</div></div>
<div class="field"><label for="f-email">Work email *</label><input id="f-email" name="email" type="email" required autocomplete="email"><div class="err">Enter a valid email address.</div></div>
<div class="field"><label for="f-org">Organisation</label><input id="f-org" name="organization" autocomplete="organization"></div>
<div class="field"><label for="f-role">Your role</label><input id="f-role" name="role" autocomplete="organization-title"></div>
<div class="field"><label for="f-sector">Sector</label><select id="f-sector" name="sector"><option value="">Select…</option>{"".join(f"<option>{e(i['name'])}</option>" for i in INDUSTRIES.values())}<option>Other</option></select></div>
<div class="field"><label for="f-country">Country</label><input id="f-country" name="country" autocomplete="country-name" value=""></div>
{extra}
<div class="field full"><label for="f-msg">How can we help? *</label><textarea id="f-msg" name="message" required placeholder="Location, scope, timelines and anything we should know."></textarea><div class="err">Tell us a little about your request.</div></div>
<div class="hp" aria-hidden="true"><label>Leave empty<input name="website" tabindex="-1" autocomplete="off"></label></div>
<p class="full"><small>We use these details only to answer your enquiry, as set out in our <a href="{u('privacy.html')}">privacy notice</a>.</small></p>
<div class="full"><button class="btn btn-primary" type="submit" data-label="Send enquiry">Send enquiry</button></div>
<div class="form-status" role="status" aria-live="polite"></div></form>'''


# ------------------------------------------------------------------ contact channels + Ask Orion concierge
WA = "254799882124"
def channels(cls="channels"):
    return f'<p class="{cls}"><span>Or reach us now:</span> <a href="https://wa.me/{WA}?text=Hello%20Orion%20TerraMetrics" target="_blank" rel="noopener">WhatsApp</a> <a href="tel:+254799882124">Call {PHONE1}</a> <a href="mailto:{EMAIL}">Email</a></p>'
def contact_launcher():
    return f"""<div class="launch"><button class="launch-btn" aria-expanded="false" aria-controls="launch-panel"><span>Talk to us</span></button>
<div class="launch-panel" id="launch-panel" hidden><p class="lp-h">How would you like to reach us?</p>
<a href="https://wa.me/{WA}?text=Hello%20Orion%20TerraMetrics%2C%20I%27d%20like%20to%20talk%20about%20" target="_blank" rel="noopener"><b>WhatsApp</b><span>Chat with our team now</span></a>
<a href="tel:+254799882124"><b>Call</b><span>{PHONE1} · Mon to Fri, 8:00 to 17:00 EAT</span></a>
<a href="{u('contact.html?type=consultation')}"><b>Book a consultation</b><span>45 minutes with a specialist</span></a>
<a href="{u('contact.html?type=proposal')}"><b>Request a proposal</b><span>Send terms of reference or an RFP</span></a>
<a href="mailto:{EMAIL}"><b>Email</b><span>{EMAIL}</span></a></div></div>"""
def concierge():
    kb = {"sectors":[{"n":i["name"],"u":u(i["file"]),"k":" ".join([i["name"],i["short"],i["lead"]]+i["needs"]).lower()} for i in INDUSTRIES.values()],
          "solutions":[{"n":s["name"],"u":u(s["file"]),"k":" ".join([s["name"],s["short"],s["lead"]]+[a+" "+b for a,b in s["offers"]]).lower()} for s in SOLUTIONS.values()],
          "projects":[{"n":p[1],"u":u("projects/"+p[0]+".html"),"m":p[7]+" "+p[8],"k":" ".join([p[1],p[2],p[6]]+p[3]+p[4]).lower()} for p in PROJECTS],
          "wa":WA,"contact":u("contact.html")}
    chips = ["Where should we open our next 20 branches?","Which farms in our portfolio are drought-stressed?","Map every health facility in our county","Verify land before we lend against it"]
    return f"""<div class="ask" data-ask><form class="ask-form" autocomplete="off"><label for="ask-q" class="ask-label"><img src="{u('assets/logos/orionai-icon.png')}" alt="" width="26" height="26"> Ask Orion</label>
<div class="ask-row"><input id="ask-q" name="q" placeholder="Describe the decision you need to make…" maxlength="400"><button class="btn btn-primary" type="submit">Ask</button></div></form>
<div class="ask-chips">{"".join(f'<button type="button">{e(c)}</button>' for c in chips)}</div>
<div class="ask-out" aria-live="polite" hidden></div>
<div class="ask-alt"><a href="https://wa.me/{WA}?text=Hello%20Orion%20TerraMetrics" target="_blank" rel="noopener">WhatsApp us</a><a href="tel:+254799882124">Call {PHONE1}</a><a href="{u('portfolio.html')}">See our work</a></div>
<script type="application/json" id="ask-kb">{json.dumps(kb).replace("</","<\\/")}</script></div>"""

# ------------------------------------------------------------------ home
HOME_IMG = {"water-agency-asset-registry":"ph-dam"}  # mockup placeholder photography

def home():
    # Hero proof strip: real figures from published case studies + the live OrionGIS index.
    # Platform scale, verified against the live OrionGIS index on 2026-11-27 (published + indexable rows).
    proof = [("43,000+","Open datasets indexed and ready to map",None),("7M+","Mapped features across those datasets",None),
             ("1,400+","Data publishers worldwide",None),("200+","Countries and territories covered",None)]
    proofh = '<p class="proof-k">On the Orion platform today</p>' + "".join(f'<a href="{COM}/data" target="_blank" rel="noopener"><b>{e(n)}</b><span>{e(t)}</span></a>' for n, t, l in proof)
    # Logo carousel: two identical runs so the CSS loop is seamless; the second run is hidden from assistive tech.
    run = "".join(f'<li><img src="{u("assets/logos/"+f)}" alt="{e(n)}" loading="eager" height="64"></li>' for f, n in CLIENTS)
    runb = "".join(f'<li aria-hidden="true"><img src="{u("assets/logos/"+f)}" alt="" loading="eager" height="64"></li>' for f, n in CLIENTS)
    # Capability rows
    stages = [("","Field data and imagery","",["surveying","remote-sensing"],"Surveys, drone mapping and satellite monitoring that give you an accurate record of your land, assets and facilities."),
              ("","Analysis and AI","",["gis","data-infrastructure"],"Spatial analysis and OrionAI to work out where to invest, where risk is rising and which communities a service is missing."),
              ("","Systems your teams use every day","",["transformation","consulting"],"Field forms, registries and dashboards on OrionGIS, set up for your teams and supported after handover.")]
    stageh = "".join(f'<li><span class="num">{n}</span><div><h3>{t} <em>{e(s)}</em></h3><p>{e(d)}</p><p class="svc">' + " ".join(f'<a href="{u(SOLUTIONS[k]["file"])}">{e(SOLUTIONS[k]["name"])}</a>' for k in ks) + '</p></div></li>' for n, t, s, ks, d in stages)
    # Sector index, two groups, image swaps on hover/focus
    def sec(group):
        return "".join(f'<li><a href="{u(i["file"])}" data-img="{u("assets/img/"+i["img"]+".webp")}"><b>{e(i["name"])}</b><span>{e(i["short"])}</span></a></li>' for i in INDUSTRIES.values() if i["group"] == group)
    first = next(iter(INDUSTRIES.values()))
    # Project carousel
    feat = ["health-network-facility-reporting","education-department-school-reporting","water-agency-asset-registry","industrial-park-lidar","drone-land-administration","power-line-lidar-thermal","crop-health-monitoring","urban-road-corridor-assets","cement-stockpile-volumes","metropolitan-urban-expansion"]
    slides = "".join(f'<li><a href="{u("projects/"+P[s][0]+".html")}"><figure>{img(HOME_IMG.get(s, P[s][5]), P[s][1])}</figure>{"<span class=on-og>Built on OrionGIS</span>" if s in ON_ORIONGIS else ""}<div><span class="tag">{e(P[s][2])}</span><h3>{e(P[s][1])}</h3><p class="m"><b>{e(P[s][7])}</b> {e(P[s][8])}</p></div></a></li>' for s in feat)
    tabs = "".join(f'<button role="tab" id="t-{k}" aria-controls="p-{k}" aria-selected="{str(i==0).lower()}" tabindex="{0 if i==0 else -1}"><img src="{u("assets/logos/"+ic+".png")}" alt=""><span><b>{e(n)}</b><small>{e(d.split(":")[0].split(",")[0])}</small></span></button>' for i,(k,n,ic,sc,d,l) in enumerate(PRODUCTS))
    panels = "".join(f'<div class="show-panel" role="tabpanel" id="p-{k}" aria-labelledby="t-{k}"{"" if i==0 else " hidden"}><figure><img src="{u("assets/img/"+sc+".webp")}" alt="{e(n)} in OrionGIS" loading="eager" decoding="async"></figure><div class="txt"><p>{e(d)}</p><a class="btn btn-ghost btn-sm" href="{COM}{l}" target="_blank" rel="noopener">See {e(n)} ↗</a></div></div>' for i,(k,n,ic,sc,d,l) in enumerate(PRODUCTS))
    body = f'''
<section class="hx"><div class="hx-media">{img("ph-hero","Nairobi skyline at dusk",eager=True)}</div>
<div class="wrap hx-body"><p class="hx-kicker">Orion TerraMetrics Africa Limited</p>
<h1>Geospatial engineering and AI for governments and enterprises.</h1>
<p class="hx-lead">We survey land and assets, analyse satellite and drone imagery, and give your teams OrionGIS, an AI-powered workspace for maps, field data and dashboards. Our clients include county governments, national agencies, utilities, health networks and private companies.</p>
<div class="hero-actions"><a class="btn btn-primary" href="{u('contact.html?type=project')}">Discuss a project</a><a class="btn btn-ghost" href="{u('portfolio.html')}">Explore our work</a></div></div>
<p class="hx-cap">Nairobi at dusk · placeholder photo: Nbi101, CC BY-SA 4.0</p></section>

<section class="marquee" aria-label="Clients and partners"><p>Trusted by</p><div class="marquee-view"><ul class="marquee-track">{run}{runb}</ul></div></section>

<section class="section stmt"><div class="wrap">
<h2 class="stmt-h">Our AI works from data we can stand behind.</h2>
<div class="stmt-grid"><p class="stmt-p">OrionAI answers questions using survey data our own teams collected and more than 43,000 open datasets we have indexed and checked. Every answer shows the data it came from, so your analysts, auditors and board can follow the reasoning.<br><br><a class="arrow-link" href="{u('solutions.html')}">All solutions</a></p>
<ol class="stages">{stageh}</ol></div></div></section>

<section class="sectors"><div class="wrap">
<div class="sectors-head"><h2>Industries we serve</h2><p>Public bodies, utilities, banks, insurers, retailers and many others use our data and analysis to decide where to invest, build and deliver services.</p></div>
<div class="sectors-grid"><figure class="sectors-img" aria-hidden="true"><img src="{u('assets/img/'+first['img']+'.webp')}" alt="" loading="eager"></figure>
<div class="sectors-lists"><div><h3>Public sector and infrastructure</h3><ul>{sec("public")}</ul></div><div><h3>Enterprise and markets</h3><ul>{sec("commercial")}</ul></div></div></div>
<p class="sectors-more">Working in another sector? <a href="{u('contact.html?type=consultation')}">Talk to us about your project.</a></p></div></section>

<section class="section work"><div class="wrap"><div class="work-head"><div><h2>Selected projects</h2><p>{len(PROJECTS)} published projects for national agencies, counties, utilities, health networks and private clients.</p></div>
<div class="work-nav"><button class="icon-btn" data-scroll="-1" aria-label="Previous projects">←</button><button class="icon-btn" data-scroll="1" aria-label="Next projects">→</button><a class="arrow-link" href="{u('portfolio.html')}">All projects</a></div></div></div>
<ul class="rail" tabindex="0" aria-label="Selected projects">{slides}</ul></section>

<section class="platform"><div class="wrap">
<div class="platform-head"><img src="{u('assets/logos/oriongis-wordmark-tagline-white.png')}" alt="OrionGIS" height="44"><div><h2>The AI-powered geospatial workspace.</h2><p>Ask a question in plain words and get back a finished map, analysis or dashboard. Bring your own data or start from 43,000+ open datasets, collect from the field and share securely across your organisation. One workspace for analysts, field teams and leadership.</p></div><div class="platform-cta"><a class="btn btn-primary" href="{COM}" target="_blank" rel="noopener">Open OrionGIS ↗</a><a class="btn btn-ghost" href="{COM}/signup" target="_blank" rel="noopener">Start free ↗</a></div></div>
<div class="showcase"><div class="show-tabs" role="tablist" aria-label="OrionGIS products">{tabs}</div><div class="show-stage">{panels}</div></div></div></section>

<section class="spot2"><figure>{img("ph-health","Mother and child at a hospital (placeholder photo)")}</figure><div class="spot2-txt"><p class="hx-kicker">Case study · Health</p><h2>Every health facility in a county, live on one screen.</h2><p>We geo-mapped all 178 facilities across five primary care networks, then connected monthly inpatient and outpatient reporting from mobile forms to executive dashboards on OrionGIS.</p>
<dl><div><dt>178</dt><dd>Facilities mapped</dd></div><div><dt>5</dt><dd>Primary care networks</dd></div><div><dt>Live</dt><dd>Executive dashboards</dd></div></dl>
<a class="btn btn-primary" href="{u('projects/county-health-intelligence-platform.html')}">Read the case study</a></div></section>

<section class="section why"><div class="wrap why-grid"><div class="why-photo">{img("about-team","Orion TerraMetrics surveyor with a total station on an engineering survey")}</div>
<div><h2>Why organisations choose us</h2><ol class="why-list">
<li><h3>We collect the data ourselves</h3><p>Our surveyors and drone pilots capture it, so we can vouch for its accuracy and where it came from.</p></li>
<li><h3>Our engineers build the software</h3><p>When your programme needs a new capability, our own engineers add it to OrionGIS.</p></li>
<li><h3>AI your team can check</h3><p>OrionAI drafts maps, forms, dashboards and analysis, and each result lists the data it used.</p></li>
<li><h3>Your data stays private</h3><p>Access is limited to your organisation, and we can host it for you or install it in your own data centre.</p></li></ol>
<a class="arrow-link" href="{u('about.html')}">About Orion TerraMetrics</a></div></div></section>

<section class="section soft"><div class="wrap"><div class="section-head"><div><h2>From the blog</h2></div><a class="arrow-link" href="{u('blog/')}">All articles</a></div><div class="bgrid">{news_cards(3)}</div></div></section>

<section class="closer closer-ask"><div class="closer-media">{img("ph-space","East African Rift Valley seen from the International Space Station")}</div><div class="wrap closer-ask-grid">
<div><h2>Not sure where to start?</h2><p>Describe what you need. We will point you to the right team and the most relevant project, or connect you with a specialist straight away.</p>{channels()}</div>
{concierge()}</div></section>
'''
    page("index.html", "Orion TerraMetrics | Geospatial intelligence for the age of AI", "Orion TerraMetrics is an AI-native geospatial engineering and technology company: we measure the physical world, turn it into intelligence and build the AI platform that puts it to work.", body, "Home", True)

NEWS = [   # company-level announcements only; product release notes stay off the public company site (founder 2026-11-27)
 ("2026-09-20","OrionGIS launches at orionterrametrics.com","Orion TerraMetrics' AI-native platform for maps, data, field collection and dashboards goes live.",COM),
]
def news_cards(n):
    out = ""
    for d, t, s, l in NEWS[:n]:
        out += f'<a class="card" href="{l}" target="_blank" rel="noopener"><span class="pill">Company news</span><h3 style="margin-top:12px">{e(t)}</h3><p>{e(s)}</p><span class="muted" style="font-size:.85rem;margin-top:auto">{d} · OrionGIS release notes ↗</span></a>'
    return out

# ------------------------------------------------------------------ solutions & industries
def solutions():
    cards = "".join(f'<a class="pcard" href="{u(s["file"])}"><figure>{img(s["img"], s["name"])}</figure><div class="body"><h3>{e(s["name"])}</h3><p>{e(s["short"])}</p><span class="arrow-link">Explore</span></div></a>' for s in SOLUTIONS.values())
    page("solutions.html","Solutions","Surveying, GIS, remote sensing, digital transformation, spatial data infrastructure and consulting from Orion TerraMetrics.", phero("Solutions","Field data, analysis and platforms, delivered end to end.","Six service lines that work as one team, so the data captured in the field is the data your leadership acts on.",[("Solutions",None)],"survey-field")+f'<section class="section"><div class="wrap"><div class="grid g3">{cards}</div></div></section>'+cta(), "Solutions", True)
    for k, s in SOLUTIONS.items():
        offers = "".join(f'<div class="card"><h3>{e(a)}</h3><p>{e(b)}</p></div>' for a, b in s["offers"])
        steps = "".join(f'<li><h4>{e(a)}</h4><p>{e(b)}</p></li>' for a, b in s["steps"])
        rel = projects_for(k, "svc")[:6]
        relh = f'<section class="section soft"><div class="wrap"><div class="section-head"><div><span class="eyebrow">Selected projects</span><h2>{e(s["name"])} in practice</h2></div><a class="arrow-link" href="{u("portfolio.html#"+k)}">All related projects</a></div><div class="grid g3">{"".join(pcard(p) for p in rel)}</div></div></section>' if rel else ""
        inds = sorted({i for p in rel for i in p[4]})
        indh = "".join(f'<a class="pill" style="margin:0 6px 6px 0" href="{u(INDUSTRIES[i]["file"])}">{e(INDUSTRIES[i]["name"])}</a>' for i in inds)
        body = phero("Solutions", s["name"], s["lead"], [("Solutions","solutions.html"),(s["name"],None)], s["img"], f'<div class="hero-actions"><a class="btn btn-primary" href="{u("contact.html?type=project")}">Discuss a project</a><a class="btn btn-ghost" href="{u("contact.html?type=proposal")}" style="color:#fff">Request a proposal</a></div>')
        body += f'<section class="section"><div class="wrap"><div class="section-head"><div><span class="eyebrow">What we deliver</span><h2>Capabilities</h2></div></div><div class="grid g3">{offers}</div>{"<p style=margin-top:20px><b>Sectors served:</b> "+indh+"</p>" if indh else ""}</div></section>'
        body += f'<section class="section soft" style="padding-top:0;background:#fff"><div class="wrap"><div class="section-head"><div><span class="eyebrow">How we work</span><h2>Our method</h2></div></div><ol class="steps">{steps}</ol></div></section>'
        body += relh
        body += f'<section class="section"><div class="wrap split"><div><span class="eyebrow">Delivered on OrionGIS</span><h2>Your results stay live.</h2><p>Deliverables can be published to OrionGIS, Orion TerraMetrics\' own platform, so your team can view, query and share them long after the project closes, with OrionAI to answer questions in plain words.</p><a class="arrow-link" href="{u("technology.html")}">Our technology</a></div><div class="media-frame">{img("wf-map","Map Studio in OrionGIS")}</div></div></section>'
        body += cta(f"Talk to our {s['name'].lower()} team")
        page(s["file"], s["name"], s["lead"][:155], body, "Solution", True, " ".join(a for a,_ in s["offers"]))

def industries():
    tiles = "".join(f'<a class="tile" href="{u(i["file"])}">{img(i["img"], "")}<div><h3>{e(i["name"])}</h3><p>{e(i["short"])}</p></div></a>' for i in INDUSTRIES.values())
    page("industries.html","Industries","Location intelligence for every sector: government, banking, insurance, retail, real estate, telecoms, mining, logistics, utilities, health, agriculture, environment and more.", phero("Industries","Industries we serve","We work with public bodies and private companies in every sector where decisions depend on location.",[("Industries",None)],"ph-space")+f'<section class="section"><div class="wrap"><div class="tiles">{tiles}</div></div></section>'+cta(), "Industry", True)
    for k, i in INDUSTRIES.items():
        rel = projects_for(k, "ind")
        svcs = i.get("svcs") or sorted({s for p in rel for s in p[3]}) or ["gis","consulting"]
        needs = "".join(f"<li>{e(n)}</li>" for n in i["needs"])
        svch = "".join(f'<a class="card" href="{u(SOLUTIONS[s]["file"])}"><div class="icon">{ico(SOL_ICON[s])}</div><h3>{e(SOLUTIONS[s]["name"])}</h3><p>{e(SOLUTIONS[s]["short"])}</p><span class="arrow-link">Explore</span></a>' for s in svcs)
        body = phero("Industries", i["name"], i["lead"], [("Industries","industries.html"),(i["name"],None)], i["img"], f'<div class="hero-actions"><a class="btn btn-primary" href="{u("contact.html?type=consultation")}">Book a consultation</a></div>')
        body += f'<section class="section"><div class="wrap split"><div><span class="eyebrow">Where we help</span><h2>Where location changes the answer</h2><ul class="checks">{needs}</ul></div><div><span class="eyebrow">Services used</span><div class="grid g2">{svch}</div></div></div></section>'
        if rel: body += f'<section class="section soft"><div class="wrap"><div class="section-head"><div><span class="eyebrow">Evidence</span><h2>Projects in {e(i["name"].lower())}</h2></div><a class="arrow-link" href="{u("portfolio.html#"+k)}">Filter the portfolio</a></div><div class="grid g3">{"".join(pcard(p) for p in rel[:6])}</div></div></section>'
        body += cta(f"Working in {i['name'].lower()}?", "Tell us about your programme. A sector lead replies within two working days.", ("Book a consultation","contact.html?type=consultation"))
        page(i["file"], i["name"], i["lead"][:155], body, "Industry", True, " ".join(i["needs"]))

# ------------------------------------------------------------------ work
def portfolio():
    filters = [("all","All")] + [(k, s["name"].split(" and ")[0]) for k, s in SOLUTIONS.items()] + [(k, i["name"].split(" and ")[0]) for k, i in INDUSTRIES.items()]
    fb = "".join(f'<button aria-pressed="{str(k=="all").lower()}" data-f="{k}">{e(l)}</button>' for k, l in filters)
    page("portfolio.html","Project portfolio","Projects delivered by Orion TerraMetrics: surveys, LiDAR, GIS, remote sensing, digital transformation and spatial data infrastructure.", phero("Our work","Project portfolio",f"{len(PROJECTS)} published projects for national agencies, county governments, utilities, health networks and enterprises.",[("Our work",None)],"ringroad")+f'<section class="section"><div class="wrap"><div class="filters" role="group" aria-label="Filter projects">{fb}</div><div class="grid g3">{"".join(pcard(p) for p in PROJECTS)}</div></div></section>'+cta(), "Our work", True)
    for p in PROJECTS:
        slug,title,tag,svc,ind,image,summary,m,ml = p
        rel = [q for q in PROJECTS if q is not p and (set(q[3])&set(svc) or set(q[4])&set(ind))][:3]
        body = f'<section class="page-hero"><div class="wrap">{crumbs([("Our work","portfolio.html"),(title,None)])}<span class="eyebrow">{e(tag)}</span><h1>{e(title)}</h1></div></section>'
        body += f'''<section class="section"><div class="wrap split wide-left" style="align-items:start"><div><div class="media-frame">{img(image,title,eager=True)}</div></div>
<aside class="card"><div class="metric" style="border:0;padding:0;margin:0 0 14px"><b style="font-size:2rem">{e(m)}</b><span>{e(ml)}</span></div><dl class="kv" style="grid-template-columns:110px 1fr"><dt>Services</dt><dd>{", ".join(f'<a href="{u(SOLUTIONS[s]["file"])}">{e(SOLUTIONS[s]["name"])}</a>' for s in svc)}</dd><dt>Sectors</dt><dd>{", ".join(f'<a href="{u(INDUSTRIES[i]["file"])}">{e(INDUSTRIES[i]["name"])}</a>' for i in ind)}</dd></dl><a class="btn btn-primary btn-sm" style="margin-top:18px" href="{u("contact.html?type=project")}">Discuss a similar project</a></aside></div>
<div class="wrap prose" style="margin-top:32px"><h2>Overview</h2><p>{e(summary)}</p></div></section>'''
        body += f'<section class="section soft"><div class="wrap"><div class="section-head"><div><span class="eyebrow">Related</span><h2>More projects like this</h2></div></div><div class="grid g3">{"".join(pcard(q) for q in rel)}</div></div></section>' + cta()
        page(f"projects/{slug}.html", title, summary[:155], body, "Project", False, tag+" "+m+" "+ml)
    names = "".join(f'<div class="card" style="align-items:center;text-align:center"><figure style="margin:0 0 12px;height:90px;display:grid;place-items:center">{logo(f,n)}</figure><h4>{e(n)}</h4></div>' for f, n in CLIENTS)
    named = []
    page("clients.html","Clients and partners","Institutions Orion TerraMetrics works with: county governments, national agencies, health networks, universities and enterprises.", phero("Our work","Clients and partners","Public institutions, health networks, universities and enterprises that trust us with their data.",[("Our work","portfolio.html"),("Clients and partners",None)])+f'<section class="section"><div class="wrap"><div class="grid g4">{names}</div></div></section>'+cta("Partner with Orion","Technology, delivery and institutional partnerships.",("Become a partner","partners.html#become"),("Talk to us","contact.html?type=partnership")), "Our work", True)

# ------------------------------------------------------------------ technology
def technology():
    prods = "".join(f'<div class="split" id="{k}" style="padding:36px 0;border-top:1px solid var(--line)"><div><img src="{u("assets/logos/"+ic+".png")}" alt="" width="56" height="56" style="margin-bottom:14px"><h3 style="font-size:1.6rem">{e(n)}</h3><p>{e(d)}</p><a class="btn btn-ghost btn-sm" href="{COM}{l}" target="_blank" rel="noopener">{e(n)} on OrionGIS ↗</a></div><div class="media-frame">{img(sc,n)}</div></div>' for k,n,ic,sc,d,l in PRODUCTS)
    gallery = [("naivasha-sentinel2","Lake Naivasha, Sentinel-2 water and vegetation"),("po-valley-false-colour","Po Valley, false-colour composite"),("mount-kenya-slope","Mount Kenya, slope analysis"),("nairobi-landcover","Nairobi, land cover classification"),("kilimanjaro-relief","Kilimanjaro, shaded relief"),("mwea-crop-vigour","Mwea irrigation scheme, crop vigour")]
    gal = "".join(f'<figure style="margin:0"><div class="media-frame">{img(f,c)}</div><figcaption class="caption">{e(c)}</figcaption></figure>' for f, c in gallery)
    body = phero("Technology","OrionGIS: the platform we build and deliver on.","Orion TerraMetrics designs and engineers OrionGIS in Nairobi. It brings maps, open data, field forms and dashboards together, with OrionAI across all of it.",[("Technology",None)],"wf-discover",f'<div class="hero-actions"><a class="btn btn-primary" href="{COM}" target="_blank" rel="noopener">Visit OrionGIS ↗</a><a class="btn btn-ghost" href="{u("contact.html?type=consultation")}" style="color:#fff">Enterprise deployment</a></div>')
    body += f'<section class="section"><div class="wrap"><div class="section-head"><div><span class="eyebrow">The ecosystem</span><h2>Five products, one platform.</h2><p>Each product has its own page on orionterrametrics.com, where users sign up, sign in and subscribe. This site covers what the technology means for enterprise programmes.</p></div></div>{prods}</div></section>'
    body += f'<section class="section dark" id="orionai"><div class="wrap"><div class="section-head"><div><span class="eyebrow">OrionAI and GeoAI</span><h2>Ask a question of any place. Get a finished, explained answer.</h2><p>Real OrionAI results, each with its sources and a colour key that matches the map.</p></div></div><div class="grid g3">{gal}</div></div></section>'
    body += f'''<section class="section" id="integration"><div class="wrap"><div class="section-head"><div><span class="eyebrow">Integration</span><h2>Works with the tools your teams already use.</h2></div></div><div class="grid g4">
<div class="card"><h3>QGIS</h3><p>Orion Connect, a QGIS plugin, syncs layers both ways.</p></div><div class="card"><h3>OGC services</h3><p>WMS, WFS and WCS for any standards-based GIS.</p></div><div class="card"><h3>Developer APIs</h3><p>REST APIs and an MCP server for agents and applications.</p></div><div class="card"><h3>Orion Collect</h3><p>Offline field collection on Android, straight to the map.</p></div></div>
<div class="grid g3" style="margin-top:20px"><div class="card"><div class="icon">{ico('shield')}</div><h3>Organisations and roles</h3><p>Data shared inside an organisation, with seats and role-based access.</p></div><div class="card"><div class="icon">{ico('db')}</div><h3>Cloud or on-premise</h3><p>Hosted by Orion, or deployed in your own data centre for residency.</p></div><div class="card"><div class="icon">{ico('book')}</div><h3>Provenance</h3><p>Every dataset keeps its source, licence and publisher.</p></div></div></div></section>'''
    body += cta("Deploying OrionGIS across an organisation?","Our team plans enterprise rollouts, integrations, training and on-premise deployments.",("Book a consultation","contact.html?type=consultation"),("Request a proposal","contact.html?type=proposal"))
    page("technology.html","Technology and OrionGIS","OrionGIS is Orion TerraMetrics' own geospatial platform: OrionAI, Map Studio, Spatial Data Hub, OrionForms and OrionInsights.", body, "Technology", True, "OrionGIS OrionAI GeoAI Map Studio Spatial Data Hub OrionForms OrionInsights QGIS API")
    body = phero("Technology","Research and innovation","Our research turns into product: GeoAI, cartography, open data at scale and tools that work on African connectivity.",[("Technology","technology.html"),("Research and innovation",None)],"ph-env")
    body += f'''<section class="section"><div class="wrap"><div class="grid g3">
<div class="card"><div class="icon">{ico('spark')}</div><h3>GeoAI</h3><p>Planning, running and explaining spatial analysis from plain-language questions, with an evaluation set that tests every release.</p></div>
<div class="card"><div class="icon">{ico('map')}</div><h3>Automated cartography</h3><p>Semantic colour ramps and classification so every AI-made map reads correctly and matches its legend.</p></div>
<div class="card"><div class="icon">{ico('db')}</div><h3>Open data at scale</h3><p>The Global Data Index: harvesting, describing, geocoding and joining statistics to boundaries so tables become maps.</p></div></div></div></section>
<section class="section soft" id="publications"><div class="wrap prose"><span class="eyebrow">Research and publications</span><h2>Published research</h2><div class="card"><span class="pill">Research paper</span><h3 style="margin-top:12px">Quantifying Tree Cover Loss in Urban Forests within Nairobi Metropolitan Area using Earth Observation Data</h3><p>Godwin Murithi · BSc Geoinformatics research, The Technical University of Kenya.</p></div><p class="muted" style="margin-top:16px">New papers, technical notes and datasets will be listed here as they are published.</p></div></section>'''
    body += cta("Collaborate on research","Universities and research groups can work with our R&D team and use OrionGIS for teaching.",("Institutional collaboration","contact.html?type=partnership"),("Partner programme","partners.html"))
    page("research.html","Research and innovation","Research and innovation at Orion TerraMetrics: GeoAI, automated cartography and open data at scale.", body, "Technology", True)

# ------------------------------------------------------------------ insights
def insights():
    body = phero("Insights","News, perspectives and research.","What we are building, what we are learning and where to meet our team.",[("Insights",None)],"ph-dusk")
    body += f'<section class="section" id="articles"><div class="wrap"><div class="xhead"><h2>Latest from the blog</h2><p>Practical writing from the people who do the work. <a href="{u("blog/")}">All articles →</a></p></div><div class="bgrid">{news_cards(6)}</div></div></section>'
    body += f'''<section class="section soft"><div class="wrap split"><div><h2>Research and publications</h2><p>Peer research and technical notes from our team.</p><a class="arrow-link" href="{u("research.html#publications")}">Publications</a></div><div class="card"><span class="pill">Research</span><h3 style="margin-top:12px">Quantifying Tree Cover Loss in Urban Forests within Nairobi Metropolitan Area</h3><p>Earth observation research by Godwin Murithi.</p></div></div></section>
<section class="section" id="events"><div class="wrap prose"><span class="eyebrow">Events and webinars</span><h2>Where to meet us</h2><p>There are no events scheduled right now. Webinars, workshops and conference appearances will be listed here with dates and registration links.</p><p><a class="arrow-link" href="{u("contact.html?type=general")}">Invite us to speak</a></p></div></section>'''
    page("insights.html","Insights","News, articles, research and events from Orion TerraMetrics.", body, "Insights", True)
    allnews = "".join(f'<li style="padding:18px 0;border-bottom:1px solid var(--line)"><span class="muted">{d}</span><h3 style="margin:4px 0">{e(t)}</h3><p style="margin:0">{e(s)} <a href="{l}" target="_blank" rel="noopener">Visit OrionGIS ↗</a></p></li>' for d,t,s,l in NEWS)
    body = phero("Insights","Newsroom","Company and product announcements from Orion TerraMetrics.",[("Insights","insights.html"),("Newsroom",None)])
    body += f'''<section class="section"><div class="wrap split wide-left" style="align-items:start"><div><h2>Announcements</h2><ul style="list-style:none;padding:0;margin:0">{allnews}</ul></div>
<aside id="media"><div class="card"><h3>Media enquiries</h3><p>Journalists and event organisers can reach our communications team for interviews, comment and speakers.</p><p><a href="mailto:{EMAIL}?subject=Media%20enquiry">{EMAIL}</a><br>{PHONE1}</p><a class="btn btn-primary btn-sm" href="{u("contact.html?type=media")}">Media enquiry form</a></div>
<div class="card" style="margin-top:16px"><h3>Brand assets</h3><p>The Orion TerraMetrics logo for editorial use.</p><a class="arrow-link" href="{u("assets/OrionLogo.svg")}" download>Download logo (SVG)</a></div></aside></div></section>'''
    page("newsroom.html","Newsroom","Company and product announcements, media enquiries and brand assets from Orion TerraMetrics.", body, "Insights", True)

# ------------------------------------------------------------------ company
def company():
    body = phero("Company","About Orion TerraMetrics","A geospatial engineering and technology company in Nairobi. We capture, analyse and publish the spatial data organisations run on, and we build OrionGIS.",[("Company",None)],"about-team")
    body += f'''<section class="section"><div class="wrap split"><div><span class="eyebrow">Our story</span><h2>From the field to a global platform.</h2><p>Orion TerraMetrics Africa Limited began as a surveying and GIS practice serving engineers, counties and development programmes in Kenya. Our clients kept asking for one thing: data they could keep using after the project closed.</p><p>So we built OrionGIS. Today our field teams, analysts and software engineers work as one company, and the platform they build is used by organisations and data users worldwide.</p></div><div class="media-frame">{img("survey-field","Survey team in the field")}</div></div></section>
<section class="section soft"><div class="wrap grid g3">
<div class="card"><span class="eyebrow">Mission</span><h3>Put trustworthy spatial intelligence in the hands of every organisation that plans, builds and serves.</h3></div>
<div class="card"><span class="eyebrow">Vision</span><h3>An Africa where every decision about land, infrastructure and services is made with good data.</h3></div>
<div class="card"><span class="eyebrow">Values</span><ul class="checks" style="margin:0"><li>Accuracy we can prove</li><li>Our clients' data stays theirs</li><li>Field reality first</li><li>Build to last, and teach</li><li>Honest about what we know</li></ul></div></div>
<div class="wrap"><p class="notice" style="margin-top:20px">Proposed wording for management approval: mission, vision and values.</p></div></section>
<section class="section" id="approach"><div class="wrap"><div class="section-head"><div><span class="eyebrow">Our approach</span><h2>How every engagement runs</h2></div></div><ol class="steps"><li><h4>Discover</h4><p>Objectives, stakeholders, data and constraints.</p></li><li><h4>Design</h4><p>Method, architecture and a costed, phased plan.</p></li><li><h4>Capture</h4><p>Field, drone, satellite and existing records.</p></li><li><h4>Build</h4><p>Analysis, registries and dashboards on OrionGIS.</p></li><li><h4>Sustain</h4><p>Training, support and measured adoption.</p></li></ol></div></section>
<section class="section soft"><div class="wrap grid g4"><a class="card" href="{u("leadership.html")}"><h3>Leadership</h3><p>The people accountable for our work.</p><span class="arrow-link">Meet them</span></a><a class="card" href="{u("careers.html")}"><h3>Careers</h3><p>Join the team.</p><span class="arrow-link">Explore</span></a><a class="card" href="{u("responsibility.html")}"><h3>Responsibility</h3><p>Open data, skills and public-interest work.</p><span class="arrow-link">Read</span></a><a class="card" href="{u("trust.html")}"><h3>Trust and governance</h3><p>Security, privacy and ethics.</p><span class="arrow-link">Read</span></a></div></section>'''
    body += cta()
    page("about.html","About us","About Orion TerraMetrics Africa Limited: our story, mission, vision, values and approach.", body, "Company", True)

    people = [("godwin","Godwin Murithi","Chief Executive Officer","A geospatial systems expert driving innovative solutions across governance, health, infrastructure and utility sectors. Passionate about spatial intelligence and digital transformation in Africa.","Godwin-Murithi.html"),("nicholas","Nicholas Mutethia","Chief Operations Officer","An experienced geospatial engineer specialising in surveying, drone mapping and infrastructure planning, dedicated to delivering precision and innovation across every project.",None)]
    ph = "".join(f'<div class="card"><div class="person" style="grid-template-columns:160px 1fr">{img(i,n)}<div><h3>{e(n)}</h3><p class="eyebrow" style="margin-bottom:10px">{e(r)}</p><p>{e(b)}</p>{f"<a class=arrow-link href={chr(34)+u(l)+chr(34)}>Full profile</a>" if l else ""}</div></div></div>' for i,n,r,b,l in people)
    page("leadership.html","Leadership","The leadership team of Orion TerraMetrics Africa Limited.", phero("Company","Leadership","The people accountable for our work and our clients' trust.",[("Company","about.html"),("Leadership",None)])+f'<section class="section"><div class="wrap grid g2">{ph}</div></section>'+cta("Talk to our leadership","Partnerships, investment and strategic engagements.",("Contact leadership","contact.html?type=general"),("Partner with us","partners.html")), "Company", True)

    body = phero("Leadership","Godwin Murithi","Chief Executive Officer, Orion TerraMetrics Africa Limited",[("Company","about.html"),("Leadership","leadership.html"),("Godwin Murithi",None)])
    body += f'''<section class="section"><div class="wrap split wide-left" style="align-items:start"><div class="prose"><h2>Profile</h2><p>Godwin is a GIS developer and systems specialist with more than five years of experience delivering enterprise GIS across public health, utilities and infrastructure in East Africa: ArcGIS Enterprise, real-time geospatial streaming, IoT data platforms and spatial analytics. He leads the vision for OrionGIS and OrionAI.</p>
<h3>Experience</h3><ul><li>Senior GIS Specialist, CTI Africa (2023 to present): enterprise GIS for water, electricity and health with ArcGIS Enterprise, Velocity and Kafka; training across Kenya, Uganda and Tanzania.</li><li>GIS Analyst, Digireg International (2022 to 2023): cadastral and tax mapping automation for urban councils.</li><li>GIS Technician, GeoPsy Research (2021 to 2022): climate and disaster spatial analytics.</li></ul>
<h3>Selected work</h3><ul><li>Utility GIS platform for a national water development agency.</li><li>Disease surveillance mapping for rural county health departments.</li><li>Digital health GIS integrating community health data with national systems.</li></ul>
<h3>Education and research</h3><p>BSc Geoinformatics, The Technical University of Kenya. Research: "Quantifying Tree Cover Loss in Urban Forests within Nairobi Metropolitan Area using Earth Observation Data".</p></div>
<aside><div class="media-frame">{img("godwin","Godwin Murithi")}</div><p class="notice" style="margin-top:14px">Verify: the experience list comes from the current site and may need updating for the CEO role.</p></aside></div></section>'''
    page("Godwin-Murithi.html","Godwin Murithi, CEO","Godwin Murithi, Chief Executive Officer of Orion TerraMetrics Africa Limited.", body, "Company")

    body = phero("Company","Corporate responsibility","We measure our contribution by what others can do with the data, skills and tools we share.",[("Company","about.html"),("Corporate responsibility",None)],"naivasha-sentinel2")
    body += f'''<section class="section"><div class="wrap grid g3">
<div class="card"><div class="icon">{ico('globe')}</div><h3>Open data for everyone</h3><p>The Global Data Index on OrionGIS lets anyone find and download open spatial data for free.</p><a class="arrow-link" href="{COM}/data" target="_blank" rel="noopener">Explore the data ↗</a></div>
<div class="card"><div class="icon">{ico('book')}</div><h3>Skills</h3><p>A free beginner GIS course, student attachments and training for public institutions through the Orion Academy.</p><a class="arrow-link" href="{u("courses.html")}">Orion Academy</a></div>
<div class="card"><div class="icon">{ico('people')}</div><h3>Public-interest work</h3><p>Health facility mapping and reporting for county governments and faith-based health networks.</p><a class="arrow-link" href="{u("health.html")}">Health and development</a></div></div></section>'''
    body += cta()
    page("responsibility.html","Corporate responsibility","Open data, skills and public-interest work at Orion TerraMetrics.", body, "Company", True)

# ------------------------------------------------------------------ careers
def careers():
    paths = [("Geospatial engineering","Surveyors, GIS analysts and remote sensing specialists who work in the field and the office."),("Software engineering","Engineers who build OrionGIS: web, data pipelines, maps and infrastructure."),("AI and data science","GeoAI, evaluation and the Global Data Index."),("Business development","Proposals, partnerships and client relationships."),("Internships and attachments","Structured placements for students and recent graduates."),("Corporate operations","Finance, people and administration.")]
    ph = "".join(f'<div class="card"><h3>{e(a)}</h3><p>{e(b)}</p></div>' for a, b in paths)
    steps = "".join(f"<li><h4>{a}</h4><p>{b}</p></li>" for a,b in [("Apply","Send your CV and a short note for a role or the talent pool."),("Review","We reply to every applicant within ten working days."),("Conversation","A first call about you, the role and the team."),("Technical step","A practical exercise or field assessment for the role."),("Offer","References, offer and a structured first month.")])
    body = phero("Careers","Build technology that shapes Africa's future.","Join a team working where geospatial engineering, artificial intelligence and real-world challenges meet.",[("Careers",None)],"nicholas",f'<div class="hero-actions"><a class="btn btn-primary" href="#open">See open roles</a><a class="btn btn-ghost" href="{u("internships.html")}" style="color:#fff">Internships and attachments</a></div>')
    body += f'<section class="section"><div class="wrap"><div class="section-head"><div><span class="eyebrow">Career pathways</span><h2>Find your place</h2></div></div><div class="grid g3">{ph}</div></div></section>'
    body += f'''<section class="section soft" id="open"><div class="wrap split" style="align-items:start"><div><span class="eyebrow">Open opportunities</span><h2>Current vacancies</h2><div class="card"><p style="margin:0"><b>No vacancies are open right now.</b> Roles are published here with a description, location and closing date when recruitment opens.</p></div><p style="margin-top:16px">Join the talent pool and we will contact you when a matching role opens.</p></div>
<div class="card">{enquiry_form("careers", "Join the talent pool", [("careers","Talent pool"),("internship","Internship or attachment")], '<div class="field full"><label for="f-link">Link to your CV, LinkedIn or portfolio</label><input id="f-link" name="link" type="url" placeholder="https://"></div>')}</div></div></section>'''
    body += f'<section class="section"><div class="wrap"><div class="section-head"><div><span class="eyebrow">Recruitment process</span><h2>What to expect</h2></div></div><ol class="steps">{steps}</ol><p class="notice" style="margin-top:20px">Proposed process for HR approval. Candidate data is handled under the Kenya Data Protection Act, 2019, as set out in our <a href="{u("privacy.html")}">privacy notice</a>.</p></div></section>'
    page("careers.html","Careers","Careers at Orion TerraMetrics: geospatial engineering, software, AI, business development, internships and attachments.", body, "Careers", True)
    body = phero("Careers","Internships and attachments","Structured placements where students and graduates work on real projects with our surveyors, analysts and engineers.",[("Careers","careers.html"),("Internships and attachments",None)],"about-team")
    body += f'''<section class="section"><div class="wrap split" style="align-items:start"><div class="prose"><h2>Who can apply</h2><ul class="checks"><li>Students on industrial attachment in geomatics, GIS, surveying, computer science or related fields</li><li>Recent graduates looking for a first placement</li></ul><h2>What you will do</h2><ul class="checks"><li>Field data collection and survey support</li><li>GIS analysis and map production</li><li>Software and data work on OrionGIS</li></ul><p class="muted">Intake dates are announced here. Applications outside an intake join the talent pool.</p></div>
<div class="card">{enquiry_form("internship", "Apply for an internship or attachment", [("internship","Internship or attachment")], '<div class="field full"><label for="f-link">Link to your CV or portfolio</label><input id="f-link" name="link" type="url" placeholder="https://"></div>')}</div></div></section>'''
    page("internships.html","Internships and attachments","Internships and industrial attachments at Orion TerraMetrics for geomatics, GIS, surveying and computer science students.", body, "Careers", True)

def partners():
    types = [("Technology partners","Integrate with OrionGIS through APIs, OGC services and QGIS."),("Delivery partners","Survey, GIS and IT firms that deliver programmes with us in new regions."),("Institutional collaboration","Universities and research groups working with our R&D team."),("Development partners","Donors and NGOs designing data programmes with us.")]
    th = "".join(f'<div class="card"><h3>{e(a)}</h3><p>{e(b)}</p></div>' for a,b in types)
    body = phero("Partners","Grow with us.","Technology firms, delivery partners, universities and development organisations that share our standards, and reach new markets with us.",[("Partners",None)],"ph-logi")
    body += f'<section class="section"><div class="wrap"><div class="grid g4">{th}</div></div></section><section class="section soft" id="become"><div class="wrap split" style="align-items:start"><div><span class="eyebrow">Become a partner</span><h2>Tell us how you would like to work together.</h2><p>Our partnerships team replies within five working days.</p></div><div class="card">{enquiry_form("partnership", None, [("partnership","Become a partner"),("research","Institutional collaboration")])}</div></div></section>'
    page("partners.html","Partners","Technology, delivery, institutional and development partnerships with Orion TerraMetrics.", body, "Partners", True)

def academy():
    cards = "".join(f'<div class="card"><span class="pill{"" if live else " soon"}">{"Now enrolling" if live else "Coming soon"}</span><h3 style="margin-top:12px">{e(t)}</h3><p class="muted" style="font-size:.88rem">{e(m)}</p><p>{e(d)}</p>{f"<a class=arrow-link href={chr(34)+u(l)+chr(34)}>Course details</a>" if l else f"<a class=arrow-link href={chr(34)+u('courses.html#enquire')+chr(34)}>Notify me</a>"}</div>' for t,m,d,live,l in COURSES)
    body = phero("Academy","Orion Academy","Practical geospatial training created by the professionals who deliver our projects.",[("Academy",None)],"ph-edu",f'<div class="hero-actions"><a class="btn btn-primary" href="{u("enroll.html")}">Enrol in the free GIS course</a><a class="btn btn-ghost" href="#corporate" style="color:#fff">Corporate training</a></div>')
    body += f'<section class="section"><div class="wrap"><div class="section-head"><div><span class="eyebrow">Courses</span><h2>Available and upcoming courses</h2></div></div><div class="grid g3">{cards}</div></div></section>'
    body += f'<section class="section soft" id="corporate"><div class="wrap split" style="align-items:start"><div id="enquire"><span class="eyebrow">Corporate and institutional training</span><h2>Train your team on your own data.</h2><ul class="checks"><li>GIS, remote sensing and surveying for technical teams</li><li>OrionGIS onboarding for programme and operations staff</li><li>Delivered in person in Nairobi, on site or online</li></ul></div><div class="card">{enquiry_form("training", None, [("training","Corporate training"),("course","Course enquiry")])}</div></div></section>'
    page("courses.html","Orion Academy","Professional geospatial training from Orion TerraMetrics: GIS, remote sensing, surveying and corporate training.", body, "Academy", True)
    body = phero("Academy","Introduction to GIS Using QGIS","A free, beginner-friendly course: spatial data, QGIS workflows, analysis and professional maps, built around real African datasets.",[("Academy","courses.html"),("Introduction to GIS Using QGIS",None)],"ph-edu",f'<div class="hero-actions"><a class="btn btn-primary" href="{u("enroll.html")}">Enrol now</a></div>')
    mods = ["What GIS is and how it is used","Getting started with QGIS","Vector data: points, lines and polygons","Raster data: elevation and land cover","Coordinate reference systems","Analysis: buffer, overlay and spatial workflows","Making professional maps","Your first project"]
    body += f'<section class="section"><div class="wrap split" style="align-items:start"><div class="prose"><h2>What you will learn</h2><ol>{"".join(f"<li>{e(m)}</li>" for m in mods)}</ol><p class="notice">Verify module titles against the live course.</p></div><div class="card"><dl class="kv" style="grid-template-columns:120px 1fr"><dt>Level</dt><dd>Beginner, no experience needed</dd><dt>Format</dt><dd>Online, self-paced</dd><dt>Modules</dt><dd>8</dd><dt>Cost</dt><dd>Free</dd><dt>Certificate</dt><dd>On completion</dd></dl><a class="btn btn-primary" style="margin-top:18px" href="{u("enroll.html")}">Enrol now</a></div></div></section>'
    page("introduction-to-GIS-using-QGIS.html","Introduction to GIS Using QGIS","A free beginner GIS course in QGIS from the Orion Academy.", body, "Academy", True)
    body = phero("Academy","Enrol in Introduction to GIS Using QGIS","Register your interest and we will send your course access details by email.",[("Academy","courses.html"),("Enrol",None)])
    body += f'<section class="section"><div class="wrap" style="max-width:860px">{enquiry_form("enrol", None, [("enrol","Enrol: Introduction to GIS Using QGIS")])}</div></section>'
    page("enroll.html","Enrol","Enrol in the Orion Academy course Introduction to GIS Using QGIS.", body, "Academy")

# ------------------------------------------------------------------ contact, trust, utility
def contact():
    body = phero("Contact","Talk to an expert","Projects, proposals, consultations, partnerships and media. Choose what you need and a specialist replies within two working days.",[("Contact",None)])
    body += f'''<section class="section"><div class="wrap split wide-left" style="align-items:start"><div class="card">{enquiry_form("project")}</div>
<aside id="office"><div class="card"><h3>Head office</h3><p>Orion TerraMetrics Africa Limited<br>{e(ADDRESS)}</p><p><a href="tel:+254799882124">{PHONE1}</a><br><a href="tel:+254729212061">{PHONE2}</a><br><a href="mailto:{EMAIL}">{EMAIL}</a></p><p class="muted">Monday to Friday, 8:00 to 17:00 EAT</p><a class="arrow-link" href="https://www.google.com/maps/search/?api=1&query=GMC+Mansion+Mukhtar+Dadah+Street+Nairobi" target="_blank" rel="noopener">Open in Google Maps</a></div>
<div class="card" style="margin-top:16px"><h3>Using OrionGIS?</h3><p>Product support, accounts and billing are handled on the OrionGIS site.</p><a class="arrow-link" href="{COM}/contact" target="_blank" rel="noopener">OrionGIS support ↗</a></div>
<div class="card" style="margin-top:16px"><h3>Where we work</h3><p>Kenya, Somalia, Somaliland and Zimbabwe, with OrionGIS used worldwide.</p></div></aside></div></section>
<script>(function(){{var q=new URLSearchParams(location.search),t=q.get("type"),m=q.get("msg");if(t){{var r=document.querySelector('input[data-k="'+t+'"]');if(r)r.checked=true;}}if(m){{var a=document.getElementById("f-msg");if(a)a.value=m;}}}})();</script>'''
    page("contact.html","Contact","Contact Orion TerraMetrics: discuss a project, request a proposal, book a consultation, partnerships and media.", body, "Contact", True)

POLICIES = {
 "privacy.html":("Privacy notice","How Orion TerraMetrics collects, uses and protects personal data under the Kenya Data Protection Act, 2019.",[("Who we are","Orion TerraMetrics Africa Limited, Nairobi, is the data controller for personal data collected through this website."),("What we collect","Details you send in enquiry, careers, partnership and training forms: name, email, organisation, role, country and your message. Basic analytics about how the site is used."),("Why we use it","To answer your enquiry, assess job applications, deliver training and improve the website. The lawful bases are your consent, steps before a contract and our legitimate interests."),("Retention","Enquiries are kept for up to 24 months; unsuccessful applications for up to 12 months unless you ask us to keep them longer."),("Your rights","You can ask to access, correct or delete your data, or object to its use, by writing to "+EMAIL+". You may also complain to the Office of the Data Protection Commissioner.")]),
 "cookies.html":("Cookie notice","How the Orion TerraMetrics website uses cookies and analytics.",[("What we use","Essential storage needed for the site to work, and Google Analytics to understand which pages are useful."),("Your choices","You can block or delete cookies in your browser. The site still works without analytics cookies.")]),
 "terms.html":("Terms of use","Terms for using the Orion TerraMetrics website.",[("Use of this site","Content is provided for information. Project figures describe completed work and are not a guarantee of future results."),("Intellectual property","Text, images and logos belong to Orion TerraMetrics or the organisations named, and may not be reused without permission."),("OrionGIS","Use of the OrionGIS platform is governed by the terms published at orionterrametrics.com.")]),
 "accessibility.html":("Accessibility statement","Our commitment to an accessible website, targeting WCAG 2.2 AA.",[("Our target","This website is built to meet WCAG 2.2 level AA: keyboard access, visible focus, sufficient contrast, text alternatives and layouts that work from 320 px wide."),("Feedback","If anything is hard to use, email "+EMAIL+" and we will respond within five working days.")]),
 "security.html":("Information security","How Orion TerraMetrics protects client and project data.",[("Principles","Least-privilege access, encryption in transit, organisation-level separation of client data and logged administrative actions."),("Client data","Client data is used only for the engagement it was provided for, and stays the client's property."),("Report a vulnerability","Email "+EMAIL+" with the subject \"Security\". We acknowledge reports within three working days.")]),
 "ethics.html":("Business ethics","The standards Orion TerraMetrics holds itself to.",[("Integrity","We do not offer or accept bribes, and we declare conflicts of interest."),("Honest claims","We publish only figures and relationships we can support."),("Speak up","Concerns can be raised in confidence with our leadership at "+EMAIL+".")]),
}
def trust():
    cards = "".join(f'<a class="card" href="{u(f)}"><h3>{e(t)}</h3><p>{e(d)}</p><span class="arrow-link">Read</span></a>' for f,(t,d,_) in POLICIES.items())
    page("trust.html","Trust and governance","Security, privacy, ethics and the policies that govern Orion TerraMetrics.", phero("Company","Trust and governance","How we protect data, behave and stay accountable.",[("Company","about.html"),("Trust and governance",None)])+f'<section class="section"><div class="wrap"><div class="grid g3">{cards}</div><p class="notice" style="margin-top:24px">All policy pages are drafts for legal and management review before launch.</p></div></section>', "Company", True)
    for f,(t,d,secs) in POLICIES.items():
        body = phero("Trust and governance", t, d, [("Trust and governance","trust.html"),(t,None)])
        body += '<section class="section"><div class="wrap prose"><p class="notice">Draft for legal and management review. Last updated 27 November 2026.</p>' + "".join(f"<h2>{e(h)}</h2><p>{e(p)}</p>" for h,p in secs) + "</div></section>"
        page(f, t, d, body, "Policy")

def proposal():
    rows = [("Bentley Systems","Behind the world's infrastructure","Products · Industries · Company; trust portal","Named case studies with hard numbers; trust centre as a destination"),
            ("Esri","Comprehensive geospatial platform","AI assistant above the hero","AI up front; frank trust statements"),
            ("Fugro","Creating a safe and liveable world","Industries · Expertise · Careers · Investors · News · About","Purpose-led identity; dated case studies; leadership, history and careers on the home page"),
            ("Woolpert","Global resources. End-to-end solutions.","About · Industries · Solutions · Products · Projects · Careers · Regions","Services firm with its own products; an Africa region; industries and solutions as two menus"),
            ("Trimble","Confidence at every turn","Platform · Customer stories · About","Platform-first; numbers tied to named customers; 'Experts lead, AI accelerates'; partner and support CTAs"),
            ("Leica Geosystems (Hexagon)","When it has to be right","Industries · Products · Services · About","Compliance and standards hub; events and newsroom; core values"),
            ("Planet, Palantir, Accenture","(benchmarked by Codex)","Careers subsystems, R&D, responsible AI","Mission-led recruitment; research and responsible AI pages")]
    tr = "".join(f"<tr><td><b>{e(a)}</b></td><td>“{e(b)}”</td><td>{e(c)}</td><td>{e(d)}</td></tr>" for a,b,c,d in rows)
    body = phero("Proposal · 27 November 2026","The Orion TerraMetrics corporate website, for the next five years.","Research, structure and engineering choices behind this preview. Everything here is a working page; nothing is live on orionterrametrics.co.ke yet.",[("Proposal",None)])
    body += f'''<section class="section"><div class="wrap prose" style="max-width:980px">
<h2>The recommendation in one paragraph</h2><p>Orion TerraMetrics is unusual: it delivers survey, GIS and data programmes in the field <i>and</i> builds its own AI-native platform, OrionGIS. Fugro and Woolpert win on delivery; Trimble and Esri win on platform. The corporate site should show both, with OrionGIS presented as Orion's own technology and every product journey handed to orionterrametrics.com. It must read as a company that will still make sense at five times its size: sector teams, regions, a careers engine and a trust centre, without claiming anything it cannot support.</p>
<h2>What the leading enterprise sites do (opened 24 and 27 November 2026)</h2>
<div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:.92rem"><thead><tr style="text-align:left;border-bottom:2px solid var(--line)"><th>Company</th><th>Hero line</th><th>Navigation</th><th>What we adopt</th></tr></thead><tbody>{tr}</tbody></table></div>
<p class="muted">hexagon.com and palantir.com refused automated reading; Leica Geosystems stands in for Hexagon.</p>
<h2>Decisions built into this preview</h2><ul class="checks">
<li><b>Identity first.</b> One line about who Orion is (“The AI-native geospatial company”), two calls to action, audience paths in the hero.</li>
<li><b>Six menus</b> that scale: Solutions, Industries, Technology, Our work, Insights, Company, plus a utility bar (Careers, Newsroom, Partners, Contact, OrionGIS ↗) and one constant “Talk to an expert”.</li>
<li><b>Proof as named client + number</b> on every case study, kept exactly as the current site states them.</li>
<li><b>OrionGIS is our technology, not a second product site.</b> No sign-up, pricing or dashboards here; every product link goes to orionterrametrics.com.</li>
<li><b>Careers, partners, Academy and trust are subsystems</b>, each with its own form, ready for vacancies and policies without redesign.</li>
<li><b>Nothing invented.</b> No vacancies, events, certificates, testimonials or staff counts. The ISO claim, the 5 vs 20 years and 500 vs 5,000 projects conflicts, and the template testimonials are removed.</li></ul>
<h2>Built to convert</h2><table style="width:100%;border-collapse:collapse;font-size:.92rem"><tbody>
<tr><td><b>Government</b></td><td>Industry page → case study → Book a consultation</td></tr><tr><td><b>Enterprise and utilities</b></td><td>Solution page → projects → Request a proposal</td></tr><tr><td><b>NGOs and donors</b></td><td>Health and development → county health spotlight → Discuss a project</td></tr><tr><td><b>Partners and universities</b></td><td>Partners → Become a partner form</td></tr><tr><td><b>Job seekers and students</b></td><td>Careers → pathways → talent pool or internship form</td></tr><tr><td><b>Learners</b></td><td>Academy → free QGIS course → Enrol</td></tr><tr><td><b>Software users</b></td><td>Hero, Technology and footer → OrionGIS ↗</td></tr></tbody></table>
<p>Every form sends a real message to {EMAIL} through the OrionGIS mail service, with a honeypot spam guard and a confirmation on screen. The form chooses its type from the link that opened it, so analytics can measure each journey.</p>
<h2>Built to stay up</h2><ul class="checks"><li>Static pages served straight from nginx: no database or container to fail, and an OrionGIS deploy cannot take the company site down.</li><li>Light pages: system-independent fonts with swap, WebP images with lazy loading, about 10 KB of JavaScript.</li><li>WCAG 2.2 AA target: keyboard menus, visible focus, skip link, labelled forms, reduced-motion support.</li><li>SEO carried over: every indexed URL (index.html, surveying.html, GIS.html, Remote-Sensing.html, Civil-Engineering.html, Utilities.html, portfolio.html, courses.html, enroll.html, Godwin-Murithi.html…) keeps its address; retired template pages redirect.</li></ul>
<h2>What comes after the design is approved</h2><ol><li>Content sign-off: the verification register in the repository lists every claim that needs management approval.</li><li>Administration: a Company site editor in Orion Central for news, projects, vacancies and enquiries, with roles and an audit log, instead of a separate CMS.</li><li>Recruitment: vacancies with closing dates and secure CV upload.</li><li>Cutover to orionterrametrics.co.ke, with the WordPress blog migrated and 301 redirects.</li></ol>
</div></section>'''
    page("proposal.html","Website proposal","Research, structure and engineering decisions behind the new Orion TerraMetrics corporate website.", body, "Proposal")

def directory():
    groups = {}
    for p in PAGES:
        groups.setdefault(p[3], []).append(p)
    out = "".join(f'<div><h3>{e(g)}</h3><ul>' + "".join(f'<li><a href="{u(p[0])}">{e(p[1])}</a></li>' for p in sorted(ps, key=lambda x: x[1])) + "</ul></div>" for g, ps in groups.items())
    page("directory.html","Site directory","Every page on the Orion TerraMetrics website.", phero("Directory","Site directory","Every page on this website.",[("Directory",None)])+f'<section class="section"><div class="wrap grid g4">{out}</div></section>', "Directory")

LEGACY = {"index01.html":"index.html","service-details.html":"solutions.html","starter-page.html":"index.html","portfolio-details_v1.html":"portfolio.html","CloudGIS.html":"technology.html","OrionSpatialDataHub.html":"technology.html#data-hub","SpatialDataHub.html":"technology.html#data-hub"}

def write():
    if DIST.exists(): shutil.rmtree(DIST)
    (DIST/"assets").mkdir(parents=True)
    shutil.copytree(ROOT/"assets/img", DIST/"assets/img"); shutil.copytree(ROOT/"assets/logos", DIST/"assets/logos"); shutil.copytree(ROOT/"assets/blog", DIST/"assets/blog")
    for f in ["OrionLogo.svg","OrionLogo.png","favicon.png","apple-touch-icon.png"]: shutil.copy(ROOT/"assets"/f, DIST/"assets"/f)
    shutil.copy(ROOT/"src/site.css", DIST/"assets/site.css"); shutil.copy(ROOT/"src/site.js", DIST/"assets/site.js")
    idx = []
    for path, title, desc, cat, featured, kw, doc in PAGES:
        out = DIST/path; out.parent.mkdir(parents=True, exist_ok=True); out.write_text(doc)
        idx.append({"u":"" if path=="index.html" else (path[:-10] if path.endswith("/index.html") else path),"t":title,"d":desc,"c":cat,"k":kw,"f":featured and cat in("Solution","Industry")})
    (DIST/"search-index.json").write_text(json.dumps(idx))
    for old, new in LEGACY.items():
        (DIST/old).write_text(f'<!doctype html><meta charset="utf-8"><title>Moved</title><link rel="canonical" href="{SITE}{new}"><meta name="robots" content="noindex"><meta http-equiv="refresh" content="0; url={u(new)}"><a href="{u(new)}">This page has moved.</a>')
    (DIST/"redirects.json").write_text(json.dumps(LEGACY, indent=1))
    urls = "".join(f"<url><loc>{SITE}{'' if p[0]=='index.html' else (p[0][:-10] if p[0].endswith('/index.html') else p[0])}</loc></url>" for p in PAGES)
    (DIST/"sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
    (DIST/"robots.txt").write_text("User-agent: *\nDisallow: /\n" if PREVIEW else f"User-agent: *\nAllow: /\nSitemap: {SITE}sitemap.xml\n")

def notfound():
    page("404.html","Page not found","The page you were looking for is not here.", phero("Error 404","We could not find that page.","It may have moved when we rebuilt the site. Try search, the site directory or one of these.",[("Not found",None)])+f'<section class="section"><div class="wrap grid g4"><a class="card" href="{u("solutions.html")}"><h3>Solutions</h3></a><a class="card" href="{u("portfolio.html")}"><h3>Our work</h3></a><a class="card" href="{u("directory.html")}"><h3>Site directory</h3></a><a class="card" href="{u("contact.html")}"><h3>Contact us</h3></a></div></section>', "Error")

# ================================================================== v2 inner pages (2026-11-27)
# Editorial components shared by every inner page. Defined after the v1 versions so they replace them.

# Mockup photography for projects whose only image is a dashboard screenshot or diagram.
# The original deliverable image still appears inside the case study as evidence.
PIMG = {"water-agency-asset-registry":"ph-dam","county-health-intelligence-platform":"ph-health","water-utility-digitization":"ph-energy",
        "ngo-health-transformation":"ph-dev","national-smart-geoportal":"ph-govt","cross-border-disease-surveillance":"ph-space",
        "county-sdi":"ph-govt","national-land-parcel-registry":"ph-estate","metropolitan-resettlement-planning":"ph-dusk",
        "rural-water-hydrogeology":"ph-agri","campus-tree-inventory":"ph-edu","residential-engineering-surveys":"ph-estate",
        "road-sewer-drainage-7km":"ph-infra"}
HOME_IMG.update(PIMG)
def pimg(p): return PIMG.get(p[0], p[5])

def phero(eyebrow, title, lead, trail, image=None, actions=""):
    media = f'<div class="xh-media">{img(image, "", eager=True)}</div>' if image else '<div class="xh-media xh-plain" aria-hidden="true"></div>'
    return f'''<section class="xh{" xh-img" if image else ""}">{media}<div class="wrap xh-body">{crumbs(trail)}<p class="hx-kicker">{e(eyebrow)}</p><h1>{e(title)}</h1><p class="xh-lead">{e(lead)}</p>{actions}</div></section>'''

def cta(title="Talk to us about your project", text="Whether it is one site survey or a national programme, a specialist will reply within two working days.", primary=("Discuss a project","contact.html?type=project"), secondary=("Request a proposal","contact.html?type=proposal"), image="ph-space"):
    return f'''<section class="closer closer-sm"><div class="closer-media">{img(image, "")}</div><div class="wrap closer-body"><div><h2>{e(title)}</h2><p>{e(text)}</p>{channels()}</div><div class="hero-actions" style="margin:0"><a class="btn btn-primary" href="{u(primary[1])}">{e(primary[0])}</a><a class="btn btn-ghost" href="{u(secondary[1])}">{e(secondary[0])}</a></div></div></section>'''

def pcard(p):
    slug,title,tag,svc,ind,image,summary,m,ml = p
    return f'<a class="xcard" href="{u("projects/"+slug+".html")}" data-tags="{"|".join(svc+ind)}"><figure>{img(pimg(p), title)}</figure>{'<span class="on-og">Built on OrionGIS</span>' if slug in ON_ORIONGIS else ''}<div><span class="tag">{e(tag)}</span><h3>{e(title)}</h3><p class="m"><b>{e(m)}</b> {e(ml)}</p></div></a>'

def rail(projects, title="Selected projects", sub="", link=("All projects","portfolio.html")):
    slides = "".join(f'<li>{pcard(p)}</li>' for p in projects)
    return f'''<section class="section work"><div class="wrap"><div class="work-head"><div><h2>{e(title)}</h2>{f"<p>{e(sub)}</p>" if sub else ""}</div><div class="work-nav"><button class="icon-btn" data-scroll="-1" aria-label="Previous">←</button><button class="icon-btn" data-scroll="1" aria-label="Next">→</button><a class="arrow-link" href="{u(link[1])}">{e(link[0])}</a></div></div></div><ul class="rail" tabindex="0">{slides}</ul></section>'''

def statement(big, small="", link=None):
    return f'<section class="section stmt stmt-sm"><div class="wrap stmt-grid"><h2 class="stmt-h">{big}</h2><div class="stmt-p">{f"<p>{e(small)}</p>" if small else ""}{f"<a class=arrow-link href={chr(34)+u(link[1])+chr(34)}>{e(link[0])}</a>" if link else ""}</div></div></section>'

def ruled(items, cols=2, numbered=True):
    li = "".join(f'<li>{f"<span class=num>{i+1:02d}</span>" if numbered else ""}<div><h3>{e(a)}</h3><p>{e(b)}</p></div></li>' for i,(a,b) in enumerate(items))
    return f'<ol class="ruled c{cols}{" nonum" if not numbered else ""}">{li}</ol>'

def platform_band(text="Project deliverables open in OrionGIS, an AI-powered geospatial workspace, where your team can explore, question and share them long after the project closes."):
    return f'''<section class="pband"><div class="wrap pband-grid"><div><img src="{u('assets/logos/oriongis-wordmark-tagline-white.png')}" alt="OrionGIS" height="38"><h2>Project results you can keep using</h2><p>{e(text)}</p><a class="btn btn-primary" href="{COM}" target="_blank" rel="noopener">Open OrionGIS ↗</a> <a class="btn btn-ghost" href="{COM}/signup" target="_blank" rel="noopener">Start free ↗</a></div><div class="pband-shot">{img("wf-map","A published map in OrionGIS Map Studio")}</div></div></section>'''

# ------------------------------------------------------------------ solutions
SOL_HOOK = {"surveying":"Accurate survey data for design, permits, land transactions and construction.",
            "gis":"Analysis that shows where to build, invest or deliver services, and who is affected.",
            "remote-sensing":"Regular monitoring of sites, farms, forests and corridors from satellite and drone imagery.",
            "transformation":"Field reporting, asset registers and dashboards moved off paper and onto one live system.",
            "data-infrastructure":"A single, well-governed source of location data for every department and partner.",
            "consulting":"Advice on where location data will pay back first, and how to buy and run it."}
def solutions():
    rows = "".join(f'''<a class="srow" href="{u(s["file"])}"><figure>{img(s["img"], s["name"])}</figure><div><span class="num">{i+1:02d}</span><h2>{e(s["name"])}</h2><p class="hook">{e(SOL_HOOK[k])}</p><p>{e(s["short"])}</p><span class="arrow-link">Explore {e(s["name"].lower())}</span></div></a>''' for i,(k,s) in enumerate(SOLUTIONS.items()))
    body = phero("Solutions","Our services","Survey, analysis, Earth observation, digital systems, data platforms and advice, delivered by one team for public and private organisations.",[("Solutions",None)],"ph-hero")
    body += f'<section class="section"><div class="wrap srows">{rows}</div></section>' + platform_band() + cta()
    page("solutions.html","Solutions","Survey, location analytics, Earth observation, digital operations, enterprise data platforms and advisory from Orion TerraMetrics.", body, "Solutions", True)
    for k, s in SOLUTIONS.items():
        rel = projects_for(k, "svc")
        inds = [INDUSTRIES[i] for i in INDUSTRIES if i in {x for p in rel for x in p[4]}] or list(INDUSTRIES.values())[:6]
        body = phero("Solutions", s["name"], s["lead"], [("Solutions","solutions.html"),(s["name"],None)], s["img"], f'<div class="hero-actions"><a class="btn btn-primary" href="{u("contact.html?type=project")}">Discuss a project</a><a class="btn btn-ghost" href="{u("contact.html?type=proposal")}">Request a proposal</a></div>')
        body += statement(e(SOL_HOOK[k]), s["short"])
        body += f'<section class="section soft"><div class="wrap"><div class="xhead"><h2>What we deliver</h2><p>Each engagement is scoped to your programme and delivered by one team.</p></div>{ruled(s["offers"])}</div></section>'
        if rel: body += rail(rel[:8], f"{s['name']} in practice", "", ("All related projects","portfolio.html#"+k))
        body += f'<section class="section soft"><div class="wrap"><div class="xhead"><h2>Sectors</h2></div><div class="chips">{"".join(f"<a href={chr(34)+u(i["file"])+chr(34)}>{e(i["name"])}</a>" for i in inds)}<a href="{u("industries.html")}">All industries →</a></div></div></section>'
        body += platform_band() + cta(f"Talk to our {s['name'].lower()} team", "Tell us about your project. A specialist will reply within two working days.")
        page(s["file"], s["name"], s["lead"][:155], body, "Solution", True, " ".join(a for a,_ in s["offers"]))

# ------------------------------------------------------------------ industries
def industries():
    tiles = "".join(f'<a class="tile" href="{u(i["file"])}">{img(i["img"], "")}<div><h3>{e(i["name"])}</h3><p>{e(i["short"])}</p></div></a>' for i in INDUSTRIES.values())
    body = phero("Industries","Industries we serve","We work with public bodies and private companies in every sector where decisions depend on location.",[("Industries",None)],"ph-space")
    body += f'<section class="section"><div class="wrap"><div class="tiles">{tiles}</div><p class="sectors-more" style="color:var(--body)">Working in another sector? <a href="{u("contact.html?type=consultation")}" style="color:var(--green-dark)">Talk to us about your project.</a></p></div></section>' + cta()
    page("industries.html","Industries","Location intelligence for every sector: government, banking, insurance, retail, real estate, telecoms, mining, logistics, utilities, health, agriculture, environment and more.", body, "Industry", True)
    for k, i in INDUSTRIES.items():
        rel = projects_for(k, "ind")
        svcs = i.get("svcs") or sorted({s for p in rel for s in p[3]}) or ["gis","consulting"]
        body = phero("Industries", i["name"], i["lead"], [("Industries","industries.html"),(i["name"],None)], i["img"], f'<div class="hero-actions"><a class="btn btn-primary" href="{u("contact.html?type=consultation")}">Book a consultation</a><a class="btn btn-ghost" href="{u("portfolio.html")}">See our work</a></div>')
        body += statement(e(i["short"]), "We combine field data, analysis and OrionGIS so that each recommendation comes with the evidence behind it.")
        body += f'<section class="section soft"><div class="wrap"><div class="xhead"><h2>Where we help</h2><p>Work we are asked to do most often in {e(i["name"].lower())}.</p></div>{ruled([(n, "") for n in i["needs"]], 2)}</div></section>'
        svch = "".join(f'<a class="srow srow-sm" href="{u(SOLUTIONS[s]["file"])}"><figure>{img(SOLUTIONS[s]["img"], "")}</figure><div><h3>{e(SOLUTIONS[s]["name"])}</h3><p>{e(SOLUTIONS[s]["short"])}</p><span class="arrow-link">Explore</span></div></a>' for s in svcs)
        body += f'<section class="section"><div class="wrap"><div class="xhead"><h2>Services involved</h2></div><div class="srows3">{svch}</div></div></section>'
        if rel: body += rail(rel[:8], f"Projects in {i['name'].lower()}", "", ("Filter the portfolio","portfolio.html#"+k))
        body += platform_band() + cta(f"Working in {i['name'].lower()}?", "Tell us about your project. A sector lead will reply within two working days.", ("Book a consultation","contact.html?type=consultation"), image=i["img"])
        page(i["file"], i["name"], i["lead"][:155], body, "Industry", True, " ".join(i["needs"]))

# ------------------------------------------------------------------ portfolio + case studies
_v1_portfolio = portfolio
def portfolio():
    _v1_portfolio()   # keeps clients.html; project pages and hub are rebuilt below
    global PAGES
    PAGES[:] = [p for p in PAGES if not (p[0] == "portfolio.html" or p[0].startswith("projects/"))]
    filters = [("all","All work")] + [(k, s["name"]) for k, s in SOLUTIONS.items()]
    used = {i for p in PROJECTS for i in p[4]}
    filters += [(k, i["name"]) for k, i in INDUSTRIES.items() if k in used]
    fb = "".join(f'<button aria-pressed="{str(k=="all").lower()}" data-f="{k}">{e(l)}</button>' for k, l in filters)
    body = phero("Our work","Our work",f"{len(PROJECTS)} published projects for national agencies, counties, utilities, health networks and private clients.",[("Our work",None)],"lidar")
    body += f'<section class="section"><div class="wrap"><div class="filters" role="group" aria-label="Filter projects">{fb}</div><div class="xgrid">{"".join(pcard(p) for p in PROJECTS)}</div></div></section>' + cta()
    page("portfolio.html","Project portfolio","Projects delivered by Orion TerraMetrics: surveys, LiDAR, location analytics, Earth observation, digital operations and data platforms.", body, "Our work", True)
    for p in PROJECTS:
        slug,title,tag,svc,ind,image,summary,m,ml = p
        rel = [q for q in PROJECTS if q is not p and (set(q[3])&set(svc) or set(q[4])&set(ind))][:8]
        hero = f'''<section class="xh xh-img xh-case"><div class="xh-media">{img(pimg(p), title, eager=True)}</div><div class="wrap xh-body">{crumbs([("Our work","portfolio.html"),(title,None)])}<p class="hx-kicker">Case study · {e(tag)}</p><h1>{e(title)}</h1></div>
<div class="hx-proof"><div class="wrap case-facts"><a><b>{e(m)}</b><span>{e(ml)}</span></a><a><b style="font-size:1.05rem">{", ".join(e(SOLUTIONS[s]["name"]) for s in svc)}</b><span>Capabilities</span></a><a><b style="font-size:1.05rem">{", ".join(e(INDUSTRIES[i]["name"]) for i in ind)}</b><span>Sectors</span></a></div></div></section>'''
        body = hero
        body += f'''<section class="section"><div class="wrap case-grid"><div><h2 class="case-lead">{e(summary)}</h2>
<p>Delivered end to end by Orion TerraMetrics: planning, field capture, processing, quality checks and handover, with results the client can keep using.</p>
<div class="chips" style="margin-top:22px">{"".join(f"<a href={chr(34)+u(SOLUTIONS[s]["file"])+chr(34)}>{e(SOLUTIONS[s]["name"])}</a>" for s in svc)}{"".join(f"<a href={chr(34)+u(INDUSTRIES[i]["file"])+chr(34)}>{e(INDUSTRIES[i]["name"])}</a>" for i in ind)}</div></div>
<aside class="case-side"><h3>Have a similar challenge?</h3><p>Talk to the team that delivered this project.</p><a class="btn btn-primary" href="{u("contact.html?type=project")}">Discuss a similar project</a></aside></div></section>
<section class="section soft"><div class="wrap"><div class="xhead"><h2>The deliverable</h2><p>Project output, as delivered to the client.</p></div><figure class="deliv">{img(image, title+" deliverable")}</figure></div></section>'''
        if rel: body += rail(rel, "More work like this")
        body += cta()
        page(f"projects/{slug}.html", title, summary[:155], body, "Project", False, tag+" "+m+" "+ml)

# ------------------------------------------------------------------ technology
PROD_HEAD = {"orionai":"Plain-language questions, answered as finished maps and analysis","map-studio":"Maps your stakeholders can read and share","data-hub":"More than 43,000 open datasets, ready to use","forms":"Field data that appears on the map as it syncs","insights":"Dashboards that update as data arrives"}
_v1_technology = technology
def technology():
    _v1_technology()
    PAGES[:] = [p for p in PAGES if p[0] != "technology.html"]
    prods = "".join(f'''<div class="prow" id="{k}"><div class="prow-txt"><img src="{u("assets/logos/"+ic+".png")}" alt="" width="52" height="52"><p class="hx-kicker" style="color:var(--green);margin:16px 0 10px">{e(n)}</p><h2>{e(PROD_HEAD[k])}</h2><p>{e(d)}</p><a class="arrow-link" href="{COM}{l}" target="_blank" rel="noopener">{e(n)} on OrionGIS ↗</a></div><figure class="browser"><img src="{u("assets/img/"+sc+".webp")}" alt="{e(n)} in OrionGIS" loading="lazy"></figure></div>''' for k,n,ic,sc,d,l in PRODUCTS)
    gallery = [("naivasha-sentinel2","Lake Naivasha: water and vegetation from Sentinel-2"),("mount-kenya-slope","Mount Kenya: slope analysis"),("nairobi-landcover","Nairobi: land cover classification"),("kilimanjaro-relief","Kilimanjaro: shaded relief"),("mwea-crop-vigour","Mwea irrigation scheme: crop vigour"),("po-valley-false-colour","Po Valley: false-colour composite")]
    gal = "".join(f'<li><figure>{img(f,c)}<figcaption>{e(c)}</figcaption></figure></li>' for f, c in gallery)
    body = phero("OrionGIS","The AI-powered geospatial workspace.","Ask questions in plain words and get finished maps and analysis. Collect from the field, run live dashboards and share securely, in one workspace your whole organisation can use.",[("Technology",None)],"ph-dusk",f'<div class="hero-actions"><a class="btn btn-primary" href="{COM}" target="_blank" rel="noopener">Visit OrionGIS ↗</a><a class="btn btn-ghost" href="{u("contact.html?type=consultation")}">Plan an enterprise rollout</a></div>')
    body += statement('Put the data you already hold to work.', "Most organisations keep location data in shapefiles, spreadsheets, survey reports and old dashboards. OrionGIS brings it together and lets your team ask questions of it in plain language.")
    body += f'<section class="section prows">{"<div class=wrap>"+prods+"</div>"}</section>'
    body += f'<section class="platform" id="orionai"><div class="wrap"><div class="xhead"><h2 style="color:#fff">Examples of OrionAI results</h2><p style="color:#b9cad7">Each map was produced from a plain-language question and comes with its sources and a colour key.</p></div></div><ul class="rail rail-wide">{gal}</ul></section>'
    body += rail([p for p in PROJECTS if p[0] in ON_ORIONGIS], "Client work on OrionGIS", "Programmes our clients run on the workspace today.", ("All projects","portfolio.html"))
    body += f'<section class="section" id="integration"><div class="wrap"><div class="xhead"><h2>Security, deployment and integration</h2><p>OrionGIS fits the systems and security rules you already have.</p></div>{ruled([("Private by default","Each organisation's data is kept separate, with roles and seats."),("Cloud or on-premise","Hosted by Orion, or deployed in your own data centre for data residency."),("Works with your tools","QGIS sync, OGC web services and developer APIs."),("Field-ready","Orion Collect captures data offline on Android and syncs straight to the map."),("Every source on record","Each dataset keeps its publisher, licence and history."),("Traceable AI answers","OrionAI lists the data and method behind every answer.")],3)}</div></section>'
    body += cta("Rolling OrionGIS out across an organisation?","We plan enterprise rollouts, integrations, training and on-premise deployments.",("Book a consultation","contact.html?type=consultation"),("Request a proposal","contact.html?type=proposal"),"ph-dusk")
    page("technology.html","Technology and OrionGIS","OrionGIS is an AI-powered geospatial workspace: ask questions in plain words, get finished maps and analysis, collect from the field and run live dashboards.", body, "Technology", True, "OrionGIS OrionAI GeoAI Map Studio Spatial Data Hub OrionForms OrionInsights QGIS API")

# ------------------------------------------------------------------ about
_v1_company = company
def company():
    _v1_company()
    PAGES[:] = [p for p in PAGES if p[0] not in ("about.html","leadership.html")]
    body = phero("Company","About Orion TerraMetrics","Orion TerraMetrics Africa Limited is a geospatial engineering and technology company based in Nairobi. We provide survey, analysis and AI services, and we develop OrionGIS.",[("Company",None)],"about-team")
    body += statement('Our story', "Orion TerraMetrics began as a surveying and GIS practice for engineers, counties and development programmes. Clients kept asking for one thing: data they could keep using after the project closed. So we built OrionGIS. Today our surveyors, analysts and software engineers work as one company, and the platform they build is used by organisations worldwide.")
    body += f'''<section class="mvv"><div class="wrap mvv-grid">
<div><p class="hx-kicker">Mission</p><h2>Put trustworthy location intelligence in the hands of every organisation that plans, builds, lends, sells or serves.</h2></div>
<div><p class="hx-kicker">Vision</p><h2>A world where every decision about a place is made on the ground truth.</h2></div></div>
<div class="wrap"><p class="hx-kicker" style="margin-top:56px">What we stand for</p>{ruled([("Accuracy we can prove","Every figure traces back to a measurement or a source."),("Your data stays yours","We never reuse a client's data beyond the engagement."),("Field checks first","We visit the site before we build a model."),("Built for handover","Systems your team can run after we leave."),("Honest about what we know","We say what the data can and cannot tell you.")],3)}<p class="notice" style="margin-top:28px">Proposed wording for management approval: mission, vision and values.</p></div></section>'''
    people = [("godwin","Godwin Murithi","Chief Executive Officer","Leads the vision for Orion TerraMetrics, OrionGIS and OrionAI. A geospatial systems specialist who has delivered enterprise GIS for water, power, health and government across East Africa.","Godwin-Murithi.html"),("nicholas","Nicholas Mutethia","Chief Operations Officer","Runs delivery. A geospatial engineer specialising in surveying, drone mapping and infrastructure planning, accountable for precision on every project.",None)]
    ppl = "".join(f'<div class="leader">{img(i,n)}<div><h3>{e(n)}</h3><p class="role">{e(r)}</p><p>{e(b)}</p>{f"<a class=arrow-link href={chr(34)+u(l)+chr(34)}>Full profile</a>" if l else ""}</div></div>' for i,n,r,b,l in people)
    lead_sec = f'<section class="section" id="leadership"><div class="wrap"><div class="xhead"><h2>Leadership</h2><p>The people accountable for our work and our clients\' trust.</p></div><div class="leaders">{ppl}</div></div></section>'
    body += lead_sec
    body += f'<section class="section"><div class="wrap chips-big"><a href="{u("careers.html")}"><b>Careers</b><span>Build technology that shapes how the world sees itself.</span></a><a href="{u("responsibility.html")}"><b>Responsibility</b><span>Open data, skills and public-interest work.</span></a><a href="{u("trust.html")}"><b>Trust and governance</b><span>Security, privacy and ethics.</span></a></div></section>'
    body += cta()
    page("about.html","About us","About Orion TerraMetrics Africa Limited: an AI-native location intelligence company in Nairobi. Our story, mission, values and leadership.", body, "Company", True)
    page("leadership.html","Leadership","The leadership team of Orion TerraMetrics Africa Limited.", phero("Company","Leadership","The people accountable for our work and our clients' trust.",[("Company","about.html"),("Leadership",None)],"ph-dusk")+lead_sec+cta("Talk to our leadership","Partnerships, investment and strategic engagements.",("Contact leadership","contact.html?type=general"),("Partner with us","partners.html")), "Company", True)

# ------------------------------------------------------------------ careers
_v1_careers = careers
def careers():
    _v1_careers()
    PAGES[:] = [p for p in PAGES if p[0] != "careers.html"]
    paths = [("Geospatial engineering","Surveyors, GIS analysts and remote sensing specialists who work in the field and the office."),("Software engineering","Engineers who build OrionGIS: web, data pipelines, maps and infrastructure."),("AI and data science","GeoAI, evaluation and the Global Data Index."),("Business development","Proposals, partnerships and client relationships."),("Internships and attachments","Structured placements for students and recent graduates."),("Corporate operations","Finance, people and administration.")]
    body = phero("Careers","Careers at Orion TerraMetrics","We hire surveyors, GIS analysts, software engineers and AI specialists who want their work used on real projects.",[("Careers",None)],"survey-field",f'<div class="hero-actions"><a class="btn btn-primary" href="#open">See open roles</a><a class="btn btn-ghost" href="{u("internships.html")}">Internships and attachments</a></div>')
    body += f'<section class="section soft"><div class="wrap"><div class="xhead"><h2>Find your place</h2></div>{ruled(paths,3,False)}</div></section>'
    body += f'''<section class="section" id="open"><div class="wrap split" style="align-items:start"><div><h2>Open roles</h2><p class="case-lead" style="font-size:1.2rem">No vacancies are open right now.</p><p>Roles are published here with a description, location and closing date when recruitment opens. Join the talent pool and we will contact you when a matching role opens.</p>
{ruled([("Apply","Send your CV and a short note."),("Review","We reply to every applicant within ten working days."),("Conversation","A first call about you, the role and the team."),("Technical step","A practical exercise or field assessment."),("Offer","References, offer and a structured first month.")],1)}<p class="notice">Proposed process for HR approval. Candidate data is handled under the Kenya Data Protection Act, 2019.</p></div>
<div class="card">{enquiry_form("careers", "Join the talent pool", [("careers","Talent pool"),("internship","Internship or attachment")], '<div class="field full"><label for="f-link">Link to your CV, LinkedIn or portfolio</label><input id="f-link" name="link" type="url" placeholder="https://"></div>')}</div></div></section>'''
    page("careers.html","Careers","Careers at Orion TerraMetrics: geospatial engineering, software, AI, business development, internships and attachments.", body, "Careers", True)

# ------------------------------------------------------------------ contact
def contact():
    body = phero("Contact","Contact us","Tell us about your project. A specialist will reply within two working days.",[("Contact",None)],"ph-hero")
    body += f'''<section class="section"><div class="wrap contact-grid"><div>{enquiry_form("project")}</div>
<aside class="contact-side" id="office"><h3>Head office</h3><p>Orion TerraMetrics Africa Limited<br>{e(ADDRESS)}</p><p><a href="tel:+254799882124">{PHONE1}</a><br><a href="tel:+254729212061">{PHONE2}</a><br><a href="mailto:{EMAIL}">{EMAIL}</a></p><p class="dim">Monday to Friday, 8:00 to 17:00 EAT</p><a class="arrow-link" href="https://www.google.com/maps/search/?api=1&query=GMC+Mansion+Mukhtar+Dadah+Street+Nairobi" target="_blank" rel="noopener">Open in Google Maps</a>
<hr><h3>Using OrionGIS?</h3><p>Product support, accounts and billing are handled on the OrionGIS site.</p><a class="arrow-link" href="{COM}/contact" target="_blank" rel="noopener">OrionGIS support ↗</a>
<hr><h3>Where we work</h3><p>Projects across Kenya, Somalia, Somaliland and Zimbabwe. OrionGIS is used worldwide.</p></aside></div></section>
<script>(function(){{var q=new URLSearchParams(location.search),t=q.get("type"),m=q.get("msg");if(t){{var r=document.querySelector('input[data-k="'+t+'"]');if(r)r.checked=true;}}if(m){{var a=document.getElementById("f-msg");if(a)a.value=m;}}}})();</script>'''
    page("contact.html","Contact","Contact Orion TerraMetrics: discuss a project, request a proposal, book a consultation, partnerships and media.", body, "Contact", True)


# ------------------------------------------------------------------ blog (migrated from WordPress 2026-11-27; content/blog/*.json is now the source)
import glob as _glob
POSTS = sorted((json.load(open(f)) for f in _glob.glob(str(ROOT/"content/blog/*.json"))), key=lambda r: r["date"], reverse=True)
def fdate(d):
    import datetime; return datetime.date.fromisoformat(d).strftime("%-d %B %Y")
def bcard(r, big=False):
    cover = f'<img src="{u(r["cover"])}" alt="" loading="lazy">' if r["cover"] else ""
    return f'<a class="bcard{" bcard-big" if big else ""}" href="{u("blog/"+r["slug"]+"/")}" data-tags="{"|".join(r["categories"])}"><figure>{cover}</figure><div><span class="tag">{e((r["categories"] or ["Article"])[0])}</span><h3>{e(r["title"])}</h3>{f"<p>{e(r[chr(101)+chr(120)+chr(99)+chr(101)+chr(114)+chr(112)+chr(116)])}</p>" if big else ""}<span class="meta">{fdate(r["date"])} · {r["minutes"]} min read</span></div></a>'
def news_cards(n):
    return "".join(bcard(r) for r in POSTS[:n])
BLOG_SLUG_FIX = {"the-5-components-of-gis":"the-components-of-geographic-information-systems-gis","how-gis-powers-your-world":"how-geographic-information-systems-gis-powers-your-world","what-is-a-gis-used-for-complete-guide-for-beginners":"what-is-a-gis"}
def blog():
    cats = sorted({c for r in POSTS for c in r["categories"]})
    fb = '<button aria-pressed="true" data-f="all">All articles</button>' + "".join(f'<button aria-pressed="false" data-f="{e(c)}">{e(c)}</button>' for c in cats)
    body = phero("Insights","The Orion TerraMetrics blog","Practical writing on GIS, surveying, Earth observation and the future of location intelligence, from the people who do the work.",[("Insights","insights.html"),("Blog",None)],"ph-dusk")
    body += f'<section class="section"><div class="wrap">{bcard(POSTS[0], True)}<div class="filters" role="group" aria-label="Filter articles" style="margin-top:56px">{fb}</div><div class="bgrid">{"".join(bcard(r) for r in POSTS[1:])}</div></div></section>' + cta()
    page("blog/index.html","Blog","Articles on GIS, surveying, remote sensing and location intelligence from Orion TerraMetrics.", body, "Insights", True)
    for i, r in enumerate(POSTS):
        rel = [x for x in POSTS if x is not r and set(x["categories"]) & set(r["categories"])][:3]
        art = r["html"].replace("{BASE}", BASE)
        for old, new in BLOG_SLUG_FIX.items(): art = art.replace(f"{BASE}blog/{old}/", f"{BASE}blog/{new}/")
        body = f'''<section class="art-hero"><div class="wrap art-head">{crumbs([("Insights","insights.html"),("Blog","blog/"),(r["title"][:40]+("…" if len(r["title"])>40 else ""),None)])}<p class="tag">{" · ".join(e(c) for c in r["categories"]) or "Article"}</p><h1>{e(r["title"])}</h1><p class="meta">Orion TerraMetrics · {fdate(r["date"])} · {r["minutes"]} min read</p></div>
{f'<figure class="art-cover wrap"><img src="{u(r["cover"])}" alt="" fetchpriority="high"></figure>' if r["cover"] else ""}</section>
<section class="section art-body"><div class="wrap art-grid"><article class="prose art">{art}</article>
<aside class="art-side"><div><h3>Working on something like this?</h3><p>Talk to the team behind this article.</p><a class="btn btn-primary btn-sm" href="{u("contact.html?type=consultation")}">Book a consultation</a><p class="art-ch"><a href="https://wa.me/{WA}?text={urllib.parse.quote("Hello Orion TerraMetrics, I read: "+r["title"])}" target="_blank" rel="noopener">WhatsApp</a> · <a href="tel:+254799882124">Call</a></p></div></aside></div></section>
{f'<section class="section soft"><div class="wrap"><div class="xhead"><h2>Keep reading</h2></div><div class="bgrid">{"".join(bcard(x) for x in rel)}</div></div></section>' if rel else ""}'''
        body += cta()
        page(f"blog/{r['slug']}/index.html", r["title"], r["excerpt"][:155] or r["title"], body, "Article", False, " ".join(r["categories"]))

if __name__ == "__main__":
    home(); solutions(); industries(); portfolio(); technology(); insights(); company(); careers(); partners(); academy(); contact(); trust(); blog(); proposal(); notfound(); directory()
    write()
    print(f"built {len(PAGES)} pages into {DIST} (BASE={BASE}, preview={PREVIEW})")
