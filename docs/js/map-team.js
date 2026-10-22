'use strict';
/* v2 player map/team drill-down. Reads one precomputed public shard, no live API. */
(function(){
  const $=id=>document.getElementById(id);
  const message=$('mt-message'),view=$('mt-view'),season=$('mt-season'),sort=$('mt-sort');
  const mapChoice=$('mt-combo-map'),teamChoice=$('mt-combo-faction');
  const KEY=/^[a-f0-9]{64}$/;
  const playerId=new URLSearchParams(location.search).get('player')||'';
  const known=n=>Number.isSafeInteger(n)&&n>=0;
  const number=n=>known(n)?n.toLocaleString():'—';
  const minutes=seconds=>known(seconds)?Math.round(seconds/60).toLocaleString()+' min':'—';
  const winPct=n=>typeof n==='number'&&Number.isFinite(n)&&n>=0&&n<=1?
    (100*n).toFixed(1)+'%':'—';
  const kd=n=>typeof n==='number'&&Number.isFinite(n)&&n>=0?n.toFixed(2):'—';
  let entry=null;
  const make=(parent,tag,value,cls)=>{
    const el=document.createElement(tag);
    if(cls)el.className=cls;
    if(value!==undefined)el.textContent=String(value);
    parent.append(el);return el;
  };
  const scope=()=>entry?.scopes?.[season.value]||null;
  const option=(select,value,label)=>{
    const el=make(select,'option',label);
    el.value=value;return el;
  };
  function updateLink(){
    const params=new URLSearchParams({player:playerId,season:season.value});
    history.replaceState(null,'','?'+params.toString());
  }
  function statBox(label,value,note){
    const item=make($('mt-summary'),'div',undefined,'mt-summary-card');
    make(item,'span',label);make(item,'strong',value);
    if(note)make(item,'small',note);
  }
  function ring(parent,rate,label,color,caption){
    const wrap=make(parent,'div',undefined,'mt-team-group');
    const holder=make(wrap,'div',undefined,'mt-ring');
    const valid=typeof rate==='number'&&Number.isFinite(rate)&&rate>=0&&rate<=1;
    const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
    svg.setAttribute('viewBox','0 0 120 120');
    svg.setAttribute('class','mt-donut-svg');
    svg.setAttribute('role','img');
    svg.setAttribute('aria-label',label+': '+(valid?winPct(rate):'no recorded data')+
      (caption?' · '+caption:''));
    const circle=(cls)=>{
      const el=document.createElementNS('http://www.w3.org/2000/svg','circle');
      el.setAttribute('class',cls);
      el.setAttribute('cx','60');el.setAttribute('cy','60');
      el.setAttribute('r','45');el.setAttribute('pathLength','100');
      svg.append(el);return el;
    };
    circle('mt-donut-track');
    const fill=circle('mt-donut-fill');
    fill.style.stroke=color;
    fill.setAttribute('stroke-dasharray',(valid?(rate*100).toFixed(2):'0')+' 100');
    holder.append(svg);
    const value=make(holder,'strong',valid?Math.round(rate*100)+'%':'—');
    value.setAttribute('aria-hidden','true');
    if(label)make(wrap,'div',label,'mt-ring-caption');
    if(caption)make(wrap,'small',caption);
  }
  function sortRows(rows){
    const kind=sort.value;
    return [...rows].sort((a,b)=>{
      const value=x=>kind==='rate'?(x.winRate??-1):kind==='kills'?x.kills:
        kind==='seconds'?x.seconds:x.matches;
      return value(b)-value(a)||
        (b.knownOutcomes||0)-(a.knownOutcomes||0)||
        (a.name||a.map||'').localeCompare(b.name||b.map||'');
    });
  }
  function bars(target,rows,team){
    const host=$(target);host.replaceChildren();
    if(!rows.length){make(host,'p','No saved completed-match data for this section.','mt-empty');return;}
    const sorted=sortRows(rows);
    for(const record of sorted){
      const card=make(host,'article',undefined,'mt-data-row');
      const first=make(card,'div');
      const title=make(first,'div',undefined,'mt-row-name');
      if(team&&window.OneADAARFactions)title.append(window.OneADAARFactions.label(record.name));
      else title.textContent=record.name;
      if(!team&&window.OneADAARMapBanners)
        window.OneADAARMapBanners.decorateMapRow(card,record.name);
      make(first,'div',number(record.matches)+' saved matches','mt-row-meta');
      if(team&&window.OneADAARFactions){
        const faction=window.OneADAARFactions.identify(record.name);
        if(faction)card.style.setProperty('--map-accent',faction.color);
      }
      const center=make(card,'div',undefined,'mt-row-bar');
      const track=make(center,'div',undefined,'mt-row-track');
      const fill=make(track,'div',undefined,'mt-row-fill');
      fill.style.width=record.winRate===null||record.winRate===undefined?'0%':
        Math.max(0,Math.min(100,record.winRate*100))+'%';
      make(center,'div',winPct(record.winRate)+' recorded win rate · '+
        number(record.wins)+' wins / '+number(record.losses)+' losses / '+
        number(record.draws)+' draws','mt-row-rate');
      const numbers=make(card,'div',undefined,'mt-row-numbers');
      make(numbers,'div','Kills '+number(record.kills)+' · Deaths '+number(record.deaths));
      make(numbers,'div','K/D '+kd(record.kd)+' · '+minutes(record.seconds));
      if(record.unknownOutcomes)make(numbers,'div',number(record.unknownOutcomes)+' results not recorded');
    }
  }
  function mapKdDots(rows){
    const host=$('mt-kd-plot');if(!host)return;
    host.replaceChildren();
    const list=(Array.isArray(rows)?rows:[]).filter(r=>
      r&&typeof r.name==='string'&&known(r.kills)&&known(r.deaths)&&known(r.matches)&&r.matches>0)
      .map(r=>({...r,aggregate:r.deaths>0?r.kills/r.deaths:null}));
    if(!list.length){make(host,'p','No completed, recorded per-map kills and deaths yet.','mt-empty');return;}
    const peak=Math.max(1,...list.map(r=>r.aggregate??0));
    for(const r of [...list].sort((a,b)=>(b.aggregate??-1)-(a.aggregate??-1))){
      const line=make(host,'div',undefined,'mt-kd-item');
      make(line,'strong',r.name,'mt-kd-label');
      const track=make(line,'div',undefined,'mt-kd-track');
      const dot=make(track,'span',undefined,'mt-kd-dot');
      if(r.aggregate===null){dot.hidden=true;}else{dot.style.left=(r.aggregate/peak*100)+'%';}
      const caption=r.aggregate===null?'— (zero recorded deaths)':r.aggregate.toFixed(2);
      make(line,'span',caption+' K/D · '+number(r.matches)+' matches','mt-kd-value');
      line.setAttribute('aria-label',r.name+': '+caption+' K/D from '+
        r.kills+' kills and '+r.deaths+' deaths over '+r.matches+' recorded matches'+
        (r.deaths===0?' (ratio undefined)':''));
    }
  }
  function fillChoice(select,values,first){
    select.replaceChildren();option(select,'',first);
    for(const name of [...new Set(values)].sort((a,b)=>a.localeCompare(b)))option(select,name,name);
  }
  function fillCombinationTable(){
    const body=$('mt-combinations');body.replaceChildren();
    const data=scope();
    if(!data)return;
    const mapFilter=mapChoice.value,teamFilter=teamChoice.value;
    const rows=sortRows((data.combinations||[]).filter(x=>
      (!mapFilter||x.map===mapFilter)&&(!teamFilter||x.faction===teamFilter)));
    if(!rows.length){
      const tr=make(body,'tr');const td=make(tr,'td','No saved matches match these filters.');
      td.colSpan=7;return;
    }
    for(const x of rows){
      const tr=make(body,'tr');
      make(tr,'td',x.map);
      const faction=make(tr,'td');
      if(window.OneADAARFactions)faction.append(window.OneADAARFactions.label(x.faction));
      else faction.textContent=x.faction;
      for(const value of [number(x.matches),
        number(x.wins)+' / '+number(x.losses)+' / '+number(x.draws),
        winPct(x.winRate),number(x.kills)+' / '+number(x.deaths),minutes(x.seconds)]){
        make(tr,'td',value);
      }
    }
  }
  function render(){
    const data=scope();
    if(!data){message.hidden=false;message.textContent='There are no saved results for this season.';view.hidden=true;return;}
    view.hidden=false;message.hidden=true;
    updateLink();
    const total=data.total||{};
    $('mt-summary').replaceChildren();
    statBox('Matches saved',number(total.matches),'Completed matches with this player recorded');
    statBox('Maps recorded',number(data.uniqueMaps),'Maps we can name from saved matches');
    statBox('Recorded win rate',winPct(total.winRate),
      number(total.knownOutcomes)+' matches with a known player result');
    const best=data.bestMap;
    statBox('Best recorded map',best?(best.tied?'Tied: '+best.names.join(', '):best.name):
      'Not enough matches yet','At least 5 matches with known outcomes per map');
    $('mt-win-ring').replaceChildren();
    ring($('mt-win-ring'),total.winRate,'Wins from recorded results','#74df9d',
      number(total.wins)+' wins from '+number(total.knownOutcomes)+' known results');
    const rings=$('mt-team-rings');rings.replaceChildren();
    const knownTeams=[['Lonestar','#465eff'],['Valkyra','#ee4138'],['Manticore','#3eba42']];
    const available=(data.factions||[]).filter(f=>knownTeams.some(t=>t[0]===f.name))
      .reduce((sum,f)=>sum+f.matches,0);
    for(const [name,color] of knownTeams){
      const item=(data.factions||[]).find(f=>f.name===name);
      const share=available>0?(item?.matches||0)/available:null;
      ring(rings,share,name,color,number(item?.matches||0)+' saved appearances');
    }
    mapKdDots(data.maps||[]);
    bars('mt-maps',data.maps||[],false);
    bars('mt-factions',data.factions||[],true);
    fillChoice(mapChoice,(data.maps||[]).map(x=>x.name),'All maps');
    fillChoice(teamChoice,(data.factions||[]).map(x=>x.name),'All teams');
    fillCombinationTable();
  }
  season.addEventListener('change',render);
  sort.addEventListener('change',()=>{
    const data=scope();if(!data)return;
    bars('mt-maps',data.maps||[],false);bars('mt-factions',data.factions||[],true);
    fillCombinationTable();
  });
  $('mt-combo-filters').addEventListener('change',fillCombinationTable);
  $('mt-combo-filters').addEventListener('submit',event=>event.preventDefault());
  $('mt-filters').addEventListener('submit',event=>event.preventDefault());
  (async()=>{
    if(!KEY.test(playerId)){
      message.textContent='Choose a player from Find a player to see their map and team results.';
      return;
    }
    $('mt-back').href='players.html#player-'+playerId;
    try{
      const idxRes=await fetch('data/map-team/index.json',{cache:'no-store'});
      if(!idxRes.ok)throw Error('Map and team index unavailable');
      const index=await idxRes.json();
      if(index.schemaVersion!==1||index.coverage!=='captured-only')throw Error('Invalid summary source');
      if(!index.capturedMatches){
        message.textContent='No completed matches saved yet. Map and team results will appear when genuine WARCON matches are recorded.';
        return;
      }
      const response=await fetch('data/map-team/'+playerId[0]+'.json',{cache:'no-store'});
      if(!response.ok)throw Error('Player summary unavailable');
      const shard=await response.json();
      if(shard.schemaVersion!==1||shard.coverage!=='captured-only')throw Error('Invalid summary shard');
      entry=shard.players?.[playerId]||null;
      if(!entry||!entry.scopes?.all){
        message.textContent='No saved completed matches include this player yet.';
        return;
      }
      $('mt-player-name').textContent=entry.name;
      document.title='Map & Team Results: '+entry.name+' — 1ADAAR';
      option(season,'all','All saved seasons');
      for(const row of index.officialSeasons||[]){
        if(entry.scopes[row.key])option(season,row.key,row.name);
      }
      const requested=new URLSearchParams(location.search).get('season');
      if(requested&&entry.scopes[requested])season.value=requested;
      render();
    }catch(_){
      message.textContent='We could not load these saved results. Try again later or return to the player profile.';
    }
  })();
})();
