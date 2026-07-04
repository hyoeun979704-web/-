/* =========================================================
   류근창 ♥ 김효은 모바일 청첩장 — app.js
   순수 바닐라 JS. 외부 런타임 의존 없음.
   ========================================================= */
(function () {
  "use strict";

  var P = function (id, w) { return "https://lh3.googleusercontent.com/d/" + id + "=w" + (w || 1200); };
  var pad2 = function (n) { return String(n).padStart(2, "0"); };
  var esc = function (s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); };

  var $ = function (id) { return document.getElementById(id); };
  var screen = $("screen");

  /* ---------- 데이터 ---------- */
  var GAL = ['1mswGgI8UV_DG1ijpeT6ovAKf1coB2hbk','1j10zq50UguAM7pwclJcnJhG5B2wBnxJB','1Ud4cd7w_Trj3yLwrQGMyFB9pY2nIHad0','1BWIAXxvMfQAiYiRY6ngT_IWOvLmH3SkA','1Pv2StB-5JL7LBwbVCAO2uf4ss29iubHn','12ofEYDOAhOuTiAyr-Oj5FxKN5xZfAwgg','1CDQSNkR5Zb_89BL3G-yKBcpjytJg4LVr','1Wz_WRuXPKREvL8XyidKktfQ76p3ELzq4','1R3z9MzKtcG0Di2JsPaYzWUln8Ayy8cPy','1apSHqwukiU96jBhju0wz3umPAROw8nlL','1gO506_Nexvkao4Ihn4J45TcH2oqVyxE0','16vbKXGfThCx0gzeZPjFLFG3wfAlZ1lRo','1sjW5gUm0Y8cmh6BUPQ_8cb8c4HwEptc4','1QIpyDf1DiCHJc2uC11aawUeKhsPCSlaa','1v1vDesQFji8fcSTzlrAdkaMm6pYDQVmr','1cpC0U4miBZZ_l7g3UoMa4wanWFWvLvhJ','1zvN4u0Ic7GYBOh1OxZjVCu537RHPJEQu','1Jm2fnFpmhOGuJpQRDbwRkv7RTBsAo4sG','1oePO6fROU_v5iRELMndapH4_pW66nYtT','1AOD6evTQV4qSPJMe9aq9EdWgt4CNOct8'];
  var gH = [232, 168, 200, 150, 214, 176, 158, 224, 186];

  var bankColors = { '국민': ['#ffbc00', '#3a2e00'], '농협': ['#0a8c3c', '#fff'], '신한': ['#1b59a6', '#fff'], '우리': ['#0067ac', '#fff'], '하나': ['#00857a', '#fff'], '카카오뱅크': ['#ffe000', '#3a2e00'] };
  var groomAccts = [
    { role: '신랑', name: '류근창', bank: '하나', num: '680-910428-16-707' },
    { role: '아버지', name: '류청림', bank: '국민', num: '735702-01-410425' },
    { role: '어머니', name: '송소영', bank: '농협', num: '485019-52-143478' }
  ];
  var brideAccts = [
    { role: '신부', name: '김효은', bank: '신한', num: '110-460-118896' },
    { role: '아버지', name: '김승수', bank: '농협', num: '352-1478-6639-13' },
    { role: '어머니', name: '변수아', bank: '농협', num: '451066-52-056303' }
  ];

  var gbSlots = [
    { top: 12, left: 8, rot: -5, w: 116, ta: 'left' },
    { top: 16, right: 8, rot: 4, w: 116, ta: 'right' },
    { top: 66, left: 4, rot: 3, w: 92, ta: 'left' },
    { top: 92, right: 4, rot: -4, w: 92, ta: 'right' },
    { top: 150, left: 2, rot: -3, w: 82, ta: 'left' },
    { top: 205, right: 2, rot: 3, w: 82, ta: 'right' },
    { top: 258, left: 4, rot: 4, w: 82, ta: 'left' },
    { top: 312, right: 6, rot: -3, w: 86, ta: 'right' },
    { top: 338, left: 12, rot: -4, w: 120, ta: 'left' },
    { top: 372, right: 14, rot: 3, w: 120, ta: 'right' },
    { top: 416, left: 26, rot: 2, w: 130, ta: 'left' },
    { top: 420, right: 22, rot: -3, w: 120, ta: 'right' }
  ];
  var GB_PER = 8;
  var DEFAULT_ENTRIES = [
    { name: '정세현', msg: '두 분 정말 잘 어울려요. 진심으로 축하해요!', date: '2026.06.20' },
    { name: '이수민', msg: '드디어 가는구나 ㅠㅠ 행복하게 잘 살아!', date: '2026.06.22' },
    { name: '박준영', msg: '결혼 축하한다! 늘 꽃길만 걷자', date: '2026.06.23' },
    { name: '최가은', msg: '두 사람 너무 예뻐요. 행복하세요!', date: '2026.06.24' },
    { name: '김도훈', msg: '평생 지금처럼 사랑하며 살길!', date: '2026.06.25' },
    { name: '한지민', msg: '축하해요 언니! 너무 부러워요', date: '2026.06.25' },
    { name: '오세훈', msg: '결혼 축하해 친구야! 행복하게 잘 살자', date: '2026.06.26' },
    { name: '윤서연', msg: '백년해로하세요. 진심으로 축복합니다', date: '2026.06.26' },
    { name: '장민재', msg: '두 분의 새 출발을 응원합니다!', date: '2026.06.27' },
    { name: '신유나', msg: '예쁜 신부 효은이 진심으로 축하해', date: '2026.06.27' },
    { name: '강태현', msg: '행복한 가정 이루길 바랄게', date: '2026.06.27' }
  ];

  /* ---------- 토스트 ---------- */
  var toastEl = $("toast"), toastTimer;
  function toast(msg) {
    toastEl.textContent = msg;
    toastEl.hidden = false;
    toastEl.style.animation = "none"; void toastEl.offsetWidth; toastEl.style.animation = "toastIn .3s ease";
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.hidden = true; }, 2200);
  }

  /* ---------- 복사 ---------- */
  function copyText(text, okMsg) {
    var done = function () { toast(okMsg || "복사되었어요"); };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, function () { fallbackCopy(text, done); });
    } else fallbackCopy(text, done);
  }
  function fallbackCopy(text, cb) {
    try { var ta = document.createElement("textarea"); ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0"; document.body.appendChild(ta); ta.select(); document.execCommand("copy"); document.body.removeChild(ta); cb && cb(); } catch (e) {}
  }

  /* ---------- 카운트다운 ---------- */
  var TARGET = new Date(2026, 7, 23, 12, 50, 0).getTime(); // 2026-08-23 12:50
  function tick() {
    var diff = Math.max(0, TARGET - Date.now());
    var d = Math.floor(diff / 86400000); diff -= d * 86400000;
    var h = Math.floor(diff / 3600000); diff -= h * 3600000;
    var m = Math.floor(diff / 60000); diff -= m * 60000;
    var s = Math.floor(diff / 1000);
    $("cdD").textContent = pad2(d); $("cdH").textContent = pad2(h);
    $("cdM").textContent = pad2(m); $("cdS").textContent = pad2(s);
  }
  tick(); setInterval(tick, 1000);

  /* ---------- 갤러리 + 라이트박스 ---------- */
  var lbIndex = 0;
  var galEl = $("gallery");
  GAL.forEach(function (id, i) {
    var cell = document.createElement("div");
    cell.setAttribute("data-reveal", "");
    cell.setAttribute("data-reveal-init", "scale(.94)");
    cell.style.cssText = "position:relative; aspect-ratio:3/4; border-radius:6px; overflow:hidden; scroll-snap-align:center; box-shadow:0 8px 20px -14px rgba(28,71,51,.5);";
    var img = document.createElement("img");
    img.src = P(id, 900); img.alt = ""; img.loading = "lazy"; img.draggable = false;
    img.style.cssText = "position:absolute; inset:0; width:100%; height:100%; object-fit:cover; pointer-events:none;";
    var btn = document.createElement("button");
    btn.setAttribute("aria-label", "확대");
    btn.style.cssText = "position:absolute; inset:0; width:100%; height:100%; border:none; background:transparent; cursor:pointer;";
    btn.addEventListener("click", function () { openLb(i); });
    cell.appendChild(img); cell.appendChild(btn); galEl.appendChild(cell);
  });

  var lb = $("lightbox"), lbImg = $("lbImg"), lbCounter = $("lbCounter");
  function openLb(i) { lbIndex = i; renderLb(); lb.hidden = false; }
  function closeLb() { lb.hidden = true; }
  function lbNav(d) { lbIndex = (lbIndex + d + GAL.length) % GAL.length; renderLb(); }
  function renderLb() { lbImg.src = P(GAL[lbIndex], 1400); lbCounter.textContent = (lbIndex + 1) + " / " + GAL.length; }
  $("lbClose").addEventListener("click", function (e) { e.stopPropagation(); closeLb(); });
  $("lbPrev").addEventListener("click", function (e) { e.stopPropagation(); lbNav(-1); });
  $("lbNext").addEventListener("click", function (e) { e.stopPropagation(); lbNav(1); });
  lb.addEventListener("click", function (e) { if (e.target === lb) closeLb(); });
  var _tx = 0;
  lb.addEventListener("touchstart", function (e) { _tx = e.changedTouches[0].clientX; }, { passive: true });
  lb.addEventListener("touchend", function (e) { var dx = e.changedTouches[0].clientX - _tx; if (Math.abs(dx) > 40) lbNav(dx < 0 ? 1 : -1); });

  /* ---------- 계좌 (마음 전하실 곳) ---------- */
  function renderAccts(container, list) {
    container.innerHTML = list.map(function (a) {
      var bc = bankColors[a.bank] || ['#2f9e5f', '#fff'];
      var chip = "width:38px; height:38px; border-radius:5.5px; flex-shrink:0; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:700; font-family:'Noto Sans KR',sans-serif; background:" + bc[0] + "; color:" + bc[1] + ";";
      return '<div style="display:flex; align-items:center; gap:11px; padding:12px 0; border-top:1px solid var(--c-line,rgba(54,68,61,.16));">' +
        '<div style="' + chip + '">' + esc(a.bank.slice(0, 2)) + '</div>' +
        '<div style="flex:1; min-width:0;"><div style="font-size:11px; color:var(--c-accent,#2f9e5f);">' + esc(a.role) + ' · ' + esc(a.name) + '</div>' +
        '<div style="font-size:12.5px; color:var(--c-deep,#36443d); margin-top:2px; letter-spacing:.01em;">' + esc(a.bank) + ' ' + esc(a.num) + '</div></div>' +
        '<div style="display:flex; gap:6px; flex-shrink:0;">' +
        '<button data-send="' + esc(a.bank) + '" style="padding:7px 13px; border-radius:999px; border:none; background:var(--c-accent,#2f9e5f); color:#fff; font-size:11px; cursor:pointer;">송금</button>' +
        '<button data-copy="' + esc(a.bank + ' ' + a.num) + '" style="padding:7px 13px; border-radius:999px; border:1px solid var(--c-accent,#2f9e5f); background:transparent; color:var(--c-accent,#2f9e5f); font-size:11px; cursor:pointer;">복사</button>' +
        '</div></div>';
    }).join("");
  }
  renderAccts(document.querySelector('[data-acc="groom"]'), groomAccts);
  renderAccts(document.querySelector('[data-acc="bride"]'), brideAccts);

  document.querySelectorAll("[data-acc-toggle]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var key = btn.getAttribute("data-acc-toggle");
      var body = document.querySelector('[data-acc="' + key + '"]');
      var open = body.hidden;
      body.hidden = !open;
      btn.querySelector(".acc-label").textContent = open ? "닫기 −" : "열기 +";
    });
  });

  // 복사/송금 이벤트 위임
  document.addEventListener("click", function (e) {
    var c = e.target.closest && e.target.closest("[data-copy]");
    if (c) { copyText(c.getAttribute("data-copy"), "계좌번호가 복사되었어요"); return; }
    var s = e.target.closest && e.target.closest("[data-send]");
    if (s) { toast(s.getAttribute("data-send") + " 송금으로 연결돼요 (샘플)"); }
  });

  /* ---------- RSVP ---------- */
  var rsvp = { side: "신랑측", attending: "참석", meal: "식사 함", count: 1 };
  document.querySelectorAll('[data-rsvp]').forEach(function (btn) {
    btn.addEventListener("click", function () {
      var group = btn.getAttribute("data-rsvp");
      rsvp[group] = btn.getAttribute("data-val");
      document.querySelectorAll('[data-rsvp="' + group + '"]').forEach(function (b) { b.classList.remove("on"); });
      btn.classList.add("on");
    });
  });
  $("countDec").addEventListener("click", function () { rsvp.count = Math.max(1, rsvp.count - 1); $("countVal").textContent = rsvp.count; });
  $("countInc").addEventListener("click", function () { rsvp.count = Math.min(9, rsvp.count + 1); $("countVal").textContent = rsvp.count; });
  $("rsvpSubmit").addEventListener("click", function () {
    var name = $("rsvpName").value.trim();
    if (!name) { toast("성함을 입력해 주세요"); return; }
    rsvp.name = name;
    // 백엔드 미사용: 응답을 localStorage에 보관 (원할 경우 서버/구글시트로 확장 가능)
    try {
      var arr = JSON.parse(localStorage.getItem("rsvp_wedding_v1") || "[]");
      arr.push({ side: rsvp.side, attending: rsvp.attending, meal: rsvp.meal, name: name, count: rsvp.count, at: new Date().toISOString() });
      localStorage.setItem("rsvp_wedding_v1", JSON.stringify(arr));
    } catch (e) {}
    $("rsvpForm").hidden = true;
    $("rsvpDone").hidden = false;
    toast("참석 의사가 전달되었어요");
  });

  /* ---------- 방명록 ---------- */
  var entries = loadEntries(), gbPage = 0;
  function loadEntries() {
    try { var raw = localStorage.getItem("gb_wedding_v1"); var e = raw ? JSON.parse(raw) : null; if (e && e.length) return e; } catch (x) {}
    return DEFAULT_ENTRIES.slice();
  }
  function saveEntries() { try { localStorage.setItem("gb_wedding_v1", JSON.stringify(entries)); } catch (x) {} }
  function renderGb() {
    var pages = Math.max(1, Math.ceil(entries.length / GB_PER));
    if (gbPage > pages - 1) gbPage = pages - 1;
    var pageEntries = entries.slice(gbPage * GB_PER, gbPage * GB_PER + GB_PER);
    var board = $("gbBoard");
    var sc = (board.clientHeight || 340) / 480; // 슬롯 좌표는 480px 보드 기준 → 실제 높이에 맞춰 스케일
    var mF = Math.max(12, Math.round(16 * sc)), nF = Math.max(11, Math.round(14 * sc));
    board.innerHTML = pageEntries.map(function (e, i) {
      var sl = gbSlots[i % gbSlots.length];
      var css = "position:absolute; width:" + Math.round(sl.w * sc) + "px; transform:rotate(" + sl.rot + "deg); text-align:" + sl.ta + "; top:" + Math.round(sl.top * sc) + "px;";
      css += sl.left !== undefined ? "left:" + Math.round(sl.left * sc) + "px;" : "right:" + Math.round(sl.right * sc) + "px;";
      return '<div style="' + css + '">' +
        '<div style="font-family:\'Nanum Pen Script\',cursive; font-size:' + mF + 'px; line-height:1.12; color:#34402f;">' + esc(e.msg) + '</div>' +
        '<div style="font-family:\'Nanum Pen Script\',cursive; font-size:' + nF + 'px; color:#6c7c61; margin-top:1px;">– ' + esc(e.name) + '</div></div>';
    }).join("");
    $("gbCount").textContent = entries.length;
    $("gbPager").hidden = pages <= 1;
    $("gbPageLabel").textContent = (gbPage + 1) + " / " + pages;
    $("gbPrev").style.opacity = gbPage > 0 ? "1" : ".35";
    $("gbNext").style.opacity = gbPage < pages - 1 ? "1" : ".35";
  }
  $("gbPrev").addEventListener("click", function () { if (gbPage > 0) { gbPage--; renderGb(); } });
  $("gbNext").addEventListener("click", function () { var pages = Math.ceil(entries.length / GB_PER); if (gbPage < pages - 1) { gbPage++; renderGb(); } });
  var gbModal = $("gbModal");
  $("gbFormBtn").addEventListener("click", function () { gbModal.hidden = false; });
  $("gbModalClose").addEventListener("click", function () { gbModal.hidden = true; });
  gbModal.addEventListener("click", function (e) { if (e.target === gbModal) gbModal.hidden = true; });
  $("gbAdd").addEventListener("click", function () {
    var n = $("gbName").value.trim() || "익명";
    var m = $("gbMsg").value.trim();
    if (!m) { toast("축하 메시지를 입력해 주세요"); return; }
    var dt = new Date();
    var ds = dt.getFullYear() + "." + pad2(dt.getMonth() + 1) + "." + pad2(dt.getDate());
    entries.push({ name: n, msg: m, date: ds });
    saveEntries();
    gbPage = Math.floor((entries.length - 1) / GB_PER);
    $("gbName").value = ""; $("gbMsg").value = "";
    gbModal.hidden = true;
    renderGb();
    toast("방명록이 등록되었어요");
  });
  var gbImg = $("gbImg");
  if (gbImg) gbImg.addEventListener("load", renderGb); // 이미지 비율 로드 후 글씨 좌표 재계산
  window.addEventListener("resize", function () { if ($("gbBoard")) renderGb(); });
  renderGb();

  /* ---------- 하단 바 ---------- */
  $("barContact").addEventListener("click", function () { toast("신랑측 010-7528-4143 · 신부측 010-7528-7504"); });
  $("barShare").addEventListener("click", function () {
    var SITE = "https://20260823.hyoeun.io";
    var data = { title: "류근창 · 김효은 결혼합니다", text: "2026년 8월 23일, 저희 두 사람의 결혼식에 초대합니다.", url: SITE };
    if (navigator.share) { navigator.share(data).catch(function () {}); }
    else { copyText(SITE, "청첩장 링크가 복사되었어요"); }
  });
  $("barCal").addEventListener("click", function () {
    var ics = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//wedding//KR", "BEGIN:VEVENT", "UID:geunchang-hyoeun-20260823", "SUMMARY:류근창 · 김효은 결혼식", "DTSTART:20260823T035000Z", "DTEND:20260823T063000Z", "LOCATION:천안 T웨딩 그레이스홀", "DESCRIPTION:두 사람의 결혼식에 초대합니다.", "END:VEVENT", "END:VCALENDAR"].join("\r\n");
    try {
      var blob = new Blob([ics], { type: "text/calendar" });
      var url = URL.createObjectURL(blob);
      var a = document.createElement("a"); a.href = url; a.download = "wedding-2026-08-23.ics";
      document.body.appendChild(a); a.click(); document.body.removeChild(a);
      setTimeout(function () { URL.revokeObjectURL(url); }, 1500);
      toast("캘린더 일정이 저장되었어요");
    } catch (e) { toast("캘린더 저장이 지원되지 않는 환경이에요"); }
  });

  /* ---------- 배경음악 ---------- */
  var audio = $("bgm"), musicBtn = $("musicBtn"), musicOn = true;
  function musicSvg(on) {
    return on
      ? '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V6l10-2v11"></path><circle cx="6" cy="18" r="3"></circle><circle cx="16" cy="15" r="3"></circle></svg>'
      : '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V6l10-2v4"></path><circle cx="6" cy="18" r="3"></circle><path d="M4 4l16 16"></path></svg>';
  }
  function paintMusic() { musicBtn.innerHTML = musicSvg(musicOn); }
  try { var s = localStorage.getItem("bgm_on"); if (s !== null) musicOn = s === "1"; } catch (e) {}
  paintMusic();
  audio.volume = 0.55;
  if (musicOn) {
    var pr = audio.play();
    if (pr && pr.catch) pr.catch(function () {
      var resume = function () { if (musicOn) audio.play().catch(function () {}); document.removeEventListener("pointerdown", resume); document.removeEventListener("touchstart", resume); };
      document.addEventListener("pointerdown", resume, { once: true });
      document.addEventListener("touchstart", resume, { once: true });
    });
  }
  musicBtn.addEventListener("click", function () {
    musicOn = !musicOn; paintMusic();
    try { localStorage.setItem("bgm_on", musicOn ? "1" : "0"); } catch (e) {}
    if (musicOn) audio.play().catch(function () {}); else audio.pause();
  });

  /* ---------- 인트로 플레어 ---------- */
  setTimeout(function () { var f = $("flare"); if (f) f.parentNode.removeChild(f); }, 2400);

  /* ---------- 이미지 다운로드 방지 ---------- */
  // 완벽한 차단은 불가능하지만(스크린샷 등), 일반적인 저장/드래그는 막습니다.
  document.addEventListener("contextmenu", function (e) {
    if (e.target && (e.target.tagName === "IMG" || e.target.closest("#gallery") || e.target.closest("#lightbox"))) e.preventDefault();
  });
  document.addEventListener("dragstart", function (e) { if (e.target && e.target.tagName === "IMG") e.preventDefault(); });

  /* ---------- 리빌 + 커스텀 스냅 스크롤 (원본 이식) ---------- */
  var scroll = $("invscroll");
  function setupScrollFx() {
    var secs = Array.prototype.slice.call(scroll.children).filter(function (el) { return el.tagName === "SECTION"; });
    secs.forEach(function (sec, i) {
      if (i === 0) return;
      var pc = "rgba(255,255,255,0)";
      try { pc = getComputedStyle(secs[i - 1]).backgroundColor; } catch (e) {}
      if (!pc || pc === "rgba(0, 0, 0, 0)" || pc === "transparent") return;
      if (getComputedStyle(sec).position === "static") sec.style.position = "relative";
      var seam = document.createElement("div");
      seam.style.cssText = "position:absolute;top:-1px;left:0;right:0;height:56px;pointer-events:none;z-index:0;background:linear-gradient(to bottom," + pc + ",transparent);";
      sec.insertBefore(seam, sec.firstChild);
    });
  }
  function setupReveal() {
    var els = scroll.querySelectorAll("[data-reveal]");
    els.forEach(function (el) {
      var sec = el.closest("section");
      var sibs = sec ? Array.prototype.slice.call(sec.querySelectorAll("[data-reveal]")) : [el];
      var idx = Math.max(0, sibs.indexOf(el));
      var dl = (idx * 150) + "ms";
      var init = el.getAttribute("data-reveal-init") || "translateY(18px)";
      var ease = el.getAttribute("data-reveal-ease") || "cubic-bezier(.22,.61,.36,1)";
      var dur = el.getAttribute("data-reveal-dur") || "1.15s";
      el.style.opacity = "0"; el.style.transform = init;
      el.style.transition = "opacity " + dur + " ease " + dl + ", transform " + dur + " " + ease + " " + dl;
    });
    // 스냅은 CSS(scroll-snap-type)가 담당. 여기서는 등장 애니메이션만 처리한다.
    function revealSection(sec) {
      sec.querySelectorAll("[data-reveal]").forEach(function (el) {
        el.style.opacity = "1";
        el.style.transform = el.getAttribute("data-reveal-to") || "none";
      });
    }
    var secs = Array.prototype.slice.call(scroll.children).filter(function (el) { return el.tagName === "SECTION"; });
    if ("IntersectionObserver" in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) { revealSection(e.target); io.unobserve(e.target); }
        });
      }, { root: scroll, threshold: 0.18 });
      secs.forEach(function (s) { io.observe(s); });
    } else {
      secs.forEach(revealSection);
    }
  }
  setTimeout(function () { setupScrollFx(); setupReveal(); }, 80);
})();
