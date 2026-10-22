'use strict';
/* Activity intelligence uses only captured completed-match start counts, never
   player sessions, occupancy, broadcasts or inferred server activity. */
(function(root){
  const HOURS=[0,6,12,18];
  const WEEK=['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
  function safe(matrix){
    return Array.isArray(matrix)&&matrix.length===7&&matrix.every(row=>
      Array.isArray(row)&&row.length===24&&row.every(n=>
        Number.isSafeInteger(n)&&n>=0));
  }
  function axis(host){
    if(!host)return;
    const old=host.querySelector(':scope > .ia-hour-axis');
    if(old)old.remove();
    const row=document.createElement('div');
    row.className='ia-hour-axis';
    row.setAttribute('aria-hidden','true');
    for(const hour of HOURS){
      const marker=document.createElement('span');
      marker.className='ia-hour-axis-label';
      marker.style.gridColumn=String(hour+2);
      marker.textContent=String(hour).padStart(2,'0')+':00';
      row.append(marker);
    }
    host.prepend(row);
  }
  function best(values){
    const high=Math.max(...values);
    if(high===0)return null;
    const indexes=values.flatMap((n,i)=>n===high?[i]:[]);
    return {count:high,indexes};
  }
  function summary(matrix){
    if(!safe(matrix))return null;
    const total=matrix.flat().reduce((a,b)=>a+b,0);
    if(total===0)return null;
    const days=matrix.map(row=>row.reduce((a,b)=>a+b,0));
    const hours=Array.from({length:24},(_,hour)=>
      matrix.reduce((acc,row)=>acc+row[hour],0));
    const blocks=Array.from({length:4},(_,block)=>
      hours.slice(block*6,block*6+6).reduce((a,b)=>a+b,0));
    return {total,day:best(days),hour:best(hours),window:best(blocks)};
  }
  const display=(result,formatter)=>
    result?(result.indexes.length>1?
      result.indexes.slice(0,2).map(formatter).join(' / ')+
        (result.indexes.length>2?' + ties':'') : formatter(result.indexes[0])):'—';
  function render(host,matrix){
    if(!host)return;
    const s=summary(matrix);
    const fields=[
      ['Captured match starts',s?s.total.toLocaleString():'—'],
      ['Most common weekday',s?display(s.day,i=>WEEK[i]):'—'],
      ['Most common start hour',s?display(s.hour,i=>String(i).padStart(2,'0')+':00'):'—'],
      ['Most common 6-hour block',s?display(s.window,i=>
        String(i*6).padStart(2,'0')+':00–'+String((i+1)*6).padStart(2,'0')+':00'):'—']
    ];
    host.replaceChildren();
    for(const [label,value] of fields){
      const cell=document.createElement('div');cell.className='ia-insight-item';
      const title=document.createElement('span');title.textContent=label;
      const figure=document.createElement('strong');figure.textContent=value;
      cell.append(title,figure);host.append(cell);
    }
    return Boolean(s);
  }
  root.OneADAARActivity=Object.freeze({axis,summary,render});
})(window);
