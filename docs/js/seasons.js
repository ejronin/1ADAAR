'use strict';
/* Read-only GitHub Pages season/month browser. No per-visitor WARCON calls. */
(function(){
  const $=id=>document.getElementById(id),message=$('season-message');
  const form=$('season-filter'),season=$('season-choice'),month=$('month-choice');
  const list=$('season-list'),more=$('season-more');
  const seasons=new Map();
  let matches=[],shown=0;
  const amount=number=>Number.isSafeInteger(number)&&number>=0?number.toLocaleString():'—';
  const seasonOk=key=>typeof key==='string'&&/^[a-z0-9-]{1,64}$/.test(key);
  const monthOk=value=>typeof value==='string'&&/^\d{4}-\d{2}$/.test(value);
  const make=(parent,tag,text,className)=>{
    const el=document.createElement(tag);
    if(className)el.className=className;
    if(text!==undefined)el.textContent=String(text);
    parent.append(el);return el;
  };
  const dateOf=value=>{
    const t=Date.parse(value);
    return Number.isFinite(t)?new Date(t).toLocaleDateString(undefined,
      {year:'numeric',month:'short',day:'numeric',hour:'numeric',minute:'2-digit'}):'Date not available';
  };
  function addOption(parent,value,title){
    const option=document.createElement('option');option.value=value;option.textContent=title;parent.append(option);
  }
  function monthsFor(key,preferred){
    month.replaceChildren();
    const s=seasons.get(key);if(!s)return;
    for(const row of s.months){
      if(!monthOk(row.month))continue;
      const friendly=new Date(row.month+'-15T12:00:00Z').toLocaleDateString(
        undefined,{month:'long',year:'numeric'});
      addOption(month,row.month,friendly+' ('+amount(row.capturedMatches)+')');
    }
    if(preferred&&[...month.options].some(o=>o.value===preferred))month.value=preferred;
  }
  function renderNext(){
    const end=Math.min(matches.length,shown+20);
    for(;shown<end;shown++){
      const match=matches[shown];if(!match||!Number.isSafeInteger(match.id))continue;
      const card=make(list,'article',undefined,'season-match');
      const header=make(card,'div',undefined,'season-match-header');
      make(header,'strong','Match #'+match.id);
      make(header,'time',dateOf(match.endedAt)).dateTime=match.endedAt;
      const details=make(card,'div',undefined,'season-match-details');
      make(details,'span',match.map||'Map unavailable');
      make(details,'span',match.winner?'Winner: '+match.winner:'Winner not available');
      if(Array.isArray(match.scores)&&match.scores.length){
        make(card,'p',match.scores.slice(0,4).map(x=>
          String(x.name||'Unknown')+': '+String(x.score)).join(' · '),'season-scores');
      }
      const expected='https://console.warcon.app/s/e30a7ee9-7ea5-4633-882e-98d2e0c03342/matches/'+match.id;
      const a=make(card,'a','View completed match on WARCON ↗','season-match-link');
      a.href=expected;a.target='_blank';a.rel='noopener noreferrer';
    }
    more.hidden=shown>=matches.length;
  }
  async function show(){
    const s=seasons.get(season.value);
    const selected=s?.months.find(m=>m.month===month.value);
    if(!selected||!seasonOk(s.seasonKey)||!monthOk(selected.month)){
      message.hidden=false;message.textContent='Choose a season and month.';return;
    }
    const expected='data/seasons/'+s.seasonKey+'/'+selected.month+'.json';
    if(selected.file!==expected)throw Error('Invalid saved match path');
    message.hidden=false;message.textContent='Loading saved matches…';
    list.replaceChildren();shown=0;matches=[];more.hidden=true;
    const response=await fetch(expected,{cache:'no-store'});
    if(!response.ok)throw Error('Saved match file not available');
    const doc=await response.json();
    if(doc.schemaVersion!==1||doc.seasonKey!==s.seasonKey||doc.month!==selected.month||
       !Array.isArray(doc.matches))throw Error('Saved match data is invalid');
    matches=doc.matches.slice().sort((a,b)=>
      (b.endedAt||'').localeCompare(a.endedAt||'')||b.id-a.id);
    const params=new URLSearchParams();
    params.set('season',s.seasonKey);params.set('month',selected.month);
    history.replaceState(null,'','?'+params.toString());
    if(!matches.length){
      message.textContent='No completed matches saved for this month.';
      return;
    }
    message.hidden=true;
    renderNext();
  }
  form.addEventListener('submit',event=>{
    event.preventDefault();
    show().catch(()=>{
      message.hidden=false;message.textContent='These saved matches could not be loaded. Try again later.';
    });
  });
  season.addEventListener('change',()=>monthsFor(season.value));
  more.addEventListener('click',renderNext);
  (async()=>{
    try{
      const response=await fetch('data/seasons/index.json',{cache:'no-store'});
      if(!response.ok)throw Error('Archive index not available');
      const doc=await response.json();
      if(doc.schemaVersion!==1||doc.coverage!=='captured-only'||!Array.isArray(doc.seasons)){
        throw Error('Invalid archive index');
      }
      for(const row of doc.seasons){
        if(row&&seasonOk(row.seasonKey)&&Array.isArray(row.months)&&row.months.length){
          seasons.set(row.seasonKey,row);
          addOption(season,row.seasonKey,row.seasonName+' ('+amount(row.capturedMatches)+')');
        }
      }
      if(seasons.size===0){
        message.textContent='No completed matches saved yet. Older matches will appear here once WARCON results have been captured.';
        return;
      }
      const params=new URLSearchParams(location.search);
      const requested=params.get('season');
      if(seasons.has(requested))season.value=requested;
      else season.value=[...seasons.keys()][seasons.size-1];
      monthsFor(season.value,params.get('month'));
      form.hidden=false;
      await show();
    }catch(_){
      message.hidden=false;message.textContent='Saved match history is not available right now.';
    }
  })();
})();
