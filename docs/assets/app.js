const search = document.querySelector('#doc-search');
const results = document.querySelector('#search-results');
const index = JSON.parse(document.querySelector('#search-index').textContent);
search.addEventListener('input', () => {
  results.replaceChildren();
  const q = search.value.trim().toLowerCase();
  if (!q) { results.hidden = true; return; }
  const hits = index.filter(item => item.text.toLowerCase().includes(q)).slice(0,10);
  if (!hits.length) {
    const p = document.createElement('p');p.className='no-results';p.textContent='No matching section or parameter.';results.append(p);
  }
  for (const hit of hits) {
    const a=document.createElement('a');a.href='#'+hit.id;a.textContent=hit.text;a.role='listitem';
    a.addEventListener('click',()=>{results.hidden=true;search.blur();});results.append(a);
  }
  results.hidden=false;
});
search.addEventListener('keydown',e=>{if(e.key==='Enter'){const first=results.querySelector('a');if(first){first.click();}}if(e.key==='Escape'){results.hidden=true;search.blur();}});
document.addEventListener('click',e=>{if(!e.target.closest('.search-wrap'))results.hidden=true;});
document.addEventListener('keydown',e=>{if(e.key==='/'&&!/input|textarea/i.test(document.activeElement.tagName)){e.preventDefault();search.focus();}if(e.key==='Escape'){document.querySelector('.sidebar').classList.remove('open');document.querySelector('.menu-scrim').hidden=true;document.querySelector('.menu-toggle').setAttribute('aria-expanded','false');}});
document.querySelectorAll('.copy-code').forEach(button=>{
  button.addEventListener('click',async()=>{
    try {await navigator.clipboard.writeText(button.parentElement.querySelector('code').textContent);button.textContent='Copied';setTimeout(()=>{button.textContent='Copy';},1500);}
    catch {button.textContent='Select code';}
  });
});
const toggle=document.querySelector('.menu-toggle');
const side=document.querySelector('.sidebar');
const scrim=document.querySelector('.menu-scrim');
function closeMenu(){side.classList.remove('open');scrim.hidden=true;toggle.setAttribute('aria-expanded','false');}
toggle.addEventListener('click',()=>{const open=side.classList.toggle('open');scrim.hidden=!open;toggle.setAttribute('aria-expanded',String(open));});
scrim.addEventListener('click',closeMenu);
side.querySelectorAll('a').forEach(a=>a.addEventListener('click',closeMenu));
const sections=[...document.querySelectorAll('.document h2')];
const links=[...document.querySelectorAll('.side-sections a,.on-this-page nav a')];
function trackSection(){let current=sections[0]?.id;for(const s of sections){if(s.getBoundingClientRect().top<=150)current=s.id;}links.forEach(a=>a.classList.toggle('active',a.hash==='#'+current));}
document.addEventListener('scroll',trackSection,{passive:true});trackSection();
