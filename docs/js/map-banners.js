'use strict';
/* Three verified local WARDOGS map photographs. Never infer missing match data.
   Named variants are generated from these originals during production packaging.
   Keep readable DOM labels on the original-image fallback. */
(function(root){
 const MAPS=Object.freeze({bakurani:'bakurani',ozeti:'ozeti',zestafona:'zestafona'});
 const base='assets/map-banners/';
 function paint(row,file,withEmbeddedName){
   if(!row||!row.isConnected)return;
   row.classList.add('map-banner-present');
   row.classList.toggle('map-banner-named',withEmbeddedName);
   row.style.setProperty('--map-banner','url("'+base+file+'")');
 }
 function checkImage(url){
   return new Promise(resolve=>{
     const image=new Image();
     image.onload=()=>resolve(true);
     image.onerror=()=>resolve(false);
     image.src=url;
   });
 }
 async function decorateMapRow(row,rawName){
   if(!row||typeof rawName!=='string')return false;
   const slug=MAPS[rawName.trim().toLowerCase()];
   if(!slug)return false;
   // We ship the unmodified original; this works even if the generated named
   // variant hasn't propagated through the Pages cache yet.
   const fallback=slug+'.webp',named=slug+'-card.webp';
   paint(row,fallback,false);
   if(await checkImage(base+named+'?v=112')){
     paint(row,named+'?v=112',true);
     return true;
   }
   if(await checkImage(base+fallback))return true;
   row.classList.remove('map-banner-present','map-banner-named');
   row.style.removeProperty('--map-banner');
   return false;
 }
 root.OneADAARMapBanners=Object.freeze({decorateMapRow});
})(window);
