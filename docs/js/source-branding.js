'use strict';
// Steam brand credit appears only after this tab has completed verified consent.
// Never infer consent from a SteamID, an avatar or a merely signed-in session.
(function(){
  const logo=document.querySelector('[data-steam-logo]');
  if(!logo)return;
  let connected=false;
  try {
    const s=JSON.parse(sessionStorage.getItem('1adaar-steam-session-v1')||'null');
    const until=Number(sessionStorage.getItem('1adaar-steam-consented-v1'));
    connected=Boolean(s&&typeof s.token==='string'&&s.token.length>=40&&
      s.expiresAt>Date.now()/1000+5&&until===s.expiresAt);
  } catch (_) {connected=false;}
  logo.hidden=!connected;
})();
