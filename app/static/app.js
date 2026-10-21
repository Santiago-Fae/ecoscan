const form = document.getElementById("form");
const input = document.getElementById("file");
const drop = document.getElementById("drop");
const preview = document.getElementById("preview");
const dropText = document.getElementById("drop-text");
const statusEl = document.getElementById("status");
const result = document.getElementById("result");
const submitBtn = document.getElementById("submit");
const cityEl = document.getElementById("city");

let items = []; // items of the latest analysis (feedback state included)

function esc(s) {
  const d = document.createElement("div");
  d.textContent = s;
  return d.innerHTML;
}

function showPreview() {
  const f = input.files[0];
  if (!f) return;
  preview.src = URL.createObjectURL(f);
  preview.hidden = false;
  dropText.textContent = f.name;
}

input.addEventListener("change", showPreview);
["dragenter", "dragover"].forEach(e => drop.addEventListener(e, ev => { ev.preventDefault(); drop.classList.add("over"); }));
["dragleave", "drop"].forEach(e => drop.addEventListener(e, ev => { ev.preventDefault(); drop.classList.remove("over"); }));
drop.addEventListener("drop", ev => {
  if (ev.dataTransfer.files.length) { input.files = ev.dataTransfer.files; showPreview(); }
});

function materialOptions(exclude) {
  return Object.entries(window.MATERIALS)
    .filter(([k]) => k !== exclude)
    .map(([k, m]) => `<option value="${k}">${m.icon} ${esc(m.name)}</option>`).join("");
}

// Interaction area: clarification question (uncertain) or feedback request.
function renderInteraction(it, idx) {
  if (it.answered) return `<p class="thanks">${tr("thanks")}</p>`;
  const m = it.material;
  if (it.uncertain) {
    const choices = [{ key: m.key, name: m.name, icon: m.icon }, ...it.alternatives]
      .map(a => `<button type="button" class="btn-op" data-action="choose" data-idx="${idx}" data-mat="${a.key}">${a.icon} ${esc(a.name)}</button>`).join("");
    return `<div class="doubt"><p>🤔 <b>${tr("not_sure")}</b> ${tr("which_item")}</p>
      <div class="ops">${choices}</div>
      <select data-action="other" data-idx="${idx}"><option value="">${tr("other_material")}</option>${materialOptions()}</select></div>`;
  }
  if (it.correcting) {
    return `<div class="doubt"><p>${tr("correct_q")}</p>
      <select data-action="other" data-idx="${idx}"><option value="">${tr("select")}</option>${materialOptions(m.key)}</select></div>`;
  }
  return `<div class="feedback"><span>${tr("is_right")}</span>
    <button type="button" class="btn-op" data-action="yes" data-idx="${idx}">${tr("yes")}</button>
    <button type="button" class="btn-op" data-action="no" data-idx="${idx}">${tr("no")}</button></div>`;
}

function renderItem(it, idx) {
  const conf = Math.round(it.confidence * 100);
  const m = it.material;
  const dropOff = m.drop_off.map(l => `<li>${esc(l)}</li>`).join("");
  const warning = it.uncertain && !it.answered ? ` · ${tr("low_conf")}` : "";
  const source = it.corrected ? tr("provided_by_you") : tr("confidence", { n: conf }) + warning;
  return `<div class="item" style="--c:${m.hex}">
    <h3>${m.icon} ${esc(m.name)} <small>(${esc(it.detected_as === "whole image" ? tr("whole_image") : it.detected_as)})</small></h3>
    <span class="conf">${source}</span>
    <p><span class="tag ${m.recyclable ? "" : "no"}">${m.recyclable ? tr("recyclable") : tr("not_recyclable")} · ${esc(m.bin_color)}</span></p>
    <p><b>${tr("how_to")}</b> ${esc(m.how_to)}</p>
    <p><b>${tr("where")}</b></p><ul>${dropOff}</ul>
    <a class="btn" href="${m.map_url}" target="_blank" rel="noopener">${tr("map_btn")}</a>
    <div class="interaction" id="int-${idx}">${renderInteraction(it, idx)}</div>
  </div>`;
}

function draw() {
  const img = result.querySelector("img");
  result.innerHTML = "";
  if (img) result.appendChild(img);
  result.insertAdjacentHTML("beforeend", items.map(renderItem).join(""));
}

async function sendFeedback(idx, realMaterial) {
  const it = items[idx];
  const correct = realMaterial === it.material.key;
  try {
    const resp = await fetch("/api/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: it.id, correct, real_material: realMaterial, city: cityEl.value, lang: window.LANG }),
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.detail || tr("send_failed"));
    if (!correct) { it.material = data.material; it.corrected = true; }
    it.answered = true;
    it.uncertain = false;
  } catch (e) {
    statusEl.className = "error";
    statusEl.textContent = e.message;
    return;
  }
  const scroll = window.scrollY;
  draw();
  window.scrollTo(0, scroll);
}

result.addEventListener("click", ev => {
  const b = ev.target.closest("button[data-action]");
  if (!b) return;
  const idx = Number(b.dataset.idx);
  const action = b.dataset.action;
  if (action === "yes") sendFeedback(idx, items[idx].material.key);
  else if (action === "choose") sendFeedback(idx, b.dataset.mat);
  else if (action === "no") {
    items[idx].correcting = true;
    document.getElementById(`int-${idx}`).innerHTML = renderInteraction(items[idx], idx);
  }
});

result.addEventListener("change", ev => {
  const s = ev.target.closest("select[data-action]");
  if (s && s.value) sendFeedback(Number(s.dataset.idx), s.value);
});

form.addEventListener("submit", async ev => {
  ev.preventDefault();
  if (!input.files[0]) return;
  statusEl.className = "";
  statusEl.textContent = tr("analyzing");
  result.innerHTML = "";
  items = [];
  submitBtn.disabled = true;
  try {
    const resp = await fetch("/api/analyze", { method: "POST", body: new FormData(form) });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.detail || tr("analysis_failed"));
    if (!data.found) {
      statusEl.textContent = tr("no_object");
    } else {
      statusEl.textContent = tr("n_found", { n: data.items.length });
      items = data.items;
      result.innerHTML = `<img src="${data.annotated_image}" alt="${tr("annotated_alt")}">`;
      draw();
    }
  } catch (e) {
    statusEl.className = "error";
    statusEl.textContent = e.message;
  } finally {
    submitBtn.disabled = false;
  }
});
