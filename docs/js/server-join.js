'use strict';
// WARDOGS supports Join by ID in its game browser, not a confirmed URL/deep link.
(function(){
  const CODE='a071b4aa-9574-4e7d-858c-0da3bea80f52';
  function fallbackCopy(text){
    const input=document.createElement('textarea');
    input.value=text;input.setAttribute('readonly','');
    input.style.cssText='position:fixed;top:-9999px;left:-9999px;';
    document.body.append(input);input.select();
    const ok=document.execCommand('copy');input.remove();
    return ok;
  }
  function bind(){
    // The exact owner-approved PNG overrides this official-brand fallback.
    // Never hide the brand row until the local file really loads.
    const banner=new Image();
    banner.onload=()=>{
      document.querySelectorAll('.server-banner-brand-fallback').forEach(x=>x.hidden=true);
    };
    banner.src='assets/oneaveragedan-server-banner.png';
    const button=document.getElementById('copy-server-join-code');
    const status=document.getElementById('server-join-copy-status');
    if(!button||!status)return;
    button.addEventListener('click',async()=>{
      // No unexpected ID from markup, URL parameters or remote scripts.
      if(button.dataset.joinCode!==CODE)return;
      let copied=false;
      try{
        if(navigator.clipboard&&window.isSecureContext){
          await navigator.clipboard.writeText(CODE);copied=true;
        }else copied=fallbackCopy(CODE);
      }catch(_){try{copied=fallbackCopy(CODE)}catch(__){copied=false}}
      status.textContent=copied?'COPIED · PASTE IN WARDOGS':'COPY BLOCKED · SELECT THE CODE';
      button.closest('.server-join-overlay')?.setAttribute('data-copied',String(copied));
      if(!copied){
        // Text remains selectable when browser/embedding blocks clipboard permission.
        const value=button.querySelector('.server-join-value');
        const selection=window.getSelection();if(!selection||!value)return;
        const range=document.createRange();range.selectNodeContents(value);
        selection.removeAllRanges();selection.addRange(range);
      }
    });
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',bind,{once:true});
  else bind();
})();
