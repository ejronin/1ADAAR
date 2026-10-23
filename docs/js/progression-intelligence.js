'use strict';
/* Game-account metrics: only source-verified Tracker data; no fabricated totals. */
(function(root){
  const NS='http://www.w3.org/2000/svg';
  const names=['Assault','Medic','Support','Recon','Driver','Pilot'];
  const by=id=>document.getElementById(id);
  const SVG=(tag,props={},value)=>{
    const n=document.createElementNS(NS,tag);
    for(const [k,v] of Object.entries(props))n.setAttribute(k,String(v));
    if(value!==undefined)n.textContent=String(value);
    return n;
  };
  const fmt=n=>Number.isSafeInteger(n)&&n>=0?n.toLocaleString('en-US'):'—';
  function draw(record){
    const svg=by('pi-role-plot'),empty=by('pi-role-plot-empty');
    if(!svg||!empty)return;
    svg.replaceChildren();
    const allowed=Boolean(record&&record.sourceStatus==='verified'&&
      record.maxLevel===100&&record.levels&&names.every(n=>
        Number.isSafeInteger(record.levels[n])&&record.levels[n]>=0&&record.levels[n]<=100));
    const x0=148,span=476;
    for(const tick of [0,25,50,75,100]){
      const x=x0+span*tick/100;
      svg.append(SVG('line',{x1:x,y1:30,x2:x,y2:239,stroke:'#45604b','stroke-width':1,
        'stroke-dasharray':tick===0?'none':'2 5'}));
      svg.append(SVG('text',{x,y:18,'text-anchor':'middle',fill:'#abc3b0','font-size':13},tick));
    }
    if(!allowed){
      svg.setAttribute('aria-label','Role levels not yet verified; blank comparison scale.');
      empty.hidden=false;
      return;
    }
    const accessible=[];
    names.forEach((name,i)=>{
      const y=48+i*35,level=record.levels[name],x=x0+span*level/100;
      svg.append(SVG('text',{x:10,y:y+5,fill:'#ecf5ed','font-size':15},name));
      svg.append(SVG('line',{x1:x0,y1:y,x2:x,y2:y,stroke:'#86f4a4','stroke-width':2,
        'stroke-opacity':.65}));
      svg.append(SVG('circle',{cx:x,cy:y,r:6,fill:'#a5f5ad',stroke:'#0a1710','stroke-width':2}));
      svg.append(SVG('text',{x:650,y:y+5,'text-anchor':'end',fill:'#f1fcf2',
        'font-size':15,'font-weight':700},level));
      accessible.push(name+': level '+level);
    });
    svg.setAttribute('aria-label','WARDOGS Tracker verified role-level comparison: '+accessible.join('; '));
    empty.hidden=true;
  }
  function render(record){
    const allowed=record&&record.sourceStatus==='verified';
    by('pi-unlocks').textContent=allowed?fmt(record.unlocks):'—';
    const rank=allowed&&Number.isSafeInteger(record.leaderboardRank)&&
      Number.isSafeInteger(record.leaderboardPlayers)&&
      record.leaderboardRank>0&&record.leaderboardPlayers>=record.leaderboardRank;
    by('pi-standing').textContent=rank?
      '#'+fmt(record.leaderboardRank)+' / '+fmt(record.leaderboardPlayers):'—';
    const avatar=by('pi-steam-avatar');
    if(avatar){
      const allowedUrl=allowed&&typeof record.avatarUrl==='string'&&
        /^https:\/\/avatars(?:\.akamai)?\.steamstatic\.com\/[A-Za-z0-9_./-]+\.(?:jpg|jpeg|png|webp)$/i.test(record.avatarUrl);
      if(allowedUrl){
        avatar.src=record.avatarUrl;
        avatar.alt='Steam profile picture for verified WARDOGS account';
        avatar.hidden=false;
      }else{
        avatar.hidden=true;avatar.removeAttribute('src');avatar.alt='';
      }
    }
    draw(allowed?record:null);
  }
  root.OneADAARProgressionIntelligence=Object.freeze({render});
})(window);
