'use strict';
/* Public aggregated server match-start heatmap; NOT session-level player activity. */
(function(){
  const el=id=>document.getElementById(id);
  const season=el('act-season'),status=el('act-status'),out=el('act-results');
  const tableHost=el('act-grid'),details=el('act-cell');
  const days=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];
  const emptyHost=el('act-empty-structure'),emptyMatrix=el('act-empty-matrix');
  if(emptyMatrix){
    for(const day of days){
      const row=document.createElement('div');row.className='ia-home-hour-row';
      const label=document.createElement('span');label.className='ia-home-day';
      label.textContent=day.slice(0,3);row.append(label);
      for(let hour=0;hour<24;hour++){
        const slot=document.createElement('span');slot.className='ia-home-hour-cell';
        slot.dataset.level='0';row.append(slot);
      }
      emptyMatrix.append(row);
    }
    if(window.OneADAARActivity)window.OneADAARActivity.axis(emptyMatrix);
  }
  const counts=x=>Number.isSafeInteger(x)&&x>=0;
  let documentData=null;
  function node(parent,tag,value,cls){
    const n=document.createElement(tag);
    if(cls)n.className=cls;
    if(value!==undefined)n.textContent=String(value);
    parent.append(n);return n;
  }
  function timeLabel(h){
    const hour=h%12||12;
    return hour+(h<12?' AM':' PM');
  }
  function stamp(value){
    if(typeof value!=='string')return 'Not recorded';
    const ms=Date.parse(value);
    if(!Number.isFinite(ms))return 'Not recorded';
    return new Intl.DateTimeFormat('en-US',{month:'short',day:'numeric',year:'numeric',
      hour:'numeric',minute:'2-digit',timeZone:'America/New_York',timeZoneName:'short'})
      .format(new Date(ms));
  }
  function valid(group){
    return group&&/^(all|[a-z0-9-]{1,64})$/.test(group.key)&&
      counts(group.count)&&Array.isArray(group.byWeekdayAndHour)&&
      group.byWeekdayAndHour.length===7&&group.byWeekdayAndHour.every(row=>
        Array.isArray(row)&&row.length===24&&row.every(counts))&&
      group.byWeekdayAndHour.flat().reduce((sum,num)=>sum+num,0)===group.count;
  }
  function change(){
    if(!documentData)return;
    const group=documentData.seasons.find(row=>row.key===season.value);
    if(!group)return;
    const summaryNode=el('act-summary-values'),summaryEmpty=el('act-summary-empty');
    const summaryDisclosure=el('act-summary-disclosure');
    const hasSummary=window.OneADAARActivity&&
      window.OneADAARActivity.render(summaryNode,group.byWeekdayAndHour);
    summaryNode.hidden=!hasSummary;
    summaryEmpty.hidden=Boolean(hasSummary);
    summaryDisclosure.hidden=!hasSummary;
    tableHost.replaceChildren();details.textContent='Select a square to inspect its recorded count.';
    el('act-count').textContent=group.count.toLocaleString();
    el('act-first').textContent=stamp(group.firstMatchStartedAt);
    el('act-last').textContent=stamp(group.lastMatchStartedAt);
    if(!group.count){
      status.hidden=true;
      out.hidden=true;
      if(emptyHost)emptyHost.hidden=false;
      return;
    }
    status.hidden=true;out.hidden=false;
    if(emptyHost)emptyHost.hidden=true;
    const max=Math.max(1,...group.byWeekdayAndHour.flat());
    const grid=node(tableHost,'table',undefined,'act-grid-table');
    const top=node(grid,'thead'),heading=node(top,'tr');
    node(heading,'th','Day').scope='col';
    for(let hour=0;hour<24;hour++){
      const th=node(heading,'th',hour%6===0?String(hour).padStart(2,'0')+':00':'');
      if(hour%6===0)th.className='act-major-hour';
      th.scope='col';th.title=timeLabel(hour)+' Eastern';
    }
    const body=node(grid,'tbody');
    let selected=null;
    for(let day=0;day<7;day++){
      const row=node(body,'tr'),label=node(row,'th',days[day].slice(0,3),'act-day');
      label.scope='row';
      for(let hour=0;hour<24;hour++){
        const cell=node(row,'td');
        if(hour%6===0)cell.className='act-major-hour-cell';
        const count=group.byWeekdayAndHour[day][hour];
        const b=node(cell,'button',undefined,'act-cell');
        b.type='button';b.dataset.level=String(count?Math.max(1,Math.ceil(4*count/max)):0);
        b.setAttribute('aria-pressed','false');
        const spoken=days[day]+' '+timeLabel(hour)+' Eastern: '+count+
          ' captured completed match'+(count===1?'':'es')+' started.';
        b.setAttribute('aria-label',spoken);
        b.title=spoken;
        b.addEventListener('click',()=>{
          if(selected)selected.setAttribute('aria-pressed','false');
          selected=b;b.setAttribute('aria-pressed','true');
          details.textContent=spoken+' These are saved match starts—not player sessions or hours played.';
        });
      }
    }
  }
  (async()=>{
    try{
      const response=await fetch('data/recorded-activity.json',{cache:'no-store'});
      if(!response.ok)throw Error('Captured-match report not available');
      const json=await response.json();
      if(!json||json.schemaVersion!==1||json.scope!=='server'||
          json.coverage!=='captured-only'||json.timestampField!=='startedAt'||
          json.timezone!=='America/New_York'||!Array.isArray(json.seasons)||
          !json.seasons.length||!json.seasons.every(valid)){
        throw Error('Captured-match report has an unexpected schema');
      }
      documentData=json;
      season.replaceChildren();
      for(const scope of json.seasons){
        const option=node(season,'option',scope.name+' ('+scope.count.toLocaleString()+')');
        option.value=scope.key;
      }
      season.disabled=false;
      season.addEventListener('change',change);
      const requested=new URLSearchParams(location.search).get('season');
      if(requested&&documentData.seasons.some(s=>s.key===requested))season.value=requested;
      change();
    }catch(error){
      status.hidden=false;
      status.textContent='Verified match activity could not be loaded. Please try again later.';
      season.disabled=true;out.hidden=true;
      if(emptyHost)emptyHost.hidden=false;
      const emptyNotice=el('act-summary-empty');if(emptyNotice){
        emptyNotice.hidden=false;
        emptyNotice.textContent='Recorded activity data is temporarily unavailable.';
      }
      el('act-summary-values').hidden=true;
      el('act-summary-disclosure').hidden=true;
    }
  })();
})();
