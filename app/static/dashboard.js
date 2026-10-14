const M = window.MATERIALS;
const label = k => (M[k] ? `${M[k].icon} ${M[k].name}` : k);

function kpi(value, caption) {
  return `<div class="kpi"><b>${value}</b><span>${caption}</span></div>`;
}

function plural(n, one, many) {
  return n === 1 ? one : many;
}

async function load() {
  const d = await (await fetch("/api/stats")).json();
  const fb = d.feedback;

  document.getElementById("kpis").innerHTML =
    kpi(d.total_analyses, plural(d.total_analyses, "photo analyzed", "photos analyzed")) +
    kpi(d.total_items, plural(d.total_items, "material identified", "materials identified")) +
    kpi(fb.accuracy === null ? "–" : Math.round(fb.accuracy * 100) + "%", "accuracy (as rated by users)") +
    kpi(d.uncertain_items, "times the model asked for help");

  const max = Math.max(1, ...d.by_material.map(m => m.total));
  document.getElementById("empty").hidden = d.by_material.length > 0;
  document.getElementById("bars").innerHTML = d.by_material.map(m => {
    const info = M[m.material] || { hex: "#999" };
    return `<div class="bar"><span class="bar-label">${label(m.material)}</span>
      <div class="track"><div class="fill" style="width:${(m.total / max) * 100}%;background:${info.hex}"></div></div>
      <b>${m.total}</b></div>`;
  }).join("");

  document.getElementById("quality").textContent = fb.answered
    ? `${fb.answered} ratings: ${fb.correct} correct and ${fb.corrected} corrected by users.`
    : "No user ratings yet.";

  document.getElementById("confusions").innerHTML = d.confusions.length
    ? "<h3>Most common mistakes</h3><ul>" + d.confusions.map(c =>
        `<li>The model said <b>${label(c.predicted)}</b>, but it was <b>${label(c.actual)}</b> (${c.total}×)</li>`).join("") + "</ul>"
    : "";
}

load();
setInterval(load, 10000);
