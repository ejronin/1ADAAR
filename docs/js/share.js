'use strict';
/* Share publicly available 1ADAAR dossiers only. Never embed SteamID64 values. */
(function () {
  function announce(status, message) {
    if (!status) return;
    status.replaceChildren();
    status.textContent = message;
    status.hidden = false;
  }
  async function share(url, title, status, message = {}) {
    const destination = new URL(url, location.href);
    if (destination.origin !== location.origin || !destination.pathname.startsWith(new URL('./', location.href).pathname)) {
      announce(status, 'This link cannot be shared from here.');
      return;
    }
    const href = destination.href;
    // Optional community introduction and invitation are attached to profile shares.
    // Match report shares can keep the original link-only behavior.
    const intro = typeof message.intro === 'string' ? message.intro.trim() : '';
    const outro = typeof message.outro === 'string' ? message.outro.trim() : '';
    const shareText = [intro, outro].filter(Boolean).join('\n\n');
    const copiedText = [intro, href, outro].filter(Boolean).join('\n\n');
    if (typeof navigator.share === 'function') {
      try {
        await navigator.share(shareText ? {title, text: shareText, url: href} : {title, url: href});
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
      await navigator.clipboard.writeText(copiedText);
      announce(status, intro ? 'Profile message copied. Paste it into Discord or send it to a friend.' : 'Link copied. Paste it into Discord or send it to a friend.');
    } catch (_) {
      if (!status) return;
      status.replaceChildren();
      const label = document.createElement('label');
      label.textContent = intro ? 'Copy this profile message: ' : 'Copy this share link: ';
      const input = document.createElement('textarea');
      input.readOnly = true;
      input.rows = intro ? 7 : 2;
      input.value = copiedText;
      input.setAttribute('aria-label', 'Shareable 1ADAAR message');
      label.append(input);
      status.append(label);
      status.hidden = false;
      input.focus();
      input.select();
    }
  }
  window.OneADAARShare = Object.freeze({share});
})();
