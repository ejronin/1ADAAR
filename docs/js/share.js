'use strict';
/* Share publicly available 1ADAAR dossiers only. Never embed SteamID64 values. */
(function () {
  function announce(status, message) {
    if (!status) return;
    status.replaceChildren();
    status.textContent = message;
    status.hidden = false;
  }
  async function share(url, title, status) {
    const destination = new URL(url, location.href);
    if (destination.origin !== location.origin || !destination.pathname.startsWith(new URL('./', location.href).pathname)) {
      announce(status, 'This link cannot be shared from here.');
      return;
    }
    const href = destination.href;
    if (typeof navigator.share === 'function') {
      try {
        await navigator.share({title, url:href});
        announce(status, 'Shared successfully.');
        return;
      } catch (err) {
        if (err && err.name === 'AbortError') {
          announce(status, 'Share cancelled.');
          return;
        }
      }
    }
    try {
      if (!navigator.clipboard || typeof navigator.clipboard.writeText !== 'function') throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(href);
      announce(status, 'Link copied. Paste it into Discord or send it to a friend.');
    } catch (_) {
      if (!status) return;
      status.replaceChildren();
      const label = document.createElement('label');
      label.textContent = 'Copy this share link: ';
      const input = document.createElement('input');
      input.type = 'text';
      input.readOnly = true;
      input.value = href;
      input.setAttribute('aria-label', 'Shareable 1ADAAR report link');
      label.append(input);
      status.append(label);
      status.hidden = false;
      input.focus();
      input.select();
    }
  }
  window.OneADAARShare = Object.freeze({share});
})();
