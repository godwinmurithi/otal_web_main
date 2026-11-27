#!/usr/bin/env python3
"""One-off: migrate the WordPress blog (orionterrametrics.co.ke/blog) into content/blog/*.json + assets/blog/.
Content is sanitised to an allow-list of tags; images are downloaded and served locally.
Usage: python3 -I tools/migrate_wp.py content/blog-src/posts.json
"""
import json, sys, re, os, html, hashlib, subprocess, urllib.request, urllib.parse
from html.parser import HTMLParser
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT, IMG = os.path.join(ROOT, "content/blog"), os.path.join(ROOT, "assets/blog")
os.makedirs(OUT, exist_ok=True); os.makedirs(IMG, exist_ok=True)
SKIP = {"young-blonde-woman-looking-around-on-terrace"}   # theme demo post, not company content
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36", "Referer": "https://orionterrametrics.co.ke/blog/", "Accept": "image/avif,image/webp,image/*,*/*"}
ALLOW = {"p","h2","h3","h4","ul","ol","li","strong","b","em","i","a","blockquote","figure","figcaption","img","table","thead","tbody","tr","th","td","br","hr","code","pre","sup","sub"}
VOID = {"img","br","hr"}

def fetch_img(url):
    url = html.unescape(url)
    if not url.startswith("http"): return None
    name = hashlib.sha1(url.encode()).hexdigest()[:12] + ".webp"
    dst = os.path.join(IMG, name)
    if not os.path.exists(dst):
        try:
            raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
            tmp = dst + ".src"; open(tmp, "wb").write(raw)
            subprocess.run(["convert", tmp + "[0]", "-resize", "1600x>", "-quality", "78", dst], check=True, capture_output=True); os.remove(tmp)
        except Exception as ex:
            print("  image failed", url, ex); return None
    return "assets/blog/" + name

class Clean(HTMLParser):
    def __init__(s): super().__init__(convert_charrefs=True); s.out=[]; s.stack=[]; s.skip=0
    def handle_starttag(s, t, a):
        if t in ("script","style","iframe","noscript","form","svg"): s.skip += 1; return
        if s.skip or t not in ALLOW: return
        a = dict(a); keep = ""
        if t == "a" and a.get("href","").startswith(("http","/","#","mailto:")):
            href = a["href"].replace("https://orionterrametrics.co.ke/blog/", "{BASE}blog/")
            keep = f' href="{html.escape(href, True)}"' + ("" if href.startswith(("{BASE}","#","/")) else ' target="_blank" rel="noopener"')
        if t == "img":
            src = a.get("data-src") or a.get("src") or ""
            loc = fetch_img(src)
            if not loc: return
            keep = f' src="{{BASE}}{loc}" alt="{html.escape(a.get("alt",""), True)}" loading="lazy"'
        if t in ("td","th") and a.get("colspan"): keep = f' colspan="{html.escape(a["colspan"],True)}"'
        s.out.append(f"<{t}{keep}>")
        if t not in VOID: s.stack.append(t)
    def handle_endtag(s, t):
        if t in ("script","style","iframe","noscript","form","svg"): s.skip = max(0, s.skip-1); return
        if s.skip or t not in ALLOW or t in VOID: return
        if t in s.stack:
            while s.stack:
                x = s.stack.pop(); s.out.append(f"</{x}>")
                if x == t: break
    def handle_data(s, d):
        if not s.skip: s.out.append(html.escape(d, False))
    def result(s):
        while s.stack: s.out.append(f"</{s.stack.pop()}>")
        h = "".join(s.out)
        h = re.sub(r"<(p|h2|h3|li)>\s*</\1>", "", h)
        return h

posts = json.load(open(sys.argv[1]))
index = []
for p in posts:
    if p["slug"] in SKIP or p["status"] != "publish": continue
    print(p["slug"])
    c = Clean(); c.feed(p["content"]["rendered"]); body = c.result()
    ex = Clean(); ex.feed(p["excerpt"]["rendered"]); excerpt = re.sub(r"<[^>]+>", "", ex.result()).replace("[&hellip;]","").replace("[…]","").strip()
    fm = (p.get("_embedded",{}).get("wp:featuredmedia") or [{}])[0]
    cover = fetch_img(fm.get("source_url","")) if fm.get("source_url") else None
    cats = [html.unescape(t["name"]) for grp in p.get("_embedded",{}).get("wp:term",[]) for t in grp if t.get("taxonomy")=="category" and t["name"]!="Uncategorized"]
    words = len(re.sub(r"<[^>]+>"," ",body).split())
    rec = dict(slug=p["slug"], title=html.unescape(p["title"]["rendered"]), date=p["date"][:10], modified=p["modified"][:10],
               excerpt=html.unescape(excerpt)[:300], cover=cover, categories=cats, minutes=max(1, round(words/220)), html=body,
               source=p["link"])
    json.dump(rec, open(os.path.join(OUT, p["slug"]+".json"), "w"), ensure_ascii=False, indent=1)
print("done")
