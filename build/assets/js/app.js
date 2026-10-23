/* Carat Tour & Study — интерфейс: меню, поиск тура, формы заявок, фильтр, лайтбокс */
(function () {
  'use strict';
  var I18N = window.CARAT_I18N || {};
  var body = document.body;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* ---------- Запоминаем выбранный язык (для автоопределения на корне) ---------- */
  try { localStorage.setItem('carat_lang', body.getAttribute('data-lang')); } catch (e) {}

  /* ---------- Тень шапки при прокрутке ---------- */
  var header = $('#site-header');
  var onScroll = function () { if (header) header.classList.toggle('shadow-soft', window.scrollY > 8); };
  window.addEventListener('scroll', onScroll, { passive: true }); onScroll();

  /* ---------- Мобильное меню ---------- */
  var menu = $('#mobile-menu'), openBtn = $('[data-menu-open]');
  function setMenu(open) {
    if (!menu) return;
    menu.classList.toggle('hidden', !open);
    body.classList.toggle('overflow-hidden', open);
    if (openBtn) openBtn.setAttribute('aria-expanded', String(open));
    if (open) { var f = $('a, button', menu); if (f) f.focus(); } else if (openBtn) openBtn.focus();
  }
  if (openBtn) openBtn.addEventListener('click', function () { setMenu(true); });
  $$('[data-menu-close]').forEach(function (el) { el.addEventListener('click', function () { setMenu(false); }); });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && menu && !menu.classList.contains('hidden')) setMenu(false);
  });

  /* ---------- Выпадающее меню «Туры» (клавиатура / тач) ---------- */
  $$('[data-dropdown]').forEach(function (btn) {
    var li = btn.parentElement, panel = $('[data-dropdown-panel]', li);
    btn.addEventListener('click', function () {
      var open = btn.getAttribute('aria-expanded') !== 'true';
      btn.setAttribute('aria-expanded', String(open));
      panel.classList.toggle('!visible', open); panel.classList.toggle('!opacity-100', open);
    });
    document.addEventListener('click', function (e) {
      if (!li.contains(e.target)) { btn.setAttribute('aria-expanded', 'false'); panel.classList.remove('!visible', '!opacity-100'); }
    });
  });

  /* ---------- Попап бронирования (<dialog>) ---------- */
  var dlg = $('#booking');
  var canDialog = !!(dlg && typeof dlg.showModal === 'function');
  var bookingForm = dlg && $('[data-lead-form]', dlg);

  function setType(form, type) {
    var el = form.elements.tour_type;
    if (!type || !el) return;
    if (el.type === 'hidden') { el.value = type; return; }   // минимальная форма
    var radio = form.querySelector('input[name="tour_type"][value="' + type + '"]');
    if (radio) radio.checked = true;
  }
  var summary = dlg && $('[data-booking-summary]', dlg);
  function openBooking(opts) {
    opts = opts || {};
    var f = bookingForm.elements;
    // в попапе форма минимальная: параметры поездки — скрытые поля (каждое открытие заново)
    f.direction.value = opts.direction || '';
    f.tour_type.value = opts.type || '';
    f.tourists.value = opts.tourists || '';
    f.dates.value = opts.dates || '';
    f.search.value = opts.search || '';
    var text = [opts.direction, opts.dates, opts.tourists].filter(Boolean).join(' · ');
    if (summary) {
      summary.lastElementChild.textContent = text;
      summary.classList.toggle('hidden', !text);
      summary.classList.toggle('flex', !!text);
    }
    dlg.showModal();
    body.classList.add('overflow-hidden');
    setTimeout(function () { f.name.focus(); }, 60);
  }
  if (canDialog) {
    $$('[data-booking]').forEach(function (el) {
      el.addEventListener('click', function (e) {
        e.preventDefault();
        openBooking({ direction: el.getAttribute('data-direction'), type: el.getAttribute('data-type') });
      });
    });
    $$('[data-booking-close]', dlg).forEach(function (b) { b.addEventListener('click', function () { dlg.close(); }); });
    dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); }); // клик по фону
    dlg.addEventListener('close', function () { body.classList.remove('overflow-hidden'); });
  }

  /* ---------- Поиск тура → попап бронирования (или форма на странице) ---------- */
  var search = $('[data-tour-search]');
  if (search) {
    search.addEventListener('submit', function (e) {
      e.preventDefault();
      var dir = search.elements.direction, dates = search.elements.dates, tour = search.elements.tourists;
      var type = '';
      if (dir.value) {
        var grp = dir.options[dir.selectedIndex].parentElement;
        if (grp && grp.tagName === 'OPTGROUP') type = ['uz', 'intl', 'info'][$$('optgroup', dir).indexOf(grp)];
      }
      var datesText = dates.value ? dates.options[dates.selectedIndex].text : '';
      var tourText = tour.options[tour.selectedIndex].text;
      var summary = [dir.value, datesText, tourText].filter(Boolean).join(' · ');
      if (canDialog) {
        openBooking({ direction: dir.value, type: type, dates: datesText, tourists: tourText, search: summary });
        return;
      }
      var form = $('#lead [data-lead-form]') || $('[data-lead-form]');
      if (!form) return;
      if (dir.value) form.elements.direction.value = dir.value;
      setType(form, type);
      if (form.elements.dates && datesText) form.elements.dates.value = datesText;
      if (form.elements.comment && !form.elements.comment.value) form.elements.comment.value = tourText;
      form.elements.search.value = summary;
      $('#lead').scrollIntoView({ behavior: 'smooth', block: 'start' });
      setTimeout(function () { form.elements.name.focus({ preventScroll: true }); }, 500);
    });
  }

  /* ---------- Формы заявок ---------- */
  var reContact = /^(\+?[\d\s\-()]{9,20}|@?[A-Za-z][A-Za-z0-9_]{4,31}|(https?:\/\/)?t\.me\/[A-Za-z0-9_]{5,32})$/;

  function validField(el) {
    var ok = true, v = (el.value || '').trim();
    if (el.type === 'checkbox') ok = el.checked;
    else if (el.required && !v) ok = false;
    else if (el.name === 'name') ok = v.length >= 2;
    else if (el.getAttribute('data-validate') === 'contact') ok = reContact.test(v) && (/[A-Za-z]/.test(v) || v.replace(/\D/g, '').length >= 9);
    if (el.type === 'checkbox') el.closest('.field-wrap').classList.toggle('is-invalid', !ok);
    else { el.classList.toggle('is-invalid', !ok); el.setAttribute('aria-invalid', String(!ok)); }
    return ok;
  }

  $$('[data-lead-form]').forEach(function (form) {
    if (form.elements.ts) form.elements.ts.value = String(Date.now());
    var fields = $$('[required]', form);
    fields.forEach(function (el) {
      el.addEventListener(el.type === 'checkbox' ? 'change' : 'blur', function () { validField(el); });
      el.addEventListener('input', function () { if (el.classList.contains('is-invalid')) validField(el); });
    });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var firstBad = null;
      fields.forEach(function (el) { if (!validField(el) && !firstBad) firstBad = el; });
      if (firstBad) { firstBad.focus(); return; }

      var btn = $('button[type="submit"]', form), label = $('[data-label]', btn), err = $('[data-form-error]', form);
      err.classList.add('hidden');
      btn.disabled = true; btn.classList.add('opacity-70'); label.textContent = I18N.sending || '…';

      fetch(body.getAttribute('data-endpoint'), { method: 'POST', body: new FormData(form), headers: { 'Accept': 'application/json' } })
        .then(function (r) { return r.json().catch(function () { return { ok: false }; }); })
        .then(function (res) {
          if (res && res.ok) { window.location.href = body.getAttribute('data-thanks'); return; }
          throw new Error(res && res.error || 'fail');
        })
        .catch(function () {
          err.classList.remove('hidden');
          btn.disabled = false; btn.classList.remove('opacity-70'); label.textContent = I18N.submit || 'OK';
        });
    });
  });

  /* ---------- Фильтр международных направлений ---------- */
  var filter = $('[data-filter]');
  if (filter) {
    var cards = $$('[data-filter-list] > *'), empty = $('[data-filter-empty]');
    filter.addEventListener('click', function (e) {
      var b = e.target.closest('[data-filter-value]'); if (!b) return;
      var v = b.getAttribute('data-filter-value'), shown = 0;
      $$('[data-filter-value]', filter).forEach(function (x) { x.classList.toggle('is-active', x === b); x.setAttribute('aria-pressed', String(x === b)); });
      cards.forEach(function (c) {
        var ok = !v || (' ' + c.getAttribute('data-kinds') + ' ').indexOf(' ' + v + ' ') > -1;
        c.classList.toggle('hidden', !ok); if (ok) shown++;
      });
      if (empty) empty.classList.toggle('hidden', shown > 0);
    });
  }

  /* ---------- Лайтбокс ---------- */
  $$('[data-lightbox]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      var d = document.createElement('div');
      d.className = 'fixed inset-0 z-[80] flex items-center justify-center bg-navy-950/90 p-4 cursor-zoom-out';
      d.setAttribute('role', 'dialog'); d.setAttribute('aria-modal', 'true');
      var img = document.createElement('img');
      img.src = a.getAttribute('href'); img.alt = ($('img', a) || {}).alt || '';
      img.className = 'max-h-full max-w-full rounded-2xl shadow-float';
      d.appendChild(img); body.appendChild(d); body.classList.add('overflow-hidden');
      var close = function () { d.remove(); body.classList.remove('overflow-hidden'); document.removeEventListener('keydown', esc); };
      var esc = function (ev) { if (ev.key === 'Escape') close(); };
      d.addEventListener('click', close); document.addEventListener('keydown', esc);
    });
  });
})();
