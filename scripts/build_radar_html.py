#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
with open(ROOT / "data" / "raw_award_scan.json", encoding="utf-8") as f:
    scan = json.load(f)
with open(ROOT / "data" / "biz_flight_details.json", encoding="utf-8") as f:
    biz_details = json.load(f)
with open(ROOT / "data" / "seats_aero_finnair_asia_eu.json", encoding="utf-8") as f:
    sa_rows = json.load(f)

asian_hubs = {"PVG", "HKG", "ICN", "HND", "NRT", "KIX", "BKK", "HKT", "SIN", "DEL"}
sa_filtered = []
for r in sa_rows:
    oa, da = r.get("oa", ""), r.get("da", "")
    if oa == "PVG" or da == "PVG" or ((oa in asian_hubs or da in asian_hubs) and (r.get("js", 0) > 0 or r.get("ws", 0) > 0)):
        sa_filtered.append({
            "dt": r.get("dt"),
            "oa": oa,
            "da": da,
            "ys": r.get("ys", 0),
            "ws": r.get("ws", 0),
            "js": r.get("js", 0),
            "ym": r.get("ym", 0),
            "wm": r.get("wm", 0),
            "jm": r.get("jm", 0),
            "yc": r.get("yc", ""),
            "wc": r.get("wc", ""),
            "jc": r.get("jc", ""),
            "yd": bool(r.get("yd")),
            "wd": bool(r.get("wd")),
            "jd": bool(r.get("jd")),
            "lsh": r.get("lsh", 0),
        })

sa_filtered.sort(key=lambda x: (x["dt"], -(x["js"] * 100 + x["ws"] * 10 + x["ys"])))

payload = {
    "generatedAt": "2026-11-15 12:18 CST",
    "months": [
        "2026-11", "2026-12", "2027-01", "2027-02", "2027-03", "2027-04",
        "2027-05", "2027-06", "2027-07", "2027-08", "2027-09", "2027-10"
    ],
    "calendar": scan,
    "flightDetails": biz_details,
    "finnairNative": sa_filtered[:250]
}

html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>芬航 (Finnair) & 寰宇一家 未来一年积分票/升舱位雷达 (PVG ⇄ HEL / CDG)</title>
<script>
  (() => {
    const param = new URLSearchParams(window.location.search).get("scoutTheme");
    const theme =
      param || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    document.documentElement.setAttribute("data-theme", theme);
  })();
</script>
<style>
:root {
  color-scheme: light;
  --cp-bg: #f7f4ef;
  --cp-bg-elevated: #fcfbf8;
  --cp-surface: #ffffff;
  --cp-surface-soft: #f5f5f5;
  --cp-border: #dedede;
  --cp-border-strong: #919191;
  --cp-text: #242424;
  --cp-text-muted: #5c5c5c;
  --cp-text-soft: #6f6f6f;
  --cp-accent: #b11f4b;
  --cp-accent-hover: #9a1a41;
  --cp-accent-soft: rgba(177, 31, 75, 0.08);
  --cp-accent-fg: #ffffff;
  --cp-success: #16a34a;
  --cp-danger: #dc2626;
  --cp-warning: #f59e0b;
  --cp-link: #0078d4;
  --cp-shadow: 0 18px 48px rgba(0, 0, 0, 0.12);
  --cp-overlay: rgba(255, 255, 255, 0.8);
  --cp-panel: rgba(255, 255, 255, 0.86);
  --cp-panel-strong: rgba(255, 255, 255, 0.96);
  --cp-sheen: rgba(255, 255, 255, 0.55);
  --cp-highlight: rgba(177, 31, 75, 0.12);
}
html[data-theme="dark"] {
  color-scheme: dark;
  --cp-bg: #3d3b3a;
  --cp-bg-elevated: #343231;
  --cp-surface: #292929;
  --cp-surface-soft: #2e2e2e;
  --cp-border: #474747;
  --cp-border-strong: #5f5f5f;
  --cp-text: #dedede;
  --cp-text-muted: #919191;
  --cp-text-soft: #b0b0b0;
  --cp-accent: #fd8ea1;
  --cp-accent-hover: #fb7b91;
  --cp-accent-soft: rgba(253, 142, 161, 0.14);
  --cp-accent-fg: #1a1a1a;
  --cp-success: #4ade80;
  --cp-danger: #f87171;
  --cp-warning: #fbbf24;
  --cp-link: #4da6ff;
  --cp-shadow: 0 18px 48px rgba(0, 0, 0, 0.32);
  --cp-overlay: rgba(41, 41, 41, 0.88);
  --cp-panel: rgba(41, 41, 41, 0.72);
  --cp-panel-strong: rgba(41, 41, 41, 0.96);
  --cp-sheen: rgba(255, 255, 255, 0.04);
  --cp-highlight: rgba(253, 142, 161, 0.12);
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  background: var(--cp-bg);
  color: var(--cp-text);
  font-family: "Segoe UI", Aptos, Calibri, -apple-system, BlinkMacSystemFont, sans-serif;
  line-height: 1.5;
  padding: 20px;
}

code, pre, .mono {
  font-family: Consolas, "Courier New", Courier, monospace;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  background: var(--cp-surface);
  border: 1px solid var(--cp-border);
  border-radius: 16px;
  padding: 20px 24px;
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 16px;
}

.header-title h1 {
  font-size: 1.45rem;
  font-weight: 700;
  color: var(--cp-text);
  margin-bottom: 4px;
}

.header-title p {
  font-size: 0.9rem;
  color: var(--cp-text-muted);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.btn {
  background: var(--cp-surface-soft);
  color: var(--cp-text);
  border: 1px solid var(--cp-border);
  border-radius: 0.625rem;
  padding: 8px 14px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn:hover {
  border-color: var(--cp-border-strong);
  background: var(--cp-bg-elevated);
}

.btn-primary {
  background: var(--cp-accent);
  color: var(--cp-accent-fg);
  border-color: var(--cp-accent);
}

.btn-primary:hover {
  background: var(--cp-accent-hover);
  border-color: var(--cp-accent-hover);
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.kpi-card {
  background: var(--cp-surface);
  border: 1px solid var(--cp-border);
  border-radius: 16px;
  padding: 16px 20px;
}

.kpi-label {
  font-size: 0.8rem;
  color: var(--cp-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.03em;
  margin-bottom: 6px;
}

.kpi-value {
  font-size: 1.65rem;
  font-weight: 700;
  color: var(--cp-accent);
  margin-bottom: 4px;
}

.kpi-sub {
  font-size: 0.82rem;
  color: var(--cp-text-soft);
}

.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.tab-btn {
  background: var(--cp-surface);
  color: var(--cp-text-muted);
  border: 1px solid var(--cp-border);
  border-radius: 0.625rem;
  padding: 10px 18px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
}

.tab-btn.active {
  background: var(--cp-accent);
  color: var(--cp-accent-fg);
  border-color: var(--cp-accent);
}

.filter-bar {
  background: var(--cp-surface);
  border: 1px solid var(--cp-border);
  border-radius: 16px;
  padding: 16px 20px;
  margin-bottom: 16px;
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: center;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.filter-group label {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--cp-text-muted);
}

.filter-group select, .filter-group input {
  background: var(--cp-bg-elevated);
  color: var(--cp-text);
  border: 1px solid var(--cp-border);
  border-radius: 0.625rem;
  padding: 8px 12px;
  font-size: 0.88rem;
  font-family: inherit;
}

.legend {
  margin-left: auto;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  font-size: 0.8rem;
  color: var(--cp-text-muted);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.badge-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.dot-accent { background: var(--cp-accent); }
.dot-success { background: var(--cp-success); }
.dot-warning { background: var(--cp-warning); }
.dot-link { background: var(--cp-link); }

.main-layout {
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 16px;
  align-items: start;
}

@media (max-width: 1100px) {
  .main-layout {
    grid-template-columns: 1fr;
  }
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(310px, 1fr));
  gap: 14px;
}

.month-card {
  background: var(--cp-surface);
  border: 1px solid var(--cp-border);
  border-radius: 16px;
  padding: 14px;
}

.month-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--cp-border);
}

.month-title {
  font-weight: 700;
  font-size: 1rem;
}

.month-count {
  font-size: 0.78rem;
  padding: 2px 8px;
  border-radius: 0.625rem;
  background: var(--cp-accent-soft);
  color: var(--cp-accent);
  font-weight: 600;
}

.weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
  font-size: 0.72rem;
  color: var(--cp-text-muted);
  font-weight: 600;
  margin-bottom: 6px;
}

.days-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.day-cell {
  min-height: 46px;
  border-radius: 8px;
  border: 1px solid transparent;
  padding: 4px 2px;
  text-align: center;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  font-size: 0.78rem;
  color: var(--cp-text-muted);
  background: var(--cp-surface-soft);
}

.day-cell.empty {
  background: transparent;
}

.day-cell.avail-ay-biz {
  background: var(--cp-accent);
  color: var(--cp-accent-fg);
  font-weight: 700;
  cursor: pointer;
  border-color: var(--cp-accent);
}

.day-cell.avail-ow-biz {
  background: var(--cp-highlight);
  color: var(--cp-accent);
  border-color: var(--cp-accent);
  font-weight: 700;
  cursor: pointer;
}

.day-cell.avail-prem {
  background: var(--cp-accent-soft);
  color: var(--cp-warning);
  border-color: var(--cp-warning);
  font-weight: 600;
  cursor: pointer;
}

.day-cell.avail-econ {
  background: var(--cp-bg-elevated);
  color: var(--cp-success);
  border-color: var(--cp-success);
  font-weight: 600;
  cursor: pointer;
}

.day-cell:hover:not(.empty) {
  border-color: var(--cp-border-strong);
}

.day-pts {
  font-size: 0.65rem;
  line-height: 1.1;
  margin-top: 2px;
  font-family: Consolas, "Courier New", monospace;
}

.side-panel {
  background: var(--cp-surface);
  border: 1px solid var(--cp-border);
  border-radius: 16px;
  padding: 20px;
  position: sticky;
  top: 20px;
}

.side-panel h3 {
  font-size: 1.05rem;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--cp-border);
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid var(--cp-border);
  font-size: 0.86rem;
}

.detail-label {
  color: var(--cp-text-muted);
}

.detail-val {
  font-weight: 600;
  text-align: right;
}

.callout {
  background: var(--cp-accent-soft);
  border-left: 4px solid var(--cp-accent);
  padding: 12px 14px;
  border-radius: 0.625rem;
  margin: 12px 0;
  font-size: 0.84rem;
}

.card-section {
  background: var(--cp-surface);
  border: 1px solid var(--cp-border);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 16px;
}

.card-section h2 {
  font-size: 1.15rem;
  margin-bottom: 12px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.86rem;
}

.data-table th, .data-table td {
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid var(--cp-border);
}

.data-table th {
  color: var(--cp-text-muted);
  font-weight: 600;
  background: var(--cp-surface-soft);
}

.pill {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 0.625rem;
  font-size: 0.76rem;
  font-weight: 600;
  background: var(--cp-accent-soft);
  color: var(--cp-accent);
}

.pill-success {
  background: var(--cp-surface-soft);
  color: var(--cp-success);
  border: 1px solid var(--cp-success);
}

.pill-warn {
  background: var(--cp-surface-soft);
  color: var(--cp-warning);
  border: 1px solid var(--cp-warning);
}

.hidden {
  display: none !important;
}
</style>
</head>
<body>
<div class="container">
  <header class="header">
    <div class="header-title">
      <h1>芬兰航空 (Finnair) & 寰宇一家 未来一年积分票/升舱位雷达</h1>
      <p>数据源：方案 A 双引擎实测（Alaska 寰宇一家 365 天日历接口 + Seats.aero 芬航 Plus 原生 Avios 库存） | 扫描基准：__GENERATED_AT__</p>
    </div>
    <div class="header-actions">
      <button class="btn" id="themeToggleBtn">切换深浅主题</button>
      <a class="btn btn-primary" href="https://www.finnair.com/en/book-flights-with-avios" target="_blank" rel="noopener">打开芬航 Avios 订票官网 ↗</a>
    </div>
  </header>

  <section class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-label">PVG ⇄ HEL 芬航直飞经济舱免票 (≥2人)</div>
      <div class="kpi-value">218 天</div>
      <div class="kpi-sub">去程 109 天 / 回程 109 天 (单程 30,000 Avios，逢周二/三/五/日几乎全放票)</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">PVG ⇄ HEL 芬航直飞商务/超经现成位</div>
      <div class="kpi-value">5 天 (U/P舱)</div>
      <div class="kpi-sub">商务直飞: 2027-03-11 (回)、2027-09-03 (去)；超经直飞: 12-10、12-31、01-11</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">PVG ⇄ CDG/HEL 伙伴联程商务舱 (≥2人)</div>
      <div class="kpi-value">12 天 (双人位)</div>
      <div class="kpi-sub">含 2027-01-18 去 + 01-26 回 (日航 JL 经东京双人商务往返) 及英航/马航巴黎双人票</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">日韩跳板 (ICN/TYO ⇄ HEL) 芬航直飞商务</div>
      <div class="kpi-value">单班最多 7 张!</div>
      <div class="kpi-sub">上海直飞被秒抢，但首尔/东京/普吉飞赫尔辛基大量放 2–7 张 62,500 Avios 商务舱</div>
    </div>
  </section>

  <nav class="tabs">
    <button class="tab-btn active" data-tab="tab-calendar">1. 全年 12 个月余票日历 (2026.11 – 2027.10)</button>
    <button class="tab-btn" data-tab="tab-sweetspots">2. 18万 Avios 双人往返最佳实战方案 (重要发现)</button>
    <button class="tab-btn" data-tab="tab-native">3. 芬航 Plus 原生库存明细表 (含精确余票数)</button>
    <button class="tab-btn" data-tab="tab-howto">4. 本地自动刷新脚本说明 (finnair_award_scanner.py)</button>
  </nav>

  <!-- TAB 1: CALENDAR -->
  <div id="tab-calendar" class="tab-pane">
    <div class="filter-bar">
      <div class="filter-group">
        <label for="routeSelect">航线选择 (Route)</label>
        <select id="routeSelect">
          <option value="PVG-HEL">上海 → 赫尔辛基 (PVG → HEL)</option>
          <option value="HEL-PVG">赫尔辛基 → 上海 (HEL → PVG)</option>
          <option value="PVG-CDG">上海 → 巴黎 (PVG → CDG 全程)</option>
          <option value="CDG-PVG">巴黎 → 上海 (CDG → PVG 全程)</option>
          <option value="HND-HEL">东京羽田 → 赫尔辛基 (HND → HEL 跳板)</option>
          <option value="HEL-HND">赫尔辛基 → 东京羽田 (HEL → HND 跳板)</option>
          <option value="HKG-HEL">香港 → 赫尔辛基 (HKG → HEL 跳板)</option>
          <option value="HEL-HKG">赫尔辛基 → 香港 (HEL → HKG 跳板)</option>
          <option value="SHA-HND">上海虹桥 → 东京羽田 (SHA → HND 日航直飞)</option>
          <option value="HND-SHA">东京羽田 → 上海虹桥 (HND → SHA 日航直飞)</option>
          <option value="PVG-NRT">上海浦东 → 东京成田 (PVG → NRT 日航直飞)</option>
          <option value="NRT-PVG">东京成田 → 上海浦东 (NRT → PVG 日航直飞)</option>
          <option value="PVG-HND">上海浦东 → 东京羽田 (PVG → HND 日航直飞)</option>
          <option value="HND-PVG">东京羽田 → 上海浦东 (HND → PVG 日航直飞)</option>
          <option value="HND-CDG">东京羽田 → 巴黎 (HND → CDG 日航直飞)</option>
          <option value="CDG-HND">巴黎 → 东京羽田 (CDG → HND 日航直飞)</option>
          <option value="NRT-CDG">东京成田 → 巴黎 (NRT → CDG 联程商务)</option>
          <option value="CDG-NRT">巴黎 → 东京成田 (CDG → NRT 联程商务)</option>
        </select>
      </div>
      <div class="filter-group">
        <label for="cabinSelect">目标舱位 (Cabin)</label>
        <select id="cabinSelect">
          <option value="ALL">智能全舱位视图 (优先高亮商务 > 超经 > 经济)</option>
          <option value="Business">仅看商务舱 (Business / 升舱 U 舱)</option>
          <option value="Premium">仅看超级经济舱 (Premium Economy)</option>
          <option value="Main">仅看经济舱 (Economy / 芬航直飞 X 舱)</option>
        </select>
      </div>
      <div class="filter-group">
        <label for="paxSelect">同行人数 (Passengers)</label>
        <select id="paxSelect">
          <option value="pax2">2 人同行 (仅显示余票 ≥ 2 张)</option>
          <option value="pax1">1 人或拆单 (显示余票 ≥ 1 张)</option>
        </select>
      </div>
      <div class="legend">
        <span class="legend-item"><span class="badge-dot dot-accent"></span>芬航直飞商务 (60k/62.5k)</span>
        <span class="legend-item"><span class="badge-dot dot-link"></span>寰宇一家联程商务 (75k-130k)</span>
        <span class="legend-item"><span class="badge-dot dot-warning"></span>超级经济舱 (43.5k-50k)</span>
        <span class="legend-item"><span class="badge-dot dot-success"></span>芬航直飞经济舱 (30k)</span>
      </div>
    </div>

    <div class="main-layout">
      <div id="calendarContainer" class="calendar-grid"></div>
      <aside class="side-panel" id="detailPanel">
        <h3>日期详情与 18万 Avios 算账</h3>
        <div id="detailContent">
          <div class="callout">
            点击左侧日历中任意带颜色的日期，即可查看当日执飞航班号、税费、以及用您的 <strong>180,000 Avios</strong> 直接兑换或升舱的精确消耗。
          </div>
          <div class="detail-row">
            <span class="detail-label">芬航 PVG⇄HEL 经济→商务升舱</span>
            <span class="detail-val">40,000 Avios / 人 / 单程</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">芬航 PVG⇄HEL 超经→商务升舱</span>
            <span class="detail-val">23,000 Avios / 人 / 单程</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">芬航 PVG⇄HEL 直飞商务免票</span>
            <span class="detail-val">62,500 Avios / 人 / 单程</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">芬航 PVG⇄HEL 直飞超经免票</span>
            <span class="detail-val">43,500 Avios / 人 / 单程</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">芬航 PVG⇄HEL 直飞经济免票</span>
            <span class="detail-val">30,000 Avios / 人 / 单程</span>
          </div>
        </div>
      </aside>
    </div>
  </div>

  <!-- TAB 2: SWEET SPOTS -->
  <div id="tab-sweetspots" class="tab-pane hidden">
    <div class="card-section">
      <h2>核心发现：为什么上海 (PVG) 芬航直飞商务舱全年几乎被秒空？怎么破局？</h2>
      <div class="callout">
        <strong>实测数据真相：</strong>扫描未来 365 天发现，芬航 <code>AY 88 / AY 87 (PVG ⇄ HEL)</code> 的经济舱奖励票极其充裕（全年 <strong>109 天以上有 ≥2 张</strong>），但<strong>直飞商务舱 (U舱)</strong> 在 T-360 天放出后几乎被抢光（目前仅 <code>2027-03-11</code> 回程和 <code>2027-09-03</code> 去程各剩 1 张，且 <code>2026-12-31</code>、<code>2026-12-10</code>、<code>2027-01-11</code> 有芬航直飞超级经济舱）。<br/>
        <strong>但好消息是：</strong>如果您有 <strong>180,000 Avios</strong> 且 2 人同行，以下 3 个实测有票的破局方案可以直接锁定商务舱！
      </div>
      <table class="data-table">
        <thead>
          <tr>
            <th>破局方案</th>
            <th>实测有票日期 (≥2人商务舱)</th>
            <th>执飞航司与航班</th>
            <th>180,000 Avios 怎么花</th>
            <th>推荐指数</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>方案 1：日韩/普吉跳板 + 芬航直飞 A350 商务舱</strong><br/>(芬航原生库存大户)</td>
            <td>
              <strong>首尔 ICN / 东京 HND·NRT / 大阪 KIX / 普吉 HKT ⇄ HEL</strong>：<br/>
              11月17日 (HKT→HEL <strong>6张</strong>, HEL→ICN <strong>4张</strong>)<br/>
              11月24日 (HEL→ICN <strong>2张</strong>)<br/>
              11月25日 (HKT→HEL <strong>2张</strong>, HEL→NRT <strong>7张!</strong>)<br/>
              11月30日 (HEL→HND <strong>7张!</strong>, HEL→NRT <strong>4张</strong>, HEL→ICN <strong>3张</strong>)<br/>
              12月03日 (HEL→HND <strong>3张</strong>)、12月10日 (HEL→HND <strong>6张!</strong>)
            </td>
            <td>芬兰航空 <code>AY</code> A350 AirLounge 直飞</td>
            <td>
              <strong>直接换免票</strong>：亚洲—赫尔辛基直飞商务舱仅需 <strong>62,500 Avios/人</strong>（2人单程 125,000 Avios）；或买首尔/东京出发的便宜经济舱用 <strong>40,000 Avios/人</strong> 秒升商务舱（去程/回程同日有 3–7 张现成 U 舱，2人 100% 当场确认！）
            </td>
            <td><span class="pill">强烈推荐 (最多7张现成商务舱)</span></td>
          </tr>
          <tr>
            <td><strong>方案 2：上海直出 · 日航 (JAL) / 英航 / 马航 2人全程商务舱</strong></td>
            <td>
              <strong>去程 (PVG出发 ≥2张商务)</strong>：<br/>
              <code>2027-01-18</code> (PVG→HND→HEL，日航 JL86+JL47)<br/>
              <code>2027-01-25</code>、<code>02-10</code>、<code>02-16</code>、<code>02-17</code>、<code>02-24</code> (PVG→CDG)<br/>
              <strong>回程 (回PVG ≥2张商务)</strong>：<br/>
              <code>2027-01-26</code> (HEL→HND→PVG，日航 JL48+JL89)<br/>
              <code>2026-11-26</code>、<code>12-02</code>、<code>12-03</code>、<code>2027-01-04</code>、<code>09-01</code> (CDG→PVG)
            </td>
            <td>日本航空 <code>JL</code> / 英国航空 <code>BA</code> / 马来西亚航空 <code>MH</code></td>
            <td>
              例如 <strong>2027-01-18 出发 + 2027-01-26 返回</strong>，完美 8 天欧洲行，去回程均有 ≥2 张日本航空 (JL) 商务舱免票，税费仅 $42.7 / $51.4！
            </td>
            <td><span class="pill-success pill">上海出发免折腾</span></td>
          </tr>
          <tr>
            <td><strong>方案 3：芬航 PVG ⇄ HEL 1人秒升 + 1人超经/经济免票</strong></td>
            <td>
              去程直飞商务 (1张)：<code>2027-09-03 (AY 88)</code><br/>
              回程直飞商务 (1张)：<code>2027-03-11 (AY 87)</code><br/>
              直飞超经 (1张)：<code>2026-12-10</code>、<code>2026-12-31</code>、<code>2027-01-11</code><br/>
              直飞经济 (≥2张)：全年 <strong>109 天</strong>
            </td>
            <td>芬兰航空 <code>AY 88 / AY 87</code> 直飞</td>
            <td>
              180,000 Avios 可直接换 <strong>2人往返全程经济舱免票 (30k×4 = 120,000 Avios)</strong> 剩余 60,000 Avios 留作升舱；或在 <code>2027-03-11</code> / <code>2027-09-03</code> 先锁 1 张直飞商务舱。
            </td>
            <td><span class="pill-warn pill">适合刚需直飞</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- TAB 3: NATIVE FINNAIR TABLE -->
  <div id="tab-native" class="tab-pane hidden">
    <div class="card-section">
      <h2>芬航 Plus 原生 Avios 库存表 (亚欧航线实测抓取，含精确余票张数)</h2>
      <div class="filter-bar">
        <div class="filter-group">
          <label for="nativeHubFilter">筛选城市/航线</label>
          <select id="nativeHubFilter">
            <option value="ALL_BIZ_PREM">全部有商务舱/超经余票的亚欧航班</option>
            <option value="PVG">仅看上海 (PVG 进出港全舱位)</option>
            <option value="AY_DIRECT_BIZ">仅看芬航直飞商务舱 (62,500 Avios, J ≥ 1)</option>
            <option value="AY_BIZ_2PLUS">仅看双人以上商务舱 (J ≥ 2 张)</option>
          </select>
        </div>
      </div>
      <table class="data-table">
        <thead>
          <tr>
            <th>日期</th>
            <th>航线</th>
            <th>商务舱余票 (Avios)</th>
            <th>超级经济舱余票 (Avios)</th>
            <th>经济舱余票 (Avios)</th>
            <th>执飞航司</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody id="nativeTableBody"></tbody>
      </table>
    </div>
  </div>

  <!-- TAB 4: HOW TO REFRESH -->
  <div id="tab-howto" class="tab-pane hidden">
    <div class="card-section">
      <h2>如何随时刷新最新余票数据？</h2>
      <p style="margin-bottom:12px;">我已在您的当前工作目录下生成了完整的双引擎采集脚本 <code>finnair_award_scanner.py</code> 与构建脚本 <code>build_radar_html.py</code>。无需任何付费 API Key，也无需登录您的芬航账号（零封号风险）。</p>
      <div class="callout">
        <strong>一键更新命令（PowerShell）：</strong><br/>
        <code class="mono">python finnair_award_scanner.py; python build_radar_html.py</code>
      </div>
      <table class="data-table">
        <thead>
          <tr>
            <th>组件文件</th>
            <th>作用说明</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="mono">finnair_award_scanner.py</td>
            <td>使用系统自带 Edge 无头浏览器并发扫描未来 12 个月（365天）寰宇一家日历接口 + Seats.aero 芬航原生库存，耗时约 60–85 秒。</td>
          </tr>
          <tr>
            <td class="mono">raw_award_scan.json</td>
            <td>保存全年 12 个月 <code>PVG⇄HEL</code>、<code>PVG⇄CDG</code>、<code>HND⇄HEL</code>、<code>HKG⇄HEL</code> 分舱位、分人数（1人/2人）原始余票 JSON。</td>
          </tr>
          <tr>
            <td class="mono">seats_aero_finnair_asia_eu.json</td>
            <td>保存芬航 Plus 原生 Avios 库存（包含精确剩余座位数 <code>js</code>/<code>ws</code>/<code>ys</code> 与所需 Avios）。</td>
          </tr>
          <tr>
            <td class="mono">finnair_award_radar.html</td>
            <td>当前自包含交互式看板 HTML 文件，双击即可在任意浏览器离线打开。</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</div>

<script>
const APP_DATA = __PAYLOAD_JSON__;

const WEEKDAYS = ["日", "一", "二", "三", "四", "五", "六"];

function getDaysInMonth(ym) {
  const [y, m] = ym.split("-").map(Number);
  return new Date(y, m, 0).getDate();
}

function getFirstDayOfWeek(ym) {
  const [y, m] = ym.split("-").map(Number);
  return new Date(y, m - 1, 1).getDay();
}

function formatPts(pts) {
  return (pts / 1000).toFixed(pts % 1000 === 0 ? 0 : 1) + "k";
}

function renderCalendars() {
  const route = document.getElementById("routeSelect").value;
  const cabinFilter = document.getElementById("cabinSelect").value;
  const pax = document.getElementById("paxSelect").value;
  const container = document.getElementById("calendarContainer");
  container.innerHTML = "";

  const bizList = APP_DATA.calendar[`${route}|Business|${pax}`] || [];
  const premList = APP_DATA.calendar[`${route}|Premium|${pax}`] || [];
  const mainList = APP_DATA.calendar[`${route}|Main|${pax}`] || [];

  const bizMap = Object.fromEntries(bizList.map(x => [x.date, x]));
  const premMap = Object.fromEntries(premList.map(x => [x.date, x]));
  const mainMap = Object.fromEntries(mainList.map(x => [x.date, x]));

  const [orig, dst] = route.split("-");
  const nativeMap = {};
  for (const r of APP_DATA.finnairNative) {
    if (r.oa === orig && r.da === dst) {
      nativeMap[r.dt] = r;
    }
  }

  for (const ym of APP_DATA.months) {
    const daysCount = getDaysInMonth(ym);
    const firstDow = getFirstDayOfWeek(ym);
    let monthMatches = 0;

    const card = document.createElement("div");
    card.className = "month-card";

    const cellsHtml = [];
    for (let i = 0; i < firstDow; i++) {
      cellsHtml.push(`<div class="day-cell empty"></div>`);
    }

    for (let d = 1; d <= daysCount; d++) {
      const dateStr = `${ym}-${String(d).padStart(2, "0")}`;
      const b = bizMap[dateStr];
      const p = premMap[dateStr];
      const m = mainMap[dateStr];
      const nat = nativeMap[dateStr];

      let cls = "day-cell";
      let badge = "";
      let chosenCabin = "";
      let chosenObj = null;

      const minSeats = pax === "pax2" ? 2 : 1;

      if (cabinFilter === "ALL" || cabinFilter === "Business") {
        if (b) {
          cls += b.points === 60000 ? " avail-ay-biz" : " avail-ow-biz";
          badge = formatPts(b.points);
          chosenCabin = "Business";
          chosenObj = b;
        } else if (nat && nat.js >= minSeats) {
          cls += nat.jm === 62500 ? " avail-ay-biz" : " avail-ow-biz";
          badge = `${nat.js}座·${formatPts(nat.jm)}`;
          chosenCabin = "Business (Finnair原生)";
          chosenObj = { date: dateStr, points: nat.jm, tax: 0, native: nat };
        }
      }

      if (!chosenObj && (cabinFilter === "ALL" || cabinFilter === "Premium")) {
        if (nat && nat.ws >= minSeats) {
          cls += " avail-prem";
          badge = `${nat.ws}座·${formatPts(nat.wm)}`;
          chosenCabin = "Premium (Finnair原生)";
          chosenObj = { date: dateStr, points: nat.wm, tax: 0, native: nat };
        } else if (p) {
          cls += " avail-prem";
          badge = formatPts(p.points);
          chosenCabin = "Premium";
          chosenObj = p;
        }
      }

      if (!chosenObj && (cabinFilter === "ALL" || cabinFilter === "Main")) {
        if (m) {
          cls += " avail-econ";
          badge = formatPts(m.points);
          chosenCabin = "Main";
          chosenObj = m;
        } else if (nat && nat.ys >= minSeats) {
          cls += " avail-econ";
          badge = `${nat.ys}座·${formatPts(nat.ym)}`;
          chosenCabin = "Economy (Finnair原生)";
          chosenObj = { date: dateStr, points: nat.ym, tax: 0, native: nat };
        }
      }

      if (chosenObj) {
        monthMatches++;
        const payloadAttr = encodeURIComponent(JSON.stringify({
          route, date: dateStr, cabin: chosenCabin, pax, data: chosenObj, native: nat || null
        }));
        cellsHtml.push(
          `<div class="${cls}" onclick="showDateDetail('${payloadAttr}')">
            <span>${d}</span>
            <span class="day-pts">${badge}</span>
          </div>`
        );
      } else {
        cellsHtml.push(`<div class="day-cell"><span>${d}</span></div>`);
      }
    }

    card.innerHTML = `
      <div class="month-header">
        <span class="month-title">${ym}</span>
        <span class="month-count">${monthMatches} 天有票</span>
      </div>
      <div class="weekdays">${WEEKDAYS.map(w => `<span>${w}</span>`).join("")}</div>
      <div class="days-grid">${cellsHtml.join("")}</div>
    `;
    container.appendChild(card);
  }
}

window.showDateDetail = function(encoded) {
  const info = JSON.parse(decodeURIComponent(encoded));
  const [orig, dst] = info.route.split("-");
  const fDetail = APP_DATA.flightDetails[`${info.route}|${info.date}`];
  const isAyDirect = info.data.points === 30000 || info.data.points === 60000 || info.data.points === 62500 || info.data.points === 43500;

  let flightText = isAyDirect
    ? (orig === "PVG" ? "AY 88 (芬兰航空 A350 直飞 PVG→HEL)" : orig === "HEL" && dst === "PVG" ? "AY 87 (芬兰航空 A350 直飞 HEL→PVG)" : "芬兰航空 (AY) 直飞")
    : "寰宇一家伙伴联程 (JL 日航 / BA 英航 / MH 马航)";

  if (fDetail && fDetail.ops && fDetail.ops.length > 0) {
    flightText = fDetail.ops.map(s => s.replace(/\\n+/g, " ")).join("<br/>");
  } else if (info.native) {
    flightText = `芬航原生库存 — 商务:${info.native.js}张(${info.native.jc || "-"}) | 超经:${info.native.ws}张(${info.native.wc || "-"}) | 经济:${info.native.ys}张(${info.native.yc || "-"})`;
  }

  const alaskaUrl = `https://www.alaskaair.com/search/results?O=${orig}&D=${dst}&OD=${info.date}&A=${info.pax === "pax2" ? 2 : 1}&RT=false&ShoppingMethod=onlineaward`;
  const finnairUrl = `https://www.finnair.com/en/book-flights-with-avios`;

  document.getElementById("detailContent").innerHTML = `
    <div class="detail-row">
      <span class="detail-label">选中日期</span>
      <span class="detail-val mono">${info.date}</span>
    </div>
    <div class="detail-row">
      <span class="detail-label">航线 / 人数</span>
      <span class="detail-val">${orig} → ${dst} (${info.pax === "pax2" ? "≥2人同行" : "≥1人"})</span>
    </div>
    <div class="detail-row">
      <span class="detail-label">命中舱位</span>
      <span class="detail-val">${info.cabin}</span>
    </div>
    <div class="detail-row">
      <span class="detail-label">里程 / 税费参考</span>
      <span class="detail-val mono">${info.data.points.toLocaleString()} pts ${info.data.tax ? "+ $" + info.data.tax : "(Finnair Avios)"}</span>
    </div>
    <div class="detail-row" style="flex-direction:column; gap:4px;">
      <span class="detail-label">执飞航班详情</span>
      <span class="detail-val" style="text-align:left; font-size:0.82rem;">${flightText}</span>
    </div>
    <div class="callout">
      <strong>180,000 Avios 升舱/兑换建议：</strong><br/>
      ${info.cabin.includes("Business") && isAyDirect
        ? "✅ 当日有<strong>芬航直飞商务舱 (U舱)</strong>！您可以立即买同航班 Economy Classic 现金票并用 <strong>40,000 Avios/人</strong> 当场秒升商务舱，或用 <strong>62,500 Avios/人</strong> 直接换商务舱免票！"
        : info.cabin.includes("Business")
        ? "✈️ 当日为寰宇一家伙伴（日航 JL / 英航 BA / 马航 MH）联程商务舱，可直接用里程兑换全额商务舱免票（无法用芬航 40k 升舱券升伙伴执飞航班）。"
        : info.cabin.includes("Premium")
        ? "✨ 当日有超级经济舱奖励/升舱位！可用 <strong>17,000 Avios/人</strong> 从经济舱升超经，或用 <strong>43,500 Avios/人</strong> 换芬航直飞超经免票。"
        : "💡 当日有芬航直飞经济舱奖励位（30,000 Avios/人），但商务舱 U 舱目前为 0，若买经济舱申请升舱将进入 Waitlist 候补。"}
    </div>
    <div style="display:flex; gap:8px; margin-top:12px; flex-wrap:wrap;">
      <a class="btn btn-primary" href="${alaskaUrl}" target="_blank" rel="noopener">查看当日航班明细 ↗</a>
      <a class="btn" href="${finnairUrl}" target="_blank" rel="noopener">前往芬航官网锁票 ↗</a>
    </div>
  `;
};

function renderNativeTable() {
  const mode = document.getElementById("nativeHubFilter").value;
  const tbody = document.getElementById("nativeTableBody");
  let rows = APP_DATA.finnairNative;

  if (mode === "PVG") {
    rows = rows.filter(r => r.oa === "PVG" || r.da === "PVG");
  } else if (mode === "AY_DIRECT_BIZ") {
    rows = rows.filter(r => r.js >= 1 && r.jm === 62500);
  } else if (mode === "AY_BIZ_2PLUS") {
    rows = rows.filter(r => r.js >= 2);
  } else {
    rows = rows.filter(r => r.js > 0 || r.ws > 0);
  }

  tbody.innerHTML = rows.map(r => `
    <tr>
      <td class="mono">${r.dt}</td>
      <td><strong>${r.oa} → ${r.da}</strong></td>
      <td>${r.js > 0 ? `<span class="pill">${r.js} 张 (${r.jm.toLocaleString()} Avios)</span>` : "-"}</td>
      <td>${r.ws > 0 ? `<span class="pill-warn pill">${r.ws} 张 (${r.wm.toLocaleString()} Avios)</span>` : "-"}</td>
      <td>${r.ys > 0 ? `<span class="pill-success pill">${r.ys} 张 (${r.ym.toLocaleString()} Avios)</span>` : "-"}</td>
      <td>${[r.jc, r.wc, r.yc].filter(Boolean)[0] || "AY"}</td>
      <td><a class="btn" style="padding:4px 10px; font-size:0.78rem;" href="https://www.finnair.com/en/book-flights-with-avios" target="_blank" rel="noopener">去芬航兑换 ↗</a></td>
    </tr>
  `).join("");
}

document.getElementById("routeSelect").addEventListener("change", renderCalendars);
document.getElementById("cabinSelect").addEventListener("change", renderCalendars);
document.getElementById("paxSelect").addEventListener("change", renderCalendars);
document.getElementById("nativeHubFilter").addEventListener("change", renderNativeTable);

document.querySelectorAll(".tab-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".tab-pane").forEach(p => p.classList.add("hidden"));
    btn.classList.add("active");
    document.getElementById(btn.getAttribute("data-tab")).classList.remove("hidden");
  });
});

document.getElementById("themeToggleBtn").addEventListener("click", () => {
  const cur = document.documentElement.getAttribute("data-theme");
  document.documentElement.setAttribute("data-theme", cur === "dark" ? "light" : "dark");
});

renderCalendars();
renderNativeTable();
</script>
</body>
</html>
"""

final_html = (
    html_template
    .replace("__GENERATED_AT__", payload["generatedAt"])
    .replace("__PAYLOAD_JSON__", json.dumps(payload, ensure_ascii=False))
)

out_path = (ROOT / "finnair_award_radar.html").resolve()
docs_out = (ROOT / "docs" / "index.html").resolve()
docs_out.parent.mkdir(parents=True, exist_ok=True)
docs_out.write_text(final_html, encoding="utf-8")
out_path.write_text(final_html, encoding="utf-8")

session_out = Path(r"C:\Users\yangrun\.copilot\session-state\c3bb2781-2229-410c-85bf-25b807544e88\files\finnair_award_radar.html")
session_out.parent.mkdir(parents=True, exist_ok=True)
session_out.write_text(final_html, encoding="utf-8")

print(f"Generated {out_path} ({len(final_html):,} bytes) and copied to session files.")


