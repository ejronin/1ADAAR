'use strict';
// The landing page must not resume at the reports anchor after a stale navigation.
(function () {
  if(location.hash==='#reports')history.replaceState(null,'',location.pathname+location.search);
  if(/^#match-\d+$/.test(location.hash))return; // Keep direct match links functional.
  if('scrollRestoration' in history)history.scrollRestoration='manual';
  const toTop=()=>window.scrollTo({top:0,left:0,behavior:'instant'});
  window.addEventListener('pageshow',toTop,{once:true});
  if(document.readyState==='complete')toTop();
  else window.addEventListener('load',toTop,{once:true});
})();
