/* The page script.
   Film: the scroll position picks the frame drawn on the <canvas> (frames are
   listed in film/manifest.js). Each chapter's words fade in while its part of
   the film is on screen, and the film slows down under them.
   Also: dialogs, calendar file, share, WhatsApp RSVP, countdown, print.
   Plain script, no modules or build step, so it also runs from file://. */
(function () {
  'use strict';

  var W = window.WEDDING || {};
  var M = window.FILM;
  var root = document.documentElement;
  function $(s, el) { return (el || document).querySelector(s); }
  function $$(s, el) { return Array.prototype.slice.call((el || document).querySelectorAll(s)); }
  function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }
  function ease(t) { t = clamp(t, 0, 1); return t * t * (3 - 2 * t); }

  /* ------------------------------------------------------------ toast */
  var toastEl = $('#toast'), toastTimer;
  function toast(msg) {
    if (!toastEl) return;
    toastEl.textContent = msg;
    toastEl.classList.add('is-on');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove('is-on'); }, 2800);
  }

  /* ------------------------------------------------------------ dialogs */
  function openDialog(id) {
    var d = document.getElementById(id);
    if (!d) return;
    $$('dialog[open]').forEach(function (o) { if (o !== d && o.close) o.close(); });
    if (typeof d.showModal === 'function') { if (!d.open) d.showModal(); }
    else d.setAttribute('open', '');
    root.classList.add('has-dialog');
  }
  function closeDialog(d) { if (d.close) d.close(); else d.removeAttribute('open'); }
  $$('dialog').forEach(function (d) {
    d.addEventListener('click', function (e) { if (e.target === d) closeDialog(d); }); // backdrop
    d.addEventListener('close', function () { if (!$('dialog[open]')) root.classList.remove('has-dialog'); });
    $$('[data-close]', d).forEach(function (b) { b.addEventListener('click', function () { closeDialog(d); }); });
  });
  document.addEventListener('click', function (e) {
    var t = e.target.closest && e.target.closest('[data-open]');
    if (!t) return;
    e.preventDefault();
    openDialog(t.getAttribute('data-open'));
  });

  /* ------------------------------------------------------------ calendar */
  function stamp(d) { return d.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}/, ''); }
  function icsText(s) {
    return String(s || '').replace(/\\/g, '\\\\').replace(/\r?\n/g, '\\n').replace(/[,;]/g, function (c) { return '\\' + c; });
  }
  function buildICS() {
    var v = W.venue || {}, now = stamp(new Date());
    var L = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Wedding invitation//EN', 'CALSCALE:GREGORIAN', 'METHOD:PUBLISH'];
    (W.events || []).forEach(function (ev, i) {
      L.push('BEGIN:VEVENT', 'UID:' + stamp(new Date(ev.start)) + '-' + i + '@wedding-invitation', 'DTSTAMP:' + now,
        'DTSTART:' + stamp(new Date(ev.start)), 'DTEND:' + stamp(new Date(ev.end)),
        'SUMMARY:' + icsText(ev.summary), 'LOCATION:' + icsText((v.name || '') + ', ' + (v.address || '')),
        'DESCRIPTION:' + icsText((ev.note ? ev.note + '\n' : '') + (v.maps || '')));
      if (ev.remindMinutes) {
        L.push('BEGIN:VALARM', 'ACTION:DISPLAY', 'DESCRIPTION:' + icsText(ev.summary), 'TRIGGER:-PT' + ev.remindMinutes + 'M', 'END:VALARM');
      }
      L.push('END:VEVENT');
    });
    L.push('END:VCALENDAR');
    return L.join('\r\n') + '\r\n';
  }
  function saveICS() {
    var url = URL.createObjectURL(new Blob([buildICS()], { type: 'text/calendar;charset=utf-8' }));
    var a = document.createElement('a');
    a.href = url;
    a.download = (W.calendarFile || 'wedding') + '.ics';
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(url); a.remove(); }, 2000);
    toast('Calendar file saved. Open it to add the day.');
  }
  function gcalUrl() {
    var ev = (W.events || [])[W.mainEvent || 0], v = W.venue || {};
    if (!ev) return '#';
    return 'https://calendar.google.com/calendar/render?action=TEMPLATE' +
      '&text=' + encodeURIComponent(ev.summary) +
      '&dates=' + stamp(new Date(ev.start)) + '/' + stamp(new Date(ev.end)) +
      '&location=' + encodeURIComponent((v.name || '') + ', ' + (v.address || '')) +
      '&details=' + encodeURIComponent((W.shareText || '') + (v.maps ? '\n' + v.maps : ''));
  }
  $$('[data-ics]').forEach(function (b) { b.addEventListener('click', saveICS); });
  $$('[data-gcal]').forEach(function (a) { a.href = gcalUrl(); });

  /* ------------------------------------------------------------ share */
  function pageUrl() {
    if (W.siteUrl) return W.siteUrl;
    return /^https?:$/.test(location.protocol) ? location.href.split('#')[0] : '';
  }
  function share() {
    var url = pageUrl(), text = W.shareText || document.title;
    var msg = text + (url ? '\n' + url : '');
    if (navigator.share) {
      var data = { title: document.title, text: text };
      if (url) data.url = url;
      navigator.share(data).catch(function () {});
      return;
    }
    var wa = function () { window.open('https://wa.me/?text=' + encodeURIComponent(msg), '_blank', 'noopener'); };
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(msg).then(function () { toast('Invitation copied. Paste it anywhere.'); }, wa);
    } else wa();
  }
  $$('[data-share]').forEach(function (b) { b.addEventListener('click', share); });

  /* ------------------------------------------------------------ print */
  $$('[data-print]').forEach(function (b) { b.addEventListener('click', function () { window.print(); }); });

  /* ------------------------------------------------------------ RSVP */
  var rsvpNumber = String(W.rsvpWhatsApp || '').replace(/\D/g, '');
  root.classList.add(rsvpNumber ? 'has-rsvp' : 'no-rsvp');
  $$('[data-cta]').forEach(function (b) {
    b.addEventListener('click', function (e) { e.preventDefault(); openDialog(rsvpNumber ? 'rsvp' : 'celebrations'); });
  });
  $$('[data-rsvp]').forEach(function (b) { b.addEventListener('click', function () { openDialog('rsvp'); }); });
  var form = $('#rsvpForm');
  if (form) form.addEventListener('submit', function (e) {
    e.preventDefault();
    var f = new FormData(form);
    var name = String(f.get('name') || '').trim(), n = String(f.get('count') || '1');
    var note = String(f.get('note') || '').trim(), coming = f.get('coming') !== 'no';
    var couple = W.couple || 'the couple', day = W.dayShort || 'the wedding day';
    var text = coming
      ? 'Vanakkam! This is ' + name + '. ' + (n === '1' ? 'I' : 'We (' + n + ')') + ' will be there to bless ' + couple + ' on ' + day + '.'
      : 'Vanakkam! This is ' + name + '. Sorry to miss the wedding. Sending all our blessings to ' + couple + '.';
    if (note) text += '\n\n' + note;
    window.open('https://wa.me/' + rsvpNumber + '?text=' + encodeURIComponent(text), '_blank', 'noopener');
    closeDialog(form.closest('dialog'));
    toast('Opening WhatsApp…');
  });

  /* ------------------------------------------------------------ countdown */
  (function () {
    var el = $('#countdown');
    if (!el || !W.muhurtham) return;
    var start = new Date(W.muhurtham.start), end = new Date(W.muhurtham.end), now = new Date();
    function istDay(d) { return Math.floor((d.getTime() + 330 * 60000) / 864e5); } // calendar day in India
    var days = istDay(start) - istDay(now);
    el.textContent = now > end ? (W.afterText || 'Thank you for your blessings')
      : days > 1 ? days + ' days to go'
      : days === 1 ? 'Tomorrow morning'
      : now < start ? 'This morning' : 'Happening now';
  })();

  /* ------------------------------------------------------------ chapters + chrome */
  var chapters = $$('.chapter');
  var railLinks = $$('.rail a');
  var chapNum = $('#chapNum'), chapName = $('#chapName'), cue = $('#cue');
  var active = -1;
  function setActive(k) {
    if (k === active || k < 0) return;
    active = k;
    railLinks.forEach(function (a, i) {
      if (i === k) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current');
    });
    if (chapNum) chapNum.textContent = (k < 9 ? '0' : '') + (k + 1);
    if (chapName) chapName.textContent = chapters[k].getAttribute('data-name') || '';
    root.classList.toggle('at-end', k === chapters.length - 1);
  }

  var film = setupFilm();
  if (!film) setupStatic();

  function setupStatic() {
    var loader = $('#loader');
    if (loader && loader.parentNode) loader.parentNode.removeChild(loader);
    root.classList.remove('film', 'bright');
    if (M && M.variants && M.chapters) {
      var r = window.innerWidth / Math.max(1, window.innerHeight);
      var vs = (r < 0.9 && M.variants.mobile) || M.variants.desktop || M.variants[Object.keys(M.variants)[0]];
      chapters.forEach(function (c, k) {
        var L = vs && vs.lum && vs.lum[M.chapters[k]];
        if (L != null) c.classList.add(L > 0.63 ? 'is-bright' : 'is-dark');
      });
    }
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          setActive(chapters.indexOf(e.target));
          root.classList.toggle('bright', e.target.classList.contains('is-bright'));
        });
      }, { threshold: 0.5 });
      chapters.forEach(function (c) { io.observe(c); });
    }
    if (cue) cue.addEventListener('click', function () {
      if (film) return;
      var k = active >= chapters.length - 1 ? 0 : active + 1;
      chapters[k].scrollIntoView({ behavior: root.classList.contains('still') ? 'auto' : 'smooth' });
    });
    setActive(0);
  }

  function setupFilm() {
    if (!M || !M.frames || !M.variants || root.classList.contains('still')) return null;
    var canvas = $('#film'), stage = $('.stage'), journey = $('#journey'), loader = $('#loader');
    var ctx = canvas && canvas.getContext && canvas.getContext('2d', { alpha: false });
    if (!ctx || !stage || !journey) return null;
    root.classList.add('film');

    var N = M.frames, C = chapters.length;
    var anchors = (M.chapters || []).slice(0, C);
    while (anchors.length < C) anchors.push(Math.round((anchors.length + 0.5) * N / C));

    /* scroll map: each chapter holds for HOLD_VH screens while the film creeps
       through +-HOLD frames around its anchor; between chapters the film runs
       at PER_VH frames per screen of scrolling. */
    var HOLD = Math.max(3, Math.round(N / 40));
    var HOLD_VH = 0.95, PER_VH = Math.max(18, N / 7), FADE = 0.36;
    var keys = [], total = 1;
    function buildKeys() {
      keys = [];
      var s = 0;
      for (var k = 0; k < C; k++) {
        var a = k === 0 ? 0 : clamp(anchors[k] - HOLD, 0, N - 1);
        var b = k === C - 1 ? N - 1 : clamp(anchors[k] + HOLD, 0, N - 1);
        if (k > 0) s += Math.max(0.45, (a - keys[keys.length - 1].f) / PER_VH);
        keys.push({ s: s, f: a });
        s += HOLD_VH * (k === 0 ? 0.8 : 1);
        keys.push({ s: s, f: b });
      }
      total = s;
    }
    function frameAt(s) {
      if (s <= keys[0].s) return keys[0].f;
      for (var i = 1; i < keys.length; i++) {
        if (s <= keys[i].s) {
          var p = keys[i - 1], q = keys[i];
          return p.f + (q.f - p.f) * ((s - p.s) / ((q.s - p.s) || 1));
        }
      }
      return N - 1;
    }
    function opacityAt(k, s) {
      var o = 1;
      if (k > 0) o = Math.min(o, ease((s - keys[2 * k].s + FADE) / FADE));
      if (k < C - 1) o = Math.min(o, 1 - ease((s - keys[2 * k + 1].s) / FADE));
      return o;
    }
    function chapterS(k) {
      return k === 0 ? 0 : k === C - 1 ? keys[2 * k + 1].s : (keys[2 * k].s + keys[2 * k + 1].s) / 2;
    }

    /* frames: first chapter first, then every 16th frame, then fill in */
    var vname, V, imgs, ready, prev = null, gen = 0, inflight = 0, queue = [];
    var coarseMark, coarseSize = 1, coarseDone = 0, good = 0, failed = 0, revealed = false;
    var loaderBar = $('#loaderBar');
    function pickVariant() {
      var r = window.innerWidth / Math.max(1, window.innerHeight);
      if (r < 0.9 && M.variants.mobile) return 'mobile';
      return M.variants.desktop ? 'desktop' : Object.keys(M.variants)[0];
    }
    function pad(i) { var s = String(i); while (s.length < (M.pad || 3)) s = '0' + s; return s; }
    function load(name) {
      var g = ++gen;
      if (imgs && good) prev = { imgs: imgs, ready: ready };
      vname = name; V = M.variants[name];
      imgs = new Array(N); ready = new Uint8Array(N); inflight = 0; good = 0; failed = 0;
      var seen = new Uint8Array(N);
      queue = [];
      function add(i) { if (i >= 0 && i < N && !seen[i]) { seen[i] = 1; queue.push(i); } }
      for (var i = 0; i <= Math.min(N - 1, anchors[0] + HOLD + 2); i++) add(i);
      var firstPart = queue.length;
      for (var st = 16; st >= 1; st = st >> 1) for (var j = 0; j < N; j += st) add(j);
      coarseSize = Math.min(N, firstPart + Math.ceil(N / 16));
      coarseMark = new Uint8Array(N);
      queue.slice(0, coarseSize).forEach(function (i) { coarseMark[i] = 1; });
      coarseDone = 0;
      function pump() { while (inflight < 6 && queue.length) fetchFrame(queue.shift()); }
      function fetchFrame(i) {
        var im = new Image();
        inflight++;
        im.decoding = 'async';
        im.onload = function () {
          if (g !== gen) return;
          var fin = function () {
            if (g !== gen) return;
            inflight--; imgs[i] = im; ready[i] = 1; good++;
            if (good === N) prev = null;
            settled(i); pump();
          };
          if (im.decode) im.decode().then(fin, fin); else fin();
        };
        im.onerror = function () {
          if (g !== gen) return;
          inflight--; failed++;
          settled(i); pump();
        };
        im.src = V.dir + '/' + pad(i) + '.' + (M.ext || 'webp');
      }
      function settled(i) {
        if (coarseMark[i]) {
          coarseDone++;
          if (loaderBar) loaderBar.style.transform = 'scaleX(' + (coarseDone / coarseSize).toFixed(3) + ')';
        }
        if (!revealed && coarseDone >= coarseSize) { if (good) reveal(); else abandon(); }
        if (Math.abs(i - curFrame) <= 2 || i === 0) { lastKey = ''; kick(); }
      }
      pump();
    }
    function reveal() {
      revealed = true;
      if (loader) {
        loader.classList.add('is-done');
        setTimeout(function () { if (loader.parentNode) loader.parentNode.removeChild(loader); }, 1300);
      }
      lastKey = ''; kick();
    }
    function abandon() { // frames missing: fall back to the still pages
      gen++;
      film = null;
      journey.style.height = '';
      setupStatic();
    }

    /* drawing */
    var cw = 0, ch = 0, lastKey = '', curFrame = 0;
    function sizeCanvas() {
      var dpr = Math.min(window.devicePixelRatio || 1, 2);
      var w = stage.clientWidth, h = stage.clientHeight;
      var scale = Math.min(dpr, Math.max(1, (V.w * 1.6) / Math.max(1, w)));
      var nw = Math.round(w * scale), nh = Math.round(h * scale);
      if (nw !== cw || nh !== ch) { cw = canvas.width = nw; ch = canvas.height = nh; lastKey = ''; }
    }
    function nearest(rd, i) {
      if (rd[i]) return i;
      for (var d = 1; d < N; d++) {
        if (i - d >= 0 && rd[i - d]) return i - d;
        if (i + d < N && rd[i + d]) return i + d;
      }
      return -1;
    }
    function paint(img, alpha) {
      var iw = img.naturalWidth || img.width, ih = img.naturalHeight || img.height;
      var s = Math.max(cw / iw, ch / ih), dw = iw * s, dh = ih * s;
      ctx.globalAlpha = alpha;
      ctx.drawImage(img, (cw - dw) / 2, (ch - dh) / 2, dw, dh);
    }
    function draw(f) {
      curFrame = f;
      var i = Math.floor(f), t = f - i, set = imgs, a = nearest(ready, i);
      if (a < 0 && prev) { set = prev.imgs; a = nearest(prev.ready, i); }
      if (a < 0) return;
      var b = (set === imgs && a === i && i + 1 < N && ready[i + 1]) ? i + 1 : -1;
      var q = b < 0 ? 0 : Math.round(t * 12);  // blend neighbouring frames in 12 steps
      var key = vname + ':' + a + ':' + q + ':' + (set === imgs);
      if (key === lastKey) return;
      lastKey = key;
      paint(set[a], 1);
      if (q > 0) paint(imgs[b], q / 12);
      ctx.globalAlpha = 1;
    }

    /* scroll -> film */
    var vh = 1, jTop = 0, lastW = 0, sTarget = 0, sNow = 0, running = false, lastT = 0, bright = false;
    var bar = $('#progress');
    function layout() {
      buildKeys();
      vh = stage.clientHeight || window.innerHeight;
      journey.style.height = Math.round(total * vh + vh) + 'px';
      jTop = journey.getBoundingClientRect().top + (window.pageYOffset || 0);
      sizeCanvas();
    }
    function readScroll() { sTarget = clamp(((window.pageYOffset || 0) - jTop) / vh, 0, total); }
    function render() {
      var f = frameAt(sNow);
      draw(f);
      var best = 0;
      for (var k = 0; k < C; k++) {
        var o = opacityAt(k, sNow), el = chapters[k];
        if (sNow >= keys[2 * k].s - FADE * 0.5) best = k;   // the chapter we are in, or arriving at
        if (el._o !== undefined && Math.abs(o - el._o) < 0.002) continue;
        el._o = o;
        var dir = sNow < keys[2 * k].s ? 1 : -1;
        el.style.opacity = o.toFixed(3);
        el.style.transform = o > 0.998 ? 'none' : 'translate3d(0,' + ((1 - o) * 26 * dir).toFixed(1) + 'px,0)';
        el.style.visibility = o < 0.01 ? 'hidden' : 'visible';
      }
      setActive(best);
      var lum = V.lum ? V.lum[clamp(Math.round(f), 0, N - 1)] : 0.3;
      if (!bright && lum > 0.63) { bright = true; root.classList.add('bright'); }
      else if (bright && lum < 0.55) { bright = false; root.classList.remove('bright'); }
      if (bar) bar.style.transform = 'scaleX(' + (sNow / total).toFixed(4) + ')';
    }
    function tick(now) {
      if (!film) { running = false; return; }
      var dt = lastT ? Math.min(0.1, (now - lastT) / 1000) : 0.016;
      lastT = now;
      var d = sTarget - sNow;
      sNow = Math.abs(d) < 0.0008 ? sTarget : sNow + d * (1 - Math.exp(-dt / 0.09));
      render();
      if (sNow !== sTarget) requestAnimationFrame(tick);
      else { running = false; lastT = 0; }
    }
    function kick() { if (!running) { running = true; requestAnimationFrame(tick); } }
    function go(k, instant) {
      window.scrollTo({ top: jTop + chapterS(k) * vh + 1, behavior: instant ? 'auto' : 'smooth' });
    }

    window.addEventListener('scroll', function () { readScroll(); kick(); }, { passive: true });
    window.addEventListener('resize', function () {
      if (!film) return;
      var nv = pickVariant();
      if (nv !== vname) load(nv);
      if (window.innerWidth !== lastW || Math.abs(stage.clientHeight - vh) > 1) {
        var keep = sTarget;
        lastW = window.innerWidth;
        layout();
        window.scrollTo(0, jTop + keep * vh);
        readScroll(); sNow = sTarget; lastKey = ''; kick();
      }
    });
    railLinks.forEach(function (a, i) { a.addEventListener('click', function (e) { if (!film) return; e.preventDefault(); go(i); }); });
    $$('[data-home]').forEach(function (a) { a.addEventListener('click', function (e) { if (!film) return; e.preventDefault(); go(0); }); });
    if (cue) cue.addEventListener('click', function () { if (film) go(active >= C - 1 ? 0 : active + 1); });
    chapters.forEach(function (el, k) {           // tabbing into a chapter brings it on screen
      el.addEventListener('focusin', function () { if (film && active !== k) go(k, true); });
    });

    lastW = window.innerWidth;
    load(pickVariant());
    layout();
    var m = /^#ch(\d)$/.exec(location.hash);
    if (m && +m[1] >= 1 && +m[1] <= C) window.scrollTo(0, jTop + chapterS(+m[1] - 1) * vh);
    readScroll(); sNow = sTarget;
    setActive(0);
    kick();
    setTimeout(function () { if (film && !revealed) { if (good) reveal(); else abandon(); } }, 15000);
    return { go: go };
  }
})();
