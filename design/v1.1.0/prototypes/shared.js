
'use strict';
/* Read-only fixture charts: no service calls, identities, credentials or fake live source. */
const data={kills:[],deaths:[],career:[],maps:['Bakurani','Ozeti','Zestafona'],teams:['Lonestar','Valkyra','Manticore']};
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

/* Paired-comparison dot plot: per-match counts share one honest zero-based axis.
   This makes relative kills/deaths legible without piling 32 crossing line segments. */
function pairedCounts(holder,kills,deaths,dates){
 if(!holder)return;holder.replaceChildren();
 const n=kills.length,W=760,left=87,right=75,top=36,bottom=32,row=23,H=top+n*row+bottom;
 const max=Math.max(1,...kills,...deaths),barW=W-left-right,scale=value=>left+value/max*barW;
 const chart=svg('svg',{viewBox:`0 0 ${W} ${H}`,class:'chart',role:'img',
 'aria-label':`Kills and deaths paired comparison for ${n} completed fictional matches. Every pair shares a zero-based count scale. Green kills, yellow deaths. See exact data table.`});
 for(let i=0;i<5;i++){const x=left+i/4*barW;
  chart.append(svg('line',{class:'guide',x1:x,x2:x,y1:top-9,y2:H-bottom+8}));
  chart.append(svg('text',{x,y:17,'text-anchor':'middle'},String(Math.round(max*i/4))));
 }
 kills.forEach((k,i)=>{
  const d=deaths[i],y=top+i*row,x1=scale(k),x2=scale(d);
  chart.append(svg('text',{x:4,y:y+4},dates[i]?.slice(5)||String(i+1)));
  chart.append(svg('line',{x1:Math.min(x1,x2),x2:Math.max(x1,x2),y1:y,y2:y,stroke:'#739281','stroke-width':2}));
  for(const [count,x,color,label] of [[k,x1,'#86f4a4','Kills'],[d,x2,'#f5c84b','Deaths']]){
    const c=svg('circle',{cx:x,cy:y,r:4.7,fill:color,stroke:'#13251a','stroke-width':1.5});
    c.append(svg('title',{},`${dates[i]} — ${label}: ${count}`));chart.append(c);
  }
 });
 holder.append(chart);
}

function initPlayer(){
 const host=$('#performance-chart');if(!host)return;const tabs=$('.tab[data-trend]'),pick=$('#point-window'),encoding=$('#kills-encoding'),encodingControl=$('#kills-chart-picker'),definition=$('#trend-definition'),summary=$('#trend-context'),legend=$('#chart-legend'),table=$('#chart-data');let active='kills';
 function render(){
  if(!data.kills.length)return;
  const n=Number(pick.value),offset=Math.max(0,data.kills.length-n),kills=data.kills.slice(offset),deaths=data.deaths.slice(offset),dates=data.dates.slice(offset);
  const kd=kills.map((k,i)=>deaths[i]===0?k:k/deaths[i]),allrolling=data.kills.map((_,i)=>i<4?null:data.kills.slice(i-4,i+1).reduce((a,b)=>a+b,0)/Math.max(1,data.deaths.slice(i-4,i+1).reduce((a,b)=>a+b,0))),roll=allrolling.slice(offset);
  const avgK=data.kills.map((_,i)=>i<4?null:data.kills.slice(i-4,i+1).reduce((a,b)=>a+b,0)/5).slice(offset),avgD=data.deaths.map((_,i)=>i<4?null:data.deaths.slice(i-4,i+1).reduce((a,b)=>a+b,0)/5).slice(offset);
  const snapshots=data.career.slice(offset);
  const legendItems=active==='kills'?[['Kills','#86f4a4'],['Deaths','#f5c84b']]:active==='kd'?[['Match K/D','#86f4a4']]:active==='rolling'?[['Trailing five-match K/D','#86f4a4']]:active==='averages'?[['Trailing 5-match avg kills','#86f4a4'],['Trailing 5-match avg deaths','#f5c84b']]:[['Tracked career K/D','#86f4a4']];
  const specs=active==='kills'?[{values:kills,color:'#86f4a4'},{values:deaths,color:'#f5c84b'}]:active==='kd'?[{values:kd,color:'#86f4a4'}]:active==='rolling'?[{values:roll,color:'#86f4a4'}]:active==='averages'?[{values:avgK,color:'#86f4a4'},{values:avgD,color:'#f5c84b'}]:[{values:snapshots,color:'#86f4a4'}];
  if(encodingControl){encodingControl.hidden=active!=='kills';if(active!=='kills' && encoding)encoding.value='trend';}
  if(active==='kills'&&encoding?.value==='paired')pairedCounts(host,kills,deaths,dates);
  else cartesian(host,specs,dates.map(d=>d.slice(5)),legendItems.map(x=>x[0]).join(' versus ')+' over '+n+' fictional observations');
  legend.textContent='';for(const [label,color] of legendItems){const item=document.createElement('span');const swatch=document.createElement('i');swatch.style.background=color;item.append(swatch,document.createTextNode(label));legend.append(item)}
  const metricDefs={
   kills:'One point = one saved completed match. The green line shows kills, yellow shows deaths. Paired dots are an alternative encoding ONLY for these raw per-match counts.',
   kd:'One point = kills ÷ deaths in one saved completed match. This is NOT the all-time career K/D; undefined division uses the documented source convention.',
   rolling:'TRAILING WINDOW — each point for match N uses matches N−4 through N, not the five matches around the point. For example, point 12 summarizes matches 8–12. Five consecutive-match kills summed ÷ those five deaths summed.',
   averages:'TRAILING WINDOW — each point for match N is the average kills and average deaths across matches N−4 through N. The first four match positions have no complete five-match window.',
   career:'Each point is a dated saved snapshot of total career K/D; it does not mean a single match and it cannot reconstruct time before observations began.'
  };
  if(definition)definition.textContent=metricDefs[active]||'';
  summary.textContent=active==='rolling'?'Each point is trailing five consecutive saved matches. Overlapping windows: 10 displayed points do not mean 50 unique matches; oldest shown points may use earlier hidden matches.':active==='career'?'Fictional WARCON-style careerHistory snapshots from the original PlayerOne fixture; real player snapshots require an actual saved WARCON history.':active==='averages'?'The trailing five-match means use current + four preceding matches. 10 / 20 / All controls how many points are visible, NOT the size of the five-match rolling window.':active==='kills'&&encoding?.value==='paired'?'Paired dots are individual kills/deaths values from the original fictional fixture; all pairs use a zero-based common count scale.':`Displaying ${n} of 32 original fictional saved-match observations · oldest → newest; career totals remain unchanged.`;
  const fields=active==='kills'?[kills,deaths]:active==='averages'?[avgK,avgD]:active==='kd'?[kd]:active==='rolling'?[roll]:[snapshots];
  table.innerHTML='<tr><th>Recorded date</th>'+legendItems.map(x=>'<th>'+x[0]+'</th>').join('')+'</tr>'+Array.from({length:n},(_,i)=>'<tr><td>'+dates[i]+'</td>'+fields.map(f=>'<td>'+((f[i]===null||!Number.isFinite(f[i]))?'—':format(f[i]))+'</td>').join('')+'</tr>').join('');
 }
 for(const tab of tabs)tab.addEventListener('click',()=>{active=tab.dataset.trend;for(const b of tabs)b.setAttribute('aria-pressed',String(tab===b));render()});pick.addEventListener('change',render);if(encoding)encoding.addEventListener('change',render);
 // Single source of truth: the existing repository PlayerOne demonstration fixture.
 // No separate chart observations or invented historical career snapshots.
 fetch('../../../docs/data/demo-player.json',{cache:'no-store'}).then(response=>{
   if(!response.ok)throw Error('Original demo fixture unavailable');
   return response.json();
 }).then(fixture=>{
   if(fixture.kind!=='demo-only'||fixture.fictional!==true||!Array.isArray(fixture.matches)||
      !Array.isArray(fixture.careerHistory)||fixture.matches.length!==32||fixture.careerHistory.length!==32)
     throw Error('Original demo fixture schema changed');
   const sorted=fixture.matches.slice().sort((a,b)=>Date.parse(a.endedAt)-Date.parse(b.endedAt));
   const rows=sorted.map(m=>(m.players||[]).find(p=>p.key===fixture.player.key));
   if(rows.some(p=>!p||!Number.isFinite(p.kills)||!Number.isFinite(p.deaths)))
     throw Error('Incomplete original demo match rows');
   data.kills=rows.map(p=>p.kills);
   data.deaths=rows.map(p=>p.deaths);
   data.dates=sorted.map(m=>m.endedAt.slice(0,10));
   data.career=fixture.careerHistory.slice().sort((a,b)=>a.date.localeCompare(b.date)).map(p=>p.deaths>0?p.kills/p.deaths:p.kills);
   render();
 }).catch(error=>{
   host.textContent='Original PlayerOne fixture could not be loaded. Do not substitute invented chart observations.';
   summary.textContent='Source fixture unavailable — no chart is shown.';
   legend.replaceChildren();table.replaceChildren();
 });
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

/* Map/team mode buttons are functional comparative encodings, not decorative filters.
   All example fractions are derived from the repo's actual fictional PlayerOne rows. */
async function initScore(){
 const buttons=$$('[data-map]'),target=$('#map-insight');if(!buttons.length||!target)return;
 let fixture;
 try{
  const response=await fetch('../../../docs/data/demo-player.json',{cache:'no-store'});
  if(!response.ok)throw Error('Missing fixture');
  fixture=await response.json();
  if(fixture.kind!=='demo-only'||fixture.fictional!==true||fixture.matches?.length!==32)throw Error('Invalid fixture');
 }catch(e){target.textContent='Original sample results unavailable. No illustrative percentages shown.';return;}
 const matches=fixture.matches.slice().sort((a,b)=>Date.parse(b.endedAt)-Date.parse(a.endedAt)).slice(0,10);
 const source=matches.map(m=>({map:m.map,faction:m.players[0].faction,result:m.players[0].result}));
 const stats=key=>{
  const count=new Map();for(const row of source)count.set(row[key],(count.get(row[key])||0)+1);
  return [...count].sort((a,b)=>b[1]-a[1]);
 };
 function render(mode){
  target.replaceChildren();const heading=document.createElement('p');heading.className='source';
  heading.textContent=mode==='outcomes'?'Known outcomes, most recent ten actual fictional fixture records (not a live server).':
    mode==='factions'?'Most-played faction is a share of ten saved fictional matches, not win percentage.':
    'Most-played map is a share of ten saved fictional matches, not win percentage.';
  target.append(heading);
  let items=mode==='outcomes'?stats('result'):mode==='factions'?stats('faction'):stats('map');
  for(const [label,count] of items){
   const block=document.createElement('div');block.style.margin='10px 0';const head=document.createElement('div');head.className='labelrow';
   const name=document.createElement('b');name.textContent=mode==='outcomes'?({win:'Wins',loss:'Losses',draw:'Draws'}[label]||label):label;
   const value=document.createElement('span');value.textContent=`${count} of ${source.length} · ${(count/source.length*100).toFixed(0)}%`;
   head.append(name,value);const bar=document.createElement('div');bar.className='meter';const fill=document.createElement('span');
   const colors={win:'#4e9b6a',loss:'#a45e54',draw:'#71827b',Lonestar:'#465eff',Valkyra:'#ee4138',Manticore:'#3eba42'};
   fill.style.width=`${(count/source.length*100).toFixed(2)}%`;fill.style.background=colors[label]||'#86f4a4';
   bar.append(fill);block.append(head,bar);target.append(block);
  }
 }
 for(const btn of buttons)btn.addEventListener('click',()=>{
  buttons.forEach(b=>b.setAttribute('aria-pressed',String(b===btn)));
  render(btn.dataset.map);
 });
 render('outcomes');
}
document.addEventListener('DOMContentLoaded',()=>{initPlayer();initHeat();initWeekly();initScore()});
