'use strict';
/* v1.1 Tier-1 gate. A read-only Tracker sync link is not Steam authentication.
   No public Steam IDs, long-lived consent or fictitious connection claims. */
(function(root){
  const host=document.getElementById('progression-panel');
  if(!host)return;
  const status=document.getElementById('progression-status');
  const check=document.getElementById('progression-check');
  let selectedKey=null;
  const KEY=/^[a-f0-9]{64}$/;
  function mount(entry){
    const allowed=entry&&!entry.demo&&typeof entry.key==='string'&&KEY.test(entry.key);
    selectedKey=allowed?entry.key:null;
    host.hidden=!allowed;
    status.textContent=allowed?
      'No 1ADAAR Steam ownership connection has been verified. WARDOGS Tracker sync is separate. Your server statistics are unaffected.':
      'Progression unavailable without a verified profile.';
  }
  check.addEventListener('click',()=>{
    // No callback/DB exists on Pages; report that limitation rather than emit
    // player-key/SteamID into a guessed third-party endpoint.
    status.textContent=selectedKey?
      'Syncing on WARDOGS Tracker does not connect your account to 1ADAAR. Checking progression here requires a private Steam OpenID consent service, pending administrator approval.':
      'Choose a real WARCON player dossier first; no account connection has been established.';
  });
  root.OneADAARProgression=Object.freeze({mount});
})(window);
