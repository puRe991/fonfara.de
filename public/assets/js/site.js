/* fonfara.de – kleine, abhängigkeitsfreie Helfer */
(function () {
  "use strict";
  var doc = document.documentElement;
  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };

  /* ---------- Theme ---------- */
  var themeBtn = document.querySelector("[data-theme-toggle]");
  if (themeBtn) {
    themeBtn.addEventListener("click", function () {
      var cur = doc.getAttribute("data-theme") ||
        (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
      var next = cur === "dark" ? "light" : "dark";
      doc.setAttribute("data-theme", next);
      store.set("theme", next);
    });
  }

  /* ---------- Mobile nav ---------- */
  var header = document.querySelector(".site-header");
  var toggle = document.querySelector(".nav-toggle");
  if (header && toggle) {
    toggle.addEventListener("click", function () {
      var open = header.classList.toggle("nav-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && header.classList.contains("nav-open")) {
        header.classList.remove("nav-open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.focus();
      }
    });
  }

  /* ---------- Back to top ---------- */
  var topBtn = document.querySelector(".to-top");
  if (topBtn) {
    var onScroll = function () { topBtn.classList.toggle("is-visible", window.scrollY > 900); };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
    topBtn.addEventListener("click", function () { window.scrollTo({ top: 0 }); });
  }

  /* ---------- Reveal on scroll ---------- */
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("is-in"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px" });
    document.querySelectorAll(".reveal").forEach(function (el) { io.observe(el); });
  } else {
    document.querySelectorAll(".reveal").forEach(function (el) { el.classList.add("is-in"); });
  }

  /* ---------- YouTube: erst nach Klick laden (Datenschutz) ---------- */
  var dialog = document.getElementById("vdialog");
  function openVideo(id, title, start) {
    var src = "https://www.youtube-nocookie.com/embed/" + encodeURIComponent(id) +
      "?autoplay=1&rel=0&modestbranding=1" + (start ? "&start=" + start : "");
    if (!dialog || typeof dialog.showModal !== "function") {
      window.open("https://www.youtube.com/watch?v=" + encodeURIComponent(id), "_blank", "noopener");
      return;
    }
    dialog.querySelector(".vdialog__title").textContent = title || "";
    var frame = dialog.querySelector(".vdialog__frame");
    frame.innerHTML = "";
    var ifr = document.createElement("iframe");
    ifr.src = src;
    ifr.title = title || "Video";
    ifr.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share";
    ifr.allowFullscreen = true;
    frame.appendChild(ifr);
    pauseAudio();
    dialog.showModal();
  }
  function closeVideo() {
    if (!dialog) return;
    dialog.querySelector(".vdialog__frame").innerHTML = "";
    if (dialog.open) dialog.close();
  }
  if (dialog) {
    dialog.addEventListener("close", function () { dialog.querySelector(".vdialog__frame").innerHTML = ""; });
    dialog.addEventListener("click", function (e) { if (e.target === dialog) closeVideo(); });
    dialog.querySelector(".vdialog__close").addEventListener("click", closeVideo);
  }
  document.addEventListener("click", function (e) {
    var b = e.target.closest("[data-yt]");
    if (!b) return;
    e.preventDefault();
    openVideo(b.getAttribute("data-yt"), b.getAttribute("data-title"), b.getAttribute("data-start"));
  });

  /* ---------- Andere Einbettungen (SoundCloud etc.) erst nach Klick ---------- */
  document.addEventListener("click", function (e) {
    var b = e.target.closest("[data-embed]");
    if (!b) return;
    e.preventDefault();
    var box = b.closest(".lazy-embed");
    var ifr = document.createElement("iframe");
    ifr.src = b.getAttribute("data-embed");
    ifr.height = b.getAttribute("data-height") || "166";
    ifr.title = b.getAttribute("data-title") || "Eingebetteter Inhalt";
    ifr.allow = "autoplay; encrypted-media";
    ifr.loading = "lazy";
    box.innerHTML = "";
    box.appendChild(ifr);
  });

  /* ---------- Audio-Archiv ---------- */
  var audio = null, current = null, bar = document.querySelector(".player-bar");
  var tracks = Array.prototype.slice.call(document.querySelectorAll(".track[data-src]"));
  function fmt(t) { if (!isFinite(t)) return "0:00"; var m = Math.floor(t / 60), s = Math.floor(t % 60); return m + ":" + (s < 10 ? "0" : "") + s; }
  function pauseAudio() { if (audio && !audio.paused) audio.pause(); }
  function setState() {
    tracks.forEach(function (t) {
      var active = t === current;
      t.classList.toggle("is-active", active);
      t.classList.toggle("is-playing", active && audio && !audio.paused);
      var btn = t.querySelector(".track__btn");
      if (btn) btn.setAttribute("aria-label", (active && audio && !audio.paused ? "Pause: " : "Abspielen: ") + t.getAttribute("data-title"));
    });
    if (bar) {
      bar.classList.toggle("is-visible", !!current);
      bar.classList.toggle("is-playing", !!(audio && !audio.paused));
      document.body.classList.toggle("has-player", !!current);
    }
  }
  function play(t) {
    if (!audio) {
      audio = new Audio();
      audio.preload = "none";
      audio.addEventListener("play", setState);
      audio.addEventListener("pause", setState);
      audio.addEventListener("timeupdate", function () {
        if (!current) return;
        var p = audio.duration ? (audio.currentTime / audio.duration) * 100 : 0;
        var i = current.querySelector(".track__progress i"); if (i) i.style.width = p + "%";
        if (bar) {
          bar.querySelector(".player-bar__seek i").style.width = p + "%";
          bar.querySelector(".player-bar__time").textContent = fmt(audio.currentTime) + " / " + fmt(audio.duration);
        }
      });
      audio.addEventListener("ended", function () { var n = tracks[tracks.indexOf(current) + 1]; if (n) play(n); else setState(); });
      audio.addEventListener("error", function () {
        if (bar) bar.querySelector(".player-bar__time").textContent = "Datei konnte nicht geladen werden.";
      });
    }
    if (current === t) { if (audio.paused) audio.play(); else audio.pause(); return; }
    current = t;
    audio.src = t.getAttribute("data-src");
    if (bar) bar.querySelector(".player-bar__title").textContent = t.getAttribute("data-title");
    audio.play().catch(function () {});
    setState();
  }
  tracks.forEach(function (t) {
    t.querySelector(".track__btn").addEventListener("click", function () { play(t); });
    var pr = t.querySelector(".track__progress");
    if (pr) pr.addEventListener("click", function (e) {
      if (current !== t || !audio.duration) return;
      var r = pr.getBoundingClientRect(); audio.currentTime = ((e.clientX - r.left) / r.width) * audio.duration;
    });
  });
  if (bar) {
    bar.querySelector("[data-act=toggle]").addEventListener("click", function () { if (current) play(current); });
    bar.querySelector("[data-act=next]").addEventListener("click", function () { var n = tracks[tracks.indexOf(current) + 1]; if (n) play(n); });
    bar.querySelector("[data-act=prev]").addEventListener("click", function () { var n = tracks[tracks.indexOf(current) - 1]; if (n) play(n); });
    bar.querySelector(".player-bar__seek").addEventListener("click", function (e) {
      if (!audio || !audio.duration) return;
      var r = this.getBoundingClientRect(); audio.currentTime = ((e.clientX - r.left) / r.width) * audio.duration;
    });
  }
  /* Andere <audio>-Elemente: immer nur eins gleichzeitig */
  document.addEventListener("play", function (e) {
    document.querySelectorAll("audio").forEach(function (a) { if (a !== e.target) a.pause(); });
    if (audio && e.target !== audio) audio.pause();
  }, true);
})();
