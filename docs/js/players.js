'use strict';
/* Public site: all identifiers are one-way lookup keys. Never render SteamID64 or Steam links. */
const $=id=>document.getElementById(id);
const publicState={players:[],matches:[],demoMatches:[],capped:false,ready:false};
const escapeFree=(tag,klass,value)=>{const el=document.createElement(tag);if(klass)el.className=klass;if(value!==undefined)el.textContent=String(value);return el;};
const num=value=>Number.isFinite(value)?Number(value).toLocaleString():'—';
const ratio=(a,b)=>!a&&!b?'—':(b? a/b:a).toFixed(2);
const percent=(part,total)=>total>0?`${(100*part/total).toFixed(1)}%`:'—';
const duration=minutes=>`${Math.floor(minutes/60)}h ${Math.round(minutes%60)}m`;
const dateText=stamp=>stamp?new Date(stamp).toLocaleDateString(undefined,{year:'numeric',month:'short',day:'numeric'}):'—';
const setMessage=s=>{$('lookup-message').textContent=s;$('lookup-message').hidden=false;};
function tile(label,value,note=publicState.selected?.demo?'DEMO / FICTIONAL':'All-time WARCON stats'){const el=escapeFree('div','metric-tile');el.append(escapeFree('span','',label),escapeFree('strong','',value),escapeFree('small','',note));return el;}
async function keyForSteamId(id){const data=new TextEncoder().encode(`1ADAAR:v1:${id}`);const hash=await crypto.subtle.digest('SHA-256',data);return Array.from(new Uint8Array(hash),c=>c.toString(16).padStart(2,'0')).join('');}
function profileMatches(key){return (publicState.selected?.demo?publicState.demoMatches:publicState.matches).filter(m=>(m.players||[]).some(p=>p.key===key)).sort((a,b)=>new Date(b.endedAt)-new Date(a.endedAt));}
function breakdown(items,field,parentId) {
 const parent=$(parentId);parent.replaceChildren();const groups=new Map();
 for(const match of items) {
   const p=(match.players||[]).find(player=>player.key===publicState.selected?.key);
   if(!p)continue;
   const label=field==='map'?match.map:p.faction||'Unassigned';
   const stats=groups.get(label)||{matches:0,wins:0,known:0};
   stats.matches++;
   if(['win','loss','draw'].includes(p.result)){stats.known++;if(p.result==='win')stats.wins++;}
   groups.set(label,stats);
 }
 if(!groups.size) {parent.append(escapeFree('div','empty-insight','No saved completed matches for this player yet.'));return;}
 for(const [label,row] of [...groups].sort((a,b)=>b[1].matches-a[1].matches||a[0].localeCompare(b[0]))) {
   const item=escapeFree('div','breakdown-row');
   if(field==='faction') {
      const faction=window.OneADAARFactions.identify(label);
      if(faction)item.style.setProperty('--faction-accent',faction.color);
   }
   const left=escapeFree('div');
   if(field==='faction')left.append(window.OneADAARFactions.label(label));
   else left.append(escapeFree('strong','',label));
   const bar=escapeFree('div','mini-meter');
   bar.setAttribute('role','img');
   bar.setAttribute('aria-label',label+' win rate: '+(row.known?percent(row.wins,row.known):'not recorded'));
   const fill=escapeFree('i');fill.style.width=row.known?100*row.wins/row.known+'%':'0%';
   bar.append(fill);left.append(bar);
   item.append(left,escapeFree('span','',row.matches+' matches'),
     escapeFree('em','',row.known?percent(row.wins,row.known)+' wins ('+row.wins+'/'+row.known+')':'Result unavailable'));
   parent.append(item);
 }
}
function recentTable(matches,key){const wrap=$('recent-match-table');wrap.replaceChildren();if(!matches.length){wrap.append(escapeFree('div','empty-insight','This player’s recent matches will show here after we save completed results.'));return;}const table=escapeFree('table','recent-table'),thead=document.createElement('thead'),tr=document.createElement('tr');['Date','Map','Faction','Result','K','D','Time'].forEach(h=>tr.append(escapeFree('th','',h)));thead.append(tr);table.append(thead);const tbody=document.createElement('tbody');for(const m of matches.slice(0,15)){const p=m.players.find(x=>x.key===key),row=document.createElement('tr');row.append(escapeFree('td','',dateText(m.endedAt)));const map=document.createElement('td');if(publicState.selected?.demo){map.append(escapeFree('span','',m.map));}else{const link=escapeFree('a','',m.map);link.href=`index.html#match-${Number(m.id)}`;map.append(link);}row.append(map);const factionCell=document.createElement('td');factionCell.append(window.OneADAARFactions.label(p.faction||'—'));row.append(factionCell);row.append(escapeFree('td',p.result?'result-'+p.result:'result-unknown',(p.result||'Not recorded').toUpperCase()));row.append(escapeFree('td','',p.kills),escapeFree('td','',p.deaths),escapeFree('td','',`${Math.floor(p.seconds/60)}m`));tbody.append(row);}table.append(tbody);wrap.append(table);}
/* Cache history by the first hex nibble so only one small shard loads per player. */
const historyCache=new Map();
function loadCareer(key) {
  if(!/^[a-f0-9]{64}$/.test(key))return Promise.resolve([]);
  const shard=key[0];
  if(!historyCache.has(shard)){
    historyCache.set(shard,fetch('data/history/'+shard+'.json',{cache:'no-store'})
      .then(response=>response.ok?response.json():{players:{}})
      .catch(()=>({players:{}})));
  }
  return historyCache.get(shard).then(doc=>
    doc&&doc.schemaVersion===1&&doc.players&&Array.isArray(doc.players[key])?doc.players[key]:[]);
}
function openProfile(entry){publicState.selected=entry;const detailed=$('map-team-details');detailed.hidden=!!entry.demo||!(/^[a-f0-9]{64}$/.test(entry.key));if(!detailed.hidden)detailed.href='map-team.html?player='+encodeURIComponent(entry.key);$('demo-warning').hidden=!entry.demo;$('profile-source-text').textContent=entry.demo?'SAMPLE PLAYER / MADE-UP STATS':'PLAYER STATS / FROM WARCON';$('lookup-results').hidden=true;$('dossier').hidden=false;$('lookup-message').hidden=true;$('dossier-title').textContent=entry.name;$('share-player').textContent='↗ Share '+(entry.name.length>28?entry.name.slice(0,25)+'…':entry.name)+' stats';$('share-player').setAttribute('aria-label','Share '+entry.name+' stats');$('profile-subtitle').textContent=entry.demo?`SAMPLE PLAYER • Made-up stats • Example ranking #${num(entry.rank)}`:`WARDOGS server • All-time WARCON stats • Player ranking #${num(entry.rank)}`;
 window.OneADAARProfile.career($('profile-metrics'),$('profile-secondary'),entry);
 window.OneADAARProfile.avatar($('player-avatar'),entry);
 $('player-avatar').setAttribute('aria-label','Player profile picture for '+entry.name+', or initials if unavailable');
 const combat=$('combat-panel');combat.hidden=!entry.hasFeed;const box=$('combat-metrics');box.replaceChildren();if(entry.hasFeed){
   for(const [label,value] of [['Headshots',entry.headshots],['Vehicle kills',entry.vehicleKills],
                                ['Best kill streak',entry.killStreak],['Team kills',entry.teamKills]]) {
     if(Number.isSafeInteger(value)&&value>=0)box.append(tile(label,num(value),'WARCON · confirmed feed'));
   }
   combat.hidden=box.children.length===0;
 }
 $('player-share-status').hidden=true;const recent=profileMatches(entry.key);
 window.OneADAARPerformance.mount($('performance-module'),{key:entry.key,matches:recent,career:[],demo:false});
 loadCareer(entry.key).then(points=>{
   if(publicState.selected?.key!==entry.key)return;
   window.OneADAARPerformance.mount($('performance-module'),{key:entry.key,matches:recent,career:points,demo:false});
 });
window.OneADAARProfile.snapshot($('player-snapshot'),entry,recent);
 breakdown(recent,'map','map-breakdown');breakdown(recent,'faction','faction-breakdown');recentTable(recent,entry.key);
 if(!entry.demo)history.replaceState(null,'',`#player-${entry.key}`);$('dossier').scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});
}
function showCandidates(rows){$('lookup-results').hidden=false;$('dossier').hidden=true;$('lookup-message').hidden=true;const list=$('player-candidates');list.replaceChildren();for(const entry of rows.slice(0,40)){const btn=escapeFree('button','candidate');btn.type='button';btn.append(escapeFree('strong','',entry.name),escapeFree('small','',`${num(entry.kills)} kills · ${num(entry.matches)} matches · rank #${num(entry.rank)}`));btn.addEventListener('click',()=>openProfile(entry));list.append(btn);}if(rows.length>40)list.append(escapeFree('p','empty-insight','Showing the first 40 matches. Refine the name to narrow your search.'));$('lookup-results').scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});}
async function submitLookup(event){event.preventDefault();if(!publicState.ready){setMessage('Player stats are still loading.');return;}const input=$('player-query'),query=input.value.trim();if(!query)return;let hits=[];if(/^\d{17}$/.test(query)){input.value='';const key=await keyForSteamId(query);hits=publicState.players.filter(p=>p.key===key);}else{hits=publicState.players.filter(p=>p.name.toLocaleLowerCase().includes(query.toLocaleLowerCase()));}
if(!hits.length){$('dossier').hidden=true;$('lookup-results').hidden=true;setMessage('We couldn’t find that player. Check the spelling, or try WARCON’s player rankings. This search includes up to 1,000 players.');return;}if(hits.length===1)openProfile(hits[0]);else showCandidates(hits);}
async function init(){try{const [playerRes,matchRes]=await Promise.all([fetch('data/players.json',{cache:'no-store'}),fetch('data/matches.json',{cache:'no-store'})]);if(!playerRes.ok||!matchRes.ok)throw Error('Data unavailable');const [index,matchData]=await Promise.all([playerRes.json(),matchRes.json()]);if(!Array.isArray(index.players)||!Array.isArray(matchData.matches))throw Error('Unexpected schema');publicState.players=index.players;publicState.matches=matchData.matches;publicState.capped=index.capped;publicState.ready=true;setMessage(`${num(index.players.length)} players found on WARCON. Search by name or SteamID64 to view their stats. ${index.capped?'Only the top 1,000 players are included.':''}`);
const incoming=/^#player-([a-f0-9]{64})$/.exec(location.hash);if(incoming){const match=index.players.find(p=>p.key===incoming[1]);if(match)openProfile(match);else setMessage('This player isn’t in the current search results. Try searching their name or checking WARCON. Only the top 1,000 ranked players are included.');}
}catch(_){setMessage('We couldn’t load player stats. Please try again after the next update.');}}

$('share-player').addEventListener('click',()=>{const entry=publicState.selected;if(!entry||entry.demo||!(/^[a-f0-9]{64}$/.test(entry.key)))return;const url=new URL(`players.html#player-${entry.key}`,location.href).href;window.OneADAARShare.share(url,`WARDOGS stats: ${entry.name} — 1ADAAR`,$('player-share-status'),{
  intro:'🐺 Check out my stats on the OneAverageDan WARDOGS Community Server!\n\n📊 View my 1ADAAR player profile:',
  outro:'🎮 Join the 1AD Discord: https://discord.gg/e9B69UkE53'
});});
$('player-search').addEventListener('submit',submitLookup);$('new-search').addEventListener('click',()=>{$('dossier').hidden=true;$('lookup-results').hidden=true;setMessage('Enter an in-game name or SteamID64 to search again.');history.replaceState(null,'','players.html');$('player-query').focus();});init();
