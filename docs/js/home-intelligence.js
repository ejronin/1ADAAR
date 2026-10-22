'use strict';
/* Real WARCON-derived completed-match starts; no inferred player sessions. */
(async function(){
  const matrix=document.getElementById('ia-home-activity-matrix');
  const note=document.getElementById('ia-home-activity-note');
  if(!matrix||!note)return;
  const days=['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
  const valid=x=>Number.isSafeInteger(x)&&x>=0;
  function empty(message){
    note.textContent=message;matrix.replaceChildren();
    matrix.setAttribute('aria-label','No trustworthy captured pattern yet');
    for(let d=0;d<7;d++){
      const row=document.createElement('div');row.className='ia-home-hour-row';
      const label=document.createElement('span');label.textContent=days[d];label.className='ia-home-day';
      row.append(label);
      for(let h=0;h<24;h++){
        const cell=document.createElement('span');cell.className='ia-home-hour-cell';
        cell.dataset.level='0';cell.setAttribute('aria-hidden','true');row.append(cell);
      }
      matrix.append(row);
    }
  }
  empty('No recorded pattern confirmed yet. Empty cells do not prove the server was inactive.');
  try{
    const response=await fetch('data/recorded-activity.json',{cache:'no-store'});
    if(!response.ok)throw Error('source unavailable');
    const data=await response.json();
    if(!data||data.schemaVersion!==1||data.coverage!=='captured-only'||data.scope!=='server'||
       !Array.isArray(data.seasons))throw Error('unexpected source schema');
    const all=data.seasons.find(x=>x&&x.key==='all');
    if(!all||!valid(all.count)||!Array.isArray(all.byWeekdayAndHour)||
       all.byWeekdayAndHour.length!==7||!all.byWeekdayAndHour.every(x=>
       Array.isArray(x)&&x.length===24&&x.every(valid))||
       all.byWeekdayAndHour.flat().reduce((s,n)=>s+n,0)!==all.count)
       throw Error('mismatched counts');
    if(all.count===0)return;
    const maximum=Math.max(1,...all.byWeekdayAndHour.flat());
    matrix.replaceChildren();
    matrix.setAttribute('aria-label',all.count+' captured completed match starts grouped by Eastern weekday and hour');
    all.byWeekdayAndHour.forEach((hours,day)=>{
      const row=document.createElement('div');row.className='ia-home-hour-row';
      const label=document.createElement('span');label.className='ia-home-day';
      label.textContent=days[day];row.append(label);
      hours.forEach((count,hour)=>{
        const cell=document.createElement('span');cell.className='ia-home-hour-cell';
        cell.dataset.level=String(count?Math.max(1,Math.ceil(count/maximum*4)):0);
        cell.title=days[day]+' '+String(hour).padStart(2,'0')+':00 Eastern: '+
          count+' captured completed match starts';
        cell.setAttribute('aria-hidden','true');row.append(cell);
      });
      matrix.append(row);
    });
    note.textContent=all.count.toLocaleString()+
      ' verified completed-match starts in available capture history. This is not a player activity log.';
  }catch(_){
    empty('Recorded match-start coverage unavailable. This is not evidence of zero activity.');
  }
})();
