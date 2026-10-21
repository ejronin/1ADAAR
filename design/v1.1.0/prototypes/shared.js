
'use strict';
/* Read-only fixture charts: no service calls, identities, credentials or fake live source. */
const data={
 kills:[14,19,13,24,17,26,11,29,21,18,15,31,19,17,26,12,22,20,27,14,16,24,29,18,22,17,33,14,25,21,18,29],
 deaths:[10,14,16,12,15,10,18,12,8,15,13,11,14,18,12,16,11,12,15,19,14,10,9,13,12,17,11,14,13,9,16,12],
 maps:['Bakurani','Ozeti','Zestafona'],teams:['Lonestar','Valkyra','Manticore']};
const $=q=>document.querySelector(q), $$=q=>[...document.querySelectorAll(q)];
const svg=(tag,attrs={},text='')=>{const node=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [k,v] of Object.entries(attrs))node.setAttribute(k,String(v));if(text)node.textContent=text;return node;};
const format=x=>Number(x).toFixed(2);
function cartesian(holder,series,labels,title){
 if(!holder)return;holder.replaceChildren();const W=760,H=250,l=41,r=17,t=18,b=32,max=Math.max(1,...series.flatMap(s=>s.values.filter(Number.isFinite))),min=0;
 const chart=svg('svg',{viewBox:`0 0 ${W} ${H}`,class:'chart',role:'img','aria-label':title});const xn=i=>l+i*(W-l-r)/(labels.length-1||1),yn=v=>H-b-v/max*(H-t-b);
 for(let i=0;i<5;i++){const y=t+i*(H-t-b)/4;chart.append(svg('line',{class:'guide',x1:l,x2:W-r,y1:y,y2:y}));chart.append(svg('text',{x:4,y:y+4},Math.round(max*(1-i/4)).toString()));}
 for(let i=0;i<labels.length;i++)if(i===0||i===labels.length-1||i%Math.max(1,Math.floor(labels.length/7))===0)chart.append(svg('text',{x:xn(i),y:H-8,'text-anchor':'middle'},String(labels[i])));
 for(const s of series){let path='';for(let i=0;i<s.values.length;i++){const v=s.values[i];if(!Number.isFinite(v)){continue}path+=(path?' L':'M')+xn(i).toFixed(2)+' '+yn(v).toFixed(2)}chart.append(svg('path',{d:path,class:'plotline',stroke:s.color,'stroke-dasharray':s.dash?'5 5':'none'}));}
 holder.append(chart);
}
function initPlayer(){
 const host=$('#performance-chart');if(!host)return;const tabs=$$('.tab[data-trend]'),pick=$('#point-window'),summary=$('#trend-context'),legend=$('#chart-legend'),table=$('#chart-data');let active='kills';
 function render(){
  const n=Number(pick.value),offset=Math.max(0,data.kills.length-n),kills=data.kills.slice(offset),deaths=data.deaths.slice(offset),d=data.kills.length;
  const kd=kills.map((k,i)=>deaths[i]===0?k:k/deaths[i]),allrolling=data.kills.map((_,i)=>i<4?null:data.kills.slice(i-4,i+1).reduce((a,b)=>a+b,0)/Math.max(1,data.deaths.slice(i-4,i+1).reduce((a,b)=>a+b,0))),roll=allrolling.slice(offset);
  const avgK=data.kills.map((_,i)=>i<4?null:data.kills.slice(i-4,i+1).reduce((a,b)=>a+b,0)/5).slice(offset),avgD=data.deaths.map((_,i)=>i<4?null:data.deaths.slice(i-4,i+1).reduce((a,b)=>a+b,0)/5).slice(offset);
  const snapshots=data.kills.map((_,i)=>data.kills.slice(0,i+1).reduce((a,b)=>a+b,0)/Math.max(1,data.deaths.slice(0,i+1).reduce((a,b)=>a+b,0))).slice(offset);
  const legendItems=active==='kills'?[['Kills','#86f4a4'],['Deaths','#f5c84b']]:active==='kd'?[['Match K/D','#86f4a4']]:active==='rolling'?[['Five-match rolling K/D','#86f4a4']]:active==='averages'?[['Five-match avg kills','#86f4a4'],['Five-match avg deaths','#f5c84b']]:[['Tracked career K/D','#86f4a4']];
  const specs=active==='kills'?[{values:kills,color:'#86f4a4'},{values:deaths,color:'#f5c84b'}]:active==='kd'?[{values:kd,color:'#86f4a4'}]:active==='rolling'?[{values:roll,color:'#86f4a4'}]:active==='averages'?[{values:avgK,color:'#86f4a4'},{values:avgD,color:'#f5c84b'}]:[{values:snapshots,color:'#86f4a4'}];
  cartesian(host,specs,Array.from({length:n},(_,i)=>String(offset+i+1)),legendItems.map(x=>x[0]).join(' versus ')+' over '+n+' fictional observations');
  legend.textContent='';for(const [label,color] of legendItems){const item=document.createElement('span');const swatch=document.createElement('i');swatch.style.background=color;item.append(swatch,document.createTextNode(label));legend.append(item)}
  summary.textContent=active==='rolling'?'Each point: five consecutive saved matches. Points overlap; 10 points are not 50 unique matches.':active==='career'?'Illustrative only: real career K/D requires recorded WARCON snapshots; this synthetic line is NOT a real career.':active==='averages'?'Kills (green) and deaths (yellow): arithmetic means over five consecutive matches; no point before five observations.':`Displaying ${n} of 32 fictional saved-match observations · oldest → newest; career totals above remain unchanged.`;
  const fields=active==='kills'?[kills,deaths]:active==='averages'?[avgK,avgD]:active==='kd'?[kd]:active==='rolling'?[roll]:[snapshots];
  table.innerHTML='<tr><th>Observation</th>'+legendItems.map(x=>'<th>'+x[0]+'</th>').join('')+'</tr>'+Array.from({length:n},(_,i)=>'<tr><td>'+String(offset+i+1)+'</td>'+fields.map(f=>'<td>'+((f[i]===null||!Number.isFinite(f[i]))?'—':format(f[i]))+'</td>').join('')+'</tr>').join('');
 }
 for(const tab of tabs)tab.addEventListener('click',()=>{active=tab.dataset.trend;for(const b of tabs)b.setAttribute('aria-pressed',String(tab===b));render()});pick.addEventListener('change',render);render();
}
function initHeat(){
 const heat=$('#heat-cells');if(!heat)return;const mode=$('#heat-mode'),detail=$('#heat-detail'),label=$('#heat-source'),demo=$('#demo-heat'),set=$('#heat-scope');const weekdays=['MON','TUE','WED','THU','FRI','SAT','SUN'];
 function redraw(){
  heat.replaceChildren();const fixture=demo.checked,personal=set.value==='personal';
  const corner=document.createElement('span');heat.append(corner);for(let h=0;h<24;h++){const item=document.createElement('span');item.className='hour';item.textContent=h%4===0?String(h).padStart(2,'0'):'';heat.append(item)}
  for(let day=0;day<7;day++){const daylabel=document.createElement('span');daylabel.className='day';daylabel.textContent=weekdays[day];heat.append(daylabel);
  for(let hour=0;hour<24;hour++){const cell=document.createElement('button');cell.className='cell';cell.type='button';let n=0;if(fixture)n=personal?Math.max(0,Math.round((Math.sin(day*2+hour)+Math.cos(hour/3)+1.5)*2-2)):(hour>=18&&hour<=23&&(day>=4||day===1)?1+(hour+day)%4:0);cell.dataset.b=String(Math.min(4,n));const metric=personal?'example session minutes (ordinal shade)':'example recorded match starts';const description=`${weekdays[day]} ${hour}:00 Eastern · ${n} ${metric}`;cell.setAttribute('aria-label',description);cell.title=description;cell.onclick=()=>{detail.textContent=fixture?description+' · FICTIONAL DEMO':`${weekdays[day]} ${hour}:00 · No saved source data; zero is not proven inactivity.`};heat.append(cell)}}
  detail.textContent=fixture?'SAMPLE / FICTIONAL activity · select any cell for values.':'No saved completed-match starts in current staged 1ADAAR data. We cannot infer inactivity or personal sessions.';
  label.textContent=personal?'PERSONAL SESSION VIEW: NOT ENABLED without authorized complete joinedAt/leftAt collection and privacy review.':fixture?'FICTIONAL DEMONSTRATION · not actual WARDOGS records':'SERVER-WIDE captured completed-match starts · actual staged source currently has zero records';
 }
 demo.addEventListener('change',redraw);set.addEventListener('change',redraw);mode.addEventListener('change',redraw);redraw();
}
function initWeekly(){const button=$('#weekly-demo');if(!button)return;button.addEventListener('change',()=>{const card=$('#podium-demo');card.hidden=!button.checked;if(!button.checked)return;card.querySelector('.first').classList.remove('champion');requestAnimationFrame(()=>card.querySelector('.first').classList.add('champion'))})}
function initScore(){const buttons=$$('[data-map]');if(!buttons.length)return;const target=$('#map-insight');buttons.forEach(btn=>btn.onclick=()=>{buttons.forEach(b=>b.setAttribute('aria-pressed',String(b===btn)));target.textContent=btn.dataset.map==='outcomes'?'Recorded outcomes: W 5 · L 3 · D 2 — latest 10 fictional match records.':btn.dataset.map==='factions'?'Lonestar 4 / Valkyra 3 / Manticore 3 · latest 10 fictional appearances.':'Most-played map Bakurani: 4/10 recent fictional matches. No unqualified best-map claim.'})}
document.addEventListener('DOMContentLoaded',()=>{initPlayer();initHeat();initWeekly();initScore()});
