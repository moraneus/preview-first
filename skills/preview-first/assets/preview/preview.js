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
  // Device frames pass the device's safe areas so the embedded draft pads itself like a real page.
  ["top", "bottom", "left", "right"].forEach(function (side) {
    var v = parseInt(params.get("sa-" + side) || "0", 10);
    if (v > 0) root.style.setProperty("--pf-safe-" + side, v + "px");
  });
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
  // Surprise me: ask the local server for a randomly composed direction, then show it.
  document.querySelectorAll('[data-action="shuffle"]').forEach(function (btn) {
    btn.addEventListener("click", function () {
      btn.disabled = true; var label = btn.textContent; btn.textContent = "Drawing";
      fetch(new URL("/shuffle", location.origin), { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" })
        .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
        .then(function (d) { location.href = d.id + "/draft.html"; })
        .catch(function () { btn.disabled = false; btn.textContent = label; toast("Surprise me needs the local preview server (serve_preview.py). Ask Claude for a random direction instead."); });
    });
  });
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

  // Font notice: name the real faces when the browser fell back. document.fonts.load resolves
  // with the faces that matched; an empty list means no @font-face exists for that family.
  var main = document.querySelector("main[data-fonts]");
  if (main && document.fonts && document.fonts.load && !root.hasAttribute("data-embed")) {
    var fams = (main.getAttribute("data-fonts") || "").split("|").filter(Boolean);
    Promise.all(fams.map(function (f) {
      return document.fonts.load('16px "' + f + '"').then(function (faces) {
        var ok = faces.some(function (face) { return face.status === "loaded"; });
        return ok ? null : f;
      }).catch(function () { return f; });
    })).then(function (results) {
      var missing = results.filter(Boolean);
      var notice = main.querySelector(".pf-font-notice");
      if (!notice) return;
      if (missing.length) {
        notice.querySelector("[data-fonts-missing]").textContent = missing.join(", ");
        notice.hidden = false;
      } else {
        notice.hidden = true;
      }
    });
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
      var rotated = dev.getAttribute("data-rotated") === "1";
      var cs = getComputedStyle(dev);
      var top = parseInt(cs.getPropertyValue("--sa-top") || "0", 10), bottom = parseInt(cs.getPropertyValue("--sa-bottom") || "0", 10);
      if (rotated) { url.searchParams.set("sa-left", top); url.searchParams.set("sa-right", top); url.searchParams.set("sa-bottom", Math.min(bottom, 21)); }
      else { url.searchParams.set("sa-top", top); url.searchParams.set("sa-bottom", bottom); }
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
        if (!externalUrl) dev.querySelector("iframe").setAttribute("src", frameSrc(dev));
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

  // ------------------------------------------------------------ render hooks (design ideas)
  (function hooks() {
    var page = document.querySelector(".pfd[data-hooks]");
    if (!page) return;
    var set = {};
    (page.getAttribute("data-hooks") || "").split(" ").forEach(function (h) { if (h) set[h] = true; });
    var embed = root.hasAttribute("data-embed");
    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    function level() { return parseInt(root.getAttribute("data-motion") || "1", 10); }
    function moving() { return !reduce && !root.hasAttribute("data-reduced") && level() > 0; }

    // Live local time wherever a direction shows metadata (split nav, colophon, overlay, collage corner).
    var clocks = document.querySelectorAll("[data-live-time]");
    if (clocks.length) {
      var tick = function () {
        var d = new Date();
        var t = ("0" + d.getHours()).slice(-2) + ":" + ("0" + d.getMinutes()).slice(-2);
        clocks.forEach(function (c) { c.textContent = t; c.setAttribute("datetime", d.toISOString()); });
      };
      tick(); setInterval(tick, 15000);
    }

    // Menu word and full-screen overlay.
    var overlay = document.querySelector("[data-menu-overlay]");
    if (overlay) {
      var toggle = function (open) {
        overlay.hidden = !open;
        document.querySelectorAll('[data-action="menu"]').forEach(function (b) { b.setAttribute("aria-expanded", open ? "true" : "false"); });
        if (open) { var first = overlay.querySelector("a"); if (first) first.focus(); }
      };
      document.querySelectorAll('[data-action="menu"]').forEach(function (b) {
        b.addEventListener("click", function () { toggle(overlay.hidden); });
      });
      document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !overlay.hidden) toggle(false); });
    }

    // Numbered rail: highlight the section in view.
    var rail = document.querySelector("[data-rail]");
    if (rail && "IntersectionObserver" in window) {
      var links = rail.querySelectorAll("a");
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (!en.isIntersecting) return;
          links.forEach(function (a) { a.setAttribute("aria-current", a.getAttribute("href") === "#" + en.target.id ? "true" : "false"); });
        });
      }, { rootMargin: "-40% 0px -50% 0px" });
      links.forEach(function (a) { var t = document.querySelector(a.getAttribute("href")); if (t) io.observe(t); });
    }

    // Line mask reveal: split headline text into lines once fonts are ready.
    if (set["motion-line-reveal"] && moving()) {
      var split = function (el) {
        if (el.querySelector(".pfd-line")) return;
        var nodes = Array.prototype.slice.call(el.childNodes);
        var words = [];
        nodes.forEach(function (n) {
          if (n.nodeType === 3) {
            n.textContent.split(/\s+/).forEach(function (w) { if (w) { var s = document.createElement("span"); s.textContent = w; words.push(s); } });
          } else if (n.nodeType === 1) { words.push(n); }
        });
        el.textContent = "";
        words.forEach(function (w, i) { el.appendChild(w); if (i < words.length - 1) el.appendChild(document.createTextNode(" ")); });
        var lines = [], top = null, cur = null;
        words.forEach(function (w) {
          var y = w.getBoundingClientRect().top;
          if (top === null || Math.abs(y - top) > 2) { top = y; cur = []; lines.push(cur); }
          cur.push(w);
        });
        if (lines.length < 1 || lines.length > 6) return;
        el.textContent = "";
        lines.forEach(function (ws, li) {
          var wrap = document.createElement("span"); wrap.className = "pfd-line-wrap";
          var line = document.createElement("span"); line.className = "pfd-line"; line.style.setProperty("--l", li);
          ws.forEach(function (w, i) { line.appendChild(w); if (i < ws.length - 1) line.appendChild(document.createTextNode(" ")); });
          wrap.appendChild(line); el.appendChild(wrap);
        });
      };
      var run = function () { document.querySelectorAll(".pfd-reveal").forEach(split); };
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(run); else run();
    }

    // Preloader counter (showcase level only, once per session, never in embeds).
    var pre = document.querySelector("[data-preloader]");
    if (pre) {
      var skip = embed || !moving() || level() < 3;
      try { if (sessionStorage.getItem("pf:preloaded:" + direction)) skip = true; } catch (e) { /* ignore */ }
      if (skip) { pre.remove(); } else {
        var num = pre.querySelector(".pfd-preloader-count"), t0 = null;
        var step = function (ts) {
          if (t0 === null) t0 = ts;
          var k = Math.min(1, (ts - t0) / 1100);
          num.textContent = Math.round(100 * (1 - Math.pow(1 - k, 3)));
          if (k < 1) requestAnimationFrame(step); else { pre.classList.add("is-done"); setTimeout(function () { pre.remove(); }, 700); }
        };
        requestAnimationFrame(step);
        try { sessionStorage.setItem("pf:preloaded:" + direction, "1"); } catch (e) { /* ignore */ }
      }
    }

    // Count up numerals once in view.
    if (set["motion-count-up"] && "IntersectionObserver" in window) {
      var nums = document.querySelectorAll("[data-count]");
      var fmt = function (n, sample) { return sample.indexOf(",") >= 0 ? n.toLocaleString("en-US") : String(n); };
      var cio = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (!en.isIntersecting) return;
          cio.unobserve(en.target);
          var raw = en.target.getAttribute("data-count") || "";
          var m = raw.match(/^([^\d]*)([\d,.]+)(.*)$/);
          if (!m || !moving()) return;
          var target = parseFloat(m[2].replace(/,/g, "")), dec = (m[2].split(".")[1] || "").length, start = null;
          var go = function (ts) {
            if (start === null) start = ts;
            var k = Math.min(1, (ts - start) / 900), e = 1 - Math.pow(1 - k, 3);
            var v = target * e;
            en.target.textContent = m[1] + fmt(dec ? +v.toFixed(dec) : Math.round(v), m[2]) + m[3];
            if (k < 1) requestAnimationFrame(go); else en.target.textContent = raw;
          };
          requestAnimationFrame(go);
        });
      }, { threshold: 0.4 });
      nums.forEach(function (n) { cio.observe(n); });
    }

    // Hover list: the image follows the pointer with a lag.
    var hl = document.querySelector("[data-hover-list]");
    if (hl && window.matchMedia("(hover: hover)").matches) {
      var arts = {}, cur2 = null, tx = 0, ty = 0, x = 0, y = 0, raf = null;
      hl.querySelectorAll("[data-hover-art-id]").forEach(function (a) { arts[a.getAttribute("data-hover-art-id")] = a; });
      var loop = function () { x += (tx - x) * 0.14; y += (ty - y) * 0.14; if (cur2) cur2.style.transform = "translate3d(" + (x + 24) + "px," + (y - 90) + "px,0)"; raf = requestAnimationFrame(loop); };
      hl.addEventListener("pointermove", function (e) { tx = e.clientX; ty = e.clientY; });
      hl.querySelectorAll("[data-hover-art]").forEach(function (row) {
        row.addEventListener("pointerenter", function (e) {
          if (cur2) cur2.classList.remove("is-on");
          cur2 = arts[row.getAttribute("data-hover-art")]; if (!cur2) return;
          x = tx = e.clientX; y = ty = e.clientY; cur2.style.transform = "translate3d(" + (x + 24) + "px," + (y - 90) + "px,0)";
          cur2.classList.add("is-on"); if (!raf) loop();
        });
        row.addEventListener("pointerleave", function () { if (cur2) cur2.classList.remove("is-on"); });
      });
    }

    // Custom cursor (fine pointers, motion on, never in embeds).
    var dot = document.querySelector("[data-cursor-dot]"), ring = document.querySelector("[data-cursor-ring]");
    if (dot && ring && !embed && moving() && window.matchMedia("(pointer: fine)").matches) {
      root.classList.add("pfd-cursor-on");
      var cx = 0, cy = 0, rx = 0, ry = 0, started = false;
      var cl = function () { rx += (cx - rx) * 0.18; ry += (cy - ry) * 0.18; ring.style.transform = "translate3d(" + rx + "px," + ry + "px,0)"; requestAnimationFrame(cl); };
      document.addEventListener("pointermove", function (e) {
        cx = e.clientX; cy = e.clientY; dot.style.transform = "translate3d(" + cx + "px," + cy + "px,0)";
        if (!started) { started = true; rx = cx; ry = cy; cl(); }
        var over = e.target.closest && e.target.closest("a, button, summary, [role=button]");
        ring.classList.toggle("is-big", !!over);
      });
    }

    // Magnetic buttons.
    if (set["motion-magnetic"] && moving() && window.matchMedia("(pointer: fine)").matches) {
      document.querySelectorAll(".pfd .pf-btn-primary, .pfd .pfd-btn-fill").forEach(function (b) {
        b.classList.add("pfd-magnetic");
        b.addEventListener("pointermove", function (e) {
          var r = b.getBoundingClientRect(), dx = e.clientX - (r.left + r.width / 2), dy = e.clientY - (r.top + r.height / 2);
          b.style.transform = "translate(" + Math.max(-8, Math.min(8, dx * 0.2)) + "px," + Math.max(-8, Math.min(8, dy * 0.2)) + "px)";
        });
        b.addEventListener("pointerleave", function () { b.style.transition = "transform 400ms cubic-bezier(.34,1.56,.64,1)"; b.style.transform = ""; setTimeout(function () { b.style.transition = ""; }, 400); });
      });
    }

    // Scroll progress fallback where scroll-driven animations are missing.
    var prog = document.querySelector("[data-progress]");
    if (prog && !(window.CSS && CSS.supports && CSS.supports("animation-timeline: scroll()"))) {
      var onScroll = function () { var h = document.documentElement; var k = h.scrollTop / Math.max(1, h.scrollHeight - h.clientHeight); prog.style.transform = "scaleX(" + k + ")"; };
      document.addEventListener("scroll", onScroll, { passive: true }); onScroll();
    }

    // Strip counter.
    var strip = document.querySelector("[data-strip]");
    if (strip) {
      var counter = strip.parentElement.querySelector(".pfd-strip-head .pfd-index");
      var cards = strip.children.length;
      strip.addEventListener("scroll", function () {
        var i = Math.min(cards, 1 + Math.round(strip.scrollLeft / Math.max(1, strip.firstElementChild.getBoundingClientRect().width + 16)));
        if (counter) counter.textContent = ("0" + i).slice(-2) + " / " + ("0" + cards).slice(-2);
      }, { passive: true });
    }
  })();

  // ------------------------------------------------------------ liveness hooks (0.5.0)
  (function liveness() {
    var page = document.querySelector(".pfd[data-hooks]");
    if (!page) return;
    var set = {};
    (page.getAttribute("data-hooks") || "").split(" ").forEach(function (h) { if (h) set[h] = true; });
    var embed = root.hasAttribute("data-embed");
    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    function level() { return parseInt(root.getAttribute("data-motion") || "1", 10); }
    function moving() { return !reduce && !root.hasAttribute("data-reduced") && level() > 0; }
    function fine() { return window.matchMedia("(pointer: fine)").matches; }
    function cssVar(name) { return getComputedStyle(page).getPropertyValue(name).trim(); }
    var hero = page.querySelector(".pfd-hero") || page;
    var h1 = page.querySelector(".pfd-hero h1, .pfd-hero .pfd-statement, .pfd-hero .pfd-clip-word, .pfd-board-figure, .pfd-article h1");

    // Dot-matrix headline: the text drawn as a field of dots that light up near the pointer.
    if (set["type-dot-matrix"] && h1 && window.HTMLCanvasElement) {
      h1.classList.add("pfd-dotmatrix-pending");
      var dm = { dots: [], px: -9999, py: -9999, raf: null, cvs: null, ctx: null, w: 0, h: 0 };
      var build = function () {
        var rect = h1.getBoundingClientRect();
        if (rect.width < 40 || rect.height < 20) return;
        var cs = getComputedStyle(h1);
        var dpr = Math.min(2, window.devicePixelRatio || 1);
        var off = document.createElement("canvas"); off.width = Math.ceil(rect.width); off.height = Math.ceil(rect.height);
        var octx = off.getContext("2d", { willReadFrequently: true });
        octx.font = cs.fontWeight + " " + cs.fontSize + "/" + cs.lineHeight + " " + cs.fontFamily;
        octx.fillStyle = "#000"; octx.textBaseline = "alphabetic";
        // draw each rendered line of text at its own position using Range rects
        var lines = [];
        var walker = document.createTreeWalker(h1, NodeFilter.SHOW_TEXT);
        var node; var range = document.createRange();
        while ((node = walker.nextNode())) {
          var text = node.textContent; var start = 0;
          for (var i = 0; i <= text.length; i++) {
            range.setStart(node, start); range.setEnd(node, i);
            var rs = range.getClientRects();
            if (rs.length > 1 || i === text.length) {
              var endAt = rs.length > 1 ? i - 1 : i;
              range.setStart(node, start); range.setEnd(node, endAt);
              var r = range.getBoundingClientRect();
              if (r.width > 0) lines.push({ text: text.slice(start, endAt), x: r.left - rect.left, y: r.bottom - rect.top - parseFloat(cs.fontSize) * 0.22 });
              start = endAt;
            }
          }
        }
        lines.forEach(function (l) { octx.fillText(l.text.trim(), l.x, l.y); });
        var size = parseFloat(cs.fontSize);
        var step = Math.max(4, Math.round(size / 11));
        var data = octx.getImageData(0, 0, off.width, off.height).data;
        dm.dots = [];
        for (var y = Math.floor(step / 2); y < off.height; y += step) {
          for (var x = Math.floor(step / 2); x < off.width; x += step) {
            if (data[(y * off.width + x) * 4 + 3] > 120) dm.dots.push({ x: x, y: y });
          }
        }
        if (!dm.dots.length) return;
        if (!dm.cvs) {
          dm.cvs = document.createElement("canvas"); dm.cvs.className = "pfd-dotmatrix-canvas"; dm.cvs.setAttribute("aria-hidden", "true");
          h1.classList.add("pfd-dotmatrix"); h1.appendChild(dm.cvs); dm.ctx = dm.cvs.getContext("2d");
        }
        dm.w = off.width; dm.h = off.height; dm.step = step; dm.dpr = dpr;
        dm.cvs.width = off.width * dpr; dm.cvs.height = off.height * dpr; dm.cvs.style.width = off.width + "px"; dm.cvs.style.height = off.height + "px";
        draw();
      };
      var draw = function () {
        var ctx = dm.ctx; if (!ctx) return;
        ctx.setTransform(dm.dpr, 0, 0, dm.dpr, 0, 0); ctx.clearRect(0, 0, dm.w, dm.h);
        var ink = cssVar("--pf-color-text") || "currentColor", hot = cssVar("--pf-color-primary") || ink;
        var base = dm.step * 0.36, radius = dm.step * 9, live = moving() && level() >= 2;
        for (var i = 0; i < dm.dots.length; i++) {
          var d = dm.dots[i], r = base, col = ink, ox = 0, oy = 0;
          if (live) {
            var dx = d.x - dm.px, dy = d.y - dm.py, dist = Math.hypot(dx, dy);
            if (dist < radius) { var k = 1 - dist / radius; r = base * (1 + k * 1.1); col = k > 0.55 ? hot : ink; ox = dx / (dist || 1) * k * dm.step * 0.6; oy = dy / (dist || 1) * k * dm.step * 0.6; }
          }
          ctx.fillStyle = col; ctx.beginPath(); ctx.arc(d.x + ox, d.y + oy, r, 0, 6.2832); ctx.fill();
        }
      };
      var onMove = function (e) {
        var rect = h1.getBoundingClientRect(); dm.px = e.clientX - rect.left; dm.py = e.clientY - rect.top;
        if (!dm.raf) dm.raf = requestAnimationFrame(function () { dm.raf = null; draw(); });
      };
      var ready = document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve();
      ready.then(function () { setTimeout(build, 50); });
      window.addEventListener("resize", function () { clearTimeout(dm.t); dm.t = setTimeout(build, 150); });
      if (fine()) { document.addEventListener("pointermove", onMove); document.addEventListener("pointerleave", function () { dm.px = dm.py = -9999; draw(); }); }
      new MutationObserver(function () { setTimeout(draw, 30); }).observe(root, { attributes: true, attributeFilter: ["data-palette", "data-theme", "data-motion"] });
    }

    // Per-character reveal on the headline.
    if (set["motion-char-reveal"] && h1 && moving() && !set["type-dot-matrix"]) {
      var splitChars = function (el) {
        if (el.querySelector(".pfd-ch")) return;
        Array.prototype.slice.call(el.childNodes).forEach(function (n) {
          if (n.nodeType !== 3) return;
          var frag = document.createDocumentFragment(), text = n.textContent;
          for (var i = 0; i < text.length; i++) {
            var s = document.createElement("span"); s.className = text[i] === " " ? "pfd-ch pfd-ch-space" : "pfd-ch"; s.textContent = text[i]; frag.appendChild(s);
          }
          el.replaceChild(frag, n);
        });
        el.querySelectorAll(".pfd-ch").forEach(function (s, i) { s.style.setProperty("--c", i); });
        el.classList.add("pfd-chars");
      };
      (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(function () { splitChars(h1); });
    }

    // Scramble: the headline decodes from a glyph set over about 700ms; nav links re-scramble on hover.
    if (set["motion-scramble"] && moving()) {
      var GLYPHS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#%&*+-";
      var scramble = function (el, duration) {
        var original = el.getAttribute("data-text") || el.textContent; el.setAttribute("data-text", original);
        var t0 = null;
        var step = function (ts) {
          if (t0 === null) t0 = ts;
          var k = Math.min(1, (ts - t0) / duration), out = "";
          for (var i = 0; i < original.length; i++) {
            var ch = original[i];
            out += (ch === " " || i / original.length < k) ? ch : GLYPHS[Math.floor(Math.random() * GLYPHS.length)];
          }
          el.textContent = out;
          if (k < 1) requestAnimationFrame(step); else el.textContent = original;
        };
        requestAnimationFrame(step);
      };
      var target = page.querySelector(".pfd-hero h1:not(.pfd-dotmatrix):not(.pfd-dotmatrix-pending), .pfd-board-figure, .pfd-statement strong");
      if (target && !target.children.length) scramble(target, 900);
      page.querySelectorAll(".pf-nav-links a, .pfd-menu-links a").forEach(function (a) { a.addEventListener("pointerenter", function () { scramble(a, 400); }); });
    }

    // Variable weight: the headline's weight follows the pointer across the viewport.
    if (set["motion-variable-weight"] && h1 && moving() && fine()) {
      var cur = 600, want = 600;
      var tick = function () { cur += (want - cur) * 0.12; h1.style.fontVariationSettings = '"wght" ' + Math.round(cur); if (Math.abs(want - cur) > 1) requestAnimationFrame(tick); };
      document.addEventListener("pointermove", function (e) { want = 300 + (e.clientX / window.innerWidth) * 600; requestAnimationFrame(tick); });
    }

    // Velocity skew: tickers and marquees lean with scroll speed.
    if (set["motion-velocity-skew"] && moving()) {
      var targets = page.querySelectorAll(".pfd-marquee-track, .pfd-ticker-track, .pfd-kinetic-row, .pfd-diag-track");
      var last = window.scrollY, vel = 0, skewRaf = null;
      var applySkew = function () { skewRaf = null; vel *= 0.86; targets.forEach(function (t) { t.style.transform = "skewX(" + Math.max(-12, Math.min(12, vel * 0.08)) + "deg)"; }); if (Math.abs(vel) > 0.2) skewRaf = requestAnimationFrame(applySkew); };
      document.addEventListener("scroll", function () { var y = window.scrollY; vel += (y - last); last = y; if (!skewRaf) skewRaf = requestAnimationFrame(applySkew); }, { passive: true });
    }

    // Pointer grid: a dot lattice behind the hero that bulges toward the pointer.
    if (set["motion-pointer-grid"] && hero && window.HTMLCanvasElement && !embed) {
      var gc = document.createElement("canvas"); gc.className = "pfd-pointer-grid"; gc.setAttribute("aria-hidden", "true"); hero.style.position = "relative"; hero.insertBefore(gc, hero.firstChild);
      var gctx = gc.getContext("2d"), gp = { x: -9999, y: -9999 }, graf = null;
      var size = function () { var r = hero.getBoundingClientRect(); var dpr = Math.min(2, window.devicePixelRatio || 1); gc.width = r.width * dpr; gc.height = r.height * dpr; gc.style.width = r.width + "px"; gc.style.height = r.height + "px"; gctx.setTransform(dpr, 0, 0, dpr, 0, 0); drawGrid(); };
      var drawGrid = function () {
        graf = null; var w = gc.clientWidth, h = gc.clientHeight; gctx.clearRect(0, 0, w, h);
        gctx.fillStyle = cssVar("--pf-color-text") || "#000"; gctx.globalAlpha = 0.22;
        var gap = 28, live = moving() && level() >= 2;
        for (var y = gap / 2; y < h; y += gap) for (var x = gap / 2; x < w; x += gap) {
          var r = 1.2, ox = 0, oy = 0;
          if (live) { var dx = x - gp.x, dy = y - gp.y, d = Math.hypot(dx, dy); if (d < 180) { var k = 1 - d / 180; r = 1.2 + k * 3; ox = dx / (d || 1) * k * 14; oy = dy / (d || 1) * k * 14; } }
          gctx.beginPath(); gctx.arc(x + ox, y + oy, r, 0, 6.2832); gctx.fill();
        }
      };
      size(); window.addEventListener("resize", size);
      if (fine()) hero.addEventListener("pointermove", function (e) { var r = hero.getBoundingClientRect(); gp.x = e.clientX - r.left; gp.y = e.clientY - r.top; if (!graf) graf = requestAnimationFrame(drawGrid); });
      hero.addEventListener("pointerleave", function () { gp.x = gp.y = -9999; if (!graf) graf = requestAnimationFrame(drawGrid); });
    }

    // Trail: small copies of the page's artwork follow the pointer across the hero and fade.
    if (set["motion-trail"] && hero && moving() && level() >= 2 && fine() && !embed) {
      var arts = Array.prototype.slice.call(page.querySelectorAll(".pfd-art")).slice(0, 8), n = 0, lastT = 0;
      if (arts.length) hero.addEventListener("pointermove", function (e) {
        var now = performance.now(); if (now - lastT < 90) return; lastT = now;
        var r = hero.getBoundingClientRect(); var ghost = document.createElement("div"); ghost.className = "pfd-trail"; ghost.setAttribute("aria-hidden", "true");
        ghost.style.left = (e.clientX - r.left) + "px"; ghost.style.top = (e.clientY - r.top) + "px"; ghost.style.setProperty("--r", (Math.random() * 20 - 10) + "deg");
        ghost.innerHTML = arts[n++ % arts.length].outerHTML; hero.appendChild(ghost);
        setTimeout(function () { ghost.remove(); }, 900);
      });
    }

    // Pinned action: a slim bar with the primary action that appears once the hero has scrolled away.
    var pinned = page.querySelector("[data-pinned-cta]");
    if (pinned && "IntersectionObserver" in window && hero) {
      new IntersectionObserver(function (es) { es.forEach(function (en) { pinned.hidden = en.isIntersecting; }); }, { threshold: 0.1 }).observe(hero);
    }
  })();
})();
