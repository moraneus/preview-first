/* preview-first: controls, theme, selection, font notice, motion demos, device frames.
   Plain JavaScript, no dependencies. */
(function () {
  "use strict";

  var root = document.documentElement;
  var params = new URLSearchParams(location.search);
  var direction = root.getAttribute("data-direction");
  var CONTROLS = ["palette", "pairing", "radius", "density", "motion"];
  var storageKey = direction ? "pf:" + direction : null;

  function readSaved() {
    if (!storageKey) return {};
    try { return JSON.parse(localStorage.getItem(storageKey) || "{}"); } catch (e) { return {}; }
  }
  function save(state) {
    if (!storageKey) return;
    try { localStorage.setItem(storageKey, JSON.stringify(state)); } catch (e) { /* private mode */ }
  }
  function currentState() {
    var s = {};
    CONTROLS.forEach(function (k) { s[k] = root.getAttribute("data-" + k); });
    s.theme = root.getAttribute("data-theme") || "system";
    return s;
  }
  function apply(key, value) {
    if (value === null || value === undefined || value === "") return;
    if (key === "theme") {
      if (value === "system") root.removeAttribute("data-theme"); else root.setAttribute("data-theme", value);
    } else {
      root.setAttribute("data-" + key, value);
    }
    var sel = document.querySelector('select[data-control="' + key + '"]');
    if (sel && sel.value !== value) sel.value = value;
    if (key === "theme") {
      var btn = document.querySelector('[data-control="theme"]');
      if (btn) {
        var dark = effectiveTheme() === "dark";
        btn.setAttribute("aria-pressed", dark ? "true" : "false");
        btn.textContent = dark ? "Light" : "Dark";
      }
    }
  }
  function effectiveTheme() {
    var t = root.getAttribute("data-theme");
    if (t) return t;
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  // Embed mode (gallery thumbnails and device frames): hide chrome, take state from the URL.
  if (params.get("embed") === "1") root.setAttribute("data-embed", "1");
  var saved = readSaved();
  CONTROLS.concat(["theme"]).forEach(function (k) {
    var v = params.get(k) || saved[k];
    if (v) apply(k, v);
  });
  if (root.hasAttribute("data-gallery")) {
    var galleryTheme = null;
    try { galleryTheme = localStorage.getItem("pf:theme"); } catch (e) { /* ignore */ }
    if (galleryTheme) apply("theme", galleryTheme);
  }

  function updateFrames() {
    var state = currentState();
    document.querySelectorAll("iframe[data-live]").forEach(function (f) {
      var base = f.getAttribute("data-src") || f.getAttribute("src");
      if (!base) return;
      var url = new URL(base, location.href);
      Object.keys(state).forEach(function (k) {
        if (state[k] && state[k] !== "system") url.searchParams.set(k, state[k]); else url.searchParams.delete(k);
      });
      url.searchParams.set("embed", "1");
      if (f.getAttribute("src") !== url.toString()) f.setAttribute("src", url.toString());
    });
  }

  document.querySelectorAll("select[data-control]").forEach(function (sel) {
    sel.addEventListener("change", function () {
      apply(sel.getAttribute("data-control"), sel.value);
      save(currentState());
      updateFrames();
    });
  });
  document.querySelectorAll('[data-control="theme"]').forEach(function (btn) {
    btn.addEventListener("click", function () {
      var next = effectiveTheme() === "dark" ? "light" : "dark";
      apply("theme", next);
      save(currentState());
      try { localStorage.setItem("pf:theme", next); } catch (e) { /* ignore */ }
      updateFrames();
    });
    apply("theme", root.getAttribute("data-theme") || "system");
  });
  var reduced = document.querySelector('[data-control="reduced"]');
  if (reduced) reduced.addEventListener("change", function () {
    if (reduced.checked) root.setAttribute("data-reduced", "1"); else root.removeAttribute("data-reduced");
  });

  // Selection: POST to the local server, fall back to a download when there is no server.
  function toast(text) {
    var el = document.createElement("div");
    el.className = "pfc-toast";
    el.setAttribute("role", "status");
    el.textContent = text;
    document.body.appendChild(el);
    setTimeout(function () { el.remove(); }, 4000);
  }
  document.querySelectorAll('[data-action="select"]').forEach(function (btn) {
    btn.addEventListener("click", function () {
      var id = btn.getAttribute("data-direction");
      var state = {};
      if (id === direction) {
        state = currentState();
      } else {
        try { state = JSON.parse(localStorage.getItem("pf:" + id) || "{}"); } catch (e) { state = {}; }
      }
      var payload = { direction: id, overrides: state, selected_at: new Date().toISOString() };
      fetch(new URL("/select", location.origin), {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload)
      }).then(function (r) {
        if (!r.ok) throw new Error("HTTP " + r.status);
        btn.classList.add("is-done");
        btn.textContent = "Selected " + id;
        toast("Direction " + id + " selected. Tell Claude you are done and it will export the design contract.");
      }).catch(function () {
        var blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
        var a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = "selection.json";
        document.body.appendChild(a); a.click(); a.remove();
        toast("No local server found. selection.json was downloaded; move it into .design-preview/ or tell Claude your pick.");
      });
    });
  });

  // Font notice: name the real faces when the browser fell back.
  var main = document.querySelector("main[data-fonts]");
  if (main && document.fonts && document.fonts.check && !root.hasAttribute("data-embed")) {
    var fams = (main.getAttribute("data-fonts") || "").split("|").filter(Boolean);
    var check = function () {
      var missing = fams.filter(function (f) {
        try { return !document.fonts.check('16px "' + f + '"'); } catch (e) { return false; }
      });
      var notice = main.querySelector(".pf-font-notice");
      if (!notice) return;
      if (missing.length) {
        notice.querySelector("[data-fonts-missing]").textContent = missing.join(", ");
        notice.hidden = false;
      } else {
        notice.hidden = true;
      }
    };
    Promise.all(fams.map(function (f) {
      try { return document.fonts.load('16px "' + f + '"').catch(function () { return null; }); } catch (e) { return Promise.resolve(null); }
    })).then(function () { return document.fonts.ready; }).then(function () { setTimeout(check, 800); });
  }

  // Motion demos.
  document.querySelectorAll(".pf-motion-demo").forEach(function (fig) {
    var play = fig.querySelector('[data-action="play"]');
    var el = fig.querySelector(".pf-demo-el");
    function run() {
      fig.classList.remove("is-playing");
      void el.offsetWidth; // restart the animation
      fig.classList.add("is-playing");
    }
    if (play) play.addEventListener("click", run);
    if (el) el.addEventListener("animationend", function () { setTimeout(function () { fig.classList.remove("is-playing"); }, 600); });
  });

  // Device frames: scale each iframe to its column, rotate, toggle, external url.
  var deviceGrid = document.querySelector(".pf-devices");
  if (deviceGrid) {
    // Only http(s) pages may be framed; anything else (javascript:, data:, file:) is ignored.
    var externalUrl = null;
    try {
      var candidate = params.get("url");
      if (candidate) {
        var parsed = new URL(candidate, location.href);
        if (parsed.protocol === "http:" || parsed.protocol === "https:") externalUrl = parsed.toString();
      }
    } catch (e) { externalUrl = null; }
    var urlInput = document.querySelector("[data-device-url]");
    if (urlInput && externalUrl) urlInput.value = externalUrl;
    var urlNotice = document.querySelector(".pf-device-url-notice");

    function frameSrc(dev) {
      if (externalUrl) return externalUrl;
      var state = currentState();
      var url = new URL("draft.html", location.href);
      Object.keys(state).forEach(function (k) { if (state[k] && state[k] !== "system") url.searchParams.set(k, state[k]); });
      url.searchParams.set("embed", "1");
      return url.toString();
    }
    function layout(dev) {
      var screen = dev.querySelector(".pf-screen");
      var frame = dev.querySelector("iframe");
      var w = +dev.getAttribute("data-w"), h = +dev.getAttribute("data-h");
      if (dev.getAttribute("data-rotated") === "1") { var t = w; w = h; h = t; }
      var col = screen.clientWidth || 280;
      var scale = col / w;
      frame.style.width = w + "px";
      frame.style.height = h + "px";
      frame.style.transform = "scale(" + scale + ")";
      screen.style.height = Math.round(h * scale) + "px";
      dev.style.setProperty("--scale", scale);
      var label = dev.querySelector("[data-viewport]");
      if (label) label.textContent = w + " × " + h;
    }
    function load(dev) {
      var frame = dev.querySelector("iframe");
      if (!frame.getAttribute("src")) {
        frame.setAttribute("src", frameSrc(dev));
        if (externalUrl) {
          var done = false;
          frame.addEventListener("load", function () { done = true; });
          setTimeout(function () {
            if (!done && urlNotice) urlNotice.hidden = false;
          }, 5000);
        }
      }
      layout(dev);
    }
    var devices = Array.prototype.slice.call(deviceGrid.querySelectorAll(".pf-device"));
    devices.forEach(function (dev) {
      if (!dev.hidden) load(dev);
      var rot = dev.querySelector('[data-action="rotate"]');
      if (rot) rot.addEventListener("click", function () {
        dev.setAttribute("data-rotated", dev.getAttribute("data-rotated") === "1" ? "0" : "1");
        layout(dev);
      });
    });
    document.querySelectorAll("input[data-device-id]").forEach(function (box) {
      box.addEventListener("change", function () {
        var dev = deviceGrid.querySelector('.pf-device[data-device-id="' + box.getAttribute("data-device-id") + '"]');
        if (!dev) return;
        dev.hidden = !box.checked;
        if (box.checked) load(dev);
      });
    });
    var all = document.querySelector('[data-action="devices-all"]');
    var none = document.querySelector('[data-action="devices-none"]');
    if (all) all.addEventListener("click", function () {
      document.querySelectorAll("input[data-device-id]").forEach(function (b) { if (!b.checked) { b.checked = true; b.dispatchEvent(new Event("change")); } });
    });
    if (none) none.addEventListener("click", function () {
      document.querySelectorAll("input[data-device-id]").forEach(function (b) { if (b.checked) { b.checked = false; b.dispatchEvent(new Event("change")); } });
    });
    var safe = document.querySelector('[data-control="safe-area"]');
    if (safe) safe.addEventListener("change", function () { deviceGrid.toggleAttribute("data-safe", safe.checked); });
    if (urlInput) {
      var form = urlInput.closest("form");
      if (form) form.addEventListener("submit", function (e) {
        e.preventDefault();
        var u = new URL(location.href);
        if (urlInput.value.trim()) u.searchParams.set("url", urlInput.value.trim()); else u.searchParams.delete("url");
        location.href = u.toString();
      });
    }
    window.addEventListener("resize", function () { devices.forEach(function (d) { if (!d.hidden) layout(d); }); });
    // Controls change the draft inside every frame.
    document.querySelectorAll("select[data-control]").forEach(function (sel) {
      sel.addEventListener("change", function () {
        if (externalUrl) return;
        devices.forEach(function (d) { if (!d.hidden) d.querySelector("iframe").setAttribute("src", frameSrc(d)); });
      });
    });
  }

  // Gallery thumbnails: scale the 1280px draft to the card width.
  function fitThumbs() {
    document.querySelectorAll(".pfg-thumb").forEach(function (t) {
      var f = t.querySelector("iframe");
      if (f) f.style.transform = "scale(" + (t.clientWidth / 1280) + ")";
    });
  }
  fitThumbs();
  window.addEventListener("resize", fitThumbs);

  updateFrames();
})();
