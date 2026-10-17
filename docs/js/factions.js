'use strict';
/* Faction artwork traced from the official images supplied by the community.
   Only known WARCON factions get team colors; unknown names stay neutral. */
(function(root) {
  const palette=Object.freeze({
    lonestar:Object.freeze({name:'Lonestar',color:'#465eff',icon:'assets/factions/lonestar.svg'}),
    valkyra:Object.freeze({name:'Valkyra',color:'#ee4138',icon:'assets/factions/valkyra.svg'}),
    manticore:Object.freeze({name:'Manticore',color:'#3eba42',icon:'assets/factions/manticore.svg'})
  });
  function identify(name) {
    if(typeof name!=='string')return null;
    return palette[name.trim().toLowerCase()]||null;
  }
  function label(name) {
    const info=identify(name);
    const span=document.createElement('span');
    span.className='faction-identity'+(info?' faction-'+info.name.toLowerCase():' faction-unmapped');
    if(info){
      span.style.setProperty('--faction-accent',info.color);
      const image=document.createElement('img');
      image.src=info.icon;image.alt='';image.loading='lazy';
      image.width=24;image.height=24;image.className='faction-emblem';
      span.append(image);
    }
    const text=document.createElement('span');text.textContent=String(name||'—');
    span.append(text);
    return span;
  }
  root.OneADAARFactions=Object.freeze({identify,label});
})(window);
