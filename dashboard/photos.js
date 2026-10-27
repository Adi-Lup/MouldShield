// photos.js - T18: photo evidence on the report page.
// server.py adds this file to the page on the EC2 server, so the other dashboard files stay as they are.
// The tenant adds a photo, the server describes it with AI, and the photo and the description
// are shown in the report (and in the printed PDF).
// Made to be easy for everyone, including older people: one big button, large text and clear messages.
(function () {
  'use strict';

  var cfg = window.MOULDSHIELD_CONFIG || {};
  var base = (cfg.apiBaseUrl || '/api').replace(/\/$/, '');
  var MAX_BYTES = 15 * 1024 * 1024;

  // Styles for this part only, with the same colours as the dashboard
  var style = document.createElement('style');
  style.textContent =
    '.photo-evidence{margin-top:30px;border-top:1px solid #9aaf9e;padding-top:8px}' +
    '.photo-steps{font-size:18px;line-height:1.7;margin:10px 0 18px;padding-left:24px}' +
    '.photo-steps li{margin:4px 0}' +
    '.photo-button{display:inline-flex;align-items:center;justify-content:center;gap:12px;min-height:60px;min-width:260px;padding:14px 26px;' +
    'border:2px solid #173d2b;border-radius:10px;background:#173d2b;color:#fff;font-size:20px;font-weight:700;cursor:pointer}' +
    '.photo-button:hover{background:#0e2b1d}' +
    '.photo-button:disabled{background:#5f7565;border-color:#5f7565;opacity:1;cursor:wait}' +
    '.photo-button svg{width:28px;height:28px}' +
    '.photo-file{position:absolute;width:1px;height:1px;margin:-1px;padding:0;overflow:hidden;clip:rect(0 0 0 0);border:0}' +
    '.photo-status{font-size:18px;line-height:1.6;border-radius:8px;padding:14px 16px;margin:18px 0;border:2px solid transparent}' +
    '.photo-status:empty{display:none}' +
    '.photo-status.info{background:#eaf0e6;border-color:#637f61;color:#22372a}' +
    '.photo-status.working{background:#fff1c4;border-color:#8e7021;color:#4c3600}' +
    '.photo-status.ok{background:#e4f3e8;border-color:#416e4a;color:#174b2e}' +
    '.photo-status.error{background:#fde8e9;border-color:#9a4350;color:#761821}' +
    '.photo-ask{background:#fff1c4;border:2px solid #8e7021;color:#4c3600;border-radius:10px;padding:16px 18px;margin:18px 0}' +
    '.photo-ask p{font-size:18px;color:#4c3600;margin:0 0 10px}' +
    '.photo-ask .photo-ai{font-style:italic}' +
    '.photo-ask-buttons{display:flex;gap:12px;flex-wrap:wrap;margin-top:14px}' +
    '.photo-ask-buttons button{min-height:56px;padding:12px 22px;border-radius:10px;font-size:19px;font-weight:700;cursor:pointer;border:2px solid #173d2b}' +
    '.photo-yes{background:#173d2b;color:#fff}.photo-no{background:#fff;color:#173d2b}' +
    '.photo-list{display:grid;gap:20px;margin-top:10px}' +
    '.photo-item{display:grid;grid-template-columns:minmax(0,260px) minmax(0,1fr);gap:18px;border:1px solid #9aaf9e;border-radius:10px;padding:16px;background:#fff}' +
    '.photo-item img{width:100%;height:auto;border-radius:8px;display:block}' +
    '.photo-item p{margin:0 0 10px;font-size:18px}' +
    '.photo-item .photo-meta{font-size:16px;color:#35493c}' +
    '.photo-note{background:#fff1c4;color:#4c3600;border-radius:6px;padding:8px 12px;font-size:16px;display:inline-block}' +
    '@media(max-width:640px){.photo-item{grid-template-columns:1fr}.photo-button,.photo-ask-buttons button{width:100%;min-width:0}}' +
    '@media print{.photo-steps,.photo-button,.photo-status,.photo-ask{display:none!important}.photo-item{break-inside:avoid;border:0;padding:0}}';
  document.head.appendChild(style);

  function el(tag, attrs, text) {
    var node = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) { node.setAttribute(k, attrs[k]); });
    if (text) node.textContent = text;
    return node;
  }

  function dateText(value, withTime) {
    if (!value) return '';
    var d = new Date(value);
    if (isNaN(d)) return value;
    var opts = { day: 'numeric', month: 'long', year: 'numeric' };
    if (withTime) { opts.hour = '2-digit'; opts.minute = '2-digit'; }
    return d.toLocaleString('en-GB', opts);
  }

  // Build the section and put it after the AI explanation, before the landlord letter
  var anchor = document.getElementById('report-explanation');
  if (!anchor) return;

  var section = el('section', { 'class': 'photo-evidence', 'aria-labelledby': 'photo-heading' });
  section.appendChild(el('h3', { id: 'photo-heading' }, 'Photo evidence'));

  var steps = el('ol', { 'class': 'photo-steps' });
  steps.appendChild(el('li', {}, 'Press the green button below.'));
  steps.appendChild(el('li', {}, 'Take a photo of the damp or mould, or choose one you already have.'));
  steps.appendChild(el('li', {}, 'Wait a few seconds. The photo and a short description will appear here.'));
  section.appendChild(steps);

  // The real file picker is hidden; the big button opens it
  var input = el('input', { type: 'file', id: 'photo-file', accept: 'image/*', 'class': 'photo-file', tabindex: '-1', 'aria-hidden': 'true' });
  var button = el('button', { type: 'button', 'class': 'photo-button', id: 'photo-upload' });
  button.innerHTML = '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
    '<path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/></svg><span>Add a photo</span>';
  var buttonText = button.querySelector('span');
  section.appendChild(input);
  section.appendChild(button);

  var status = el('div', { id: 'photo-status', 'class': 'photo-status', role: 'status', 'aria-live': 'polite' });
  section.appendChild(status);

  // Shown only when AI sees no damp: the tenant decides if the photo is still evidence
  var ask = el('div', { 'class': 'photo-ask', id: 'photo-ask', role: 'alertdialog', 'aria-labelledby': 'photo-ask-title' });
  ask.hidden = true;
  ask.appendChild(el('p', { id: 'photo-ask-title' }, 'This photo does not seem to show damp or mould.'));
  var askAi = el('p', { 'class': 'photo-ai' });
  ask.appendChild(askAi);
  ask.appendChild(el('p', {}, 'Do you still want to add it to your report as evidence?'));
  var askButtons = el('div', { 'class': 'photo-ask-buttons' });
  var yes = el('button', { type: 'button', 'class': 'photo-yes', id: 'photo-yes' }, 'Yes, add it');
  var no = el('button', { type: 'button', 'class': 'photo-no', id: 'photo-no' }, 'No, choose another photo');
  askButtons.appendChild(yes);
  askButtons.appendChild(no);
  ask.appendChild(askButtons);
  section.appendChild(ask);
  var waitingFile = null;

  section.appendChild(el('p', { 'class': 'muted' },
    'AI describes what it can see; it does not diagnose anything. The photo is saved without its hidden data. ' +
    'The date, the phone model and the location are kept privately as evidence and are never shown on this page.'));

  var list = el('div', { 'class': 'photo-list' });
  section.appendChild(list);

  anchor.parentNode.insertBefore(section, anchor.nextSibling);

  function say(kind, text) {
    status.className = 'photo-status' + (kind ? ' ' + kind : '');
    status.textContent = text;
  }

  function showPhoto(photo) {
    var item = el('article', { 'class': 'photo-item' });
    item.appendChild(el('img', { src: base + photo.image_url, alt: 'Photo ' + photo.id + ' added by the tenant', loading: 'lazy' }));
    var text = el('div');
    text.appendChild(el('p', {}, photo.description));
    var meta = [];
    var taken = photo.taken_at ? 'Taken on ' + dateText(photo.taken_at) : '';
    if (photo.camera) taken = (taken ? taken + ' with ' : 'Taken with ') + photo.camera;
    if (taken) meta.push(taken);
    meta.push('added on ' + dateText(photo.uploaded_at, true));
    text.appendChild(el('p', { 'class': 'photo-meta' }, meta.join(' · ')));
    if (photo.days_before_upload !== null && photo.days_before_upload >= 7) {
      text.appendChild(el('span', { 'class': 'photo-note' },
        'This photo was taken ' + photo.days_before_upload + ' days before it was added.'));
    }
    item.appendChild(text);
    return item;
  }

  function load() {
    return fetch(base + '/photos', { headers: { Accept: 'application/json' } })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (photos) {
        list.textContent = '';
        photos.forEach(function (p) { list.appendChild(showPhoto(p)); });
      })
      .catch(function () {
        // For example on the local preview, where there is no photo service
        steps.hidden = true;
        button.hidden = true;
        say('info', 'Photo evidence works on the live website only.');
      });
  }

  function busy(on) {
    button.disabled = on;
    buttonText.textContent = on ? 'Please wait…' : 'Add a photo';
  }

  // One press: the button opens the camera or the photo library
  button.addEventListener('click', function () {
    ask.hidden = true;
    waitingFile = null;
    input.value = '';
    input.click();
  });

  function send(file, confirm) {
    busy(true);
    ask.hidden = true;
    say('working', confirm
      ? 'Adding your photo to the report, please wait…'
      : 'Sending your photo and asking AI to describe it. This takes a few seconds, please wait…');
    return fetch(base + '/photos' + (confirm ? '?confirm=true' : ''), {
      method: 'POST',
      headers: { 'Content-Type': file.type || 'application/octet-stream' },
      body: file
    })
      .then(function (r) {
        return r.json().catch(function () { return {}; }).then(function (data) {
          if (!r.ok) throw new Error(data.detail || 'The photo could not be added. Please try again.');
          return data;
        });
      })
      .then(function (data) {
        if (data.needs_confirmation) {
          // AI saw no damp: nothing is saved yet, the tenant chooses
          waitingFile = file;
          say('', '');
          askAi.textContent = 'AI: ' + data.description;
          ask.hidden = false;
          yes.focus();
          return;
        }
        waitingFile = null;
        return load().then(function () {
          say('ok', 'Done. Your photo has been added below.');
          if (list.firstChild) list.firstChild.scrollIntoView({ behavior: 'smooth', block: 'center' });
        });
      })
      .catch(function (e) { say('error', e.message === 'Failed to fetch' ? 'No connection to the website. Please check your internet and try again.' : e.message); })
      .then(function () { busy(false); });
  }

  // As soon as a photo is chosen, it is sent. No second button to press.
  input.addEventListener('change', function () {
    var file = input.files && input.files[0];
    if (!file) return;
    if (file.size > MAX_BYTES) {
      say('error', 'This photo is too big (more than 15 MB). Please choose a smaller photo.');
      return;
    }
    send(file, false);
  });

  yes.addEventListener('click', function () { if (waitingFile) send(waitingFile, true); });
  no.addEventListener('click', function () {
    waitingFile = null;
    ask.hidden = true;
    say('info', 'Nothing was saved. Press "Add a photo" to choose another one.');
    button.focus();
  });

  load();
})();
