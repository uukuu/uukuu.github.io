// static/js/toc-collapse.js
(function () {
  // === 选择器更宽，兼容多种结构 ===
  const SELECTORS = [
    'nav#TableOfContents',          // Hugo 默认
    '#TableOfContents',             // 退而求其次
    '.toc nav',                     // PaperMod 常见包裹
    '.toc',                         // 兜底：整个 toc 容器
  ];

  // 等待某个元素出现
  function waitForTOC(timeoutMs = 3000) {
    return new Promise((resolve) => {
      // 先同步找一次
      const found = findTOC();
      if (found) return resolve(found);

      const obs = new MutationObserver(() => {
        const el = findTOC();
        if (el) { obs.disconnect(); resolve(el); }
      });
      obs.observe(document.documentElement, { childList: true, subtree: true });
      setTimeout(() => { obs.disconnect(); resolve(findTOC()); }, timeoutMs);
    });
  }

  function findTOC() {
    for (const sel of SELECTORS) {
      const el = document.querySelector(sel);
      if (el) return el;
    }
    return null;
  }

  function depthOf(li) {
    let d = 1, p = li.closest('ul');
    while (p && p.parentElement) {
      const up = p.parentElement.closest('ul');
      if (up) d++;
      p = up;
    }
    return d;
  }

  function setOpen(sub, btn, open) {
    sub.hidden = !open;
    btn.setAttribute('aria-expanded', String(open));
    btn.textContent = open ? '▾' : '▸';
  }

  function enhance(navRoot) {
    // 如果拿到的是外层 .toc，就找里面的 nav
    const nav = navRoot.matches('nav') ? navRoot : navRoot.querySelector('nav, #TableOfContents') || navRoot;
    nav.querySelectorAll('li').forEach(li => {
      const sub  = li.querySelector(':scope > ul');
      const link = li.querySelector(':scope > a');
      if (!sub || !link) return;

      const btn = document.createElement('button');
      btn.className = 'toc-toggle';
      btn.type = 'button';
      btn.textContent = '▸';
      btn.setAttribute('aria-expanded', 'false');
      li.classList.add('toc-has-children');
      link.parentNode.insertBefore(btn, link);
      // 默认：展开到二级（按需改成 1/2/3…）
      setOpen(sub, btn, depthOf(li) <= 0);
      // console.log(depthOf(li));
      btn.addEventListener('click', (e) => {
        e.preventDefault(); e.stopPropagation();
        const open = btn.getAttribute('aria-expanded') === 'true';
        setOpen(sub, btn, !open);
      });
    });

    // Alt+点文字 => 折叠/展开本分支（不跳转）
    nav.addEventListener('click', (e) => {
      const a = e.target.closest('a');
      if (!a || !e.altKey) return;
      const li  = a.closest('li');
      const sub = li?.querySelector(':scope > ul');
      const btn = li?.querySelector(':scope > .toc-toggle');
      if (sub && btn) { e.preventDefault(); setOpen(sub, btn, btn.getAttribute('aria-expanded') !== 'true'); }
    });

    // 打开当前锚点所在链
    const openChainFromHash = () => {
      const hash = decodeURIComponent(location.hash || '');
      if (!hash) return;
      const a = nav.querySelector(`a[href="${hash}"]`);
      if (!a) return;
      let li = a.closest('li');
      while (li) {
        const sub = li.querySelector(':scope > ul');
        const btn = li.querySelector(':scope > .toc-toggle');
        if (sub && btn) setOpen(sub, btn, true);
        li = li.parentElement?.closest('li');
      }
    };
    openChainFromHash();
    window.addEventListener('hashchange', openChainFromHash);
  }

  // 开始：等 TOC 出现再增强
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => waitForTOC().then(el => el && enhance(el)));
  } else {
    waitForTOC().then(el => el && enhance(el));
  }
})();
