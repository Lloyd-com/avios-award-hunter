---
name: avios-award-hunter
description: 查询与规划 Avios 体系（芬兰航空 Finnair、英国航空 BA、卡塔尔航空 Qatar、西班牙国家航空 Iberia、日本航空 JAL、国泰航空 CX 等寰宇一家航司）未来一年的积分票（Award Flights）与升舱位（U/P舱）余票。内置双引擎无风控扫描脚本（Alaska 寰宇一家 365 天按月日历接口 + Seats.aero 芬航 Plus 原生库存）与交互式 HTML 日历看板生成器。当用户询问 Avios 换票、芬航升舱、日航东京/欧洲里程票、查某月哪些天有积分票、Waitlist 成功率或汇丰 RC 转 Avios 算账时使用。触发词：Avios、芬航、Finnair、卡航、英航、日航、JAL、Iberia、积分票、里程票、升舱、U舱、PVG-HEL、SHA-HND、寰宇一家。
---

# Avios Award & Upgrade Hunter (`avios-award-hunter`)

本 Skill 提供 **Avios 生态（AY / BA / QR / IB / EI）与寰宇一家（oneworld）伙伴航司**的实时余票扫描、幽灵票过滤、升舱/免票算账及全年日历看板生成能力，同时兼容**本机 Windows 会话**与 **GitHub Cloud Session / 手机 GitHub App**。

---

## 1. 核心查票工具与命令

脚本位于本 Skill 目录下的 `scripts/` 文件夹（本机路径：`C:\Users\yangrun\.copilot\skills\avios-award-hunter\scripts\`；云端仓库相对路径：`scripts/`）。

### 1.1 按需扫描指定航线与月份（推荐日常问答调用）

```powershell
python "C:\Users\yangrun\.copilot\skills\avios-award-hunter\scripts\scan_oneworld_avios.py" `
  --routes "SHA-HND,HND-SHA,PVG-HEL,HEL-PVG" `
  --months "2027-03,2027-04,2027-05" `
  --pax 2 `
  --cabins "Business,Main"
```

- **云端 Linux / GitHub Sandbox 环境运行**：
  ```bash
  python scripts/scan_oneworld_avios.py --routes "PVG-HEL,HEL-PVG" --months "2027-04" --pax 2 --cabins "Business,Premium,Main"
  ```
- **单日航班号与反幽灵票核验（`--verify`）**：
  ```bash
  python scripts/scan_oneworld_avios.py --verify "SHA-HND:2027-04-12:2"
  ```

### 1.2 重新生成全年 12 个月交互式 HTML 看板

```powershell
python "C:\Users\yangrun\.copilot\skills\avios-award-hunter\scripts\build_radar_html.py"
```
生成文件：
- `finnair_award_radar.html`（本机双击即开）
- `docs/index.html`（自动同步至 GitHub Pages，供手机端随时浏览）

---

## 2. 寰宇一家日历接口识别码与“反幽灵票”铁律（必读）

通过 Alaska Airlines 寰宇一家按月日历接口（`/search/calendar`）抓取的数据，**必须按以下规则过滤真直飞与幽灵票（Phantom Availability）**：

| 航线区间 | 真实直飞识别特征 (`awardPoints` + `tax`) | 幽灵票 / 转机票特征（需过滤或单独说明） | 对应 Avios 兑换/升舱标准 |
| :--- | :--- | :--- | :--- |
| **上海 ⇄ 赫尔辛基**<br>(`PVG ⇄ HEL`) | • **芬航直飞经济 (`AY 88/87`)**：`30,000 pts` + `$33.5` (去) / `$42.2` (回)<br>• **芬航直飞超经 (`AY 88/87`)**：`40,000 pts` (或芬航原生 `43,500 Avios`)<br>• **芬航直飞商务 (`AY 88/87`)**：`60,000 pts` + `$33.5` / `$42.2` (芬航原生 `62,500 Avios`) | • `37,500 pts` (经济) / `50,000 pts` (超经) / `75,000 pts` (商务) + `$42.7`/`$51.4`：实为 **日本航空 (`JL`) 经东京羽田 (`HND`) 转机**，真实可出票但非芬航直飞（不可用芬航升舱券）。 | • **芬航直飞免票**：经济 `30,000` / 超经 `43,500` / 商务 `62,500` Avios<br>• **芬航现金票升商务**：经济→商务 **`40,000 Avios`**；超经→商务 **`23,000 Avios`** |
| **上海 ⇄ 东京**<br>(`SHA/PVG ⇄ HND/NRT`) | • **日航直飞经济 (`JL 82/81/80/86/876`)**：**`15,000 pts`** + `$33.5` (去) / `$57.3` (回)<br>• **日航直飞商务 (`JL`)**：**`32,500 pts`** + `$33.5` (去) / `$57.3` (回) | ❌ **`7,500 pts` (经济) 与 `50,000 pts` (商务)**：在日历页显示有价，但点进单日详情页提示 `No results available`，属于**幽灵票/断头票，严禁向用户报告为有票**！ | • 在 **英航 (BA)** 或 **卡航 (QR)** 官网兑换：<br>• **经济舱**：**`10,000–11,000 Avios`**（送 2件×23kg 行李）<br>• **商务舱**：**`20,000–22,000 Avios`**（送 3件×32kg 行李） |
| **东京羽田 ⇄ 巴黎**<br>(`HND ⇄ CDG`) | • **日航直飞 (`JL 45/46`, A350-1000)**：商务舱 **`75,000 pts`** + `$57.3`，超经 **`50,000 pts`** | • `130,000 pts`：多为马航 (`MH`) 经吉隆坡、国泰 (`CX`) 经香港或芬航混舱联程。 | • **破局技巧**：若 `HND-CDG` 无票，分段单搜 **`HND/NRT ⇄ HEL`**（芬航常放单班 3–7 张 62,500 Avios 直飞商务舱），再单买 `HEL-CDG` 经济舱。 |
| **巴黎 ⇄ 马德里/西班牙**<br>(`ORY/CDG ⇄ MAD/SVQ/GRX`) | • **Iberia 直飞 (`ORY ⇄ MAD`, 643 mi)**：落入英航 **Zone 1 (≤650 mi)**<br>• **Iberia 直飞 (`CDG ⇄ MAD`, 661 mi)**：跨入英航 **Zone 2 (651–1,151 mi)** | • 伏林航空 (`Vueling VY`) 直飞塞维利亚/格拉纳达属于按票价动态抵扣，非固定表格。 | • **`ORY ⇄ MAD`**：经济舱 **`5,000–5,250 Avios`** / 商务 **`9,250–10,000 Avios`**（含 23kg 行李）<br>• **`ORY → MAD → SVQ/GRX` 联程**：约 **`10,000–10,500 Avios`** |

---

## 3. 芬兰航空 (Finnair) 升舱与候补 (Waitlist) 关键规则

1. **舱位结构**：芬航全机队（A350/A330）仅设 **商务舱 (Business) + 超级经济舱 (Premium Economy) + 经济舱 (Economy)**，**无头等舱**。
2. **行李陷阱（2025年6月4日起新规）**：积分升舱后**托运行李额仍按原购现金票规则执行**！购买 `Economy Light`（无托运行李票）即使升上商务舱也只有 0 件免费托运行李，因此现金购票请务必买 **`Economy Classic`**。
3. **Waitlist 候补机制**：
   - **双人绑死（All-or-Nothing）**：同一订单（PNR）下的 2 人必须等到系统**同时释放 ≥2 个 U 舱座位**才会一起确认；若只放 1 个座位，系统会跳过该双人订单给后面的单人旅客。
   - **会员等级插队**：按 `Lumo > Platinum > Gold > Silver > Basic` 排序。
     - **若用户为 Basic 白板**：建议分拆为 2 个独立订单（Split PNR）分别排单人候补。
     - **若用户已升为 Silver 银卡**：2 人务必放在**同一订单（同一 PNR）**，以便同行人共享银卡优先级，压过全机所有白板散客。
   - **定级分（Tier Points）补齐规则**：银卡门槛为 `15,000 定级分`；可用 Avios 按 **`3 Avios = 1 定级分`** 兑换（每年上限兑换 `7,500 定级分` = `22,500 Avios`，在线手续费 €10，实时生效）。

---

## 4. Avios 跨航司互转与汇丰香港 (HSBC HK) 转点路径

- **Avios 内部 1:1 免费实时互转**：**芬兰航空 (AY) ⇄ 英国航空 (BA) ⇄ 卡塔尔航空 (QR) ⇄ 西班牙国家航空 (IB) ⇄ 爱尔兰航空 (EI)**（账户姓名、邮箱、生日需一致）。
- **不能转入阿拉斯加航空 (AS)**：阿拉斯加仅作为免登录日历查票探针，查到票后回 **芬航官网（换/升 AY 自家航班）** 或 **英航/卡航官网（换 JL/CX/IB/BA/QR 航班）** 出票。
- **汇丰香港 RewardCash (RC) 转点**：
  - **卓越理财 Mastercard (`1 RC = 15 Avios`)**：仅支持转入 **英国航空 (BA)**，带 `*` 批处理通常需 **2–5 个工作日**（官方写最多 2 周），到账 BA 后可 1 秒转入芬航或卡航。
  - **EveryMile 卡 (`1 RC = 20 Avios`)**：支持直转芬航 Plus / 卡航（实时到账）或英航。
