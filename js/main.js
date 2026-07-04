/* =========================================================
   청첩장 (Wedding Invitation) — main.js
   Vanilla JS. No external dependencies.
   ========================================================= */
(function () {
  "use strict";

  /* ---- Wedding config (replace with real values) ---- */
  var WEDDING = {
    date: new Date(2026, 9, 17, 13, 0, 0), // month is 0-based → October
    year: 2026,
    month: 10, // human-readable
    day: 17,
  };

  /* ---------------------------------------------------------
     Scroll reveal
  --------------------------------------------------------- */
  var reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) {
            e.target.classList.add("is-visible");
            io.unobserve(e.target);
          }
        });
      },
      { threshold: 0.12 }
    );
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("is-visible"); });
  }

  /* ---------------------------------------------------------
     Toast
  --------------------------------------------------------- */
  var toastEl = document.getElementById("toast");
  var toastTimer;
  function toast(msg) {
    if (!toastEl) return;
    toastEl.textContent = msg;
    toastEl.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () {
      toastEl.classList.remove("show");
    }, 1900);
  }

  /* ---------------------------------------------------------
     Calendar render + D-day
  --------------------------------------------------------- */
  (function buildCalendar() {
    var body = document.getElementById("cal-body");
    if (!body) return;
    var first = new Date(WEDDING.year, WEDDING.month - 1, 1);
    var startDow = first.getDay();
    var daysInMonth = new Date(WEDDING.year, WEDDING.month, 0).getDate();
    var frag = document.createDocumentFragment();

    for (var b = 0; b < startDow; b++) {
      frag.appendChild(document.createElement("span"));
    }
    for (var d = 1; d <= daysInMonth; d++) {
      var cell = document.createElement("span");
      cell.textContent = d;
      var dow = (startDow + d - 1) % 7;
      if (dow === 0) cell.classList.add("day--sun");
      if (dow === 6) cell.classList.add("day--sat");
      if (d === WEDDING.day) cell.classList.add("day--wed");
      frag.appendChild(cell);
    }
    body.appendChild(frag);
  })();

  (function ddayCount() {
    var el = document.getElementById("dday-count");
    if (!el) return;
    var today = new Date();
    today.setHours(0, 0, 0, 0);
    var target = new Date(WEDDING.date);
    target.setHours(0, 0, 0, 0);
    var diff = Math.round((target - today) / 86400000);
    if (diff > 0) el.textContent = "D-" + diff + " 일";
    else if (diff === 0) el.textContent = "D-DAY";
    else el.textContent = "성혼";
  })();

  /* ---------------------------------------------------------
     Gallery (placeholder tiles + lightbox)
  --------------------------------------------------------- */
  (function gallery() {
    var grid = document.getElementById("gallery");
    if (!grid) return;
    var hues = [28, 20, 34, 16, 30, 22, 26, 18, 32];
    var lb = document.createElement("div");
    lb.className = "lightbox";
    lb.innerHTML = '<div class="lightbox__img"></div>';
    document.body.appendChild(lb);
    var lbImg = lb.querySelector(".lightbox__img");

    hues.forEach(function (h) {
      var tile = document.createElement("div");
      tile.className = "gallery__tile";
      var bg =
        "linear-gradient(135deg, hsl(" + h + ",30%,78%), hsl(" + (h + 12) + ",28%,62%))";
      tile.style.background = bg;
      tile.addEventListener("click", function () {
        lbImg.style.background = bg;
        lb.classList.add("open");
      });
      grid.appendChild(tile);
    });
    lb.addEventListener("click", function () { lb.classList.remove("open"); });
  })();

  /* ---------------------------------------------------------
     Contact toggle
  --------------------------------------------------------- */
  document.querySelectorAll("[data-toggle]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var panel = document.getElementById(btn.getAttribute("data-toggle"));
      if (panel) panel.hidden = !panel.hidden;
    });
  });

  /* ---------------------------------------------------------
     Copy buttons (accounts)
  --------------------------------------------------------- */
  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise(function (resolve, reject) {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand("copy"); resolve(); }
      catch (e) { reject(e); }
      document.body.removeChild(ta);
    });
  }
  document.querySelectorAll("[data-copy]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      copyText(btn.getAttribute("data-copy")).then(
        function () { toast("계좌번호가 복사되었습니다"); },
        function () { toast("복사에 실패했습니다"); }
      );
    });
  });

  /* ---------------------------------------------------------
     Share buttons
  --------------------------------------------------------- */
  document.querySelectorAll("[data-share]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var kind = btn.getAttribute("data-share");
      if (kind === "top") {
        document.getElementById("top").scrollIntoView({ behavior: "smooth" });
      } else if (kind === "link") {
        copyText(window.location.href).then(
          function () { toast("링크가 복사되었습니다"); },
          function () { toast("복사에 실패했습니다"); }
        );
      }
    });
  });

  /* ---------------------------------------------------------
     RSVP form (stores locally; wire to a backend in production)
  --------------------------------------------------------- */
  var rsvpForm = document.getElementById("rsvp-form");
  if (rsvpForm) {
    rsvpForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var data = {
        side: rsvpForm.side.value,
        name: rsvpForm.name.value.trim(),
        attend: rsvpForm.attend.value,
        count: rsvpForm.count.value || "1",
      };
      try {
        var list = JSON.parse(localStorage.getItem("rsvp") || "[]");
        list.push(data);
        localStorage.setItem("rsvp", JSON.stringify(list));
      } catch (e2) { /* ignore storage errors */ }
      var msg = document.getElementById("rsvp-msg");
      if (msg) {
        msg.hidden = false;
        msg.textContent = "참석 의사가 전달되었습니다. 감사합니다 :)";
      }
      rsvpForm.reset();
    });
  }

  /* ---------------------------------------------------------
     Guestbook (localStorage-backed demo)
  --------------------------------------------------------- */
  var gbForm = document.getElementById("gb-form");
  var gbList = document.getElementById("gb-list");

  function escapeHtml(s) {
    return s.replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function loadGb() {
    try { return JSON.parse(localStorage.getItem("guestbook") || "[]"); }
    catch (e) { return []; }
  }
  function renderGb() {
    if (!gbList) return;
    var items = loadGb();
    if (!items.length) {
      gbList.innerHTML = '<li class="gb__empty">첫 번째 축하 메시지를 남겨주세요.</li>';
      return;
    }
    gbList.innerHTML = items
      .slice()
      .reverse()
      .map(function (it) {
        return (
          '<li class="gb__item"><div class="gb__item-head">' +
          '<span class="gb__item-name">' + escapeHtml(it.name) + "</span>" +
          '<span class="gb__item-date">' + escapeHtml(it.date) + "</span></div>" +
          '<p class="gb__item-msg">' + escapeHtml(it.msg) + "</p></li>"
        );
      })
      .join("");
  }
  if (gbForm) {
    gbForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var name = gbForm.gbname.value.trim();
      var msg = gbForm.gbmsg.value.trim();
      if (!name || !msg) return;
      var now = new Date();
      var date =
        now.getFullYear() + "." +
        String(now.getMonth() + 1).padStart(2, "0") + "." +
        String(now.getDate()).padStart(2, "0");
      var items = loadGb();
      items.push({ name: name, msg: msg, date: date });
      try { localStorage.setItem("guestbook", JSON.stringify(items)); }
      catch (e2) { /* ignore */ }
      gbForm.reset();
      renderGb();
      toast("축하 메시지가 등록되었습니다");
    });
    renderGb();
  }
})();
