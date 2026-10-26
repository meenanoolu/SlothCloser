(() => {
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];

  let mood = "neutral";
  let preferredModel = null;
  let lastResult = null;

  // Cursor parallax on background orbs
  const orbs = $$(".orb");
  let targetX = 0, targetY = 0, curX = 0, curY = 0;
  window.addEventListener("mousemove", (e) => {
    const cx = window.innerWidth / 2;
    const cy = window.innerHeight / 2;
    targetX = (e.clientX - cx) / cx;
    targetY = (e.clientY - cy) / cy;
  });
  function tickParallax() {
    curX += (targetX - curX) * 0.06;
    curY += (targetY - curY) * 0.06;
    orbs.forEach((orb, i) => {
      const depth = (i + 1) * 12;
      orb.style.transform = `translate(${curX * depth}px, ${curY * depth}px)`;
    });
    requestAnimationFrame(tickParallax);
  }
  requestAnimationFrame(tickParallax);

  // Nav
  $$(".nav-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      $$(".nav-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      $$(".page").forEach((p) => p.classList.remove("active"));
      $(`#page-${btn.dataset.page}`).classList.add("active");
      if (btn.dataset.page === "history") loadHistory();
    });
  });

  async function initMoods() {
    const res = await fetch("/api/moods");
    const data = await res.json();
    const box = $("#moods");
    box.innerHTML = "";
    data.moods.forEach((m, i) => {
      const pill = document.createElement("button");
      pill.type = "button";
      pill.className = "mood-pill" + (i === 0 ? " active" : "");
      pill.textContent = m.label;
      pill.dataset.id = m.id;
      pill.addEventListener("click", () => {
        $$(".mood-pill").forEach((p) => p.classList.remove("active"));
        pill.classList.add("active");
        mood = m.id;
      });
      box.appendChild(pill);
    });
  }

  async function initStatus() {
    const el = $("#status");
    try {
      const res = await fetch("/api/health");
      const data = await res.json();
      preferredModel = data.default_model;
      if (data.local_ready && data.models?.length) {
        const gemma = data.models.find((m) => m.toLowerCase().includes("gemma"));
        preferredModel = gemma || data.models[0];
        el.className = "badge badge-local";
        el.textContent = `● Local · ${preferredModel}`;
      } else {
        el.className = "badge badge-fallback";
        el.textContent = "○ Offline fallback";
      }
    } catch {
      el.className = "badge badge-fallback";
      el.textContent = "○ Offline fallback";
    }
  }

  function toast(msg) {
    const t = $("#toast");
    t.textContent = msg;
    t.classList.remove("hidden");
    setTimeout(() => t.classList.add("hidden"), 2800);
  }

  function esc(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function renderResults(r) {
    lastResult = r;
    $("#empty").classList.add("hidden");
    const box = $("#results");
    box.classList.remove("hidden");

    const cards = [
      ["Day summary", r.summary, ""],
      ["Still open", r.open_loops, ""],
      ["Bedtime reflection", r.bedtime, ""],
      ["A few lines for the night", r.poem || "", "card-poem"],
      ["Hold this", r.quote || "", "card-quote"],
      ["One tiny thing for tomorrow", r.tomorrow, ""],
      ["Ambient soundscape", r.ambient, ""],
    ];

    let html = "";
    if (r.used_fallback) {
      html += `<div class="badge badge-fallback" style="margin-bottom:0.8rem">Calm offline fallback</div>`;
    } else {
      html += `<div class="badge badge-local" style="margin-bottom:0.8rem">Local open-weight</div>`;
    }

    cards.forEach(([label, body, cls], i) => {
      if (!body || !String(body).trim()) return;
      html += `
        <div class="card ${cls}" style="animation-delay:${0.04 + i * 0.06}s">
          <div class="card-label">${label}</div>
          <div class="card-body">${esc(body)}</div>
        </div>`;
    });

    html += `
      <div class="voice">
        <div class="voice-label">Bedtime voice</div>
        <button id="btn-voice" class="btn btn-primary" style="width:100%">🎙️ Play soft reading</button>
        <div id="voice-player"></div>
      </div>
      <div class="payoff">
        <div class="payoff-title">Day closed.</div>
        <div class="payoff-text">You can stop carrying it now.<br>Whatever is left can wait until morning.</div>
      </div>
      <button id="btn-save" class="btn btn-ghost" style="width:100%;margin-top:0.3rem">💾 Save this closing</button>
    `;

    box.innerHTML = html;
    $("#btn-voice").addEventListener("click", playVoice);
    $("#btn-save").addEventListener("click", () => {
      const md = `# Day Closed — ${r.timestamp}
**Mood:** ${r.mood}

## Summary
${r.summary}

## Still open
${r.open_loops}

## Bedtime reflection
${r.bedtime}

## Poem
${r.poem || ""}

## Quote
${r.quote || ""}

## One tiny thing for tomorrow
${r.tomorrow}

## Ambient soundscape
${r.ambient}
`;
      const blob = new Blob([md], { type: "text/markdown" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = `day-closed-${r.timestamp.replace(/[\s:]/g, "-")}.md`;
      a.click();
    });
  }

  function voiceScript(r) {
    // Warm spoken package: reflection + pause + poem + quote
    const parts = [r.bedtime];
    if (r.poem) parts.push(r.poem.replace(/\n/g, ". "));
    if (r.quote) parts.push(r.quote);
    parts.push("Day closed. You can stop carrying it now.");
    return parts.filter(Boolean).join("\n\n");
  }

  async function playVoice() {
    if (!lastResult) return;
    const btn = $("#btn-voice");
    btn.disabled = true;
    btn.classList.add("loading");
    btn.textContent = "Speaking softly…";
    try {
      const res = await fetch("/api/voice", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: voiceScript(lastResult) }),
      });
      if (!res.ok) throw new Error("voice failed");
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const player = $("#voice-player");
      player.innerHTML = `<audio controls autoplay src="${url}"></audio>
        <p style="font-size:0.85rem;color:var(--muted);margin-top:0.55rem">Soft reading — reflection, poem, and a line to hold.</p>`;
      btn.textContent = "🎙️ Play again";
    } catch {
      toast("Voice couldn’t be generated right now.");
      btn.textContent = "🎙️ Play soft reading";
    } finally {
      btn.disabled = false;
      btn.classList.remove("loading");
    }
  }

  async function closeDay() {
    const notes = $("#notes").value.trim();
    if (!notes) {
      toast("Write a few notes first — even one line is enough.");
      return;
    }
    const btn = $("#btn-close");
    btn.disabled = true;
    btn.classList.add("loading");
    try {
      const res = await fetch("/api/close", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ notes, mood, model: preferredModel }),
      });
      if (!res.ok) throw new Error("close failed");
      const data = await res.json();
      renderResults(data);
    } catch {
      toast("Something went wrong closing the day. Try again.");
    } finally {
      btn.disabled = false;
      btn.classList.remove("loading");
    }
  }

  async function loadHistory() {
    const box = $("#history-list");
    box.innerHTML = `<p style="color:var(--muted);font-size:0.9rem">Loading…</p>`;
    try {
      const res = await fetch("/api/history");
      const data = await res.json();
      if (!data.closings?.length) {
        box.innerHTML = `
          <div class="empty">
            <div class="empty-icon">📭</div>
            <p>No closings yet.<br>When you close a day it will appear here.</p>
          </div>`;
        return;
      }
      box.innerHTML = data.closings
        .map((h) => {
          let s = h.summary || "";
          if (s.length > 150) s = s.slice(0, 150) + "…";
          return `<div class="history-item"><strong>${esc(h.timestamp || "")}</strong> · ${esc(h.mood || "")}<br>${esc(s)}</div>`;
        })
        .join("");
    } catch {
      box.innerHTML = `<p style="color:var(--muted)">Could not load history.</p>`;
    }
  }

  $("#btn-close").addEventListener("click", closeDay);
  $("#btn-clear").addEventListener("click", () => {
    $("#notes").value = "";
    $("#results").classList.add("hidden");
    $("#results").innerHTML = "";
    $("#empty").classList.remove("hidden");
    lastResult = null;
  });
  $("#btn-example").addEventListener("click", async () => {
    try {
      const res = await fetch("/api/example");
      const data = await res.json();
      if (data.notes) $("#notes").value = data.notes;
    } catch {
      toast("Could not load example.");
    }
  });

  initMoods();
  initStatus();
})();