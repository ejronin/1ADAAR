'use strict';
/* Public, read-only weekly results. DOM textContent protects player names. */
(async function () {
  const message=document.getElementById('weekly-message');
  const summary=document.getElementById('weekly-summary');
  const history=document.getElementById('weekly-history');
  const add=(parent,tag,className,text)=>{
    const e=document.createElement(tag);
    if(className)e.className=className;
    if(text!==undefined)e.textContent=String(text);
    parent.append(e);return e;
  };
  const displayDate=value=>{
    const t=new Date(value+'T12:00:00Z');
    return Number.isFinite(t.getTime())?
      t.toLocaleDateString(undefined,{year:'numeric',month:'long',day:'numeric'}):value;
  };
  function metric(parent,title,value){
    const x=add(parent,'div','weekly-metric');
    add(x,'span','',title);add(x,'strong','',value);
  }
  function awards(parent,rows){
    const labels={
      mostMatches:'Most matches played',mostKills:'Most kills',
      mostWins:'Most wins',mostPlaytime:'Most time played',
      mostHeadshots:'Most headshots',longestShot:'Longest shot'
    };
    const entries=Object.entries(labels).filter(([key])=>rows[key]&&rows[key].name);
    if(!entries.length)return;
    add(parent,'h5','','Recorded match leaders');
    const cards=add(parent,'div','weekly-awards');
    for(const [key,label] of entries){
      const a=rows[key],tile=add(cards,'div','weekly-award');
      add(tile,'span','',label);add(tile,'strong','',a.name);
      const value=key==='mostPlaytime'?
        Math.round(a.value/60)+' minutes':
        a.value+' '+(key==='longestShot'?'meters':a.unit||'');
      add(tile,'small','',value);
    }
  }
  async function season(parent,entry){
    const path=entry.file;
    if(typeof path!=='string'||!/^data\/weekly\/[a-z0-9-]+\/\d{4}-\d{2}-\d{2}\.json$/.test(path)){
      throw Error('Unknown weekly report file');
    }
    const response=await fetch(path,{cache:'no-store'});
    if(!response.ok)throw Error('Weekly report unavailable');
    const data=await response.json();
    if(!data||data.schemaVersion!==1||data.seasonKey!==entry.seasonKey)throw Error('Invalid weekly report');
    const panel=add(parent,'section','weekly-season');
    const h=add(panel,'h4','',data.seasonName);
    h.setAttribute('aria-label','Results for '+data.seasonName);
    add(panel,'p','weekly-caveat','These results only include completed matches we saved. Other matches may be missing.');
    const metrics=add(panel,'div','weekly-metrics');
    metric(metrics,'Matches saved',data.completedMatchesInArchive);
    metric(metrics,'Different players recorded',data.uniqueRecordedPlayers);
    awards(panel,data.awards||{});
    if(Array.isArray(data.factions)&&data.factions.length){
      add(panel,'h5','','Teams played');
      const list=add(panel,'ul','weekly-list');
      for(const f of data.factions.slice(0,8)){
        const item=add(list,'li');
        add(item,'span','',f.name);
        add(item,'strong','',f.appearances+' player appearances');
      }
    }
    if(Array.isArray(data.maps)&&data.maps.length){
      add(panel,'h5','','Maps played');
      const list=add(panel,'ul','weekly-list');
      for(const m of data.maps.slice(0,7)){
        const item=add(list,'li');
        add(item,'span','',m.name);
        add(item,'strong','',m.matches+' matches');
      }
    }
  }
  try {
    const response=await fetch('data/weekly/index.json',{cache:'no-store'});
    if(!response.ok)throw Error('Weekly history unavailable');
    const index=await response.json();
    if(index.schemaVersion!==1||!Array.isArray(index.weeks))throw Error('Invalid weekly index');
    if(index.weeks.length===0){
      message.textContent='No weekly results yet. We’ll add the first roundup after completed matches are saved.';
      return;
    }
    const requested=new URLSearchParams(location.search).get('week');
    const selected=/^\d{4}-\d{2}-\d{2}$/.test(requested||'')?
      index.weeks.find(w=>w.weekEnding===requested):null;
    const week=selected||index.weeks[0];
    if(!week||!Array.isArray(week.seasons))throw Error('Invalid weekly entry');
    message.hidden=true;
    const overview=add(summary,'section','weekly-overview');
    add(overview,'h3','','Week ending '+displayDate(week.weekEnding));
    add(overview,'p','','Only matches saved in 1ADAAR are counted. Each WARDOGS season is shown separately.');
    add(overview,'span','weekly-count',week.completedMatchesSaved);
    add(overview,'span','weekly-count-label','completed matches saved');
    for(const entry of week.seasons)await season(summary,entry);
    add(history,'h3','','Earlier weeks');
    const links=add(history,'div','weekly-week-links');
    for(const item of index.weeks){
      const a=add(links,'a','',displayDate(item.weekEnding));
      a.href='weekly.html?week='+encodeURIComponent(item.weekEnding);
      if(item.weekEnding===week.weekEnding)a.setAttribute('aria-current','page');
    }
  } catch (_) {
    message.hidden=false;
    message.textContent='We couldn’t load this week’s results. Try again later or view the match history.';
    const a=add(message,'a','',' View match history →');
    a.href='index.html#reports';
  }
})();
