@'
/* ==========================================================================
   Deye Inverter Home Energy System — Dark Theme & Responsive Stylesheet
   Palette: Background #0f172a, Cards #1e293b, Text #f8fafc / #94a3b8
   ========================================================================== */

:root {
  --bg-main: #0f172a;
  --bg-card: #1e293b;
  --bg-card-hover: #24344d;
  --bg-subtle: #334155;
  --border-card: rgba(148, 163, 184, 0.12);
  --border-focus: rgba(56, 189, 248, 0.5);

  --text-main: #f8fafc;
  --text-muted: #94a3b8;
  --text-dim: #64748b;

  --color-online: #10b981;
  --color-online-glow: rgba(16, 185, 129, 0.25);
  --color-online-bg: rgba(16, 185, 129, 0.12);

  --color-offline: #f43f5e;
  --color-offline-glow: rgba(244, 63, 94, 0.35);
  --color-offline-bg: rgba(244, 63, 94, 0.15);

  --color-warning: #f59e0b;
  --color-warning-glow: rgba(245, 158, 11, 0.25);

  --color-cyan: #38bdf8;
  --color-violet: #a855f7;
  --color-blue: #3b82f6;

  --radius-sm: 8px;
  --radius-md: 14px;
  --radius-lg: 20px;
  --radius-xl: 26px;

  --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;

  --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.25);
  --shadow-md: 0 8px 24px rgba(0, 0, 0, 0.35);
  --shadow-lg: 0 16px 36px rgba(0, 0, 0, 0.45);
  --shadow-glow-green: 0 0 25px rgba(16, 185, 129, 0.25);
  --shadow-glow-red: 0 0 35px rgba(244, 63, 94, 0.3);

  --transition-fast: 0.18s ease;
  --transition-normal: 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

html, body {
  min-height: 100vh;
  background-color: var(--bg-main);
  color: var(--text-main);
  font-family: var(--font-sans);
  line-height: 1.5;
  overflow-x: hidden;
  position: relative;
}

/* Декоративне фонове свічення */
.bg-glow {
  position: fixed;
  border-radius: 50%;
  pointer-events: none;
  filter: blur(120px);
  z-index: 0;
  opacity: 0.4;
  transition: opacity 0.8s ease, background 0.8s ease;
}

.bg-glow-1 {
  width: 500px;
  height: 500px;
  top: -100px;
  left: 10%;
  background: radial-gradient(circle, rgba(16, 185, 129, 0.15) 0%, transparent 70%);
}

.bg-glow-2 {
  width: 450px;
  height: 450px;
  top: 300px;
  right: 5%;
  background: radial-gradient(circle, rgba(56, 189, 248, 0.12) 0%, transparent 70%);
}

body.blackout-active .bg-glow-1 {
  background: radial-gradient(circle, rgba(244, 63, 94, 0.25) 0%, transparent 70%);
  opacity: 0.6;
}

body.blackout-active .bg-glow-2 {
  background: radial-gradient(circle, rgba(245, 158, 11, 0.18) 0%, transparent 70%);
}

/* Основний контейнер додатку */
.app-container {
  position: relative;
  z-index: 1;
  max-width: 1440px;
  margin: 0 auto;
  padding: 18px 24px 36px 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Header */
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 20px;
  background: var(--bg-card);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  backdrop-filter: blur(8px);
}

.header-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-icon {
  width: 42px;
  height: 42px;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  box-shadow: 0 4px 12px rgba(2, 132, 199, 0.35);
  flex-shrink: 0;
}

.brand-icon svg { width: 24px; height: 24px; }

.brand-title {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.brand-name {
  font-weight: 800;
  font-size: 1.25rem;
  letter-spacing: 0.05em;
  color: #fff;
}

.brand-model {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--color-cyan);
  background: rgba(56, 189, 248, 0.12);
  padding: 2px 7px;
  border-radius: 6px;
}

.brand-subtitle {
  font-size: 0.76rem;
  color: var(--text-muted);
}

.header-center {
  display: flex;
  align-items: center;
}

.clock-widget {
  text-align: center;
  padding: 4px 14px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-sm);
}

.clock-time {
  font-family: var(--font-mono);
  font-size: 1.15rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: var(--text-main);
}

.clock-date {
  font-size: 0.72rem;
  color: var(--text-muted);
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.bms-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid var(--border-card);
  border-radius: 20px;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-muted);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-online);
}

.pulse-green {
  box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
  animation: pulse-ring 2s infinite;
}

@keyframes pulse-ring {
  0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
  70% { box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
  100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

.sound-toggle-btn {
  width: 38px;
  height: 38px;
  border-radius: var(--radius-md);
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid var(--border-card);
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition-fast);
}

.sound-toggle-btn:hover {
  background: var(--bg-subtle);
  color: var(--text-main);
}

.sound-toggle-btn svg { width: 18px; height: 18px; }

.settings-btn {
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-md);
  width: 38px;
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  cursor: pointer;
  text-decoration: none;
  transition: var(--transition-fast);
}

.settings-btn:hover {
  background: var(--bg-subtle);
  color: var(--text-main);
  border-color: rgba(56, 189, 248, 0.4);
}

.settings-btn svg { width: 18px; height: 18px; }

.sim-switch-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(16, 185, 129, 0.16);
  border: 1px solid rgba(16, 185, 129, 0.4);
  border-radius: 30px;
  color: #a7f3d0;
  font-family: var(--font-sans);
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 0 15px rgba(16, 185, 129, 0.2);
  transition: all var(--transition-normal);
}

.sim-switch-btn.active-blackout {
  background: rgba(244, 63, 94, 0.22);
  border-color: rgba(244, 63, 94, 0.65);
  color: #fecdd3;
  box-shadow: 0 0 20px rgba(244, 63, 94, 0.4);
}

.switch-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Banner */
.network-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 24px 28px;
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-glow-green);
  transition: all 0.4s ease;
  position: relative;
  overflow: hidden;
}

.network-banner::before {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, #10b981 0%, #34d399 50%, #10b981 100%);
}

body.blackout-active .network-banner {
  border-color: rgba(244, 63, 94, 0.5);
  box-shadow: var(--shadow-glow-red);
}

body.blackout-active .network-banner::before {
  background: linear-gradient(90deg, #f43f5e 0%, #fb7185 50%, #f43f5e 100%);
}

.banner-main-status {
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 1;
}

.status-indicator-badge {
  display: flex;
  align-items: center;
  gap: 18px;
  position: relative;
}

.status-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  background: var(--color-online-bg);
  border: 1px solid rgba(16, 185, 129, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-online);
  flex-shrink: 0;
}

body.blackout-active .status-icon {
  background: var(--color-offline-bg);
  border-color: rgba(244, 63, 94, 0.5);
  color: var(--color-offline);
}

.status-icon svg { width: 28px; height: 28px; }

.status-headline {
  font-size: 1.85rem;
  font-weight: 800;
  color: var(--color-online);
  line-height: 1.2;
}

body.blackout-active .status-headline {
  color: var(--color-offline);
}

.status-subtext {
  font-size: 0.88rem;
  color: var(--text-muted);
  margin-top: 4px;
}

.status-mode-tag {
  align-self: flex-start;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 5px 14px;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid var(--border-card);
  border-radius: 30px;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--color-cyan);
}

.mode-bullet {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--color-cyan);
}

body.blackout-active .status-mode-tag {
  background: rgba(245, 158, 11, 0.15);
  border-color: rgba(245, 158, 11, 0.4);
  color: #fbbf24;
}

body.blackout-active .mode-bullet {
  background: #fbbf24;
}

.banner-divider {
  width: 1px;
  height: 80px;
  background: rgba(148, 163, 184, 0.15);
}

.banner-runtime {
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 320px;
  padding-left: 12px;
}

.runtime-caption {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.07em;
  color: var(--text-muted);
  text-transform: uppercase;
}

.runtime-caption svg { width: 16px; height: 16px; color: var(--color-cyan); }

.runtime-value {
  font-size: 1.85rem;
  font-weight: 800;
  color: var(--text-main);
  margin: 4px 0 2px 0;
}

.runtime-value .highlight {
  color: #38bdf8;
  font-family: var(--font-mono);
}

body.blackout-active .runtime-value .highlight {
  color: #fbbf24;
}

.runtime-sub {
  font-size: 0.78rem;
  color: var(--text-dim);
}

.runtime-sub strong { color: var(--text-muted); }

/* Power Flow */
.power-flow-section { width: 100%; }

.flow-card {
  background: var(--bg-card);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-lg);
  padding: 18px 24px 22px 24px;
  box-shadow: var(--shadow-sm);
}

.flow-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.flow-title {
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
}

.flow-badge {
  font-size: 0.74rem;
  font-weight: 600;
  color: var(--color-online);
  background: var(--color-online-bg);
  padding: 3px 10px;
  border-radius: 12px;
  border: 1px solid rgba(16, 185, 129, 0.25);
}

.flow-diagram {
  position: relative;
  display: grid;
  grid-template-columns: 1fr 120px 1.2fr 120px 1fr;
  grid-template-rows: auto 80px auto;
  align-items: center;
  justify-items: center;
  max-width: 900px;
  margin: 0 auto;
}

.flow-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 6px;
  position: relative;
  z-index: 2;
}

.node-icon {
  width: 54px;
  height: 54px;
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.8);
  border: 2px solid var(--border-card);
  display: flex;
  align-items: center;
  justify-content: center;
}

.node-icon svg { width: 26px; height: 26px; }

.grid-icon { color: var(--color-online); border-color: rgba(16, 185, 129, 0.5); }
.deye-icon { color: var(--color-cyan); border-color: rgba(56, 189, 248, 0.6); }
.home-icon { color: #f59e0b; border-color: rgba(245, 158, 11, 0.5); }
.bat-icon { color: #10b981; border-color: rgba(16, 185, 129, 0.5); }

body.blackout-active .grid-icon {
  color: var(--text-dim);
  border-color: rgba(100, 116, 139, 0.3);
  opacity: 0.5;
}

.node-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-muted);
}

.node-val {
  font-family: var(--font-mono);
  font-size: 0.84rem;
  font-weight: 700;
  color: var(--text-main);
  background: rgba(15, 23, 42, 0.7);
  padding: 2px 8px;
  border-radius: 6px;
  border: 1px solid var(--border-card);
}

.highlight-val {
  color: var(--color-cyan);
  border-color: rgba(56, 189, 248, 0.3);
}

#nodeGrid { grid-column: 1; grid-row: 1; }
.flow-line-left { grid-column: 2; grid-row: 1; }
#nodeInverter { grid-column: 3; grid-row: 1; }
.flow-line-right { grid-column: 4; grid-row: 1; }
#nodeHome { grid-column: 5; grid-row: 1; }

.flow-line-bottom {
  grid-column: 3;
  grid-row: 2;
  height: 100%;
  display: flex;
  justify-content: center;
}

#nodeBattery { grid-column: 3; grid-row: 3; }

.flow-line-wrap {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 1;
}

.flow-line {
  position: relative;
  width: 100%;
  height: 3px;
  background: rgba(148, 163, 184, 0.18);
  border-radius: 2px;
  overflow: hidden;
}

.flow-line-vert { width: 3px; height: 100%; }

.flow-particles {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
}

.flow-particles.active {
  background: repeating-linear-gradient(90deg, transparent, transparent 10px, var(--color-online) 10px, var(--color-online) 20px);
  animation: flow-anim 0.8s linear infinite;
}

@keyframes flow-anim {
  0% { background-position: 0 0; }
  100% { background-position: 40px 0; }
}

.flow-particles.bat-discharging {
  background: repeating-linear-gradient(0deg, transparent, transparent 8px, var(--color-warning) 8px, var(--color-warning) 16px);
  animation: flow-up 0.8s linear infinite;
}

@keyframes flow-up {
  0% { background-position: 0 32px; }
  100% { background-position: 0 0; }
}

/* 4 Cards Grid */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px;
  width: 100%;
}

.metric-card {
  background: var(--bg-card);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-lg);
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: var(--shadow-sm);
  position: relative;
}

.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.card-title-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-icon-badge {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.card-icon-badge svg { width: 20px; height: 20px; }

.battery-badge { background: rgba(16, 185, 129, 0.15); color: #10b981; }
.load-badge { background: rgba(56, 189, 248, 0.15); color: #38bdf8; }
.grid-badge { background: rgba(168, 85, 247, 0.15); color: #a855f7; }
.energy-badge { background: rgba(245, 158, 11, 0.15); color: #f59e0b; }

.card-title {
  font-size: 0.96rem;
  font-weight: 700;
  color: var(--text-main);
}

.card-subtitle {
  font-size: 0.72rem;
  color: var(--text-muted);
}

.card-pill {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 3px 9px;
  border-radius: 12px;
}

.pill-normal, .pill-green { background: rgba(16, 185, 129, 0.15); color: #34d399; }
.pill-blue { background: rgba(56, 189, 248, 0.15); color: #38bdf8; }
.pill-violet { background: rgba(168, 85, 247, 0.15); color: #c084fc; }
.pill-warning { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
.pill-danger { background: rgba(244, 63, 94, 0.2); color: #fb7185; }

.battery-dial-container {
  position: relative;
  width: 120px;
  height: 120px;
  margin: 0 auto 14px auto;
  display: flex;
  align-items: center;
  justify-content: center;
}

.battery-circular-gauge { width: 100%; height: 100%; }

.gauge-bg {
  fill: none;
  stroke: rgba(148, 163, 184, 0.12);
  stroke-width: 9;
}

.gauge-fill {
  fill: none;
  stroke: #10b981;
  stroke-width: 9;
  stroke-linecap: round;
  stroke-dasharray: 314;
  stroke-dashoffset: 40;
  transition: stroke-dashoffset 0.8s ease;
}

.gauge-center-text {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.big-percent {
  font-family: var(--font-mono);
  font-size: 1.7rem;
  font-weight: 800;
  color: var(--text-main);
  line-height: 1;
}

.big-percent .unit { font-size: 0.95rem; color: var(--text-muted); }

.gauge-state-text {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-cyan);
  margin-top: 3px;
  font-family: var(--font-mono);
}

.meter-bar-track {
  width: 100%;
  height: 6px;
  background: rgba(15, 23, 42, 0.8);
  border-radius: 4px;
  overflow: hidden;
}

.meter-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981 0%, #34d399 100%);
  border-radius: 4px;
}

.meter-ticks {
  display: flex;
  justify-content: space-between;
  font-size: 0.65rem;
  color: var(--text-dim);
  margin-top: 4px;
  font-family: var(--font-mono);
}

.data-mini-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 12px;
}

.data-mini-item {
  background: rgba(15, 23, 42, 0.6);
  padding: 8px 10px;
  border-radius: var(--radius-sm);
  border: 1px solid rgba(148, 163, 184, 0.08);
  display: flex;
  flex-direction: column;
}

.mini-label {
  font-size: 0.68rem;
  color: var(--text-muted);
  text-transform: uppercase;
}

.mini-value {
  font-family: var(--font-mono);
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-main);
  margin-top: 2px;
}

.color-green { color: #34d399; }
.color-rose { color: #fb7185; }
.color-amber { color: #fbbf24; }

.large-value-display {
  display: flex;
  align-items: baseline;
  gap: 6px;
  margin-bottom: 12px;
}

.value-number {
  font-family: var(--font-mono);
  font-size: 2.3rem;
  font-weight: 800;
  color: #fff;
  line-height: 1;
}

.value-unit { font-size: 1.15rem; font-weight: 600; color: var(--text-muted); }

.sparkline-bar-group {
  display: flex;
  align-items: flex-end;
  gap: 4px;
  height: 38px;
  padding: 2px 0;
  border-bottom: 1px solid var(--border-card);
}

.sparkline-bar {
  flex: 1;
  background: rgba(56, 189, 248, 0.3);
  border-radius: 2px 2px 0 0;
  min-height: 4px;
}

.sparkline-bar.latest {
  background: var(--color-cyan);
}

.sparkline-sub {
  font-size: 0.68rem;
  color: var(--text-dim);
  margin-top: 4px;
}

.quick-load-controls {
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid var(--border-card);
}

.quick-label {
  display: block;
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.load-buttons-group {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.load-btn {
  padding: 5px 9px;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid var(--border-card);
  border-radius: 6px;
  color: var(--text-muted);
  font-size: 0.72rem;
  font-weight: 600;
  cursor: pointer;
}

.load-btn:hover {
  background: var(--bg-subtle);
  color: var(--text-main);
}

.load-btn.active-load {
  background: rgba(245, 158, 11, 0.18);
  border-color: rgba(245, 158, 11, 0.5);
  color: #fbbf24;
}

.grid-params-split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 14px;
}

.param-half {
  background: rgba(15, 23, 42, 0.6);
  padding: 12px;
  border-radius: var(--radius-sm);
  border: 1px solid rgba(148, 163, 184, 0.08);
  display: flex;
  flex-direction: column;
}

.param-title {
  font-size: 0.68rem;
  color: var(--text-muted);
  font-weight: 700;
}

.param-big-val {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin: 6px 0;
}

.param-big-val .value-number { font-size: 1.7rem; }
.param-big-val .value-unit { font-size: 0.95rem; }

.param-status-bar {
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 6px;
}

.param-gauge-bar {
  height: 100%;
  background: var(--color-online);
  border-radius: 2px;
}

.param-norm { font-size: 0.66rem; color: var(--text-dim); }

.grid-card-footer {
  padding-top: 10px;
  border-top: 1px solid var(--border-card);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.grid-info-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.74rem;
}

.info-label { color: var(--text-muted); }
.info-val { font-weight: 600; color: var(--text-main); font-family: var(--font-mono); }

.energy-details-stack {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.energy-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 10px;
  background: rgba(15, 23, 42, 0.6);
  border-radius: var(--radius-sm);
  border: 1px solid rgba(148, 163, 184, 0.08);
}

.energy-row-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.energy-icon-bullet {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.grid-bullet { background: #a855f7; }
.bat-bullet { background: #10b981; }
.home-bullet { background: #38bdf8; }

.energy-row-title { font-size: 0.78rem; font-weight: 600; color: var(--text-main); }
.energy-row-desc { font-size: 0.68rem; color: var(--text-dim); }
.energy-num { font-size: 1.05rem; font-weight: 700; color: var(--text-main); font-family: var(--font-mono); }
.highlight-num { color: #38bdf8; }
.energy-unit { font-size: 0.75rem; color: var(--text-muted); margin-left: 2px; }

.total-row {
  background: rgba(56, 189, 248, 0.08);
  border-color: rgba(56, 189, 248, 0.2);
}

.energy-ratio-bar {
  display: flex;
  height: 8px;
  width: 100%;
  border-radius: 4px;
  overflow: hidden;
  margin-top: 4px;
  background: rgba(15, 23, 42, 0.9);
}

.ratio-segment { height: 100%; }
.ratio-grid { background: #a855f7; }
.ratio-bat { background: #10b981; }

.ratio-legend {
  display: flex;
  justify-content: space-between;
  font-size: 0.72rem;
  color: var(--text-muted);
}

.legend-item { display: flex; align-items: center; gap: 5px; }
.legend-color { width: 8px; height: 8px; border-radius: 2px; }
.grid-bg { background: #a855f7; }
.bat-bg { background: #10b981; }

/* DTEK Section */
.dtek-schedule-section {
  background: var(--bg-card);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-lg);
  padding: 22px 24px;
  box-shadow: var(--shadow-sm);
  width: 100%;
}

.dtek-icon-badge {
  background: rgba(56, 189, 248, 0.12);
  border: 1px solid rgba(56, 189, 248, 0.25);
  color: var(--color-cyan);
}

.dtek-timeline-container {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-top: 14px;
}

.dtek-hours-grid {
  display: grid;
  grid-template-columns: repeat(24, 1fr);
  gap: 4px;
}

.dtek-hour-cell {
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(148, 163, 184, 0.1);
  border-radius: 6px;
  padding: 8px 2px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.dtek-hour-cell.current-hour {
  border-color: var(--color-cyan);
  box-shadow: 0 0 10px rgba(56, 189, 248, 0.3);
}

.dtek-hour-num {
  font-size: 0.65rem;
  color: var(--text-dim);
  font-family: var(--font-mono);
}

.dtek-hour-status-dot {
  width: 100%;
  height: 24px;
  border-radius: 4px;
}

.dot-yes { background: rgba(16, 185, 129, 0.7); }
.dot-maybe { background: rgba(245, 158, 11, 0.7); }
.dot-no { background: rgba(244, 63, 94, 0.75); }

.dtek-legend {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  flex-wrap: wrap;
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 6px;
}

.dtek-leg-item { display: flex; align-items: center; gap: 6px; }
.dtek-box { width: 12px; height: 12px; border-radius: 3px; }
.box-yes { background: #10b981; }
.box-maybe { background: #f59e0b; }
.box-no { background: #f43f5e; }

/* Outage Section */
.outage-section {
  background: var(--bg-card);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-lg);
  padding: 22px 24px;
  box-shadow: var(--shadow-sm);
  width: 100%;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
  flex-wrap: wrap;
}

.section-title-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: rgba(244, 63, 94, 0.12);
  border: 1px solid rgba(244, 63, 94, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fb7185;
  flex-shrink: 0;
}

.section-icon svg { width: 20px; height: 20px; }
.section-title { font-size: 1.1rem; font-weight: 700; color: var(--text-main); }
.section-subtitle { font-size: 0.78rem; color: var(--text-muted); }

.outage-summary-stats {
  display: flex;
  align-items: center;
  gap: 10px;
}

.summary-stat-badge {
  display: flex;
  flex-direction: column;
  padding: 6px 14px;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-sm);
}

.stat-num { font-family: var(--font-mono); font-size: 1rem; font-weight: 700; color: #f8fafc; }
.stat-label { font-size: 0.68rem; color: var(--text-dim); }

.table-container {
  width: 100%;
  overflow-x: auto;
  border-radius: var(--radius-md);
  border: 1px solid rgba(148, 163, 184, 0.08);
}

.outage-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.84rem;
}

.outage-table th {
  background: rgba(15, 23, 42, 0.85);
  color: var(--text-muted);
  font-weight: 600;
  padding: 12px 16px;
  font-size: 0.7rem;
  letter-spacing: 0.04em;
  border-bottom: 1px solid var(--border-card);
}

.outage-table td {
  padding: 13px 16px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.06);
  color: var(--text-main);
  vertical-align: middle;
}

.outage-table tr:hover td { background: rgba(255, 255, 255, 0.02); }

.outage-status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.72rem;
  font-weight: 700;
}

.status-restored { background: rgba(16, 185, 129, 0.15); color: #34d399; }
.status-active { background: rgba(244, 63, 94, 0.22); color: #fb7185; }

.badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.table-time-range { font-family: var(--font-mono); font-weight: 600; }

.duration-tag {
  display: inline-block;
  padding: 2px 8px;
  background: rgba(15, 23, 42, 0.6);
  border-radius: 6px;
  font-family: var(--font-mono);
  font-weight: 600;
  color: #38bdf8;
}

/* Footer */
.footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  font-size: 0.75rem;
  color: var(--text-dim);
  border-top: 1px solid rgba(148, 163, 184, 0.08);
  flex-wrap: wrap;
  gap: 10px;
}

.footer-separator { margin: 0 8px; color: rgba(148, 163, 184, 0.2); }
.footer-right strong { color: var(--text-muted); }

/* Toast */
.toast-container {
  position: fixed;
  bottom: 24px;
  right: 24px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 9999;
  pointer-events: none;
  max-width: 420px;
}

.toast {
  pointer-events: auto;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 18px;
  background: #1e293b;
  border: 1px solid var(--border-card);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  color: var(--text-main);
}

.toast-danger {
  border-color: rgba(244, 63, 94, 0.6);
  background: linear-gradient(135deg, #1e293b 0%, rgba(244, 63, 94, 0.15) 100%);
}

.toast-success {
  border-color: rgba(16, 185, 129, 0.6);
  background: linear-gradient(135deg, #1e293b 0%, rgba(16, 185, 129, 0.15) 100%);
}

.toast-icon { font-size: 1.3rem; }
.toast-title { font-size: 0.88rem; font-weight: 700; margin-bottom: 2px; }
.toast-desc { font-size: 0.78rem; color: var(--text-muted); }

.hidden { display: none !important; }

@media (max-width: 1200px) {
  .cards-grid { grid-template-columns: repeat(2, 1fr); }
  .network-banner { flex-direction: column; align-items: stretch; gap: 18px; }
  .banner-divider { width: 100%; height: 1px; }
  .banner-runtime { padding-left: 0; min-width: unset; }
}

@media (max-width: 900px) {
  .flow-diagram { grid-template-columns: 1fr 60px 1fr 60px 1fr; }
}

@media (max-width: 640px) {
  .cards-grid { grid-template-columns: 1fr; }
  .flow-diagram { display: flex; flex-direction: column; gap: 14px; }
  .flow-line-wrap { display: none; }
}
'@ | Set-Content -Path "styles.css" -Encoding UTF8

Write-Host "✅ styles.css полностью заменен на чистый эталон!" -ForegroundColor Green