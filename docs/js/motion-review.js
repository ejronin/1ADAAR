'use strict';
/* Staging design lab only. Does not authorize community awards or alter player data. */
(function(){
  const hero=document.querySelector('.motion-hero');
  const test=document.getElementById('test-champion');
  const replay=element=>{
    if(!element)return;
    // Remove, force a style/layout flush on an explicitly clicked design button,
    // and restore the class to restart one finite CSS animation.
    element.classList.add('motion-replay');
    void element.offsetWidth;
    requestAnimationFrame(()=>requestAnimationFrame(()=>
      element.classList.remove('motion-replay')));
  };
  document.getElementById('replay-hero')?.addEventListener('click',()=>replay(hero));
  document.getElementById('replay-crown')?.addEventListener('click',()=>replay(test));
})();
