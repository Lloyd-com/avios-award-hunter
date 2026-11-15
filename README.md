# Avios 积分票与升舱位全年雷达 (`avios-award-hunter`)

专为 **Avios 体系（芬兰航空 Finnair、英国航空 BA、卡塔尔航空 Qatar、西班牙国家航空 Iberia、日本航空 JAL）** 打造的跨设备 **Copilot Skill + 未来一年（365天）余票日历看板**。

---

## 🌐 在线交互式日历看板（手机 / 电脑浏览器直接打开）

- **GitHub Pages 在线看板**：[https://lloyd-com.github.io/avios-award-hunter/](https://lloyd-com.github.io/avios-award-hunter/)
- **本地离线文件**：双击仓库根目录下的 `finnair_award_radar.html` 即可打开。

---

## 📱 如何在手机（GitHub Mobile App）或其他设备的 Copilot App 中使用？

### 方式 1：在任何设备的 GitHub Copilot App / 手机 App 中直接对话查票
1. 打开 **GitHub Copilot App**（桌面端）或 **GitHub Mobile App**（手机端）；
2. 选择本仓库 `Lloyd-com/avios-award-hunter` 开启一个会话（本地或 Cloud Session）；
3. 直接用自然语言提问（Copilot 会自动加载 `.github/skills/avios-award-hunter/SKILL.md` 规则库与查票脚本）：
   - *“帮我查下 2027 年 4 月上海虹桥飞东京羽田（SHA-HND）2 个人有哪些天有日航商务舱？”*
   - *“刷一下明年 4 月 PVG-HEL 芬航有没有新放出的商务舱 U 舱？”*
   - *“我有 16 万 Avios，帮我算下巴黎去塞维利亚怎么换最划算？”*

### 方式 2：在手机 GitHub App 一键触发云端刷新 (`Actions -> Update Avios Award Radar`)
1. 在手机 **GitHub App** 进入本仓库 → 点击 **`Actions`** → 选择 **`Update Avios Award Radar`**；
2. 点击右上角 **`Run workflow`**，可自定义输入想查的航线（如 `SHA-HND,HND-SHA`）和月份（如 `2027-04,2027-05`）；
3. 云端自动运行完后，点开 [https://lloyd-com.github.io/avios-award-hunter/](https://lloyd-com.github.io/avios-award-hunter/) 即可查看最新日历热力图。

---

## 💻 在另一台电脑上同步为全局本地 Skill

```bash
git clone https://github.com/Lloyd-com/avios-award-hunter.git ~/.copilot/skills/avios-award-hunter
```
