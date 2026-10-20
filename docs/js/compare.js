'use strict';
/* Public all-time WARCON player comparison; no new API or player identifiers. */
(function(){
  const get=id=>document.getElementById(id);
  const form=get('compare-form'),first=get('compare-first'),second=get('compare-second');
  const message=get('compare-message'),results=get('compare-results');
  const out=get('compare-rows'),share=get('compare-copy'),feedback=get('compare-share-feedback');
  const players=new Map(),keyPattern=/^[a-f0-9]{64}$/;
  const integer=n=>Number.isSafeInteger(n)&&n>=0;
  const show=n=>integer(n)?new Intl.NumberFormat().format(n):'—';
  const duration=m=>integer(m)?(m>=60?Math.floor(m/60)+'h '+m%60+'m':m+'m'):'—';
  const ratio=p=>{
    if(!integer(p.kills)||!integer(p.deaths)||p.deaths===0)return '—';
    return (p.kills/p.deaths).toFixed(2);
  };
  const percent=p=>{
    if(!integer(p.matches)||p.matches===0||!integer(p.wins))return '—';
    return (100*p.wins/p.matches).toFixed(1)+'%';
  };
  const rows=[
    ['Matches played',p=>show(p.matches)],
    ['Wins',p=>show(p.wins)],
    ['Losses',p=>show(p.losses)],
    ['Win rate',percent],
    ['Kills',p=>show(p.kills)],
    ['Deaths',p=>show(p.deaths)],
    ['K/D',ratio],
    ['Time played',p=>duration(p.minutes)],
    ['Player ranking',p=>integer(p.rank)&&p.rank>0?'#'+show(p.rank):'—'],
    ['Headshots',p=>p.hasFeed===true?show(p.headshots):'—'],
    ['Vehicle kills',p=>p.hasFeed===true?show(p.vehicleKills):'—']
  ];
  function option(select,p){
    const o=document.createElement('option');o.value=p.key;o.textContent=p.name;
    select.append(o);
  }
  function selected(value){
    return keyPattern.test(value)?players.get(value):undefined;
  }
  function openComparison(a,b){
    if(!a||!b||a.key===b.key){message.hidden=false;message.textContent='Choose two different players.';results.hidden=true;return;}
    message.hidden=true;
    results.hidden=false;
    get('compare-name-one').textContent=a.name;
    get('compare-name-two').textContent=b.name;
    out.replaceChildren();
    for(const [label,format] of rows){
      const tr=document.createElement('tr');
      for(const [tag,value,scope] of [['th',label,'row'],['td',format(a),null],['td',format(b),null]]){
        const cell=document.createElement(tag);cell.textContent=value;
        if(scope)cell.scope=scope;tr.append(cell);
      }
      out.append(tr);
    }
    const params=new URLSearchParams();
    params.set('a',a.key);params.set('b',b.key);
    history.replaceState(null,'','?'+params.toString());
    feedback.textContent='';
  }
  form.addEventListener('submit',event=>{
    event.preventDefault();openComparison(selected(first.value),selected(second.value));
  });
  share.addEventListener('click',async()=>{
    const a=selected(first.value),b=selected(second.value);
    if(!a||!b||a.key===b.key)return;
    const url=location.href;
    try{
      if(navigator.clipboard&&navigator.clipboard.writeText){
        await navigator.clipboard.writeText(url);
        feedback.textContent='Comparison link copied.';
      }else{
        feedback.textContent='Copy this address to share: '+url;
      }
    }catch(_){feedback.textContent='Copy this address to share: '+url;}
  });
  (async()=>{
    try{
      const response=await fetch('data/players.json',{cache:'no-store'});
      if(!response.ok)throw Error('Player index unavailable');
      const data=await response.json();
      if(data.schemaVersion!==2||!Array.isArray(data.players))throw Error('Invalid player index');
      for(const p of data.players){
        if(p&&keyPattern.test(p.key)&&typeof p.name==='string'&&p.name.trim()&&
           !/^\d{17}$/.test(p.name)){
          players.set(p.key,p);
        }
      }
      if(players.size<2){
        message.textContent='Not enough public player stats yet. Two players are needed for a comparison.';
        return;
      }
      const sorted=[...players.values()].sort((a,b)=>a.name.localeCompare(b.name));
      for(const p of sorted){option(first,p);option(second,p);}
      form.hidden=false;message.hidden=true;
      const params=new URLSearchParams(location.search);
      const a=selected(params.get('a')||''),b=selected(params.get('b')||'');
      if(a&&b&&a.key!==b.key){
        first.value=a.key;second.value=b.key;openComparison(a,b);
      }
    }catch(_){
      message.textContent='Player stats could not be loaded. Try again later.';
    }
  })();
})();
