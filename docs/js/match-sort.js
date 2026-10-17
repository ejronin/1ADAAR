'use strict';
/* Deterministic, side-effect-free sorting of completed match reports. */
(function(root){
  function visible(matches,query,order){
    const search=String(query||'').trim().toLocaleLowerCase();
    return (Array.isArray(matches)?matches:[]).filter(m=>m&&
      (String(m.map||'')+' '+String(m.winner||'')).toLocaleLowerCase().includes(search))
      .slice().sort((a,b)=>{
        const time=Date.parse(a.endedAt)-Date.parse(b.endedAt);
        const diff=Number.isFinite(time)?time:0;
        return (order==='oldest'?diff:-diff)||(Number(a.id)||0)-(Number(b.id)||0);
      });
  }
  const api=Object.freeze({visible});
  if(typeof module!=='undefined'&&module.exports)module.exports=api;
  if(root)root.OneADAARArchive=api;
})(typeof window==='undefined'?null:window);
