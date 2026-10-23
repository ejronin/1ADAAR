'use strict';
/* Player profile v1.1.0: truthful career tiles and saved-match insights.
 * The displayed percentages are never guessed from WARCON career totals.
 */
(function (root) {
  function make(tag,cls,text) {
    const n=document.createElement(tag);
    if(cls)n.className=cls;
    if(text!==undefined)n.textContent=String(text);
    return n;
  }
  const number=v=>Number.isSafeInteger(v)&&v>=0?v.toLocaleString():'—';
  const ratio=(a,b)=>Number.isSafeInteger(a)&&Number.isSafeInteger(b)&&a>=0&&b>=0?
    (b===0?(a===0?'—':a+' (0 deaths)'):(a/b).toFixed(2)):'—';
  const time=v=>Number.isSafeInteger(v)&&v>=0?Math.floor(v/60)+'h '+(v%60)+'m':'—';
  const rate=(n,d)=>d>0?(100*n/d).toFixed(1)+'%':'—';
  const validKey=key=>/^[a-f0-9]{64}$/.test(key);

  function career(primary,secondary,entry) {
    primary.replaceChildren();secondary.replaceChildren();
    // WARCON's leaderboard is ALL-TIME ON THIS SERVER. The public WARDOGS
    // Tracker profile currently publishes progression, NOT global combat K/D.
    // Never recycle this-server totals as global totals.
    const add=(host,label,serverValue,compact)=>{
      const card=make('div',compact?'career-secondary-card career-source-pair':'metric-tile career-source-pair');
      card.append(make('span','career-pair-heading',label));
      const row=make('div','career-pair-values');
      for(const [source,value] of [['1AD SERVER',serverValue],['TRACKER · ALL','—']]){
        const group=make('div','career-pair-column');
        group.append(make('small','career-pair-source',source),
          make('strong','career-pair-number',value));
        if(source.startsWith('TRACKER'))group.title='Global combat total is not published by WARDOGS Tracker.';
        row.append(group);
      }
      card.append(row);host.append(card);
    };
    for(const [label,value] of [
      ['K/D',ratio(entry.kills,entry.deaths)],['Kills',number(entry.kills)],
      ['Deaths',number(entry.deaths)],['Matches',number(entry.matches)]])add(primary,label,value,false);
    for(const [label,value] of [
      ['Wins',number(entry.wins)],['Playtime',time(entry.minutes)],
      ['Seeding time',time(entry.seedMinutes)]])add(secondary,label,value,true);
    primary.insertAdjacentElement('beforebegin',(()=>{
      // No duplicated source legend on repeated player selections.
      const previous=document.getElementById('career-source-note');if(previous)previous.remove();
      return make('p','career-source-note',
        '1AD = WARCON totals for this server. Tracker does not yet publish global combat totals; — means unavailable, not zero.');
    })());
  }

  function observations(records,key) {
    const matches=[];
    for(const m of Array.isArray(records)?records:[]){
      const p=m?.players?.find(x=>x.key===key);
      if(!p)continue;
      matches.push({map:m.map,faction:p.faction,result:p.result});
    }
    return matches;
  }
  function groupTop(items,key) {
    const counts=new Map();let denominator=0;
    for(const item of items){
      const name=item[key];
      if(typeof name!=='string'||!name.trim()||/^(unknown|unassigned|—)/i.test(name))continue;
      denominator++;
      counts.set(name,(counts.get(name)||0)+1);
    }
    const sorted=[...counts].sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0]));
    if(!sorted.length)return {name:null,count:0,denominator:0,tied:false};
    return {name:sorted[0][0],count:sorted[0][1],denominator,tied:sorted.length>1&&sorted[0][1]===sorted[1][1]};
  }

  function avatar(frame,entry) {
    if(!frame)return;
    frame.replaceChildren();
    const fallback=make('span','avatar-initials',(entry.name||'?').trim().split(/\s+/).slice(0,2)
      .map(word=>word.slice(0,1).toUpperCase()).join('')||'?');
    frame.append(fallback);
    if(entry.demo)return;
    // Only a Steam CDN image explicitly sanitized by the private collector is allowed.
    const url=entry.avatar;
    if(typeof url!=='string'||!/^https:\/\/(?:avatars\d*\.steamstatic\.com|steamcommunity-a\.akamaihd\.net|community\.cloudflare\.steamstatic\.com)\/[A-Za-z0-9/_\-.]+\.(?:jpg|jpeg|png)(?:\?[A-Za-z0-9=&_-]+)?$/i.test(url))return;
    const picture=make('img','steam-avatar');
    picture.alt='Steam profile picture of '+entry.name;
    picture.referrerPolicy='no-referrer';
    picture.loading='lazy';
    picture.decoding='async';
    picture.onerror=()=>picture.remove();
    picture.src=url;
    frame.append(picture);
  }

  function donut(host,entry){
    const known=Number(entry.wins)+Number(entry.losses)+Number(entry.draws);
    const isKnown=[entry.wins,entry.losses,entry.draws].every(x=>Number.isSafeInteger(x)&&x>=0);
    const part=isKnown?entry.wins:0,denom=isKnown?known:0,share=denom?part/denom:0;
    const ring=make('div','profile-win-donut');
    const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
    svg.setAttribute('viewBox','0 0 120 120');svg.setAttribute('role','img');
    svg.setAttribute('aria-label',denom?
      rate(part,denom)+' career win rate, '+part+' wins out of '+denom+' recorded WARCON career results':
      'Career win rate not available');
    for(const [type,segment] of [['track','100 100'],['progress',(share*100).toFixed(3)+' 100']]){
      const circle=document.createElementNS('http://www.w3.org/2000/svg','circle');
      for(const [key,val] of Object.entries({cx:60,cy:60,r:45,pathLength:100,
        'stroke-dasharray':segment,class:'donut-'+type}))circle.setAttribute(key,val);
      svg.append(circle);
    }
    ring.append(svg);
    const inside=make('div','donut-center');
    inside.append(make('strong','',denom?rate(part,denom):'—'),make('small','','Win rate'));
    ring.append(inside);host.append(ring);
    host.append(make('p','snapshot-count',denom?number(part)+' wins / '+number(denom)+' career results':
      'No recorded career results'));
    host.append(make('p','snapshot-explain',entry.demo?'Fictional PlayerOne career':'WARCON all-time career'));
  }

  function insight(host,label,group,kind,scope) {
    const card=make('section','snapshot-insight');
    card.append(make('h4','',label));
    const heading=make('div','snapshot-insight-heading');
    if(group.name&&kind==='faction'&&root.OneADAARFactions)heading.append(root.OneADAARFactions.label(group.name));
    else heading.append(make('strong','',group.name?(group.tied?'Tied: ':'')+group.name:'Not enough data'));
    card.append(heading);
    const value=group.denominator?rate(group.count,group.denominator):'—';
    const bar=make('div','snapshot-track');
    bar.setAttribute('role','img');
    bar.setAttribute('aria-label',group.name?
      group.name+' '+group.count+' of '+group.denominator+' saved '+kind+' appearances':
      'No known '+kind+' appearances');
    const fill=make('div','snapshot-fill');
    fill.style.width=group.denominator?100*group.count/group.denominator+'%':'0%';
    if(kind==='faction'&&root.OneADAARFactions&&group.name){
      const faction=root.OneADAARFactions.identify(group.name);
      if(faction)fill.style.backgroundColor=faction.color;
    }
    bar.append(fill);card.append(bar);
    card.append(make('p','snapshot-count',group.name?
      number(group.count)+' of '+number(group.denominator)+' '+scope+' · '+value:
      'No saved matches with known '+kind));
    card.append(make('p','snapshot-explain',group.tied?'Several share the top count; showing one.':'Participation, not win rate'));
    host.append(card);
  }

  function snapshot(host,entry,records) {
    host.replaceChildren();
    const header=make('div','snapshot-heading');
    header.append(make('h3','','Player snapshot'),
      make('p','',entry.demo?'Fictional PlayerOne sample data':'Career data and recent saved matches'));
    host.append(header);
    const win=make('section','snapshot-win');
    win.append(make('h4','','Career win rate'));donut(win,entry);host.append(win);
    const observed=observations(records,entry.key);
    const knownFaction=groupTop(observed,'faction');
    const knownMap=groupTop(observed,'map');
    insight(host,'Most-played faction',knownFaction,'faction','known faction appearances');
    insight(host,'Most-played map',knownMap,'map','known map appearances');
    host.append(make('p','snapshot-disclaimer','Participation uses this player’s matches in the latest 120 saved server matches. Career win rate comes from WARCON all-time totals.'));
  }
  root.OneADAARProfile=Object.freeze({career,snapshot,avatar,groupTop,observations});
})(window);
