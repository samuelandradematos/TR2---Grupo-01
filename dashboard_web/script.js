
async function tick() {
  const tbody = document.getElementById('live-data-body');

  let json;
  try {
    const res = await fetch('/last', { cache: 'no-store' });
    if (!res.ok) throw new Error(`Erro HTTP: ${res.status}`);
    json = await res.json();
  } catch (error) {
    console.error("Falha ao buscar dados LIVE:", error);
    tbody.innerHTML = `<tr><td colspan="5" style="color:red">Erro de conexão. Verifique o terminal.</td></tr>`;
    return;
  }

  const roomsData = Object.values(json);
  
  if (roomsData.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5">Aguardando dados... (Verifique se o Mock está rodando)</td></tr>';
    return;
  }

  roomsData.sort((a, b) => a.sala.localeCompare(b.sala));

  let html = '';
  for (const data of roomsData) {
    const timestamp = new Date(data.timestamp * 1000).toLocaleString('pt-BR');
    
    
    // 1. TEMPERATURA (> 26.0) - Crítico (Vermelho)
    const LIMIT_TEMP = 26.0; 
    let styleTemp = '';
    let textTemp = '';
    
    if (Number(data.temperatura) > LIMIT_TEMP) {
        styleTemp = 'style="background-color: #ffcccc; color: #cc0000; font-weight: bold;"';
        textTemp = ' (ALERTA!)';
    }

    // 2. UMIDADE (< 30 ou > 70) - Atenção (Amarelo)
    const UMID_MIN = 30.0;
    const UMID_MAX = 70.0;
    let styleUmid = '';
    let textUmid = '';
    const umid = Number(data.umidade);
    
    if (umid < UMID_MIN || umid > UMID_MAX) {
        styleUmid = 'style="background-color: #fff3cd; color: #856404; font-weight: bold;"';
        if (umid < UMID_MIN) textUmid = ' (BAIXA!)';
        if (umid > UMID_MAX) textUmid = ' (ALTA!)';
    }

    // 3. POEIRA (> 35) - Sujo (Cinza)
    const LIMIT_POEIRA = 35; 
    let stylePoeira = '';
    let textPoeira = '';
    
    if (Number(data.poeira) > LIMIT_POEIRA) {
        stylePoeira = 'style="background-color: #d6d8d9; color: #1b1e21; font-weight: bold;"';
        textPoeira = ' (ALTA!)';
    }

    html += `
      <tr>
        <td>${data.sala}</td>
        <td ${styleTemp}>${Number(data.temperatura).toFixed(1)} °C${textTemp}</td>
        <td ${styleUmid}>${Number(data.umidade).toFixed(1)} %${textUmid}</td>
        <td ${stylePoeira}>${data.poeira}${textPoeira}</td>
        <td>${timestamp}</td>
      </tr>
    `;
  }
  tbody.innerHTML = html;
}


async function loadHistory() {
  const tbody = document.getElementById('history-data-body');
  let historyData;
  try {
    const res = await fetch('/all', { cache: 'no-store' });
    if (!res.ok) throw new Error(`Erro HTTP: ${res.status}`);
    historyData = await res.json();
  } catch (error) {
    console.error("Falha ao buscar histórico:", error);
    tbody.innerHTML = `<tr><td colspan="6">Erro ao carregar histórico.</td></tr>`;
    return;
  }
  if (historyData.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6">Nenhum dado no histórico ainda.</td></tr>';
    return;
  }
  let html = '';
  for (const data of historyData) {
    const timestamp = new Date(data.ts * 1000).toLocaleString('pt-BR');
    html += `
      <tr>
        <td>${data.id}</td>
        <td>${data.sala}</td>
        <td>${Number(data.temperatura).toFixed(1)} °C</td>
        <td>${Number(data.umidade).toFixed(1)} %</td>
        <td>${data.poeira}</td>
        <td>${timestamp}</td>
      </tr>
    `;
  }
  tbody.innerHTML = html;
}

let isHistoryLoaded = false;
function setupToggleButton() {
  const btn = document.getElementById('btn-toggle-history');
  const container = document.getElementById('history-container');
  if(!btn || !container) return;

  btn.addEventListener('click', async () => {
    const isHidden = container.classList.contains('hidden');
    if (isHidden) {
      if (!isHistoryLoaded) {
        btn.textContent = 'Carregando...';
        btn.disabled = true;
        await loadHistory();
        isHistoryLoaded = true;
        btn.disabled = false;
      }
      container.classList.remove('hidden');
      btn.textContent = 'Esconder Histórico';
    } else {
      container.classList.add('hidden');
      btn.textContent = 'Mostrar Histórico';
    }
  });
}

setInterval(tick, 2000);
tick();                  
window.onload = setupToggleButton;