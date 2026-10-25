/* 1ADAAR GOLD: public daily price only, no account data or subscriptions; separately validated model forecasts. */
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
  // Multi-day candles from actual daily UTC price observations, never invented intraday OHLC.
  function candleSpan(range,count){
    if(range==='7')return 2;
    if(range==='30')return 3;
    if(range==='90')return 7;
    return count>180?14:7;
  }
  function buildCandles(rows,range){
    if(!rows.length)return [];
    const span=candleSpan(range,rows.length);
    const latest=Math.floor(rows[rows.length-1].ts/DAY);
    const groups=new Map();
    for(const point of rows){
      const bucket=Math.floor((latest-Math.floor(point.ts/DAY))/span);
      if(!groups.has(bucket))groups.set(bucket,[]);
      groups.get(bucket).push(point);
    }
    return Array.from(groups.values()).map(values=>{
      values.sort((a,b)=>a.ts-b.ts);
      return {ts:values[Math.floor((values.length-1)/2)].ts,
        from:values[0].ts,to:values[values.length-1].ts,
        open:values[0].price,close:values[values.length-1].price,
        high:Math.max(...values.map(row=>row.price)),
        low:Math.min(...values.map(row=>row.price)),
        readings:values.length,span};
    }).sort((a,b)=>a.ts-b.ts);
  }
  function node(tag,attrs,text){
    const el=document.createElementNS('http://www.w3.org/2000/svg',tag);
    for(const [key,value] of Object.entries(attrs||{}))el.setAttribute(key,String(value));
    if(text!==undefined)el.textContent=text;
    return el;
  }
  function renderChart(rows,selectedTs,projection,mode='line',range='30'){
    const svg=get('gold-chart');
    svg.replaceChildren();
    const W=Math.max(310,Math.floor(svg.getBoundingClientRect().width||svg.parentElement.clientWidth||940));
    const H=W<540?360:W<900?440:480,L=W<540?58:76,R=W<540?12:24,T=20,B=52,base=H-B,plotW=W-L-R,plotH=base-T;
    svg.setAttribute('viewBox','0 0 '+W+' '+H);
    svg.style.height=H+'px';
    if(!rows.length){get('gold-chart-note').textContent='No daily gold price history available.';return;}
    const projected=projection&&projection.state==='ready'?projection.rows:[];
    const max=Math.max(...rows.map(row=>row.price),...projected.map(row=>row.upper));
    const maxY=Math.max(100000,Math.ceil(max*1.16/100000)*100000);
    const first=rows[0].ts,last=rows[rows.length-1].ts;
    const end=projected.length?projected[projected.length-1].ts:last;
    const x=ts=>L+(end===first?.5:(ts-first)/(end-first))*plotW;
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
    const candleData=mode==='candles'?buildCandles(rows,range):[];
    if(mode==='candles'){
      const bodyWidth=Math.max(6,Math.min(34,plotW/(candleData.length+3)*.70));
      for(const c of candleData){
        const xx=x(c.ts),rise=c.close>c.open,fall=c.close<c.open;
        const kind=rise?'up':fall?'down':'flat';
        svg.appendChild(node('line',{class:'gold-candle-wick gold-candle-'+kind,
          x1:xx,y1:y(c.high),x2:xx,y2:y(c.low)}));
        const top=Math.min(y(c.open),y(c.close)),height=Math.max(3,Math.abs(y(c.open)-y(c.close)));
        svg.appendChild(node('rect',{class:'gold-candle-body gold-candle-'+kind,
          x:xx-bodyWidth/2,y:top,width:bodyWidth,height:height}));
      }
    }else{
      const groups=[];let group=[];
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
        }else svg.appendChild(node('circle',{cx:x(batch[0].ts),cy:y(batch[0].price),r:3,fill:'#ffd36b'}));
      }
    }
    const mean=average(rows);
    svg.appendChild(node('line',{class:'gold-mean',x1:L,x2:W-R,y1:y(mean),y2:y(mean)}));
    if(projected.length){
      const observed=rows[rows.length-1];
      svg.appendChild(node('line',{class:'gold-future-separator',x1:x(last),x2:x(last),y1:T,y2:base}));
      const low=[[x(last),y(observed.price)],...projected.map(r=>[x(r.ts),y(r.lower)])];
      const high=projected.map(r=>[x(r.ts),y(r.upper)]).reverse();
      svg.appendChild(node('path',{class:'gold-forecast-band',d:'M'+[...low,...high].map(pair=>pair.join(',')).join(' L')+' Z'}));
      svg.appendChild(node('path',{class:'gold-forecast-line',d:'M'+[[x(last),y(observed.price)],...projected.map(r=>[x(r.ts),y(r.price)])].map(pair=>pair.join(',')).join(' L')}));
      svg.appendChild(node('text',{class:'gold-axis',x:x(end),y:H-2,'text-anchor':'end'},'Est. '+dateText(end,true)));
    }
    if(mode==='candles'){
      const candle=candleData.find(c=>selectedTs!==null&&c.from<=selectedTs&&selectedTs<=c.to)
        ||candleData[candleData.length-1];
      if(candle){
        svg.appendChild(node('line',{class:'gold-focus-line',x1:x(candle.ts),x2:x(candle.ts),y1:T,y2:base}));
        get('gold-chart-note').textContent=dateText(candle.from,true)+' – '+dateText(candle.to,true)+
          ' · O '+number(candle.open)+' · H '+number(candle.high)+
          ' · L '+number(candle.low)+' · C '+number(candle.close);
      }
    }else{
      const chosen=rows.find(r=>r.ts===selectedTs)||rows[rows.length-1];
      svg.appendChild(node('line',{class:'gold-focus-line',x1:x(chosen.ts),x2:x(chosen.ts),y1:T,y2:base}));
      svg.appendChild(node('circle',{class:'gold-focus-dot',cx:x(chosen.ts),cy:y(chosen.price),r:6}));
      get('gold-chart-note').textContent=dateText(chosen.ts)+' · '+number(chosen.price)+' cash per bar';
    }
    // Transform browser pointer coordinates through the SVG screen matrix.
    // Pixel/viewBox ratios drift if the SVG letterboxes or the user zooms.
    const tooltip=get('gold-tooltip');
    if(tooltip)tooltip.hidden=true;
    const candidates=mode==='candles'?candleData:rows;
    const focusLine=svg.querySelector('.gold-focus-line');
    let focusDot=svg.querySelector('.gold-focus-dot');
    if(!focusDot){
      focusDot=node('circle',{class:'gold-focus-dot',r:6,cx:-100,cy:-100});
      svg.appendChild(focusDot);
    }
    function hideHover(){if(tooltip)tooltip.hidden=true;}
    function showHover(evt){
      const screen=svg.getScreenCTM();
      if(!screen||!candidates.length)return;
      const cursor=svg.createSVGPoint();
      cursor.x=evt.clientX;cursor.y=evt.clientY;
      let pos;
      try{pos=cursor.matrixTransform(screen.inverse());}catch(_){hideHover();return;}
      if(pos.x<L-12||pos.x>x(last)+10||pos.y<T-14||pos.y>base+16){
        hideHover();return;
      }
      const selected=candidates.reduce((closest,item)=>
        Math.abs(x(item.ts)-pos.x)<Math.abs(x(closest.ts)-pos.x)?item:closest,candidates[0]);
      const cx=x(selected.ts);
      const closePrice=mode==='candles'?selected.close:selected.price;
      const cy=y(closePrice);
      if(focusLine){
        focusLine.setAttribute('x1',cx);focusLine.setAttribute('x2',cx);
      }
      focusDot.setAttribute('cx',cx);focusDot.setAttribute('cy',cy);
      const label=mode==='candles'
        ?dateText(selected.from,true)+' – '+dateText(selected.to,true)+
         '\nOPEN  '+number(selected.open)+'\nHIGH  '+number(selected.high)+
         '\nLOW   '+number(selected.low)+'\nCLOSE '+number(selected.close)
        :dateText(selected.ts)+'\n'+number(selected.price)+' cash per bar';
      get('gold-chart-note').textContent=label.replace(/\n/g,' · ');
      if(!tooltip)return;
      tooltip.textContent=label;
      tooltip.hidden=false;
      const point=svg.createSVGPoint();point.x=cx;point.y=cy;
      const anchor=point.matrixTransform(screen);
      const bounds=svg.parentElement.getBoundingClientRect();
      const margin=9,localX=anchor.x-bounds.left,localY=anchor.y-bounds.top;
      const left=Math.max(margin,Math.min(bounds.width-tooltip.offsetWidth-margin,
        localX+14+tooltip.offsetWidth>bounds.width?localX-tooltip.offsetWidth-15:localX+14));
      const above=localY-tooltip.offsetHeight-13;
      tooltip.style.left=Math.round(left)+'px';
      tooltip.style.top=Math.round(above<margin?localY+13:above)+'px';
    }
    svg.onpointermove=showHover;
    svg.onpointerdown=showHover;
    svg.onpointerleave=function(evt){if(evt.pointerType!=='touch')hideHover();};
  }
  function init(){
    const rangeButtons=Array.from(document.querySelectorAll('[data-range]'));
    const chartButtons=Array.from(document.querySelectorAll('[data-chart-mode]'));
    const qty=get('gold-count'),cash=get('gold-cash'),quick=Array.from(document.querySelectorAll('[data-bars]'));
    let price=null,rows=[],range='30',selected=null,forecast=null,chartMode='line';
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
          renderHistory();renderChart(sliceDays(rows,range),selected,forecast,chartMode,range);
        });
        host.appendChild(btn);
      }
    }
    function showRange(){
      const selectedRows=sliceDays(rows,range);
      selected=null;
      renderChart(selectedRows,null,forecast,chartMode,range);
      for(const b of rangeButtons)b.setAttribute('aria-pressed',String(b.dataset.range===range));
    }
    for(const b of rangeButtons)b.addEventListener('click',function(){if(!rows.length)return;range=b.dataset.range;showRange();renderHistory();});
    function changeMode(){
      for(const button of chartButtons)button.setAttribute('aria-pressed',String(button.dataset.chartMode===chartMode));
      const explanation=get('gold-candle-explainer');
      if(explanation)explanation.hidden=chartMode!=='candles';
      if(rows.length)renderChart(sliceDays(rows,range),selected,forecast,chartMode,range);
    }
    for(const button of chartButtons)button.addEventListener('click',function(){
      chartMode=button.dataset.chartMode;changeMode();
    });
    let resizeTask;
    if(typeof window!=='undefined')window.addEventListener('resize',function(){
      clearTimeout(resizeTask);
      resizeTask=setTimeout(function(){
        if(rows.length)renderChart(sliceDays(rows,range),selected,forecast,chartMode,range);
      },100);
    });
    fetch('data/gold-observations.json',{cache:'no-store'}).then(response=>response.ok?response.json():null).then(data=>{
      const list=data&&Array.isArray(data.observations)?data.observations:[];
      const newest=list[list.length-1];
      const target=get('gold-observed-at');
      if(newest&&target&&Number.isSafeInteger(newest.observedAt)&&Number.isSafeInteger(newest.price)){
        const date=new Date(newest.observedAt).toLocaleString('en-US',{
          timeZone:'UTC',month:'short',day:'numeric',hour:'2-digit',minute:'2-digit',hour12:false});
        target.textContent='Last four-hour check: '+date+' UTC · '+number(newest.price)+' cash';
      }
    }).catch(()=>{});

    function renderForecast(){
      const forecastSource=root.GoldForecast;
      forecast=forecastSource&&typeof forecastSource.evaluate==='function'?forecastSource.evaluate(rows):{state:'insufficient',reason:'Forecast module unavailable.'};
      const message=get('gold-forecast-message');
      if(forecast.state!=='ready'){
        message.textContent=forecast.reason||'Not enough daily history for a validated forecast.';
        get('gold-forecast-model').textContent='Model: not selected';
        get('gold-forecast-backtest').textContent='Validation requires sufficient consecutive daily observations.';
        return;
      }
      const one=forecast.rows[0],seven=forecast.rows[6];
      get('gold-forecast-1').textContent=number(one.price);
      get('gold-forecast-7').textContent=number(seven.price);
      get('gold-forecast-range-1').textContent='Observed-error range: '+number(one.lower)+'–'+number(one.upper);
      get('gold-forecast-range-7').textContent='Observed-error range: '+number(seven.lower)+'–'+number(seven.upper);
      message.textContent='Daily-price outlook through '+dateText(seven.ts)+' (UTC).';
      get('gold-forecast-model').textContent='Selected model: '+forecast.modelLabel+(forecast.model==='naive'?' · advanced models did not beat the baseline by 5%':' · improvement vs no-change: '+forecast.improvementPct+'%');
      get('gold-forecast-backtest').textContent='Walk-forward validation: '+forecast.validations+' origins. 1-day mean absolute error '+number(forecast.modelMae1)+' cash (no-change: '+number(forecast.baselineMae1)+'). 7-day mean absolute error '+number(forecast.modelMae7)+' (no-change: '+number(forecast.baselineMae7)+').';
    }
    fetch(SOURCE,{headers:{'Accept':'application/json'},cache:'no-store'})
      .then(response=>{if(!response.ok)throw Error('Price service returned HTTP '+response.status);return response.json();})
      .then(data=>{rows=normalize(data).rows;renderForecast();renderStats();})
      .catch(()=>{get('gold-price').textContent='Unavailable';get('gold-asof').textContent='No price data could be loaded.';get('gold-error').hidden=false;get('gold-error').textContent='The independent price source is unavailable right now. No last-known price has been substituted. You can check the linked source directly.';get('gold-chart-note').textContent='Gold price history unavailable.';get('gold-days').textContent='No verified daily prices available.';get('gold-forecast-message').textContent='Forecast unavailable without verified price history.';});
  }
  if(typeof module!=='undefined'&&module.exports)module.exports={normalize,sliceDays,diffDays,average,changeText,buildCandles,candleSpan};
  if(typeof document!=='undefined')document.addEventListener('DOMContentLoaded',init);
})(typeof globalThis!=='undefined'?globalThis:this);