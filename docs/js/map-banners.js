'use strict';
/* Official WARDOGS map art. Resolve images against the PAGE URL, not the CSS
   filename; otherwise CSS var() backgrounds can resolve as assets/assets/....
   Named map previews remain useful even when no completed match is archived. */
(function(root){
  const maps=Object.freeze({
    bakurani:'bakurani',ozeti:'ozeti',zestafona:'zestafona'
  });
  const galleryBase=new URL('assets/map-banners/',document.baseURI);

  function resolveMap(rawName){
    if(typeof rawName!=='string')return null;
    return maps[rawName.trim().toLowerCase()]||null;
  }

  function decorateMapRow(row,rawName){
    const slug=resolveMap(rawName);
    if(!row||!row.isConnected||!slug)return false;

    // A stale image callback must not restore a previous map after a live update.
    row.dataset.mapBanner=slug;
    const paint=(file,named)=>{
      if(!row.isConnected||row.dataset.mapBanner!==slug)return;
      const url=new URL(file,galleryBase).href;
      row.style.setProperty('--map-banner','url("'+url+'")');
      row.classList.add('map-banner-present');
      row.classList.toggle('map-banner-named',named);
    };

    paint(slug+'-card.webp?v=117',true);
    // On an older cached deployment, preserve the readable DOM map name and
    // fall back to the approved original map preview.
    const testImage=new Image();
    testImage.onerror=()=>paint(slug+'.webp?v=117',false);
    testImage.src=new URL(slug+'-card.webp?v=117',galleryBase).href;
    return true;
  }

  root.OneADAARMapBanners=Object.freeze({resolveMap,decorateMapRow});
})(window);
