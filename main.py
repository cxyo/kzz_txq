# -*- coding: utf-8 -*-
"""可转债提醒器主程序（迁移自华为云函数 index.py）

每天运行一次：
  1. 从同花顺数据源获取当天「新债申购 / 新债上市」数据
  2. 组装 HTML 消息
  3. 通过 pushplus 推送到微信（支持多个 token，英文逗号分隔）

环境变量：
  PUSHPLUS_TOKEN  pushplus 的 token，必填；多个接收人用英文逗号分隔
"""

import os
import sys
from datetime import datetime

import requests

import ths

PUSHPLUS_API = "https://www.pushplus.plus/send"

# 与原版保持一致的标题风格
TITLE = "【可转债提醒器】"


def build_message(xzdata, ssdata, today):
    """组装 HTML 消息正文"""
    lines = [f"📅 {today}"]

    # ------ 新债数据（申购） ------
    if xzdata:
        lines.append(f"<h4>🆕 今日新债申购（{len(xzdata)} 只）</h4>")
        for b in xzdata:
            lines.append(
                f"<font color='red'>🔸 {b['name']}（{b['code']}）</font> "
                f"{b['stock']} ｜ 转股估值 <b>{b['guzhi']}</b>"
            )
    else:
        lines.append("🆕 今日<strong>无</strong>新债申购")

    lines.append("─" * 16)

    # ------ 上市数据 ------
    if ssdata:
        lines.append(f"<h4>📈 今日新债上市（{len(ssdata)} 只）</h4>")
        for b in ssdata:
            lines.append(
                f"<font color='red'>🔸 {b['name']}（{b['code']}）</font> "
                f"{b['stock']} ｜ 转股估值 <b>{b['guzhi']}</b>"
            )
    else:
        lines.append("📈 今日无新债上市")

    lines.append("")
    lines.append("<small>数据来源：同花顺 ｜ 由 GitHub Actions 每日 09:00 自动推送</small>")
    return "<br/>".join(lines)


def send_pushplus(token, title, content, timeout=15):
    """调用 pushplus 推送接口，返回是否成功"""
    payload = {
        "token": token.strip(),
        "title": title,
        "content": content,
        "template": "html",
    }
    response = requests.post(PUSHPLUS_API, json=payload, timeout=timeout)
    response.raise_for_status()
    result = response.json()
    if result.get("code") != 200:
        raise RuntimeError(f"pushplus 返回异常: {result}")
    return True


def main():
    tokens = [t for t in os.environ.get("PUSHPLUS_TOKEN", "").split(",") if t.strip()]
    if not tokens:
        print("错误：未配置 PUSHPLUS_TOKEN 环境变量")
        return 1

    # 1. 抓取并筛选数据
    try:
        xzdata, ssdata = ths.get_today_bonds()
    except Exception as e:
        print(f"抓取数据失败: {e}")
        return 1

    today = datetime.now().strftime("%Y-%m-%d")
    content = build_message(xzdata, ssdata, today)
    title = TITLE
    if xzdata or ssdata:
        title += f"{'申购' if xzdata else ''}{'/' if xzdata and ssdata else ''}{'上市' if ssdata else ''}提醒"
    else:
        title += "今日无新债"

    print(f"今日申购 {len(xzdata)} 只，上市 {len(ssdata)} 只，推送 {len(tokens)} 个接收人")

    # 2. 逐个 token 推送
    failed = 0
    for token in tokens:
        try:
            send_pushplus(token, title, content)
            print(f"推送成功：token {token[:6]}****")
        except Exception as e:
            failed += 1
            print(f"推送失败（token {token[:6]}****）: {e}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
