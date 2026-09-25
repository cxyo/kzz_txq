# -*- coding: utf-8 -*-
"""可转债数据抓取与筛选模块（迁移自华为云函数 ths.py）

数据源：同花顺 http://data.hexin.cn/ipo/bond/cate/info/
筛选逻辑：
  - 今日申购（sgDate == today） -> 打新列表
  - 今日上市（ssDay  == today） -> 上市列表
"""

import requests

URL = "http://data.hexin.cn/ipo/bond/cate/info/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}


def fetch_data(timeout=15):
    """抓取原始数据，失败返回 None"""
    response = requests.get(URL, headers=HEADERS, timeout=timeout)
    response.raise_for_status()
    return response.json()


def process_data(data):
    """补充交易所字段并计算转股估值"""
    for item in data:
        # 深市可转债代码以 12 开头（123/127/128），其余（110/111/113/118）为沪市
        item["stock"] = "深市" if str(item["zqCode"]).startswith("12") else "沪市"
        # 转股估值 = 正股价/转股价*100*(1+溢价率调整)，保留两位小数
        item["guzhi"] = round(
            float(item["stockPrice"]) / float(item["bondPrice"]) * 100
            * (1 + float(item["disRate"]) * 0.01),
            2,
        )
    return data


def filter_data(data):
    """按今日申购/今日上市分类，返回 (申购列表, 上市列表)"""
    xzdata, ssdata = [], []
    for item in data:
        record = {
            "code": item["zqCode"],
            "name": item["zqName"],
            "stock": item["stock"],
            "guzhi": item["guzhi"],
        }
        if item.get("today") == item.get("sgDate"):
            xzdata.append(record)
        elif item.get("today") == item.get("ssDay"):
            ssdata.append(record)
    return xzdata, ssdata


def get_today_bonds():
    """主入口：返回 (申购列表, 上市列表)；抓取失败抛出异常"""
    data = fetch_data()
    if not data:
        raise RuntimeError("数据源返回为空")
    return filter_data(process_data(data))
