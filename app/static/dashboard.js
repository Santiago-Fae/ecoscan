const M = window.MATERIALS;
const label = k => (M[k] ? `${M[k].icon} ${M[k].name}` : k);

function kpi(value, caption) {
  return `<div class="kpi"><b>${value}</b><span>${caption}</span></div>`;
}

function plural(n, forms) {
  return n === 1 ? forms[0] : forms[1];
}

async function load() {
  const d = await (await fetch("/api/stats")).json();
  const fb = d.feedback;

  document.getElementById("kpis").innerHTML =
    kpi(d.total_analyses, plural(d.total_analyses, tr("photos"))) +
    kpi(d.total_items, plural(d.total_items, tr("materials"))) +
    kpi(fb.accuracy === null ? "–" : Math.round(fb.accuracy * 100) + "%", tr("accuracy")) +
    kpi(d.uncertain_items, tr("asked_help"));

  const max = Math.max(1, ...d.by_material.map(m => m.total));
  document.getElementById("empty").hidden = d.by_material.length > 0;
  document.getElementById("bars").innerHTML = d.by_material.map(m => {
    const info = M[m.material] || { hex: "#999" };
    return `<div class="bar"><span class="bar-label">${label(m.material)}</span>
      <div class="track"><div class="fill" style="width:${(m.total / max) * 100}%;background:${info.hex}"></div></div>
      <b>${m.total}</b></div>`;
  }).join("");

  document.getElementById("quality").textContent = fb.answered
    ? tr("ratings", { answered: fb.answered, correct: fb.correct, corrected: fb.corrected })
    : tr("no_ratings");

  document.getElementById("confusions").innerHTML = d.confusions.length
    ? `<h3>${tr("mistakes")}</h3><ul>` + d.confusions.map(c =>
        `<li>${tr("model_said", { predicted: label(c.predicted), actual: label(c.actual), n: c.total })}</li>`).join("") + "</ul>"
    : "";
}

load();
setInterval(load, 10000);
