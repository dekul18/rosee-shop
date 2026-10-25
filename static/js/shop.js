(function () {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const root = document.documentElement;

  // Theme toggle
  const themeBtn = $('#theme');
  const paintTheme = () => (themeBtn.textContent = root.classList.contains('dark') ? '☀️' : '🌙');
  paintTheme();
  themeBtn.onclick = () => {
    root.classList.toggle('dark');
    localStorage.theme = root.classList.contains('dark') ? 'dark' : 'light';
    paintTheme();
  };

  // Fade-in on scroll
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { threshold: 0.1 });
  $$('.reveal').forEach(el => io.observe(el));

  const toast = msg => {
    const t = $('#toast'); t.textContent = msg; t.classList.remove('hidden');
    clearTimeout(toast.t); toast.t = setTimeout(() => t.classList.add('hidden'), 2200);
  };

  // Category filter + live search (no page reload)
  const grid = $('#grid');
  if (grid) {
    let cat = $('#cats').dataset.active || '', term = ($('#search').value || '').toLowerCase().trim();
    const apply = () => {
      let shown = 0;
      $$('.product', grid).forEach(p => {
        const ok = (!cat || p.dataset.cat === cat) && (!term || p.dataset.name.includes(term));
        p.classList.toggle('hidden', !ok); shown += ok;
      });
      $('#empty').classList.toggle('hidden', shown > 0 || !$$('.product', grid).length);
      $$('.cat').forEach(b => {
        const on = b.dataset.cat === cat;
        b.classList.toggle('bg-blush-500', on); b.classList.toggle('text-white', on);
        b.classList.toggle('bg-blush-100', !on);
      });
    };
    $$('.cat').forEach(b => b.onclick = () => { cat = b.dataset.cat; apply(); });
    $('#search').addEventListener('input', e => { term = e.target.value.toLowerCase().trim(); apply(); });
    $('#search').form.addEventListener('submit', e => e.preventDefault());
    apply();
  }

  // Product popup
  const dataEl = $('#products-data');
  if (!dataEl) return;
  const products = Object.fromEntries(JSON.parse(dataEl.textContent).map(p => [p.id, p]));
  const modal = $('#modal');
  let cur, size = '', color = '', qty = 1;

  const pills = (box, list, onPick) => {
    box.innerHTML = '';
    list.forEach(v => {
      const b = document.createElement('button'); b.type = 'button'; b.textContent = v;
      b.className = 'pill px-4 py-1.5 rounded-full border border-blush-300 text-sm';
      b.onclick = () => { $$('.pill', box).forEach(x => x.classList.remove('bg-blush-500', 'text-white')); b.classList.add('bg-blush-500', 'text-white'); onPick(v); };
      box.appendChild(b);
    });
    if (list.length === 1) box.firstChild.click();
  };
  const showImg = src => {
    const m = $('#m-main'); m.innerHTML = src ? `<img src="${src}" alt="" class="w-full h-full object-cover">` : '🌸';
  };
  const open = id => {
    cur = products[id]; size = color = ''; qty = 1; $('#q').textContent = 1; $('#m-err').classList.add('hidden');
    $('#m-cat').textContent = cur.catName; $('#m-name').textContent = cur.name;
    $('#m-price').textContent = cur.price + ' DZD'; $('#m-desc').textContent = cur.desc;
    showImg(cur.images[0]);
    const th = $('#m-thumbs'); th.innerHTML = '';
    if (cur.images.length > 1) cur.images.forEach(src => {
      const i = document.createElement('img'); i.src = src; i.alt = '';
      i.className = 'w-16 h-20 rounded-xl object-cover cursor-pointer shrink-0'; i.onclick = () => showImg(src); th.appendChild(i);
    });
    pills($('#m-sizes'), cur.sizes, v => size = v);
    $('#m-colors-wrap').classList.toggle('hidden', !cur.colors.length);
    pills($('#m-colors'), cur.colors, v => color = v);
    $('#m-stock').textContent = cur.stock ? (cur.stock <= 5 ? `Only ${cur.stock} left` : '') : 'Sold out';
    $('#m-add').disabled = !cur.stock; $('#m-add').classList.toggle('opacity-50', !cur.stock);
    modal.classList.remove('hidden'); modal.classList.add('flex'); document.body.style.overflow = 'hidden';
  };
  const close = () => { modal.classList.add('hidden'); modal.classList.remove('flex'); document.body.style.overflow = ''; };

  document.addEventListener('click', e => { const c = e.target.closest('.product'); if (c) open(c.dataset.id); });
  $('#m-close').onclick = close;
  modal.addEventListener('click', e => { if (e.target === modal) close(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
  $('#q-').onclick = () => { qty = Math.max(1, qty - 1); $('#q').textContent = qty; };
  $('#q+').onclick = () => { qty = Math.min(cur.stock || 1, qty + 1); $('#q').textContent = qty; };

  $('#m-add').onclick = async () => {
    const err = $('#m-err'); err.classList.add('hidden');
    try {
      const r = await fetch('/cart/add/', {
        method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': $('meta[name=csrf]').content },
        body: JSON.stringify({ id: cur.id, qty, size, color })
      });
      const d = await r.json();
      if (!r.ok) { err.textContent = d.error; err.classList.remove('hidden'); return; }
      const c = $('#cart-count'); c.textContent = d.count; c.classList.remove('hidden');
      close(); toast('Added to your cart 🛍');
    } catch { err.textContent = 'Connection problem. Please try again.'; err.classList.remove('hidden'); }
  };
})();
