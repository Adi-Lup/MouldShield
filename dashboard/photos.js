// photos.js - T18: photo evidence on the report page.
// server.py adds this file to the page on the EC2 server, so the other dashboard files stay as they are.
// The tenant adds a photo, the server describes it with AI, and the photo and the description
// are shown in the report (and in the printed PDF).
(function () {
  'use strict';

  var cfg = window.MOULDSHIELD_CONFIG || {};
  var base = (cfg.apiBaseUrl || '/api').replace(/\/$/, '');
  var MAX_BYTES = 15 * 1024 * 1024;

  // Small styles for this part only, using the same colours as the dashboard
  var style = document.createElement('style');
  style.textContent =
    '.photo-evidence{margin-top:26px}' +
    '.photo-add{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin:12px 0}' +
    '.photo-add input[type=file]{font-size:16px;max-width:100%}' +
    '.photo-list{display:grid;gap:18px;margin-top:14px}' +
    '.photo-item{display:grid;grid-template-columns:minmax(0,220px) minmax(0,1fr);gap:16px;border:1px solid #9aaf9e;border-radius:8px;padding:14px;background:#fff}' +
    '.photo-item img{width:100%;height:auto;border-radius:6px;display:block}' +
    '.photo-item p{margin:0 0 8px}' +
    '.photo-note{background:#fff1c4;color:#4c3600;border-radius:5px;padding:6px 10px;font-size:15px;display:inline-block}' +
    '@media(max-width:640px){.photo-item{grid-template-columns:1fr}.photo-add .button{width:100%}}' +
    '@media print{.photo-add,#photo-status{display:none!important}.photo-item{break-inside:avoid;border:0;padding:0}}';
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
    var opts = { day: 'numeric', month: 'short', year: 'numeric' };
    if (withTime) { opts.hour = '2-digit'; opts.minute = '2-digit'; }
    return d.toLocaleString('en-GB', opts);
  }

  // Build the section and put it after the AI explanation, before the landlord letter
  var anchor = document.getElementById('report-explanation');
  if (!anchor) return;

  var section = el('section', { 'class': 'photo-evidence', 'aria-labelledby': 'photo-heading' });
  section.appendChild(el('h3', { id: 'photo-heading' }, 'Photo evidence'));
  section.appendChild(el('p', { 'class': 'muted' },
    'Add a photo of the damp or mould. AI describes what it can see; it does not diagnose anything. ' +
    'The photo is saved without its hidden data. The date, the phone model and the location are kept ' +
    'privately as evidence and are never shown on this page.'));

  var add = el('div', { 'class': 'photo-add' });
  var label = el('label', { 'for': 'photo-file', 'class': 'muted' }, 'Choose a photo (JPG, PNG, WebP or HEIC, 15 MB at most)');
  var input = el('input', { type: 'file', id: 'photo-file', accept: 'image/*' });
  var button = el('button', { type: 'button', 'class': 'button secondary', id: 'photo-upload' }, 'Add photo');
  add.appendChild(label);
  add.appendChild(input);
  add.appendChild(button);
  section.appendChild(add);

  var status = el('p', { id: 'photo-status', 'class': 'muted', role: 'status' });
  section.appendChild(status);
  var list = el('div', { 'class': 'photo-list' });
  section.appendChild(list);

  anchor.parentNode.insertBefore(section, anchor.nextSibling);

  function showPhoto(photo) {
    var item = el('article', { 'class': 'photo-item' });
    item.appendChild(el('img', { src: base + photo.image_url, alt: 'Photo ' + photo.id + ' added by the tenant', loading: 'lazy' }));
    var text = el('div');
    text.appendChild(el('p', {}, photo.description));
    var meta = [];
    var taken = photo.taken_at ? 'Taken ' + dateText(photo.taken_at) : '';
    if (photo.camera) taken = (taken ? taken + ' on ' : 'Taken on ') + photo.camera;
    if (taken) meta.push(taken);
    meta.push('added ' + dateText(photo.uploaded_at, true));
    text.appendChild(el('p', { 'class': 'muted' }, meta.join(' · ')));
    if (photo.days_before_upload !== null && photo.days_before_upload >= 7) {
      text.appendChild(el('span', { 'class': 'photo-note' },
        'This photo was taken ' + photo.days_before_upload + ' days before it was added.'));
    }
    item.appendChild(text);
    return item;
  }

  function render(photos) {
    list.textContent = '';
    photos.forEach(function (p) { list.appendChild(showPhoto(p)); });
    if (!photos.length) status.textContent = 'No photos added yet.';
  }

  function load() {
    fetch(base + '/photos', { headers: { Accept: 'application/json' } })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(render)
      .catch(function () {
        // For example on the local preview, where there is no photo service
        add.hidden = true;
        status.textContent = 'Photo evidence works on the live server only.';
      });
  }

  button.addEventListener('click', function () {
    var file = input.files && input.files[0];
    if (!file) { status.textContent = 'Choose a photo first.'; return; }
    if (file.size > MAX_BYTES) { status.textContent = 'The photo is too big (15 MB at most).'; return; }
    button.disabled = true;
    status.textContent = 'Uploading and describing the photo. This can take a few seconds…';
    fetch(base + '/photos', {
      method: 'POST',
      headers: { 'Content-Type': file.type || 'application/octet-stream' },
      body: file
    })
      .then(function (r) {
        return r.json().catch(function () { return {}; }).then(function (data) {
          if (!r.ok) throw new Error(data.detail || 'The photo could not be added.');
          return data;
        });
      })
      .then(function () { input.value = ''; status.textContent = 'Photo added.'; load(); })
      .catch(function (e) { status.textContent = e.message; })
      .then(function () { button.disabled = false; });
  });

  load();
})();
