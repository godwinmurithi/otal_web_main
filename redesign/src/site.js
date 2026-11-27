(function(){
  var BASE=document.documentElement.dataset.base||"/";
  // Mega menus
  var tops=[].slice.call(document.querySelectorAll(".nav-top"));
  function closeAll(except){tops.forEach(function(b){if(b!==except){b.setAttribute("aria-expanded","false");document.getElementById(b.getAttribute("aria-controls")).classList.remove("open");}});}
  tops.forEach(function(b){
    var m=document.getElementById(b.getAttribute("aria-controls"));
    b.addEventListener("click",function(e){e.stopPropagation();var o=b.getAttribute("aria-expanded")==="true";closeAll(b);b.setAttribute("aria-expanded",String(!o));m.classList.toggle("open",!o);});
  });
  document.addEventListener("click",function(e){if(!e.target.closest(".nav"))closeAll();});
  document.addEventListener("keydown",function(e){if(e.key==="Escape"){closeAll();closeSearch();}});
  var mt=document.querySelector(".menu-toggle"),nav=document.querySelector(".nav");
  if(mt)mt.addEventListener("click",function(){var o=nav.classList.toggle("open");mt.setAttribute("aria-expanded",String(o));});

  // Search
  var panel=document.querySelector(".search-panel"),input=panel&&panel.querySelector("input"),out=panel&&panel.querySelector(".search-results"),idx=null;
  function openSearch(){panel.classList.add("open");input.focus();if(!idx){fetch(BASE+"search-index.json").then(function(r){return r.json()}).then(function(j){idx=j;run();});}}
  function closeSearch(){if(panel)panel.classList.remove("open");}
  function esc(s){return s.replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]});}
  function run(){if(!idx)return;var q=input.value.trim().toLowerCase();var terms=q.split(/\s+/).filter(Boolean);
    var res=idx.filter(function(p){var h=(p.t+" "+p.d+" "+p.k).toLowerCase();return terms.every(function(t){return h.indexOf(t)>-1});}).slice(0,12);
    out.innerHTML=(q?res:idx.filter(function(p){return p.f}).slice(0,8)).map(function(p){return '<li><a href="'+BASE+p.u+'"><span class="kind">'+esc(p.c)+'</span><br>'+esc(p.t)+'<small>'+esc(p.d)+'</small></a></li>'}).join("")||'<li class="muted" style="padding:12px">No pages match. Try a service, sector or project name.</li>';}
  document.querySelectorAll("[data-search]").forEach(function(b){b.addEventListener("click",openSearch)});
  if(panel){panel.addEventListener("click",function(e){if(e.target===panel)closeSearch()});input.addEventListener("input",run);}

  // Portfolio filter
  var fb=[].slice.call(document.querySelectorAll(".filters button"));
  fb.forEach(function(b){b.addEventListener("click",function(){fb.forEach(function(x){x.setAttribute("aria-pressed",String(x===b))});var f=b.dataset.f;
    document.querySelectorAll("[data-tags]").forEach(function(c){c.hidden=!(f==="all"||c.dataset.tags.split("|").indexOf(f)>-1)});});});
  var hash=decodeURIComponent(location.hash.slice(1));if(hash){var hb=fb.filter(function(b){return b.dataset.f===hash})[0];if(hb)hb.click();}

  // Product showcase tabs
  var tabs=[].slice.call(document.querySelectorAll(".show-tabs [role=tab]"));
  tabs.forEach(function(t){t.addEventListener("click",function(){tabs.forEach(function(x){var on=x===t;x.setAttribute("aria-selected",String(on));x.tabIndex=on?0:-1;document.getElementById(x.getAttribute("aria-controls")).hidden=!on;});});
    t.addEventListener("keydown",function(e){var i=tabs.indexOf(t);if(e.key==="ArrowDown"||e.key==="ArrowRight"){e.preventDefault();var n=tabs[(i+1)%tabs.length];n.focus();n.click();}if(e.key==="ArrowUp"||e.key==="ArrowLeft"){e.preventDefault();var p=tabs[(i-1+tabs.length)%tabs.length];p.focus();p.click();}});});

  // Enquiry forms -> OrionGIS contact endpoint
  document.querySelectorAll("form[data-enquiry]").forEach(function(form){
    var status=form.querySelector(".form-status");
    form.addEventListener("submit",function(e){e.preventDefault();var ok=true;
      form.querySelectorAll("[required]").forEach(function(f){var w=f.closest(".field");var bad=!f.value.trim()||(f.type==="email"&&!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(f.value));if(w)w.classList.toggle("invalid",bad);if(bad)ok=false;});
      if(!ok){status.className="form-status bad";status.textContent="Please complete the highlighted fields.";return;}
      if(form.querySelector(".hp input").value){return;}
      var d=new FormData(form),type=(d.get("type")||form.dataset.enquiry);
      var lines=["["+type+"] via Orion TerraMetrics corporate site ("+location.pathname+")"];
      ["role","sector","country","timeline","budget","link"].forEach(function(k){if(d.get(k))lines.push(k[0].toUpperCase()+k.slice(1)+": "+d.get(k))});
      lines.push("",d.get("message"));
      var btn=form.querySelector("button[type=submit]");btn.disabled=true;btn.textContent="Sending…";
      fetch(form.dataset.endpoint,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({name:d.get("name"),email:d.get("email"),organization:d.get("organization")||"",message:lines.join("\n")})})
        .then(function(r){if(!r.ok)throw 0;status.className="form-status ok";status.textContent="Thank you. Your enquiry has reached our team at info@orionterrametrics.co.ke, and we reply within two working days.";form.reset();})
        .catch(function(){status.className="form-status bad";status.textContent="We could not send that just now. Please email info@orionterrametrics.co.ke or call +254 799 882 124.";})
        .finally(function(){btn.disabled=false;btn.textContent=btn.dataset.label;});
    });
  });
})();
(function(){
  // Sector index: swap the large image on hover/focus
  var fig=document.querySelector(".sectors-img"),im=fig&&fig.querySelector("img");
  if(im){[].forEach.call(document.querySelectorAll(".sectors-lists a[data-img]"),function(a){
    var pre=new Image();pre.src=a.dataset.img;
    function show(){if(im.getAttribute("src")===a.dataset.img)return;fig.classList.add("fade");setTimeout(function(){im.src=a.dataset.img;fig.classList.remove("fade");},160);}
    a.addEventListener("mouseenter",show);a.addEventListener("focus",show);});}
  // Project rail arrows
  var rail=document.querySelector(".rail");
  [].forEach.call(document.querySelectorAll("[data-scroll]"),function(b){b.addEventListener("click",function(){if(!rail)return;var w=rail.querySelector("li");rail.scrollBy({left:(+b.dataset.scroll)*((w?w.offsetWidth:400)+22)*2,behavior:"smooth"});});});
})();
(function(){
  // "Talk to us" launcher
  var lb=document.querySelector(".launch-btn"),lp=document.getElementById("launch-panel");
  if(lb){lb.addEventListener("click",function(e){e.stopPropagation();var o=lp.hidden;lp.hidden=!o;lb.setAttribute("aria-expanded",String(o));});
    document.addEventListener("click",function(e){if(!e.target.closest(".launch")){lp.hidden=true;lb.setAttribute("aria-expanded","false");}});
    document.addEventListener("keydown",function(e){if(e.key==="Escape"){lp.hidden=true;lb.setAttribute("aria-expanded","false");}});}

  // Ask Orion concierge (preview): routes a plain-language need to the right sector, capabilities, proof and a human handoff.
  var box=document.querySelector("[data-ask]");if(!box)return;
  var kb=JSON.parse(document.getElementById("ask-kb").textContent),form=box.querySelector("form"),q=box.querySelector("input"),out=box.querySelector(".ask-out");
  var SYN={"Banking":"bank branch atm agent loan lend lending credit collateral mortgage microfinance fintech sacco unbanked","Insurance":"insur claim claims exposure premium underwrit parametric reinsur catastrophe","Retail":"store stores shop shops outlet outlets catchment footfall retail fmcg distributor supermarket franchise sales territory","Real estate":"property properties real estate developer development plot plots valuation housing apartment land buy","Telecoms":"tower towers fibre fiber coverage network telecom mobile operator 5g site acquisition","Mining":"mine mining quarry stockpile pit tailings concession oil gas mineral","Transport":"route routes routing depot warehouse fleet delivery deliveries logistics last-mile address truck trucks transport","Agriculture":"farm farms farmer crop crops drought yield tea coffee irrigation agri harvest livestock traceab deforestation","Health":"health clinic clinics hospital hospitals facility facilities disease malaria patients maternal","Government":"county counties ministry government public citizen registry parcel parcels cadastr planning permit","Energy":"water pipe pipes power utility utilities electricity grid meter leakage non-revenue transmission","Infrastructure":"road roads bridge bridges construction contractor engineering corridor dam railway","Environment":"forest forests climate carbon flood floods wetland conservation environment biodiversity emissions","Education":"school schools university universities research students enrolment","International development":"ngo donor donors beneficiar humanitarian refugee programme vulnerab aid"};
  var SSYN={"Survey":"survey surveys measure boundary topographic lidar drone uav setting-out volume volumes","Location analytics":"where site sites select selection location analysis best open next suitab catchment risk","Earth observation":"satellite imagery monitor monitoring change drought stress crop vegetation flood from space","Digital operations":"dashboard dashboards report reporting forms paper spreadsheet field team live operations","Enterprise data":"registry registries portal platform database single source data hub catalogue","Strategy":"strategy plan advise advice procurement roadmap where to start"};
  function words(t){return t.toLowerCase().replace(/[^a-z0-9\s-]/g," ").split(/\s+/).filter(function(w){return w.length>2});}
  function score(list,syn,ws){return list.map(function(x){var s=0;for(var key in syn){if(x.n.indexOf(key)===0||x.n.indexOf(key)>-1){syn[key].split(" ").forEach(function(sw){ws.forEach(function(w){if(w.indexOf(sw)===0||sw.indexOf(w)===0&&w.length>4)s+=3;});});}}
    ws.forEach(function(w){if(w.length>3&&x.k.indexOf(w)>-1)s+=1;});return {x:x,s:s};}).sort(function(a,b){return b.s-a.s});}
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]});}
  function answer(text){
    var ws=words(text);if(!ws.length)return;
    var sec=score(kb.sectors,SYN,ws),sol=score(kb.solutions,SSYN,ws),s0=sec[0].s>2?sec[0].x:null,sols=sol.filter(function(r){return r.s>1}).slice(0,2).map(function(r){return r.x});
    if(!sols.length)sols=[kb.solutions[1],kb.solutions[3]];
    var pr=kb.projects.map(function(p){var s=0;ws.forEach(function(w){if(w.length>3&&p.k.indexOf(w)>-1)s++;});if(s0&&p.k.indexOf(s0.n.split(" ")[0].toLowerCase())>-1)s+=1;return{p:p,s:s}}).sort(function(a,b){return b.s-a.s})[0];
    var msg=encodeURIComponent(text),h='<p class="ask-q">“'+esc(text)+'”</p><div class="ask-a">';
    h+=s0?'<p>This is '+(/^[aeiou]/i.test(s0.n)?'an':'a')+' <a href="'+s0.u+'">'+esc(s0.n.toLowerCase())+'</a> decision, and one we can help with. ':'<p>We can help with that. ';
    h+='We would typically combine '+sols.map(function(s){return'<a href="'+s.u+'">'+esc(s.n.toLowerCase())+'</a>'}).join(' and ')+', then put the answer on a live map your team can question in plain words.</p>';
    if(pr&&pr.s>1)h+='<a class="ask-proof" href="'+pr.p.u+'"><span>Related work</span><b>'+esc(pr.p.n)+'</b><em>'+esc(pr.p.m)+'</em></a>';
    h+='<div class="ask-act"><a class="btn btn-primary btn-sm" href="'+kb.contact+'?type=project&msg='+msg+'">Send this to a specialist</a><a class="btn btn-ghost btn-sm" href="https://wa.me/'+kb.wa+'?text='+encodeURIComponent("Hello Orion TerraMetrics. "+text)+'" target="_blank" rel="noopener">Continue on WhatsApp</a><a class="btn btn-ghost btn-sm" href="tel:+'+kb.wa+'">Call us</a></div>';
    h+='<p class="ask-note">Preview assistant. At launch this connects to OrionAI for full answers.</p></div>';
    out.innerHTML=h;out.hidden=false;
  }
  form.addEventListener("submit",function(e){e.preventDefault();answer(q.value.trim());});
  [].forEach.call(box.querySelectorAll(".ask-chips button"),function(b){b.addEventListener("click",function(){q.value=b.textContent;answer(b.textContent);});});
})();
