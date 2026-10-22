'use strict';
/* Optional approved local map photography only; never hotlink third-party art. */
(function(root){
  const REQUIRED=Object.freeze({
    Bakurani:'bakurani.webp',Ozeti:'ozeti.webp',Zestafona:'zestafona.webp'
  });
  const source='assets/map-banners/';
  let promised;
  async function config(){
    if(!promised)promised=fetch(source+'manifest.json',{cache:'no-store'})
      .then(r=>r.ok?r.json():null).catch(()=>null);
    return promised;
  }
  async function decorateMapRow(row,rawName){
    if(!row||typeof rawName!=='string')return false;
    const name=Object.keys(REQUIRED).find(n=>n.toLowerCase()===rawName.trim().toLowerCase());
    if(!name)return false;
    const data=await config();
    if(!data||data.schemaVersion!==1||!data.images||
      data.images[name]!==REQUIRED[name])return false;
    const img=new Image();
    const localUrl=source+REQUIRED[name];
    // Only locally packaged, attribution-cleared map art may be displayed.
    if(!await new Promise(resolve=>{
      img.onload=()=>resolve(true);img.onerror=()=>resolve(false);
      img.src=localUrl;
    }))return false;
    if(!row.isConnected)return false;
    row.classList.add('map-banner-present');
    row.style.setProperty('--map-banner','url("'+localUrl+'")');
    return true;
  }
  root.OneADAARMapBanners=Object.freeze({decorateMapRow});
})(window);
