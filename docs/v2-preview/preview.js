'use strict';
/* 1ADAAR V2 VISUAL CONCEPT ONLY. Every number and name is fictional.
   No WARCON or Discord requests; no identities or private identifiers. */
(function(){
  const nav=[...document.querySelectorAll('[data-target]')];
  const views=['profile','maps','weekly'];
  const titles={profile:'PLAYER PROFILE',maps:'MAP & TEAM RESULTS',weekly:'WEEKLY ROUNDUP'};
  function show(target,updateHash=true){
    if(!views.includes(target))target='profile';
    for(const name of views){
      const section=document.getElementById('view-'+name);
      if(section)section.hidden=name!==target;
    }
    for(const button of nav){
      const active=button.dataset.target===target;
      button.classList.toggle('selected',active);
      button.setAttribute('aria-pressed',active?'true':'false');
    }
    const crumb=document.getElementById('breadcrumb');
    if(crumb)crumb.textContent=titles[target];
    if(updateHash)history.replaceState(null,'','#'+target);
    window.scrollTo({top:0,behavior:'instant'});
  }
  for(const button of nav)button.addEventListener('click',()=>show(button.dataset.target));
  for(const button of document.querySelectorAll('.go-maps'))button.addEventListener('click',()=>show('maps'));
  window.addEventListener('hashchange',()=>show(location.hash.slice(1),false));
  show(location.hash.slice(1),false);

  const maps=[
    {name:'Bakurani',matches:9,wins:6,losses:3,kills:143,time:'7h 30m',color:'#63d89f'},
    {name:'Ozeti',matches:8,wins:4,losses:4,kills:118,time:'6h 40m',color:'#ac87e3'},
    {name:'Zestafona',matches:7,wins:4,losses:3,kills:101,time:'5h 50m',color:'#e9a65a'}
  ];
  const factions=[
    {name:'Lonestar',matches:15,wins:9,losses:6,kills:211,time:'12h 30m',color:'#465eff',icon:'../assets/factions/lonestar.svg'},
    {name:'Valkyra',matches:6,wins:3,losses:3,kills:102,time:'5h 0m',color:'#ee4138',icon:'../assets/factions/valkyra.svg'},
    {name:'Manticore',matches:3,wins:2,losses:1,kills:49,time:'2h 30m',color:'#3eba42',icon:'../assets/factions/manticore.svg'}
  ];
  const combos=[
    {map:'Bakurani',team:'Lonestar',matches:5,wins:4,kd:2.17},
    {map:'Bakurani',team:'Valkyra',matches:3,wins:1,kd:1.36},
    {map:'Bakurani',team:'Manticore',matches:1,wins:1,kd:1.91},
    {map:'Ozeti',team:'Lonestar',matches:5,wins:3,kd:1.84},
    {map:'Ozeti',team:'Valkyra',matches:2,wins:1,kd:1.24},
    {map:'Ozeti',team:'Manticore',matches:1,wins:0,kd:1.67},
    {map:'Zestafona',team:'Lonestar',matches:5,wins:2,kd:1.76},
    {map:'Zestafona',team:'Valkyra',matches:1,wins:1,kd:2.40},
    {map:'Zestafona',team:'Manticore',matches:1,wins:1,kd:1.55}
  ];
  const sorted=()=>[...maps].sort((a,b)=>{
    const choice=document.getElementById('map-sort').value;
    const value=record=>choice==='winrate'?record.wins/record.matches:choice==='kills'?record.kills:record.matches;
    return value(b)-value(a);
  });
  function node(tag,content,parent,cls){
    const el=document.createElement(tag);
    if(content!==undefined)el.textContent=String(content);
    if(cls)el.className=cls;
    if(parent)parent.append(el);
    return el;
  }
  function drawRows(host,items,team){
    host.replaceChildren();
    for(const row of items){
      const box=node('article',undefined,host,'map-result');
      box.style.setProperty('--bar',row.color);
      box.style.setProperty('--width',(row.wins/row.matches*100)+'%');
      const top=node('div',undefined,box,'map-line');
      const left=node('strong',undefined,top);
      if(team){
        const emblem=node('img',undefined,left,'faction-logo');
        emblem.src=row.icon;emblem.alt='';emblem.loading='lazy';
      }
      node('span',row.name,left);
      node('span',(row.wins/row.matches*100).toFixed(1)+'% wins',top);
      node('div',row.matches+' saved matches • '+row.wins+' wins / '+row.losses+' losses • '+row.kills+' kills • '+row.time,box,'map-meta');
      const track=node('div',undefined,box,'map-track');
      node('div',undefined,track);
    }
  }
  const mapHost=document.getElementById('map-bars');
  const factionHost=document.getElementById('faction-bars');
  const sortSelect=document.getElementById('map-sort');
  if(sortSelect)sortSelect.addEventListener('change',()=>drawRows(mapHost,sorted(),false));
  drawRows(mapHost,sorted(),false);
  drawRows(factionHost,factions,true);
  const selects=[document.getElementById('combo-map'),document.getElementById('combo-team')];
  function drawCombos(){
    const body=document.getElementById('combination-rows');
    body.replaceChildren();
    const [mapFilter,teamFilter]=selects.map(s=>s.value);
    const visible=combos.filter(c=>(mapFilter==='all'||mapFilter===c.map)&&(teamFilter==='all'||teamFilter===c.team));
    if(!visible.length){
      const tr=node('tr',undefined,body);const td=node('td','No matches in this example for that combination.',tr);td.colSpan=6;
      return;
    }
    for(const row of visible){
      const tr=node('tr',undefined,body);
      for(const value of [row.map,row.team,row.matches,row.wins,
        (row.wins/row.matches*100).toFixed(1)+'%',row.kd.toFixed(2)]){
        node('td',value,tr);
      }
    }
  }
  selects.forEach(s=>s.addEventListener('change',drawCombos));
  drawCombos();
  document.getElementById('share-preview').addEventListener('click',async()=>{
    const feedback=document.getElementById('feedback');
    const url=location.href.split('#')[0]+'#profile';
    let text='Design preview link: '+url;
    try{if(navigator.clipboard?.writeText){await navigator.clipboard.writeText(url);text='Design preview link copied.';}}catch(_){}
    feedback.textContent=text;feedback.hidden=false;
  });
})();
