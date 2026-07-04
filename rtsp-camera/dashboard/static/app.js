// Cap nhat dong ho
function tick() {
  const el = document.getElementById("s-clock");
  if (el) el.textContent = new Date().toLocaleTimeString("vi-VN", { hour12: false });
}
setInterval(tick, 1000);
tick();

// Format "gan nhat"
function fmtLast(sec) {
  if (sec === null || sec === undefined) return "—";
  if (sec < 1) return "vừa xong";
  if (sec < 60) return Math.round(sec) + "s trước";
  if (sec < 3600) return Math.round(sec / 60) + "p trước";
  return Math.round(sec / 3600) + "h trước";
}

const STATUS_TEXT = { online: "Trực tuyến", offline: "Mất KN", connecting: "Đang KN" };

async function refresh() {
  let data;
  try {
    const res = await fetch("/api/stats", { cache: "no-store" });
    data = await res.json();
  } catch (e) {
    return; // giu nguyen UI khi loi mang tam thoi
  }

  // Tung camera
  for (const c of data.cameras) {
    const card = document.getElementById("card-" + c.id);
    if (!card) continue;

    const dot = document.getElementById("dot-" + c.id);
    if (dot) dot.className = "dot " + c.status;

    const st = document.getElementById("status-" + c.id);
    if (st) st.textContent = STATUS_TEXT[c.status] || c.status;

    setText("fps-" + c.id, c.fps);
    setText("det-" + c.id, c.detections);
    setText("alerts-" + c.id, c.alerts);
    setText("last-" + c.id, fmtLast(c.last_alert));

    card.classList.toggle("alert", c.detections > 0 && c.status === "online");
    card.classList.toggle("offline", c.status === "offline");
  }

  // Tong quan
  const s = data.summary;
  setText("s-online", s.online);
  setText("s-total", s.total);
  setText("s-alerts", s.alerts);
  setText("s-fps", s.avg_fps);
}

function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

refresh();
setInterval(refresh, 1000);
