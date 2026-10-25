/**
 * Deye Inverter Home Energy System Dashboard — Frontend Client
 * Підключення до FastAPI бекенду та українізований інтерфейс
 */

(function () {
  'use strict';

  const state = {
    soundEnabled: true,
    sparklineHistory: [460, 480, 510, 490, 530, 520, 500, 540, 510, 530, 520, 520],
    lastGridOnline: true
  };

  const dom = {
    clockTime: document.getElementById('clockTime'),
    clockDate: document.getElementById('clockDate'),
    lastUpdateTs: document.getElementById('lastUpdateTs'),

    gridToggleBtn: document.getElementById('gridToggleBtn'),
    gridSwitchText: document.getElementById('gridSwitchText'),
    soundToggleBtn: document.getElementById('soundToggleBtn'),
    soundIconOn: document.getElementById('soundIconOn'),
    soundIconOff: document.getElementById('soundIconOff'),

    networkBanner: document.getElementById('networkBanner'),
    gridHeadline: document.getElementById('gridHeadline'),
    gridSubtext: document.getElementById('gridSubtext'),
    modeTagText: document.getElementById('modeTagText'),
    runtimeHighlight: document.getElementById('runtimeHighlight'),
    runtimeLoadRef: document.getElementById('runtimeLoadRef'),

    flowGridVal: document.getElementById('flowGridVal'),
    flowInverterVal: document.getElementById('flowInverterVal'),
    flowHomeVal: document.getElementById('flowHomeVal'),
    flowBatVal: document.getElementById('flowBatVal'),
    lineGridToInv: document.getElementById('lineGridToInv'),
    batParticles: document.getElementById('batParticles'),

    batterySocText: document.getElementById('batterySocText'),
    batteryVoltsText: document.getElementById('batteryVoltsText'),
    batteryGaugeFill: document.getElementById('batteryGaugeFill'),
    batteryBarFill: document.getElementById('batteryBarFill'),
    batteryPowerText: document.getElementById('batteryPowerText'),
    batteryCurrentText: document.getElementById('batteryCurrentText'),
    batteryTempText: document.getElementById('batteryTempText'),
    batteryStatePill: document.getElementById('batteryStatePill'),

    homeLoadPower: document.getElementById('homeLoadPower'),
    homeLoadCurrent: document.getElementById('homeLoadCurrent'),
    homePeakLoad: document.getElementById('homePeakLoad'),
    homeUpsVoltage: document.getElementById('homeUpsVoltage'),
    sparklineBars: document.getElementById('sparklineBars'),
    loadStatusPill: document.getElementById('loadStatusPill'),
    btnFridge: document.getElementById('btnFridge'),
    btnKettle: document.getElementById('btnKettle'),
    btnResetLoad: document.getElementById('btnResetLoad'),

    gridVolts: document.getElementById('gridVolts'),
    gridFreq: document.getElementById('gridFreq'),
    gridVoltsBar: document.getElementById('gridVoltsBar'),
    gridFreqBar: document.getElementById('gridFreqBar'),
    gridQualityPill: document.getElementById('gridQualityPill'),
    gridRelayState: document.getElementById('gridRelayState'),
    gridPhaseLoss: document.getElementById('gridPhaseLoss'),

    energyGridToday: document.getElementById('energyGridToday'),
    energyBatToday: document.getElementById('energyBatToday'),
    energyTotalToday: document.getElementById('energyTotalToday'),
    ratioGridBar: document.getElementById('ratioGridBar'),
    ratioBatBar: document.getElementById('ratioBatBar'),
    ratioGridPercent: document.getElementById('ratioGridPercent'),
    ratioBatPercent: document.getElementById('ratioBatPercent'),

    dtekSubtitle: document.getElementById('dtekSubtitle'),
    dtekStatusPill: document.getElementById('dtekStatusPill'),
    dtekHoursGrid: document.getElementById('dtekHoursGrid'),

    outageLogBody: document.getElementById('outageLogBody'),
    outageCountThisWeek: document.getElementById('outageCountThisWeek'),
    outageTotalHours: document.getElementById('outageTotalHours'),

    toastContainer: document.getElementById('toastContainer')
  };

  // --- Web Audio API ---
  let audioCtx = null;

  function initAudio() {
    if (!audioCtx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (AudioContext) audioCtx = new AudioContext();
    }
    if (audioCtx && audioCtx.state === 'suspended') {
      audioCtx.resume();
    }
  }

  function playAlertSound(type = 'alarm') {
    if (!state.soundEnabled) return;
    try {
      initAudio();
      if (!audioCtx) return;
      const now = audioCtx.currentTime;
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.connect(gain);
      gain.connect(audioCtx.destination);

      if (type === 'alarm') {
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(440, now);
        osc.frequency.setValueAtTime(350, now + 0.12);
        gain.gain.setValueAtTime(0.15, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
        osc.start(now);
        osc.stop(now + 0.35);
      } else {
        osc.type = 'sine';
        osc.frequency.setValueAtTime(523.25, now);
        osc.frequency.exponentialRampToValueAtTime(659.25, now + 0.15);
        gain.gain.setValueAtTime(0.12, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.4);
        osc.start(now);
        osc.stop(now + 0.4);
      }
    } catch (err) {}
  }

  function showToast(title, desc, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type === 'danger' ? 'toast-danger' : type === 'success' ? 'toast-success' : ''}`;
    const icon = type === 'danger' ? '⚡' : type === 'success' ? '✅' : 'ℹ️';

    toast.innerHTML = `
      <div class="toast-icon">${icon}</div>
      <div class="toast-content">
        <div class="toast-title">${title}</div>
        <div class="toast-desc">${desc}</div>
      </div>
    `;
    dom.toastContainer.appendChild(toast);
    setTimeout(() => {
      toast.classList.add('toast-hiding');
      setTimeout(() => toast.remove(), 350);
    }, 4800);
  }

  function renderSparkline(currentVal) {
    state.sparklineHistory.shift();
    state.sparklineHistory.push(currentVal);

    dom.sparklineBars.innerHTML = '';
    const maxVal = Math.max(...state.sparklineHistory, 1000);

    state.sparklineHistory.forEach((val, idx) => {
      const bar = document.createElement('div');
      bar.className = 'sparkline-bar';
      if (idx === state.sparklineHistory.length - 1) bar.classList.add('latest');
      const pct = Math.min(100, Math.max(8, (val / maxVal) * 100));
      bar.style.height = `${pct}%`;
      bar.title = `${val} W`;
      dom.sparklineBars.appendChild(bar);
    });
  }

  async function fetchHistory() {
    try {
      const res = await fetch('/api/history?days=30');
      const data = await res.json();
      dom.outageCountThisWeek.textContent = data.count || 0;

      dom.outageLogBody.innerHTML = '';
      if (data.events && data.events.length > 0) {
        data.events.forEach(item => {
          const tr = document.createElement('tr');
          if (item.status === 'active') tr.className = 'outage-row-active';

          const badge = item.status === 'active'
            ? `<span class="outage-status-badge status-active"><span class="badge-dot"></span> АКТИВНО (АКБ)</span>`
            : `<span class="outage-status-badge status-restored"><span class="badge-dot"></span> Відновлено</span>`;

          tr.innerHTML = `
            <td>${badge}</td>
            <td><strong>${item.date}</strong></td>
            <td class="table-time-range">${item.time_down}</td>
            <td class="table-time-range">${item.time_up}</td>
            <td><span class="duration-tag">${item.duration}</span></td>
            <td>${item.bat_used}</td>
          `;
          dom.outageLogBody.appendChild(tr);
        });
      }
    } catch (e) {
      console.error('Помилка завантаження історії:', e);
    }
  }

  function renderDtekSchedule(dtek) {
    if (!dtek || !dtek.hourly) return;
    dom.dtekSubtitle.textContent = `Черга №${dtek.group} • Статус: ${dtek.status_label}`;
    dom.dtekStatusPill.textContent = dtek.status_label;

    if (dtek.status === 'no' || dtek.is_emergency) {
      dom.dtekStatusPill.className = 'card-pill pill-danger';
    } else if (dtek.status === 'maybe') {
      dom.dtekStatusPill.className = 'card-pill pill-warning';
    } else {
      dom.dtekStatusPill.className = 'card-pill pill-green';
    }

    dom.dtekHoursGrid.innerHTML = '';
    dtek.hourly.forEach(h => {
      const cell = document.createElement('div');
      cell.className = 'dtek-hour-cell';
      if (h.hour === dtek.current_hour) cell.classList.add('current-hour');

      const dotClass = h.status === 'yes' ? 'dot-yes' : h.status === 'maybe' ? 'dot-maybe' : 'dot-no';

      cell.innerHTML = `
        <span class="dtek-hour-num">${h.hour}</span>
        <div class="dtek-hour-status-dot ${dotClass}" title="${h.label}: ${h.status}"></div>
      `;
      dom.dtekHoursGrid.appendChild(cell);
    });
  }

  async function updateStatus() {
    try {
      const res = await fetch('/api/status');
      const data = await res.json();

      // Мережа
      const gridOnline = data.grid_online;
      if (gridOnline !== state.lastGridOnline) {
        if (gridOnline) {
          playAlertSound('restore');
          showToast('Мережу відновлено!', 'Живлення від міської мережі стабілізовано.', 'success');
        } else {
          playAlertSound('alarm');
          showToast('Світло зникло!', 'Інвертор перейшов на автономне живлення від АКБ.', 'danger');
        }
        state.lastGridOnline = gridOnline;
        fetchHistory();
      }

      if (gridOnline) {
        document.body.classList.remove('blackout-active');
        dom.gridToggleBtn.classList.remove('active-blackout');
        dom.gridSwitchText.textContent = 'Мережа: В нормі';
        dom.gridHeadline.textContent = `МЕРЕЖА: ОНЛАЙН (${Math.round(data.grid_volts)}V)`;
        dom.gridSubtext.textContent = 'Живлення будинку від зовнішньої мережі • Батарея в буфері';
        dom.modeTagText.textContent = 'РЕЖИМ: МЕРЕЖЕВИЙ (BYPASS)';

        dom.gridVolts.textContent = data.grid_volts.toFixed(0);
        dom.gridFreq.textContent = data.grid_freq.toFixed(1);
        dom.gridVoltsBar.style.width = `${Math.min(100, Math.max(0, ((data.grid_volts - 180) / 80) * 100))}%`;
        dom.gridVoltsBar.style.background = 'var(--color-online)';
        dom.gridQualityPill.textContent = 'Стабільно';
        dom.gridQualityPill.className = 'card-pill pill-green';
        dom.gridRelayState.textContent = 'Замкнуто (Підключено)';
        dom.gridRelayState.style.color = 'var(--color-online)';

        dom.batteryStatePill.textContent = 'Буфер';
        dom.batteryStatePill.className = 'card-pill pill-normal';
        dom.batteryPowerText.textContent = '+35 W';
        dom.batteryPowerText.className = 'mini-value color-green';
        dom.batteryCurrentText.textContent = '0.7 A';

        dom.flowGridVal.textContent = `${data.current_load} W`;
        dom.flowGridVal.style.color = 'var(--text-main)';
        dom.flowInverterVal.textContent = `${data.current_load} W`;
        dom.flowHomeVal.textContent = `${data.current_load} W`;
        dom.flowBatVal.textContent = 'Буфер (+35 W)';

        const gp = dom.lineGridToInv.querySelector('.flow-particles');
        if (gp) gp.className = 'flow-particles active';
        dom.batParticles.className = 'flow-particles';
      } else {
        document.body.classList.add('blackout-active');
        dom.gridToggleBtn.classList.add('active-blackout');
        dom.gridSwitchText.textContent = '⚠️ Мережа: Відключена';
        dom.gridHeadline.textContent = 'МЕРЕЖА: ВІДКЛЮЧЕНА (0V)';
        dom.gridSubtext.textContent = 'Аварія на лінії • Автономний режим від акумулятора (UPS)';
        dom.modeTagText.textContent = 'РЕЖИМ: АВТОНОМНИЙ UPS';

        dom.gridVolts.textContent = '0';
        dom.gridFreq.textContent = '0.0';
        dom.gridVoltsBar.style.width = '0%';
        dom.gridQualityPill.textContent = 'ОБРИВ МЕРЕЖІ';
        dom.gridQualityPill.className = 'card-pill pill-danger';
        dom.gridRelayState.textContent = 'Разомкнуто (Аварія)';
        dom.gridRelayState.style.color = 'var(--color-offline)';

        dom.batteryStatePill.textContent = 'РОЗРЯД (UPS)';
        dom.batteryStatePill.className = 'card-pill pill-warning';
        const dischargeCurrent = (data.current_load / data.battery_volts).toFixed(1);
        dom.batteryPowerText.textContent = `-${data.current_load} W`;
        dom.batteryPowerText.className = 'mini-value color-amber';
        dom.batteryCurrentText.textContent = `-${dischargeCurrent} A`;

        dom.flowGridVal.textContent = '0 W (Відкл)';
        dom.flowGridVal.style.color = 'var(--text-dim)';
        dom.flowInverterVal.textContent = `${data.current_load} W`;
        dom.flowHomeVal.textContent = `${data.current_load} W`;
        dom.flowBatVal.textContent = `Віддача: -${data.current_load} W`;

        const gp = dom.lineGridToInv.querySelector('.flow-particles');
        if (gp) gp.className = 'flow-particles grid-flow-off';
        dom.batParticles.className = 'flow-particles bat-discharging';
      }

      // Час роботи
      dom.runtimeHighlight.textContent = data.runtime;
      dom.runtimeLoadRef.textContent = `${data.current_load} W`;

      // Батарея
      dom.batterySocText.innerHTML = `${Math.round(data.battery_soc)}<span class="unit">%</span>`;
      dom.batteryVoltsText.textContent = `${data.battery_volts.toFixed(1)} V`;
      dom.batteryTempText.textContent = `${data.battery_temp.toFixed(1)} °C`;

      const soc = Math.max(0, Math.min(100, data.battery_soc));
      dom.batteryGaugeFill.style.strokeDashoffset = 314.16 - (soc / 100) * 314.16;
      dom.batteryBarFill.style.width = `${soc}%`;
      if (soc < 20) {
        dom.batteryGaugeFill.style.stroke = 'var(--color-offline)';
        dom.batteryBarFill.style.background = 'var(--color-offline)';
      } else if (soc < 40) {
        dom.batteryGaugeFill.style.stroke = 'var(--color-warning)';
        dom.batteryBarFill.style.background = 'var(--color-warning)';
      } else {
        dom.batteryGaugeFill.style.stroke = 'var(--color-online)';
        dom.batteryBarFill.style.background = 'linear-gradient(90deg, #10b981 0%, #34d399 100%)';
      }

      // Навантаження будинку
      dom.homeLoadPower.textContent = data.current_load;
      dom.homeLoadCurrent.textContent = `${(data.current_load / 230).toFixed(2)} A`;
      dom.homePeakLoad.textContent = `${data.peak_load.toLocaleString('uk-UA')} W`;
      renderSparkline(data.current_load);

      if (data.current_load > 1800) {
        dom.loadStatusPill.textContent = 'Високе';
        dom.loadStatusPill.className = 'card-pill pill-warning';
      } else {
        dom.loadStatusPill.textContent = 'Звичайне';
        dom.loadStatusPill.className = 'card-pill pill-blue';
      }

      // Енергобаланс
      dom.energyGridToday.textContent = data.energy_grid_today.toFixed(2);
      dom.energyBatToday.textContent = data.energy_bat_today.toFixed(2);
      dom.energyTotalToday.textContent = data.energy_total_today.toFixed(2);

      const gridPct = Math.round((data.energy_grid_today / data.energy_total_today) * 100) || 75;
      const batPct = 100 - gridPct;
      dom.ratioGridBar.style.width = `${gridPct}%`;
      dom.ratioBatBar.style.width = `${batPct}%`;
      dom.ratioGridPercent.textContent = `${gridPct}%`;
      dom.ratioBatPercent.textContent = `${batPct}%`;

      // ДТЕК графік
      if (data.dtek) {
        renderDtekSchedule(data.dtek);
      }

      dom.lastUpdateTs.textContent = new Date().toLocaleTimeString('uk-UA');
    } catch (e) {
      console.error('Помилка оновлення статусу з API:', e);
    }
  }

  function updateClock() {
    const now = new Date();
    dom.clockTime.textContent = now.toLocaleTimeString('uk-UA');

    const days = ['Неділя', 'Понеділок', 'Вівторок', 'Середа', 'Четвер', 'П’ятниця', 'Субота'];
    const months = ['', 'січня', 'лютого', 'березня', 'квітня', 'травня', 'червня', 'липня', 'серпня', 'вересня', 'жовтня', 'листопада', 'грудня'];
    dom.clockDate.textContent = `${days[now.getDay()]}, ${now.getDate()} ${months[now.getMonth()]} ${now.getFullYear()}`;
  }

  function setupEvents() {
    dom.gridToggleBtn.addEventListener('click', async () => {
      initAudio();
      try {
        const res = await fetch('/api/toggle-grid', { method: 'POST' });
        const data = await res.json();
        updateStatus();
        fetchHistory();
      } catch (e) {
        showToast('Помилка', 'Не вдалося надіслати запит на перемикання мережі', 'danger');
      }
    });

    dom.soundToggleBtn.addEventListener('click', () => {
      initAudio();
      state.soundEnabled = !state.soundEnabled;
      if (state.soundEnabled) {
        dom.soundIconOn.classList.remove('hidden');
        dom.soundIconOff.classList.add('hidden');
        showToast('Звук увімкнено', 'Звукові сповіщення активовано');
      } else {
        dom.soundIconOn.classList.add('hidden');
        dom.soundIconOff.classList.remove('hidden');
        showToast('Звук вимкнено', 'Звукові сповіщення деактивовано');
      }
    });

    dom.btnFridge.addEventListener('click', async () => {
      const active = dom.btnFridge.classList.toggle('active-load');
      await fetch('/api/control-load', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ device: 'fridge', action: active })
      });
      showToast('Навантаження', active ? 'Холодильник увімкнено (+150W)' : 'Холодильник вимкнено');
      updateStatus();
    });

    dom.btnKettle.addEventListener('click', async () => {
      const active = dom.btnKettle.classList.toggle('active-load');
      await fetch('/api/control-load', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ device: 'kettle', action: active })
      });
      showToast('Висока потужність!', active ? 'Чайник увімкнено (+1.8 кВт)' : 'Чайник вимкнено', active ? 'danger' : 'info');
      updateStatus();
    });

    dom.btnResetLoad.addEventListener('click', async () => {
      dom.btnFridge.classList.remove('active-load');
      dom.btnKettle.classList.remove('active-load');
      await fetch('/api/control-load', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ device: 'reset', action: false })
      });
      showToast('Скидання', 'Додаткові прилади вимкнено.');
      updateStatus();
    });
  }

  function init() {
    updateClock();
    setInterval(updateClock, 1000);

    updateStatus();
    fetchHistory();

    setupEvents();

    // Опитування бекенду кожні 2 секунди
    setInterval(updateStatus, 2000);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
