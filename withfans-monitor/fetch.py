import json
import os
from datetime import datetime, timezone, timedelta
import requests


API_URL = "https://www.withfans.com/aidouapi/appProduct/details"  # 填入真实 Request URL
PAYLOAD = {
    "securityProductId": "37A98AA2F7644BF3",
    "P": "web_pop",
    "V": "4.2.15",
    "sv": "2",
    "clientDevice": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36 Edg/157.0.0.0",
    "FKEY": "d0e37ae3-2eaa-4b8a-9517-8bfb08fedaea",
    "signTime": "1794461662201",
    "usKey": "B3D7295A1D2F03C3FC2B7C18C30C8D24447DAC180F544F426D93AC16A1D7A6D4",
    "sign": "a019e5a1e33b1a0b9de17a5d65acbc10"
}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.withfans.com/"
}

DATA_FILE = "data.json"
BJT = timezone(timedelta(hours=8))


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        store = json.load(f)

    now_str = datetime.now(BJT).strftime("%Y-%m-%d %H:%M:%S")

    try:
        resp = requests.post(API_URL, headers=HEADERS, data=PAYLOAD, timeout=15)
        res_json = resp.json()
        datas = res_json.get("datas", {})

        current_total = int(datas.get("collection_count", 0))
        if current_total <= 0:
            print("未获取到有效收藏数，跳过本次写入")
            return

        # 更新元数据
        if datas.get("shop_name"):
            store["meta"]["title"] = datas["shop_name"]
        if datas.get("start_time"):
            store["meta"]["start_time"] = datas["start_time"]
        if datas.get("end_time"):
            store["meta"]["end_time"] = datas["end_time"]
        store["meta"]["last_updated"] = datas.get("current_time", now_str)

        # 计算与上一条记录的增量
        records = store.get("records", [])
        last_total = records[-1]["total"] if records else 0
        delta = current_total - last_total

        if delta != 0:
            records.append({
                "time": store["meta"]["last_updated"],
                "total": current_total,
                "delta": delta
            })
            store["records"] = records
            print(f"[{now_str}] 检测到变动: {last_total} -> {current_total} (增量 {delta:+d})")
        else:
            print(f"[{now_str}] 收藏量无变化，维持 {current_total}")

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(store, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"[{now_str}] 请求失败: {e}")


if __name__ == "__main__":
    main()
