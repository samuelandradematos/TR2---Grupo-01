async function tick() {
  const res = await fetch('/last', {cache: 'no-store'});
  const json = await res.json();
  document.getElementById('out').textContent = JSON.stringify(json, null, 2);
}
setInterval(tick, 2000);
tick();
