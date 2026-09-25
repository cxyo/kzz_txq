# 可转债提醒器（kzz_txq）

> 每天早上 **9 点** 通过 pushplus 推送微信消息：今天有无可**申购（打新）**和**上市**的可转债。
> 数据来源：同花顺 `http://data.hexin.cn/ipo/bond/cate/info/`，跑在 GitHub Actions 上，零本地运维。

## 功能特性

- ⏰ 每天**北京时间 09:00**（UTC 01:00）自动推送，电脑无需开机
- 🆕 提醒当日**新债申购**（打新）：名称、代码、交易所、转股估值
- 📈 提醒当日**新债上市**：同上
- 📵 无新债也会推送「今日无新债」，保持每日打卡式通知节奏
- 👥 支持多个接收人：`PUSHPLUS_TOKEN` Secret 中用英文逗号分隔多个 token
- 📱 消息模板为 HTML，红色高亮新债名称

## 使用方法

1. Fork 或使用本仓库；
2. 添加 Secret：仓库 **Settings → Secrets and variables → Actions → New repository secret**
   - Name：`PUSHPLUS_TOKEN`
   - Value：你的 [pushplus](https://www.pushplus.plus/) token（微信扫码登录即可获取；多个接收人用英文逗号分隔，每人用自己微信注册各自的 pushplus 账号）
   - ⚠️ pushplus 需完成**实名认证**（https://verify.pushplus.plus ）才能发消息
3. 工作流 `kzz-daily-notify` 默认按计划运行；也可到 Actions 页面手动 **Run workflow** 测试；
4. 微信接收推送。

## 消息示例

```
【可转债提醒器】申购/上市提醒
📅 2026-09-25
🆕 今日新债申购（1 只）
🔸 神码转债（127xxx） 深市 ｜ 转股估值 92.35
────────────────
📈 今日无新债上市
```

## 项目结构

```
kzz_txq/
├── .github/workflows/
│   └── kzz-daily-notify.yml   # GitHub Actions 定时工作流
├── main.py                    # 组装消息 + pushplus 推送
├── ths.py                     # 同花顺数据抓取与筛选
├── requirements.txt
└── README.md
```

## 本地运行

```bash
pip install -r requirements.txt
export PUSHPLUS_TOKEN=你的token
python main.py
```

## 常见问题

- **推送报 code 905**：pushplus 未实名认证，去 https://verify.pushplus.plus 完成。
- **想改推送时间**：编辑 `.github/workflows/kzz-daily-notify.yml` 的 cron（GitHub 用 UTC，北京时间 = UTC + 8；9 点对应 `0 1 * * *`）。
- **某天没收到**：查仓库 Actions 运行记录；GitHub 定时任务在高峰期可能延迟几十分钟。
- **换微信号接收**：新微信扫码注册 pushplus 拿新 token，加进 Secret（逗号分隔）即可。
