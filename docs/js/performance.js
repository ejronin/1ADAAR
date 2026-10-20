'use strict';
/* Zero-dependency, keyboard-operable SVG graphics. All labels use textContent. */
(function (root) {
  const M=root.OneADAARMetrics, NS='http://www.w3.org/2000/svg';
  let identity=0;
  function el(tag,cls,value) {
    const n=document.createElement(tag);
    if(cls)n.className=cls;
    if(value!==undefined)n.textContent=String(value);
    return n;
  }
  function se(tag,attrs={},value) {
    const n=document.createElementNS(NS,tag);
    for(const [key,val] of Object.entries(attrs))n.setAttribute(key,String(val));
    if(value!==undefined)n.textContent=String(value);
    return n;
  }
  function graph(container,rows,metric,report) {
    container.replaceChildren();
    const series=metric==='kills'?
      [{label:'Kills',key:'kills',color:'#86f4a4',fill:true},
       {label:'Deaths',key:'deaths',color:'#e7ad96',fill:false}]:
      metric==='career'?
      [{label:'Career K/D',key:'kd',color:'#86f4a4',fill:true}]:
      [{label:'Match K/D',key:'kd',color:'#86f4a4',fill:true},
       {label:'Five-match rolling',key:'rolling',color:'#e4c47d',fill:false}];
    const raw=rows.flatMap(row=>series.map(s=>row[s.key]).filter(v=>typeof v==='number'&&Number.isFinite(v)));
    const isCount=metric==='kills';
    const peak=Math.max(1,...raw)*1.14;
    const scale=peak<=5?1:peak<=15?2:peak<=50?5:10;
    const ymax=Math.max(isCount?4:1,Math.ceil(peak/(4*scale))*4*scale);
    const box={x:67,y:24,w:684,h:247};
    const x=i=>box.x+(rows.length===1?box.w/2:box.w*i/(rows.length-1));
    const y=value=>box.y+box.h*(1-Math.max(0,value)/ymax);
    const svg=se('svg',{viewBox:'0 0 780 323',class:'perf-svg',role:'img',
      'aria-label':(metric==='career'?'Career K/D':isCount?'Kills versus deaths':'Match K/D and five-match rolling trend')+' for '+rows.length+' observations'});
    svg.append(se('title',{},'WARDOGS player performance'));
    svg.append(se('desc',{},'Exact values are available in the data table beneath this interactive graph.'));
    const gradientId='aarPerf'+(++identity),defs=se('defs'),
      grad=se('linearGradient',{id:gradientId,x1:'0',y1:'0',x2:'0',y2:'1'});
    grad.append(se('stop',{offset:'0%','stop-color':'#77ef99','stop-opacity':'0.25'}),
      se('stop',{offset:'100%','stop-color':'#77ef99','stop-opacity':'0'}));
    defs.append(grad);svg.append(defs);
    for(let i=0;i<=4;i++){
      const v=ymax*i/4;
      svg.append(se('line',{x1:box.x,y1:y(v),x2:box.x+box.w,y2:y(v),class:'perf-gridline'}));
      svg.append(se('text',{x:box.x-14,y:y(v)+4,'text-anchor':'end',class:'perf-axis-label'},
        isCount?String(Math.round(v)):v.toFixed(v<10?2:1)));
    }
    for(const i of [...new Set([0,Math.floor((rows.length-1)/2),rows.length-1])]){
      const anchor=rows.length===1?'middle':i===0?'start':i===rows.length-1?'end':'middle';
      svg.append(se('text',{x:x(i),y:304,'text-anchor':anchor,class:'perf-axis-label'},M.tickDate(rows[i].date)));
    }
    svg.append(se('line',{x1:box.x,y1:box.y+box.h,x2:box.x+box.w,y2:box.y+box.h,class:'perf-baseline'}));
    for(const s of series.slice().reverse()){
      const chunks=[];let run=[];
      rows.forEach((row,i)=>{
        const value=row[s.key];
        if(typeof value!=='number'||!Number.isFinite(value)){
          if(run.length)chunks.push(run);
          run=[];return;
        }
        run.push({px:x(i),py:y(value),i,value});
      });
      if(run.length)chunks.push(run);
      for(const points of chunks){
        const path=points.map((p,j)=>(j?'L ':'M ')+p.px.toFixed(2)+' '+p.py.toFixed(2)).join(' ');
        if(s.fill&&points.length>1)svg.append(se('path',{
          d:path+' L '+points[points.length-1].px+' '+(box.y+box.h)+' L '+points[0].px+' '+(box.y+box.h)+' Z',
          fill:'url(#'+gradientId+')'}));
        if(points.length>1)svg.append(se('path',{d:path,fill:'none',stroke:s.color,
          'stroke-width':s.key==='rolling'?2.3:3,'stroke-linecap':'round','stroke-linejoin':'round',
          class:s.key==='rolling'?'perf-dashed':'perf-stroke'}));
        for(const p of points){
          const group=se('g',{class:'perf-point'});
          const label=M.tickDate(rows[p.i].date)+' · '+(rows[p.i].map||'Career snapshot')+' · '+s.label+': '+
            (isCount?String(p.value):p.value.toFixed(2));
          group.append(se('circle',{cx:p.px,cy:p.py,r:4.7,fill:'#0c1710',stroke:s.color,'stroke-width':2.4,class:'perf-dot'}));
          const hit=se('circle',{cx:p.px,cy:p.py,r:16,fill:'transparent',tabindex:'0',role:'button',
            'aria-label':label,class:'perf-hit'});
          hit.append(se('title',{},label));
          const describe=()=>{report.hidden=false;report.textContent=label;};
          hit.addEventListener('focus',describe);
          hit.addEventListener('mouseenter',describe);
          hit.addEventListener('click',describe);
          hit.addEventListener('keydown',e=>{
            if(e.key==='Enter'||e.key===' '){e.preventDefault();describe();}
          });
          group.append(hit);svg.append(group);
        }
      }
    }
    container.append(svg);
    return series;
  }
  function mount(host,config) {
    if(!host||!config||typeof config.key!=='string')return;
    const matches=M.matchSeries(config.matches,config.key);
    const careers=M.careerSeries(config.career);
    // Preserve a visitor's selected view while the background history shard loads.
    const oldMetric=host.querySelector('.perf-tab[aria-pressed="true"]')?.dataset.metric;
    const oldRange=host.querySelector('.perf-window')?.value;
    let metric=['kd','kills','career'].includes(oldMetric)?oldMetric:'kd';
    let range=oldRange==='25'?25:oldRange==='all'?Infinity:10;
    host.replaceChildren();
    const header=el('header','perf-header'),
      left=el('div','perf-heading');
    left.append(el('span','eyebrow','PLAYER RESULTS OVER TIME'),
      el('h3','','Performance over time'),
      el('p','perf-subtitle','See recent results and how your overall stats have changed.'));
    header.append(left,el('span','perf-source',config.demo?'SAMPLE / MADE-UP STATS':'DATA FROM WARCON'));
    host.append(header);
    const toolbar=el('div','perf-toolbar'),tabs=el('div','perf-tabs');
    tabs.setAttribute('role','group');
    tabs.setAttribute('aria-label','Select a performance metric');
    for(const [key,label] of [['kd','K/D OVER TIME'],['kills','KILLS / DEATHS'],['career','ALL-TIME K/D']]){
      const button=el('button','perf-tab',label);
      button.type='button';button.dataset.metric=key;
      button.addEventListener('click',()=>{metric=key;update();});
      tabs.append(button);
    }
    const selectLabel=el('label','perf-window-label','WINDOW');
    const select=el('select','perf-window');
    select.setAttribute('aria-label','Number of recent observations');
    for(const [value,label] of [['10','Last 10'],['25','Last 25'],['all','All available']]){
      const option=el('option','',label);option.value=value;select.append(option);
    }
    select.value=range===Infinity?'all':String(range);
    select.addEventListener('change',()=>{
      if(select.disabled)return;
      range=select.value==='all'?Infinity:Number(select.value);
      update();
    });
    selectLabel.append(select);
    toolbar.append(tabs,selectLabel);host.append(toolbar);
    const coverage=el('p','perf-coverage');
    host.append(coverage);
    const summary=el('div','perf-summary'),canvas=el('div','perf-canvas'),
      empty=el('div','perf-empty'),legend=el('div','perf-legend'),
      inspector=el('div','perf-inspector'),footnote=el('p','perf-footnote'),
      details=el('details','perf-details'),scroller=el('div','perf-data-scroll');
    inspector.setAttribute('role','status');inspector.setAttribute('aria-live','polite');
    details.append(el('summary','','View exact chart data'),scroller);
    host.append(summary,canvas,empty,legend,inspector,footnote,details);
    function tile(label,value,caption){
      const card=el('div','perf-mini-stat');
      card.append(el('span','',label),el('strong','',value),el('small','',caption));
      return card;
    }
    function table(rows){
      scroller.replaceChildren();
      const headings=metric==='career'?['Date','Career K/D','Kills','Deaths','Matches']:
        metric==='kills'?['Date','Map','Kills','Deaths']:
        ['Date','Map','Match K/D','5-game K/D','Kills','Deaths'];
      const t=el('table','perf-table'),head=el('thead'),line=el('tr');
      headings.forEach(v=>line.append(el('th','',v)));head.append(line);t.append(head);
      const body=el('tbody');
      for(const row of rows){
        const cols=metric==='career'?[M.tickDate(row.date),M.format(row.kd),row.kills,row.deaths,row.matches]:
          metric==='kills'?[M.tickDate(row.date),row.map,row.kills,row.deaths]:
          [M.tickDate(row.date),row.map,M.format(row.kd),M.format(row.rolling),row.kills,row.deaths];
        const tr=el('tr');cols.forEach(v=>tr.append(el('td','',v)));body.append(tr);
      }
      t.append(body);scroller.append(t);
    }
    function update(){
      const full=metric==='career'?careers:matches;
      const total=full.length;
      // Do not leave a live selector enabled when every option renders the same data.
      // Each metric may have different match and career sample sizes.
      if(total<=10)range=10;
      else if(total<=25&&range===25)range=Infinity;
      select.disabled=total<=10;
      for(const option of select.children){
        if(option.value==='10')option.textContent='Last 10';
        if(option.value==='25'){
          option.textContent='Last 25';
          option.disabled=total<=25;
        }
        if(option.value==='all')option.textContent='All '+total+' available';
      }
      select.value=range===Infinity?'all':String(range);
      const rows=M.windowed(full,range);
      coverage.textContent=total===0?'No saved results yet':
        total<=10?'Only '+total+' observations available · More windows unlock as data grows':
        rows.length+' of '+total+' '+(metric==='career'?'career snapshots':'completed matches')+' in view';
      for(const button of tabs.children)button.setAttribute('aria-pressed',String(button.dataset.metric===metric));
      for(const node of [summary,canvas,empty,legend,inspector])node.replaceChildren();
      empty.hidden=true;inspector.hidden=true;footnote.hidden=false;details.hidden=false;
      if(!rows.length){
        empty.hidden=false;footnote.hidden=true;details.hidden=true;
        empty.append(el('strong','',metric==='career'?'All-time changes will appear here':'Waiting for saved match results'),
          el('p','',metric==='career'?
            'We can show changes starting when we began saving WARCON data. Earlier totals are not available.':
            'Kills and deaths from saved completed matches will show here when available.'));
        return;
      }
      const last=rows[rows.length-1];
      if(metric==='career'){
        summary.append(tile('SNAPSHOTS',String(rows.length),'saved daily updates'),
          tile('LATEST CAREER K/D',M.format(last.kd),'WARCON career totals'),
          tile('TRACKED SINCE',M.tickDate(rows[0].date),'from saved results only'));
      }else if(metric==='kills'){
        summary.append(tile('MATCHES IN VIEW',String(rows.length),'completed match records'),
          tile('KILLS IN VIEW',String(rows.reduce((sum,row)=>sum+row.kills,0)),'kills in shown matches'),
          tile('DEATHS IN VIEW',String(rows.reduce((sum,row)=>sum+row.deaths,0)),'deaths in shown matches'));
      }else{
        summary.append(tile('MATCHES IN VIEW',String(rows.length),'completed match records'),
          tile('LATEST MATCH K/D',M.format(last.kd),'last saved match'),
          tile('FIVE-MATCH K/D',M.format(last.rolling),last.rolling===null?'unlocks after 5 matches':'total kills / total deaths'));
      }
      const graphSeries=graph(canvas,rows,metric,inspector);
      for(const s of graphSeries){
        if(s.key==='rolling'&&!rows.some(r=>r.rolling!==null))continue;
        const indicator=el('span','perf-legend-item'),dot=el('i');
        dot.style.background=s.color;
        indicator.append(dot,document.createTextNode(s.label));legend.append(indicator);
      }
      inspector.hidden=false;
      inspector.textContent='Focus or tap a point to inspect its exact recorded result.';
      footnote.textContent=metric==='career'?
        'Dated WARCON career snapshots. Up to 60 changed daily observations within the past 180 days; no inferred past values.':
        metric==='kills'?
        'Kills and deaths are from completed WARCON match records in the available 1ADAAR archive.':
        'Five-match K/D is total kills divided by total deaths over five matches. If there are no deaths, we show the kill count. If there are no kills or deaths, we show a dash.';
      if(config.demo)footnote.textContent='DEMO / FICTIONAL — '+footnote.textContent;
      table(rows);
    }
    update();
  }
  root.OneADAARPerformance=Object.freeze({mount});
})(window);
