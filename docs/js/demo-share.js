'use strict';
document.getElementById('share-demo').addEventListener('click', () => {
  const url = new URL('playerone-demo.html', location.href).href;
  window.OneADAARShare.share(url, '1ADAAR PlayerOne sample profile — fictional stats', document.getElementById('demo-share-status'), {
    intro: '🐺 See what player stats look like on the OneAverageDan WARDOGS Community Server!\n\n🧪 PlayerOne DEMO — fictional statistics, not a real WARCON profile:',
    outro: '🎮 Join the 1AD Discord: https://discord.gg/Yv5HPEFzGj'
  });
});
