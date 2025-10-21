// --- Função para a tabela LIVE (TEMPO REAL)
async function tick() {
  const tbody = document.getElementById('live-data-body'); // ID ATUALIZADO

  let json;
  try {
    const res = await fetch('/last', { cache: 'no-store' });
    if (!res.ok) throw new Error(`Erro HTTP: ${res.status}`);
    json = await res.json();
  } catch (error) {
    console.error("Falha ao buscar dados LIVE:", error);
    tbody.innerHTML = `<tr><td colspan="5">Erro ao carregar dados.</td></tr>`;
    return;
  }

  const roomsData = Object.values(json);
  if (roomsData.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5">Nenhum dado recebido ainda...</td></tr>';
    return;
  }

  roomsData.sort((a, b) => a.sala.localeCompare(b.sala));

  let html = '';
  for (const data of roomsData) {
    const timestamp = new Date(data.timestamp * 1000).toLocaleString('pt-BR');
    html += `
      <tr>
        <td>${data.sala}</td>
        <td>${data.temperatura.toFixed(1)} °C</td>
        <td>${data.umidade.toFixed(1)} %</td>
        <td>${data.poeira}</td>
        <td>${timestamp}</td>
      </tr>
    `;
  }
  tbody.innerHTML = html;
}

// FUNÇÃO para a tabela de HISTÓRICO
async function loadHistory() {
  const tbody = document.getElementById('history-data-body');
  let historyData;
  try {
    const res = await fetch('/all', { cache: 'no-store' }); // Busca no endpoint /all
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
        <td>${data.temperatura.toFixed(1)} °C</td>
        <td>${data.umidade.toFixed(1)} %</td>
        <td>${data.poeira}</td>
        <td>${timestamp}</td>
      </tr>
    `;
  }
  tbody.innerHTML = html;
}

//FUNÇÃO para configurar o BOTÃO DE TOGGLE
let isHistoryLoaded = false;

function setupToggleButton() {
  const btn = document.getElementById('btn-toggle-history');
  const container = document.getElementById('history-container');

  btn.addEventListener('click', async () => {
    const isHidden = container.classList.contains('hidden');

    if (isHidden) {
      // Carrega os dados (apenas se for a 1ª vez)
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
setupToggleButton();