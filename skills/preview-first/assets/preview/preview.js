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
})();
