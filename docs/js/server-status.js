'use strict';
/* GitHub Pages snapshot: refreshed by the existing collector, targeting ~5 minutes.
   Never claim live status from an old snapshot or an unrelated data-source light. */
(function(){
  const card=document.getElementById('server-status');
  if(!card)return;
  const target={
    level:document.getElementById('server-status-label'),
    players:document.getElementById('server-status-players'),
    map:document.getElementById('server-status-map'),
    updated:document.getElementById('server-status-updated')
  };
  const LABELS={
    online:'ONLINE / LIVE',
    offline:'OFFLINE',
    reconnecting:'RECONNECTING',
    unknown:'STATUS NOT VERIFIED'
  };
  // GitHub Actions scheduled workflows are best-effort, and may be delayed.
  const MAX_SNAPSHOT_AGE_MS=20*60*1000;
  function fresh(value,ms=MAX_SNAPSHOT_AGE_MS){
    if(typeof value!=='string')return false;
    const time=Date.parse(value);
    return Number.isFinite(time)&&time<=Date.now()+2*60*1000&&Date.now()-time<=ms;
  }
  function present(doc){
    const valid=doc&&doc.schemaVersion===1&&fresh(doc.checkedAt)&&fresh(doc.observedAt);
    const state=valid&&Object.hasOwn(LABELS,doc.state)?doc.state:'unknown';
    card.dataset.state=state;
    const line=LABELS[state];
    if(target.level.textContent!==line)target.level.textContent=line;
    const online=state==='online';
    target.players.textContent=online&&Number.isSafeInteger(doc.players)&&doc.players>=0?
      String(doc.players)+(Number.isSafeInteger(doc.maxPlayers)&&doc.maxPlayers>0?' / '+doc.maxPlayers:''):'—';
    target.map.textContent=online&&typeof doc.map==='string'&&doc.map.trim()?
      doc.map.slice(0,55):'—';
    target.updated.textContent=valid?
      'WARCON observed '+new Date(doc.observedAt).toLocaleTimeString(undefined,{hour:'numeric',minute:'2-digit'}):
      'No recent verified WARCON observation · Check live WARCON ↗';
    card.setAttribute('aria-label','Server status: '+line+
      (online?', '+target.players.textContent+' players, map '+target.map.textContent:''));
  }
  async function refresh(){
    if(document.visibilityState==='hidden')return;
    try {
      const response=await fetch('data/server-status.json',{cache:'no-store'});
      if(!response.ok)throw Error('Status snapshot unavailable');
      present(await response.json());
    } catch(_){present(null);}
  }
  present(null);
  refresh();
  window.setInterval(refresh,120000);
  document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')refresh();});
})();
