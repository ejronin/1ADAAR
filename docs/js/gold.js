/* 1ADAAR GOLD: public daily price only, no account data, subscriptions, or forecasts. */
(function (root) {
  'use strict';
  const SOURCE='https://wardogserverlist.com/api/gold-bars';
  const DAY=86400000;
  const fmt=new Intl.NumberFormat('en-US',{maximumFractionDigits:0});
  const fmtDate=new Intl.DateTimeFormat('en-US',{timeZone:'UTC',month:'short',day:'numeric',year:'numeric'});
  const fmtShort=new Intl.DateTimeFormat('en-US',{timeZone:'UTC',month:'short',day:'numeric'});
  const get=id=>document.getElementById(id);
  function normalize(doc) {
    if(!doc||!Array.isArray(doc.points))throw Error('Invalid gold price data');
    const prices=new Map();
    for(const row of doc.points){
      if(!Array.isArray(row)||row.length!==2)continue;
      const ts=row[0],price=row[1];
      if(!Number.isSafeInteger(ts)||ts%DAY!==0||!Number.isSafeInteger(price)||price<=0||price>100000000)continue;
      prices.set(ts,price);
    }
    const rows=Array.from(prices,(entry)=>({ts:entry[0],price:entry[1]})).sort((a,b)=>a.ts-b.ts);
    if(!rows.length)throw Error('No valid daily gold prices supplied');
    const newest=rows[rows.length-1];
    if(doc.latest&&Number.isSafeInteger(doc.latest.ts)&&Number.isSafeInteger(doc.latest.price)&&doc.latest.ts===newest.ts&&doc.latest.price>0&&doc.latest.price<=100000000){
      newest.price=doc.latest.price;
    }
    return {rows,checkedAt:Number.isSafeInteger(doc.checkedAt)&&doc.checkedAt>0?doc.checkedAt:null};
  }
  function sliceDays(rows,days){
    if(!rows.length)return [];
    if(days==='all')return rows;
    const cutoff=rows[rows.length-1].ts-(Number(days)-1)*DAY;
    return rows.filter(row=>row.ts>=cutoff);
  }
  function diffDays(rows,days){
    if(!rows.length)return null;
    const end=rows[rows.length-1];
    const start=rows.find(r=>r.ts===end.ts-days*DAY);
    return start?((end.price-start.price)/start.price)*100:null;
  }
  function average(rows){return rows.length?Math.round(rows.reduce((sum,r)=>sum+r.price,0)/rows.length):null;}
  function dateText(ts,short=false){return (short?fmtShort:fmtDate).format(new Date(ts));}
  function number(price){return price==null?'—':fmt.format(price);}
  function compact(price){return price>=1000000?(price/1000000).toFixed(2)+'M':price>=1000?Math.round(price/1000)+'K':number(price);}
  function changeText(value){return value==null?'—':(value>0?'+':'')+value.toFixed(1)+'%';}
  function changeClass(v){return v==null||v===0?'gold-neutral':v>0?'gold-positive':'gold-negative';}
  function node(tag,attrs,text){
    const el=document.createElementNS('http://www.w3.org/2000/svg',tag);
    for(const [key,value] of Object.entries(attrs||{}))el.setAttribute(key,String(value));
    if(text!==undefined)el.textContent=text;
    return el;
  }
  function renderChart(rows,selectedTs){
    const svg=get('gold-chart');
    svg.replaceChildren();
    const W=940,H=420,L=76,R=25,T=20,B=52,base=H-B,plotW=W-L-R,plotH=base-T;
    if(!rows.length){get('gold-chart-note').textContent='No daily gold price history available.';return;}
    const max=Math.max(...rows.map(row=>row.price));
    const maxY=Math.max(100000,Math.ceil(max*1.16/100000)*100000);
    const first=rows[0].ts,last=rows[rows.length-1].ts;
    const x=ts=>L+(last===first?.5:(ts-first)/(last-first))*plotW;
    const y=price=>base-price/maxY*plotH;
    for(let i=0;i<=4;i++){
      const val=maxY*i/4,yy=y(val);
      svg.appendChild(node('line',{class:'gold-grid',x1:L,y1:yy,x2:W-R,y2:yy}));
      svg.appendChild(node('text',{class:'gold-axis',x:L-12,y:yy+4,'text-anchor':'end'},compact(Math.round(val))));
    }
    const intervals=Math.min(6,rows.length-1);
    for(let i=0;i<=intervals;i++){
      const item=rows[Math.round(i*(rows.length-1)/Math.max(1,intervals))];
      svg.appendChild(node('text',{class:'gold-axis',x:x(item.ts),y:H-18,'text-anchor':i===0?'start':i===intervals?'end':'middle'},dateText(item.ts,true)));
    }
    const groups=[];
    let group=[];
    for(const r of rows){
      if(group.length&&r.ts-group[group.length-1].ts>DAY){groups.push(group);group=[];}
      group.push(r);
    }
    if(group.length)groups.push(group);
    for(const batch of groups){
      const points=batch.map(r=>x(r.ts)+','+y(r.price));
      if(batch.length>1){
        svg.appendChild(node('path',{class:'gold-area',d:'M'+x(batch[0].ts)+','+base+' L'+points.join(' L')+' L'+x(batch[batch.length-1].ts)+','+base+' Z'}));
        svg.appendChild(node('path',{class:'gold-line',d:'M'+points.join(' L')}));
      }else{
        svg.appendChild(node('circle',{cx:x(batch[0].ts),cy:y(batch[0].price),r:3,fill:'#ffd36b'}));
      }
    }
    const mean=average(rows);
    svg.appendChild(node('line',{class:'gold-mean',x1:L,x2:W-R,y1:y(mean),y2:y(mean)}));
    const chosen=rows.find(r=>r.ts===selectedTs)||rows[rows.length-1];
    svg.appendChild(node('line',{class:'gold-focus-line',x1:x(chosen.ts),x2:x(chosen.ts),y1:T,y2:base}));
    svg.appendChild(node('circle',{class:'gold-focus-dot',cx:x(chosen.ts),cy:y(chosen.price),r:6}));
    get('gold-chart-note').textContent=dateText(chosen.ts)+' · '+number(chosen.price)+' cash per bar';
    svg.onpointermove=function(evt){
      const rect=svg.getBoundingClientRect();
      if(!rect.width)return;
      const px=(evt.clientX-rect.left)*W/rect.width;
      const ratio=Math.max(0,Math.min(1,(px-L)/plotW));
      const target=first+ratio*(last-first);
      const near=rows.reduce((best,r)=>Math.abs(r.ts-target)<Math.abs(best.ts-target)?r:best,rows[0]);
      if(near.ts!==selectedTs){selectedTs=near.ts;renderChart(rows,selectedTs);}
    };
  }
  function init(){
    const rangeButtons=Array.from(document.querySelectorAll('[data-range]'));
    const qty=get('gold-count'),cash=get('gold-cash'),quick=Array.from(document.querySelectorAll('[data-bars]'));
    let price=null,rows=[],range='30',selected=null;
    function updateConverter(){
      const bars=Number(qty.value);
      cash.textContent=price!=null&&Number.isSafeInteger(bars)&&bars>=1&&bars<=1000000?number(price*bars)+' cash':'—';
      for(const b of quick)b.setAttribute('aria-pressed',String(Number(b.dataset.bars)===bars));
    }
    qty.addEventListener('input',updateConverter);
    for(const b of quick)b.addEventListener('click',function(){qty.value=b.dataset.bars;updateConverter();});
    function setChange(id,v){const el=get(id);el.textContent=changeText(v);el.className=changeClass(v);}
    function renderStats(){
      if(!rows.length)return;
      const newest=rows[rows.length-1];
      price=newest.price;
      get('gold-price').textContent=number(price);
      get('gold-asof').textContent='Quote for '+dateText(newest.ts)+' (UTC)'+(newest.ts<Date.now()-2*DAY?' · Last recorded price; may be stale':'');
      setChange('gold-change-1',diffDays(rows,1));
      setChange('gold-change-7',diffDays(rows,7));
      setChange('gold-change-30',diffDays(rows,30));
      const low=rows.reduce((a,r)=>r.price<a.price?r:a,rows[0]);
      const high=rows.reduce((a,r)=>r.price>a.price?r:a,rows[0]);
      get('gold-low').textContent=number(low.price);
      get('gold-low-date').textContent=dateText(low.ts);
      get('gold-high').textContent=number(high.price);
      get('gold-high-date').textContent=dateText(high.ts);
      get('gold-avg-30').textContent=number(average(sliceDays(rows,30)));
      const recent=sliceDays(rows,7);
      get('gold-trend-average').textContent=number(average(recent));
      get('gold-trend-low').textContent='LOW '+number(Math.min(...recent.map(r=>r.price)));
      get('gold-trend-high').textContent='HIGH '+number(Math.max(...recent.map(r=>r.price)));
      updateConverter();
      renderHistory();
      showRange();
    }
    function renderHistory(){
      const host=get('gold-days');
      host.replaceChildren();
      const last14=rows.slice(-14).reverse();
      for(let i=0;i<last14.length;i++){
        const r=last14[i];
        const earlier=rows.find(p=>p.ts===r.ts-DAY);
        const v=earlier?(r.price/earlier.price-1)*100:null;
        const btn=document.createElement('button');
        btn.type='button';btn.className='gold-day';
        btn.setAttribute('aria-pressed',String(selected===r.ts));
        const date=document.createElement('time');
        date.dateTime=new Date(r.ts).toISOString().slice(0,10);date.textContent=i===0?'LATEST · '+dateText(r.ts,true):dateText(r.ts,true);
        const amount=document.createElement('strong');amount.textContent=compact(r.price);
        const delta=document.createElement('span');delta.textContent=changeText(v);delta.className=changeClass(v);
        btn.append(date,amount,delta);
        btn.addEventListener('click',function(){
          selected=r.ts;
          if(!sliceDays(rows,range).some(p=>p.ts===selected)){
            range='all';for(const b of rangeButtons)b.setAttribute('aria-pressed',String(b.dataset.range===range));
          }
          renderHistory();renderChart(sliceDays(rows,range),selected);
        });
        host.appendChild(btn);
      }
    }
    function showRange(){
      const selectedRows=sliceDays(rows,range);
      selected=null;
      renderChart(selectedRows,null);
      for(const b of rangeButtons)b.setAttribute('aria-pressed',String(b.dataset.range===range));
    }
    for(const b of rangeButtons)b.addEventListener('click',function(){if(!rows.length)return;range=b.dataset.range;showRange();renderHistory();});
    fetch(SOURCE,{headers:{'Accept':'application/json'},cache:'no-store'})
      .then(response=>{if(!response.ok)throw Error('Price service returned HTTP '+response.status);return response.json();})
      .then(data=>{rows=normalize(data).rows;renderStats();})
      .catch(()=>{get('gold-price').textContent='Unavailable';get('gold-asof').textContent='No price data could be loaded.';get('gold-error').hidden=false;get('gold-error').textContent='The independent price source is unavailable right now. No last-known price has been substituted. You can check the linked source directly.';get('gold-chart-note').textContent='Gold price history unavailable.';get('gold-days').textContent='No verified daily prices available.';});
  }
  if(typeof module!=='undefined'&&module.exports)module.exports={normalize,sliceDays,diffDays,average,changeText};
  if(typeof document!=='undefined')document.addEventListener('DOMContentLoaded',init);
})(typeof globalThis!=='undefined'?globalThis:this);