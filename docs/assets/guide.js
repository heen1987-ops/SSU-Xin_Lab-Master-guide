'use strict';

// 공개 안내의 개인 설정은 이 브라우저에만 저장한다.
const settings = {
  get(key, fallback) { try { return JSON.parse(localStorage.getItem(key)) ?? fallback; } catch { return fallback; } },
  set(key, value) { try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* 저장 불가여도 읽기·입력은 계속한다. */ } }
};
const themeButton = document.getElementById('theme-toggle');
const preferredTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  if (themeButton) {
    themeButton.textContent = theme === 'dark' ? '라이트 모드' : '다크 모드';
    themeButton.setAttribute('aria-label', theme === 'dark' ? '라이트 모드로 전환' : '다크 모드로 전환');
  }
}
applyTheme(settings.get('thesis-guide-theme', preferredTheme));
themeButton?.addEventListener('click', () => {
  const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  applyTheme(theme);
  settings.set('thesis-guide-theme', theme);
});

// 변경된 공통 체크리스트는 이전 석사 안내의 체크 상태를 자동 승계하지 않는다.
const checklistKey = 'thesis-guide-checklist-unified-v1';
const rawChecks = settings.get(checklistKey, {});
const checks = rawChecks && typeof rawChecks === 'object' && !Array.isArray(rawChecks) ? rawChecks : {};
document.querySelectorAll('#checklist input[type="checkbox"]').forEach(box => {
  box.checked = checks[box.id] === true;
  box.addEventListener('change', () => {
    const saved = settings.get(checklistKey, {});
    const current = saved && typeof saved === 'object' && !Array.isArray(saved) ? saved : {};
    current[box.id] = box.checked;
    settings.set(checklistKey, current);
  });
});

// 링크의 실제 대상 id만 관찰한다. 다른 페이지 URL은 CSS 선택자로 전달하지 않는다.
const navLinks = [...document.querySelectorAll('#navlinks a[href^="#"]')];
if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      navLinks.forEach(link => {
        const active = link.hash.slice(1) === entry.target.id;
        link.classList.toggle('active', active);
        if (active) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
    });
  }, { rootMargin:'-15% 0px -65% 0px' });
  navLinks.forEach(link => {
    const target = document.getElementById(link.hash.slice(1));
    if (target) observer.observe(target);
  });
}

// 검색은 현재 페이지의 절과 공통 진입점을 찾아 연결한다. 입력은 HTML로 해석하지 않는다.
const searchEntries = [
  { title:'학술총무 운영 · 검토 접수·수정·재검토·인수인계', href:'coordinator.html' },
  { title:'석박사 검토 기준 · 연구 범위·독립성·기여', href:'degree-review.html' },
  { title:'연구방법별 검토 · 실증·실험·혼합·질적·이론', href:'method-review.html' },
  { title:'SSU 논문 스킬 · ssu-paper 요청문·판본·결과 확인', href:'skill-workflow.html' },
  { title:'검토 서식 · 요청서·현황판·수정·기여·인수인계·규정', href:'templates.html' },
  { title:'운영 핸드북 · 전체 문서 지도', href:'handbook.html' },
  { title:'논문 가이드 · 전체 연구 단계', href:'index.html#stages' },
  { title:'실증연구 · 설문·측정·표집·분석', href:'empirical.html' },
  { title:'실험연구 · 비교군·실험·성능평가', href:'experiment.html' },
  { title:'학사·제출 요건 · 학점·종합시험·연구실적·심사', href:'requirements.html' },
  { title:'연구설계와 근거검증 · 연구방법·산출형식 선택', href:'research-workbench.html#routing' },
  { title:'문제정의 · 연구공백·연구질문·기여·반증 조건', href:'research-workbench.html#problem' },
  { title:'실증설계 · 이론·가설·문항·표본·분석계획', href:'research-workbench.html#empirical' },
  { title:'원문검수 · PDF·페이지·표·수식·OCR·근거추적', href:'research-workbench.html#fulltext' },
  { title:'연구설계·근거검증 작업지 내려받기', href:'research-workbench.html#workbook' },
  ...[...document.querySelectorAll('section[id]')].map(section => ({
    title:section.querySelector('h2,h3')?.textContent.trim() || section.id,
    href:'#' + section.id,
    keywords:section.textContent
  }))
];
const dialog = document.createElement('dialog');
dialog.className = 'guide-search';
dialog.setAttribute('aria-labelledby', 'guide-search-title');
dialog.innerHTML = '<div class="guide-search-head"><h2 id="guide-search-title">가이드 검색</h2><button type="button" class="action-btn" aria-label="검색 닫기">닫기</button></div><label for="guide-search-input">단계·주제·요건 검색</label><input id="guide-search-input" type="search" placeholder="예: 연구질문, 분석, 종합시험" autocomplete="off"><p class="guide-search-status" role="status" aria-live="polite"></p><ul aria-label="검색 결과"></ul>';
document.body.append(dialog);
const input = dialog.querySelector('input');
const resultList = dialog.querySelector('ul');
const status = dialog.querySelector('[role="status"]');
let searchOpener;
let searchDestination;
function renderSearch() {
  const query = input.value.trim().toLocaleLowerCase('ko');
  const results = searchEntries.filter(entry => (entry.title + ' ' + (entry.keywords || '')).toLocaleLowerCase('ko').includes(query));
  resultList.replaceChildren();
  results.forEach(entry => {
    const item = document.createElement('li');
    const link = document.createElement('a');
    link.href = entry.href;
    link.textContent = entry.title;
    link.addEventListener('click', () => {
      searchDestination = entry.href.startsWith('#') ? document.getElementById(entry.href.slice(1)) : null;
      dialog.close();
    });
    item.append(link);
    resultList.append(item);
  });
  status.textContent = results.length ? results.length + '개 항목 · 현재 페이지 본문과 공통 진입점에서 검색합니다.' : '검색 결과가 없습니다. 다른 단어나 상위 단계로 검색하세요.';
}
function openSearch() {
  if (dialog.open) return;
  searchOpener = document.activeElement;
  searchDestination = null;
  input.value = '';
  renderSearch();
  dialog.showModal();
  input.focus();
}
document.querySelectorAll('.search-trigger-btn').forEach(button => button.addEventListener('click', openSearch));
dialog.querySelector('button').addEventListener('click', () => dialog.close());
dialog.addEventListener('close', () => {
  if (searchDestination) { searchDestination.tabIndex = -1; searchDestination.focus(); }
  else searchOpener?.focus();
});
dialog.addEventListener('click', event => { if (event.target === dialog) { const r = dialog.getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close(); } });
input.addEventListener('input', renderSearch);
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && dialog.open) { event.preventDefault(); dialog.close(); return; }
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') { event.preventDefault(); openSearch(); }
});

document.querySelectorAll('main pre, main table').forEach(block => {
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'action-btn table-copy';
  button.textContent = '내용 복사';
  button.setAttribute('aria-live', 'polite');
  block.before(button);
  button.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(block.innerText);
      button.textContent = '복사했습니다';
    } catch { button.textContent = '복사할 수 없습니다. 내용을 선택해 복사하세요'; }
    setTimeout(() => { button.textContent = '내용 복사'; }, 4000);
  });
});
