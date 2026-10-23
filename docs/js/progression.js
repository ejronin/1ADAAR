'use strict';
// Public, opt-in WARDOGS Tracker lookup. This is NOT Steam authentication.
// One-time user-provided ID stays in this browser only when Remember is checked.
(function(root){
  const PROFILE_KEY='1adaar-public-tracker-profile-v1';
  const api='https://wardogstracker.gg/api/v1/';
  const ID=/^7656119\d{10}$/;
  const KEY=/^[a-f0-9]{64}$/;
  const roles=['Assault','Medic','Support','Recon','Driver','Pilot'];
  const el=id=>document.getElementById(id);
  let active=null,seq=0;
  const validInt=n=>Number.isSafeInteger(n)&&n>=0;
  const fmt=n=>validInt(n)?n.toLocaleString('en-US'):'—';
  const status=message=>{const e=el('progression-status');if(e)e.textContent=message;};
  function parseId(value){
    const text=String(value||'').trim();
    const m=/^(?:https:\/\/wardogstracker\.gg\/profile\/)?(7656119\d{10})\/?$/.exec(text);
    return m&&ID.test(m[1])?m[1]:null;
  }
  async function keyFor(id){
    const bytes=new TextEncoder().encode('1ADAAR:v1:'+id);
    const bytesHash=new Uint8Array(await crypto.subtle.digest('SHA-256',bytes));
    return Array.from(bytesHash,b=>b.toString(16).padStart(2,'0')).join('');
  }
  function blank(){
    root.OneADAARRoleRadar?.render(el('progression-role-radar'),null);
    root.OneADAARProgressionIntelligence?.render(null);
    for(const id of ['progression-wardog-level','progression-career-xp'])el(id).textContent='—';
    for(const id of ['progression-cash','progression-gold'])el(id).textContent='Hidden';
    el('progression-synced-at').textContent='Last Tracker sync: —';
    const rows=el('progression-role-values');
    if(rows){
      rows.replaceChildren();
      for(const role of roles){
        const tr=document.createElement('tr'),th=document.createElement('th');
        th.scope='row';th.textContent=role;
        const a=document.createElement('td'),b=document.createElement('td');
        a.textContent='—';b.textContent='—';tr.append(th,a,b);rows.append(tr);
      }
    }
  }
  function normalize(payload,id){
    const p=payload?.player,st=p?.stats;
    if(p?.steamId!==id||!st||!validInt(st.wardogLevel)||!validInt(st.careerXp)||
      !Number.isFinite(Date.parse(st.syncedAt)))return null;
    const levels={},xp={};
    for(const role of roles){
      const value=st.roles?.[role.toLowerCase()];
      if(!validInt(value?.level)||value.level>100||!validInt(value?.xp))return null;
      levels[role]=value.level;xp[role]=value.xp;
    }
    const known=n=>validInt(n)?n:null;
    return {sourceStatus:'verified',source:'WARDOGS Tracker public API',
      dataScope:'Published, synced account progression; not proof of account ownership',
      maxLevel:100,levels,xp,wardogLevel:st.wardogLevel,careerXp:st.careerXp,
      unlocks:known(st.unlocks),syncedAt:st.syncedAt,
      cash:known(st.cash),gold:known(st.gold),
      leaderboardRank:known(p.leaderboardRank),leaderboardPlayers:known(p.leaderboardPlayers),
      avatarUrl:typeof p.avatarUrl==='string'?p.avatarUrl:null};
  }
  function paint(record){
    root.OneADAARRoleRadar?.render(el('progression-role-radar'),record);
    root.OneADAARProgressionIntelligence?.render(record);
    el('progression-wardog-level').textContent=fmt(record.wardogLevel);
    el('progression-career-xp').textContent=fmt(record.careerXp);
    const economy=Boolean(el('tracker-public-economy')?.checked);
    el('progression-cash').textContent=economy?fmt(record.cash):'Hidden';
    el('progression-gold').textContent=economy?fmt(record.gold):'Hidden';
    el('progression-synced-at').textContent='Last Tracker sync: '+
      new Date(record.syncedAt).toLocaleString(undefined,{dateStyle:'medium',timeStyle:'short'});
    const rows=el('progression-role-values');rows.replaceChildren();
    for(const role of roles){
      const tr=document.createElement('tr'),th=document.createElement('th');
      th.scope='row';th.textContent=role;
      const lv=document.createElement('td'),xp=document.createElement('td');
      lv.textContent='Level '+record.levels[role];
      xp.textContent=fmt(record.xp[role])+' XP';
      tr.append(th,lv,xp);rows.append(tr);
    }
    const caption=rows.closest('table')?.querySelector('caption');
    if(caption)caption.textContent='Six roles · WARDOGS Tracker public record';
    status('Public Tracker record loaded. No Steam login was performed by 1ADAAR; this does not verify account ownership.');
  }
  async function load(input,remember){
    const id=parseId(input);
    if(!id){blank();status('Enter a valid SteamID64 or WARDOGS Tracker public profile URL.');return;}
    const thisSeq=++seq;
    if(active?.key && (await keyFor(id))!==active.key){
      blank();status('That public Tracker account does not match the selected WARCON player.');return;
    }
    if(remember)localStorage.setItem(PROFILE_KEY,id);
    else localStorage.removeItem(PROFILE_KEY);
    const submit=el('tracker-public-submit');submit.disabled=true;
    status('Reading your published WARDOGS Tracker progression…');
    try{
      const response=await fetch(api+'players/'+id,{credentials:'omit',cache:'no-store',
        referrerPolicy:'no-referrer',headers:{Accept:'application/json'}});
      if(thisSeq!==seq)return;
      if(response.status===404){blank();status('This account is private, unknown, or not synced on WARDOGS Tracker. Sync there and allow public profile access.');return;}
      if(response.status===429){status('Tracker is rate limiting requests; try again later.');return;}
      if(!response.ok)throw Error('Tracker API unavailable');
      const value=normalize(await response.json(),id);
      if(!value){blank();status('Tracker did not return complete public progression for this account. No values were guessed.');return;}
      paint(value);
      const community=el('tracker-community-controls');
      if(community)community.hidden=false;
    }catch(_){blank();status('Could not retrieve the public Tracker record. The Steam authentication Worker was not contacted.');}
    finally{submit.disabled=false;}
  }
  const serverId=/^[a-zA-Z0-9_-]{3,80}$|^[a-f0-9-]{36}$/;
  async function community(event){
    event.preventDefault();
    const server=el('tracker-community-server')?.value.trim()||'';
    const result=el('tracker-community-status');
    if(!serverId.test(server)){result.textContent='Enter a Tracker server slug, ID, or join code.';return;}
    const id=parseId(el('tracker-public-id')?.value);
    if(!id){result.textContent='Load a public player profile first.';return;}
    result.textContent='Checking community kill-feed coverage…';
    try{
      const url=api+'servers/'+encodeURIComponent(server)+'/leaderboard?range=7d&limit=100';
      const response=await fetch(url,{credentials:'omit',referrerPolicy:'no-referrer',cache:'no-store'});
      if(response.status===404){result.textContent='No connected public kill feed was found for this server. No match statistics can be recovered from the server list alone.';return;}
      if(!response.ok){result.textContent='Community leaderboard unavailable.';return;}
      const data=await response.json();
      const player=(Array.isArray(data.players)?data.players:[]).find(p=>p.steamId===id);
      if(!player){result.textContent='Server feed found, but this player is not in the returned top 100 for the last 7 days. This is not a zero-stat result.';return;}
      const summary=['Kills '+fmt(player.kills),'Deaths '+fmt(player.deaths),
        'K/D '+(Number.isFinite(player.kd)?player.kd.toFixed(2):'—'),
        'Headshots '+fmt(player.headshots),'Longest '+(Number.isFinite(player.longestKillM)?player.longestKillM+' m':'—')];
      result.textContent='Recorded community kills · last 7 days · '+summary.join(' · ');
    }catch(_){result.textContent='Community feed could not be reached. No missing play was inferred.';}
  }
  function mount(entry){
    const standalone=document.body.dataset.progressStandalone==='true';
    const host=el('progression-panel');
    const ok=standalone||Boolean(entry&&!entry.demo&&KEY.test(entry.key));
    host.hidden=!ok;if(!ok)return;
    active=standalone?null:entry;
    ++seq;blank();
    const saved=parseId(localStorage.getItem(PROFILE_KEY));
    const field=el('tracker-public-id');
    field.value=saved||'';
    el('tracker-public-remember').checked=Boolean(saved);
    el('tracker-community-controls').hidden=true;
    status('Load public Tracker progression without signing in through 1ADAAR.');
    if(saved)void load(saved,true);
  }
  const form=el('tracker-public-form');
  if(form)form.addEventListener('submit',e=>{e.preventDefault();void load(
    el('tracker-public-id').value,el('tracker-public-remember').checked);});
  el('tracker-public-clear')?.addEventListener('click',()=>{
    ++seq;localStorage.removeItem(PROFILE_KEY);el('tracker-public-id').value='';
    el('tracker-public-remember').checked=false;blank();
    el('tracker-community-controls').hidden=true;
    status('Saved public profile cleared from this browser.');
  });
  el('tracker-community-form')?.addEventListener('submit',community);
  root.OneADAARProgression=Object.freeze({mount});
})(window);
