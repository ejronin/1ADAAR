'use strict';
/* Authenticated game-wide progression. WARDOGS server analytics remain WARCON.
   No SteamID, credentials, OpenID assertions or private profile values in Pages.
   A real service is disabled until a verified HTTPS endpoint is configured. */
(function(root){
  const host=document.getElementById('progression-panel');
  if(!host)return;
  const $=id=>document.getElementById(id);
  const KEY=/^[a-f0-9]{64}$/;
  const endpoint=String(root.OneADAARProgressionConfig?.endpoint||'').replace(/\/$/,'');
  const enabled=(()=>{
    try{return new URL(endpoint).protocol==='https:' &&
       !endpoint.includes('REPLACE')&&!endpoint.includes('localhost');}
    catch(_){return false;}
  })();
  const SAVED='1adaar-steam-session-v1', VERIFIER='1adaar-steam-pkce-v1';
  let currentKey=null,connected=false,inFlight=false,lastCheck=0;
  const url=new URL(root.location.href);
  // Code is a 90-second one-time credential. Remove before fetching any data.
  const callbackCode=url.searchParams.get('progression_code')||'';
  const callbackError=url.searchParams.get('progression_error')||'';
  if(callbackCode||callbackError){
    url.searchParams.delete('progression_code');url.searchParams.delete('progression_error');
    root.history.replaceState(null,'',url.pathname+url.search+url.hash);
  }
  const btn=$('progression-check'),refresh=$('progression-refresh'),
    disconnect=$('progression-disconnect'),consentBox=$('progression-consent-panel'),
    consentMain=$('progression-consent-main'),consentEconomy=$('progression-consent-economy'),
    consentSave=$('progression-consent-save'),status=$('progression-status'),
    synced=$('progression-synced-at'),connectedActions=$('progression-connected-actions'),
    economyToggle=$('progression-economy-toggle'),economySave=$('progression-economy-save'),
    radar=$('progression-role-radar'),roleRows=$('progression-role-values');
  function note(message){status.textContent=message;}
  function readSession(){
    try{
      const s=JSON.parse(sessionStorage.getItem(SAVED)||'null');
      return s&&KEY.test(s.playerKey)&&typeof s.token==='string'&&
        s.token.length>=40&&Number(s.expiresAt)>Date.now()/1000+5?s:null;
    }catch(_){return null;}
  }
  function clearSession(){
    sessionStorage.removeItem(SAVED);sessionStorage.removeItem(VERIFIER);
  }
  function show(state){
    connected=state==='connected';
    consentBox.hidden=state!=='consent';
    connectedActions.hidden=!connected;
    refresh.hidden=!connected;disconnect.hidden=!connected;
    btn.hidden=state==='connected'||state==='consent';
    btn.disabled=!enabled||inFlight;
    btn.textContent=enabled?'Connect with Steam':'Connect with Steam (setup pending)';
    refresh.disabled=inFlight;disconnect.disabled=inFlight;
  }
  const number=n=>Number.isSafeInteger(n)&&n>=0?n.toLocaleString('en-US'):'—';
  function blank(){
    root.OneADAARRoleRadar?.render(radar,null);
    $('progression-wardog-level').textContent='—';
    $('progression-career-xp').textContent='—';
    $('progression-cash').textContent='Hidden';
    $('progression-gold').textContent='Hidden';
    synced.textContent='Last Tracker sync: —';
    const roles=['Assault','Medic','Support','Recon','Driver','Pilot'];
    roleRows.replaceChildren();
    for(const role of roles){
      const tr=document.createElement('tr'),name=document.createElement('th');name.scope='row';name.textContent=role;
      const lv=document.createElement('td'),xp=document.createElement('td');
      lv.textContent='—';xp.textContent='—';tr.append(name,lv,xp);roleRows.append(tr);
    }
  }
  function paint(record){
    if(!record||record.sourceStatus!=='verified'||!record.levels||!record.xp){
      blank();note('Your Steam account is verified, but Tracker progression is private, not synchronized or unavailable. Sync on WARDOGS Tracker and try Refresh.');return;
    }
    const roles=root.OneADAARRoleRadar.ROLES;
    if(!roles.every(r=>Number.isFinite(record.levels[r])&&Number.isSafeInteger(record.xp[r]))) {
      blank();note('Tracker supplied incomplete role data. No values have been inferred.');return;
    }
    root.OneADAARRoleRadar.render(radar,record);
    $('progression-wardog-level').textContent=number(record.wardogLevel);
    $('progression-career-xp').textContent=number(record.careerXp);
    $('progression-cash').textContent=record.economyConsented?number(record.cash):'Hidden';
    $('progression-gold').textContent=record.economyConsented?number(record.gold):'Hidden';
    synced.textContent='Last Tracker sync: '+(record.syncedAt?
      new Date(record.syncedAt).toLocaleString(undefined,{dateStyle:'medium',timeStyle:'short'}):'Unavailable')+
      ' · Source: WARDOGS Tracker · Game-wide progression, not server match data';
    roleRows.replaceChildren();
    for(const role of roles){
      const tr=document.createElement('tr'),name=document.createElement('th');
      name.scope='row';name.textContent=role;
      const lv=document.createElement('td'),xp=document.createElement('td');
      lv.textContent='Level '+record.levels[role];xp.textContent=number(record.xp[role])+' XP';
      tr.append(name,lv,xp);roleRows.append(tr);
    }
    note('Connected ✓ — Steam ownership verified. Synced game-account progression shown separately from WARCON server statistics.');
  }
  async function api(path,method='GET',payload){
    const session=readSession();if(!session)throw Error('session_expired');
    const r=await fetch(endpoint+path,{
      method,headers:{Authorization:'Bearer '+session.token,
        ...(payload?{'Content-Type':'application/json'}:{})},
      ...(payload?{body:JSON.stringify(payload)}:{}),cache:'no-store'
    });
    const data=await r.json().catch(()=>({}));
    if(!r.ok)throw Error(data.error||'service_unavailable');
    return data;
  }
  async function load(){
    const key=currentKey;
    if(!key)return;
    const s=readSession();
    if(!s||s.playerKey!==key){show('unlinked');blank();return;}
    inFlight=true;show(connected?'connected':'unlinked');
    try{
      const info=await api('/api/me');
      if(currentKey!==key)return;
      if(info.playerKey!==key)throw Error('account_mismatch');
      if(info.state!=='connected'){
        blank();show('consent');
        note('Steam ownership verified. Choose the public progression and optional economy permissions below.');
        return;
      }
      economyToggle.checked=Boolean(info.economy);
      show('connected');
      const data=await api('/api/progression');
      if(currentKey!==key)return;
      if(data.state==='connected')paint(data.record);
      else paint(null);
    }catch(e){
      if(currentKey!==key)return;
      if(e.message==='session_expired'||e.message==='unauthenticated'||e.message==='account_mismatch'){
        clearSession();blank();show('unlinked');
        note('Session expired or the connected Steam account does not match this dossier. Reconnect with Steam.');
      }else note('Progression is temporarily unavailable ('+e.message+'). Your WARCON stats remain unchanged.');
    }finally{inFlight=false;show(connected?'connected':!consentBox.hidden?'consent':'unlinked');}
  }
  async function onReturn(code){
    if(!enabled){note('Steam service has not been activated.');return;}
    const verifier=sessionStorage.getItem(VERIFIER)||'';
    sessionStorage.removeItem(VERIFIER);
    if(!/^[A-Za-z0-9_-]{43}$/.test(verifier)){note('Steam verification expired. Start the connection again.');return;}
    const response=await fetch(endpoint+'/api/exchange',{method:'POST',
      headers:{'Content-Type':'application/json'},cache:'no-store',
      body:JSON.stringify({code,verifier})});
    const data=await response.json();
    if(!response.ok||data.playerKey!==currentKey){
      note('Steam verification was not completed for this player. '+(data.error||'Try again.'));
      return;
    }
    sessionStorage.setItem(SAVED,JSON.stringify({token:data.token,
      expiresAt:data.expiresAt,playerKey:data.playerKey}));
    await load();
  }
  btn.addEventListener('click',async()=>{
    if(!enabled||!currentKey)return;
    // Authorization code + PKCE: no naked SteamID ever enters the static app.
    const raw=crypto.getRandomValues(new Uint8Array(32));
    const verifier=Array.from(raw,b=>b.toString(16).padStart(2,'0')).join('').slice(0,43);
    const digest=new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(verifier)));
    const challenge=btoa(String.fromCharCode(...digest))
      .replaceAll('+','-').replaceAll('/','_').replace(/=+$/,'');
    sessionStorage.setItem(VERIFIER,verifier);
    note('Redirecting to Steam account verification. You will return to this 1ADAAR dossier.');
    root.location.assign(endpoint+'/auth/start?challenge='+encodeURIComponent(challenge)+
      '&player='+encodeURIComponent(currentKey));
  });
  consentSave.addEventListener('click',async()=>{
    if(!consentMain.checked){note('Public progression permission must be checked before connection.');return;}
    consentSave.disabled=true;
    try{
      await api('/api/consent','POST',{progression:true,economy:consentEconomy.checked});
      consentBox.hidden=true;await load();
    }catch(e){note('Could not save consent: '+e.message);}
    finally{consentSave.disabled=false;}
  });
  refresh.addEventListener('click',async()=>{
    if(!connected||inFlight)return;
    refresh.disabled=true;note('Refreshing your synchronized public WARDOGS progression…');
    try{const r=await api('/api/refresh','POST');
      if(r.state==='connected')paint(r.record);else paint(null);
    }catch(e){note('Refresh unavailable ('+e.message+'). Existing displayed data may be outdated.');}
    finally{refresh.disabled=false;}
  });
  economySave.addEventListener('click',async()=>{
    economySave.disabled=true;
    try{await api('/api/consent','POST',{progression:true,economy:economyToggle.checked});
      await load();}catch(e){note('Could not update visibility: '+e.message);}
    finally{economySave.disabled=false;}
  });
  disconnect.addEventListener('click',async()=>{
    disconnect.disabled=true;
    try{await api('/api/disconnect','POST');}
    catch(_){/* Revoke server session on next authenticated request if unreachable. */}
    clearSession();blank();connected=false;show('unlinked');
    note('Disconnected locally. Reconnect with Steam to verify server-side consent revocation.');
    disconnect.disabled=false;
  });
  root.addEventListener('focus',()=>{if(Date.now()-lastCheck>60000&&readSession()&&currentKey){
    lastCheck=Date.now();load();
  }});
  let usedCallback=false;
  async function mount(entry){
    const allowed=entry&&!entry.demo&&KEY.test(entry.key);
    currentKey=allowed?entry.key:null;
    host.hidden=!allowed;
    if(!allowed)return;
    blank();connected=false;show('unlinked');
    if(!enabled){note('Steam connection service is not deployed yet. Your WARCON player statistics still work.');return;}
    if(callbackError){note('Steam connection could not finish: '+callbackError+'. Retry if necessary.');return;}
    if(callbackCode&&!usedCallback){
      usedCallback=true;
      try{await onReturn(callbackCode);}catch(e){note('Steam callback failed: '+e.message);}
    }else await load();
  }
  root.OneADAARProgression=Object.freeze({mount});
})(window);
