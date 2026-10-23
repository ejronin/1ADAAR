'use strict';
/* PlayerOne-only offline demonstration. NEVER performs authentication, API calls,
   writes consent cookies, stores account connections or uses real player IDs. */
(function(){
  if(document.body.dataset.fictionalDemo!=='true')return;
  const panel=document.getElementById('demo-progression-panel');
  const radar=document.getElementById('demo-role-radar');
  const badge=document.getElementById('demo-progression-badge');
  const info=document.getElementById('demo-progression-status');
  const connect=document.getElementById('demo-progression-connect');
  const refresh=document.getElementById('demo-progression-refresh');
  const disconnect=document.getElementById('demo-progression-disconnect');
  const grid=document.getElementById('demo-role-values');
  const last=document.getElementById('demo-last-sync');
  const economy=document.getElementById('demo-economy-visible');
  if(!panel||!radar||!window.OneADAARRoleRadar)return;
  const FIXTURE=Object.freeze({
    sourceStatus:'fictional-demo',source:'FICTIONAL PLAYERONE FIXTURE',demo:true,
    maxLevel:50, // VISUAL EXAMPLE SCALE ONLY; NOT a published WARDOGS level cap.
    levels:Object.freeze({Assault:38,Medic:26,Support:22,Recon:19,Driver:14,Pilot:30}),
    xp:Object.freeze({Assault:612000,Medic:180400,Support:140800,
                       Recon:350200,Driver:90050,Pilot:457000}),
    wardogLevel:142,careerXp:1830450,cash:220531,gold:4
  });
  let connected=false;
  const format=n=>n.toLocaleString('en-US');
  const setValue=(id,value)=>{const el=document.getElementById(id);if(el)el.textContent=value;};
  const roles=window.OneADAARRoleRadar.ROLES;
  function paint(){
    radar.setAttribute('data-role-demo','true');
    window.OneADAARRoleRadar.render(radar,connected?FIXTURE:null);
    panel.dataset.demoState=connected?'connected':'unlinked';
    badge.textContent=connected?'SIMULATED CONNECTION · NOT A REAL STEAM ACCOUNT':
      'NOT CONNECTED · FICTIONAL PLAYER';
    info.textContent=connected?
      'Example: Steam ownership confirmed, permission granted, then public Tracker progression refreshed. This is an OFFLINE DEMO; none of those real actions occurred.':
      'Example unlinked profile. Use the test button to see how the approved connected state will look. This never signs you in or queries WARDOGS Tracker.';
    connect.hidden=connected;refresh.hidden=!connected;disconnect.hidden=!connected;
    last.textContent=connected?'Fictional example snapshot · no API request':'No connection';
    setValue('demo-wardog-level',connected?String(FIXTURE.wardogLevel):'—');
    setValue('demo-career-xp',connected?format(FIXTURE.careerXp):'—');
    setValue('demo-cash',connected&&economy.checked?format(FIXTURE.cash):'Hidden');
    setValue('demo-gold',connected&&economy.checked?String(FIXTURE.gold):'Hidden');
    economy.disabled=!connected;
    grid.replaceChildren();
    for(const role of roles){
      const tr=document.createElement('tr');
      const title=document.createElement('th');title.scope='row';title.textContent=role;
      const level=document.createElement('td');
      level.textContent=connected?'Level '+FIXTURE.levels[role]:'—';
      const xp=document.createElement('td');
      xp.textContent=connected?format(FIXTURE.xp[role])+' XP':'—';
      tr.append(title,level,xp);grid.append(tr);
    }
  }
  connect.addEventListener('click',()=>{connected=true;paint();});
  refresh.addEventListener('click',()=>{
    if(!connected)return;
    paint();
    info.textContent='Fictional refresh complete. The same demonstration values were re-rendered; no network request or account link exists.';
  });
  disconnect.addEventListener('click',()=>{connected=false;economy.checked=false;paint();});
  economy.addEventListener('change',paint);
  paint();
})();
