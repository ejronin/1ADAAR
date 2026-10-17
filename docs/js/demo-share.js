'use strict';
document.getElementById('share-demo').addEventListener('click', () => {
  const url = new URL('playerone-demo.html', location.href).href;
  window.OneADAARShare.share(url, '1ADAAR PlayerOne sample profile — fictional stats', document.getElementById('demo-share-status'));
});
