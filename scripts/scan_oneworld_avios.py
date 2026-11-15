#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parameterized Oneworld & Finnair Avios Award/Upgrade Scanner
============================================================
Supports both Windows (Edge/Chrome) and Linux/Cloud (Headless Chromium).

Examples:
  # Scan specific routes and months for 2 passengers:
  python scripts/scan_oneworld_avios.py --routes SHA-HND,HND-SHA --months 2027-03,2027-04 --pax 2

  # Full 12-month default scan + Finnair native T-60 inventory:
  python scripts/scan_oneworld_avios.py --full

  # Verify a specific date's exact flight numbers and filter phantom space:
  python scripts/scan_oneworld_avios.py --verify SHA-HND:2027-03-03:2
"""

import argparse
import asyncio
import datetime
import json
import platform
import re
import sys
import time
from pathlib import Path
from playwright.async_api import async_playwright

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_next_12_months() -> list[str]:
    today = datetime.date.today()
    months = []
    y, m = today.year, today.month
    for _ in range(12):
        months.append(f"{y:04d}-{m:02d}")
        m += 1
        if m > 12:
            m = 1
            y += 1
    return months


async def launch_browser(p):
    if platform.system().lower() == "windows":
        for ch in ("chrome", "msedge"):
            try:
                return await p.chromium.launch(channel=ch, headless=True)
            except Exception:
                pass
    return await p.chromium.launch(headless=True)


def filter_phantom_entries(origin: str, dest: str, cabin: str, items: list[dict]) -> list[dict]:
    """Filter out known Alaska calendar phantom prices on SHA/PVG <-> HND/NRT."""
    sh_tyo = {("SHA", "HND"), ("HND", "SHA"), ("PVG", "HND"), ("HND", "PVG"), ("PVG", "NRT"), ("NRT", "PVG")}
    if (origin, dest) in sh_tyo:
        if cabin == "Business":
            return [x for x in items if x["points"] == 32500]
        if cabin == "Main":
            return [x for x in items if x["points"] == 15000]
    return items


async def fetch_alaska_month(context, sem, origin: str, dest: str, month: str, pax: int, cabin: str):
    today_ym = datetime.date.today().strftime("%Y-%m")
    od = f"{month}-20" if month == today_ym else f"{month}-15"
    url = (
        f"https://www.alaskaair.com/search/calendar?"
        f"O={origin}&D={dest}&OD={od}&A={pax}&RT=false"
        f"&RequestType=Calendar&ShoppingMethod=onlineaward&CM={month}&FareType={cabin}"
    )
    async with sem:
        for _ in range(3):
            try:
                resp = await context.request.get(
                    url,
                    headers={"Accept": "text/html,application/xhtml+xml"},
                    timeout=25000,
                )
                if resp.status == 200:
                    txt = await resp.text()
                    matches = re.findall(
                        r'\{date:"([^"]+)",price:([^,]+),awardPoints:([^,]+)', txt
                    )
                    avail = [
                        {"date": d, "tax": float(p), "points": int(pts)}
                        for d, p, pts in matches
                        if pts != "null" and p != "null"
                    ]
                    avail = filter_phantom_entries(origin, dest, cabin, avail)
                    return (origin, dest, month, pax, cabin, avail)
            except Exception:
                pass
            await asyncio.sleep(0.7)
    return (origin, dest, month, pax, cabin, [])


async def verify_single_date(context, origin: str, dest: str, date_str: str, pax: int):
    page = await context.new_page()
    url = f"https://www.alaskaair.com/search/results?O={origin}&D={dest}&OD={date_str}&A={pax}&RT=false&ShoppingMethod=onlineaward"
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=25000)
        await page.wait_for_timeout(3200)
        txt = await page.inner_text("body")
        ops = [o.strip().replace("\n", " ") for o in re.findall(r'([A-Z0-9,\s]+—\s*Operated by[^\n]+)', txt)]
        no_res = "No results available" in txt
        print(f"=== Verify {origin} -> {dest} on {date_str} (pax={pax}) ===")
        if no_res or not ops:
            print("  Result: NO FLIGHTS / PHANTOM AVAILABILITY")
        else:
            for o in ops:
                print(f"  Flight: {o}")
    finally:
        await page.close()


async def fetch_finnair_native_60d(context) -> list[dict]:
    page = await context.new_page()
    all_rows = []
    try:
        await page.goto("https://seats.aero/finnair", wait_until="domcontentloaded", timeout=25000)
        await page.wait_for_timeout(2000)
        for orig_reg, dst_reg in [("Asia", "Europe"), ("Europe", "Asia")]:
            start = 0
            while True:
                url = (
                    f"/_api/availability_table_modern_ss?"
                    f"origin_region={orig_reg}&destination_region={dst_reg}"
                    f"&source=finnair&length=100&start={start}"
                )
                res = await page.evaluate(f"fetch({json.dumps(url)}).then(r => r.json())")
                data = res.get("data", [])
                if not data:
                    break
                all_rows.extend(data)
                start += len(data)
                if start >= res.get("recordsFiltered", 0) or start >= 1000:
                    break
    finally:
        await page.close()
    return all_rows


async def main():
    parser = argparse.ArgumentParser(description="Avios & Oneworld Award Scanner")
    parser.add_argument("--routes", type=str, default="PVG-HEL,HEL-PVG,SHA-HND,HND-SHA", help="Comma-separated routes e.g. PVG-HEL,SHA-HND")
    parser.add_argument("--months", type=str, default="", help="Comma-separated YYYY-MM, default next 12 months")
    parser.add_argument("--pax", type=str, default="2", help="Comma-separated passenger counts e.g. 1,2")
    parser.add_argument("--cabins", type=str, default="Business,Main", help="Comma-separated cabins: Business,Premium,Main")
    parser.add_argument("--verify", type=str, default="", help="Verify single date format ORIG-DEST:YYYY-MM-DD:PAX")
    parser.add_argument("--full", action="store_true", help="Run full multi-route 12-month scan and update data/ files")
    args = parser.parse_args()

    t0 = time.time()
    async with async_playwright() as p:
        browser = await launch_browser(p)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
            )
        )

        if args.verify:
            parts = args.verify.split(":")
            orig, dst = parts[0].split("-")
            dt = parts[1]
            px = int(parts[2]) if len(parts) > 2 else 2
            await verify_single_date(context, orig, dst, dt, px)
            await browser.close()
            return

        months = [m.strip() for m in args.months.split(",") if m.strip()] or get_next_12_months()
        pax_list = [int(x.strip()) for x in args.pax.split(",") if x.strip()]
        cabins = [c.strip() for c in args.cabins.split(",") if c.strip()]
        routes = [tuple(r.strip().split("-")) for r in args.routes.split(",") if "-" in r]

        if args.full:
            months = get_next_12_months()
            pax_list = [1, 2]
            routes = [
                ("PVG", "HEL"), ("HEL", "PVG"),
                ("PVG", "CDG"), ("CDG", "PVG"),
                ("HND", "HEL"), ("HEL", "HND"),
                ("HKG", "HEL"), ("HEL", "HKG"),
                ("SHA", "HND"), ("HND", "SHA"),
                ("PVG", "NRT"), ("NRT", "PVG"),
                ("PVG", "HND"), ("HND", "PVG"),
                ("HND", "CDG"), ("CDG", "HND"),
                ("NRT", "CDG"), ("CDG", "NRT"),
            ]
            cabins = ["Business", "Premium", "Main"]

        sem = asyncio.Semaphore(8)
        tasks = []
        for orig, dst in routes:
            for cab in cabins:
                if cab == "Premium" and (orig, dst) not in {("PVG", "HEL"), ("HEL", "PVG")}:
                    continue
                for px in pax_list:
                    for m in months:
                        tasks.append(fetch_alaska_month(context, sem, orig, dst, m, px, cab))

        print(f"[*] Scanning {len(tasks)} monthly calendars across {len(routes)} routes...")
        results = await asyncio.gather(*tasks)

        scan_file = DATA_DIR / "raw_award_scan.json"
        existing = {}
        if scan_file.exists():
            try:
                existing = json.loads(scan_file.read_text(encoding="utf-8"))
            except Exception:
                existing = {}

        current = {}
        for orig, dst, m, px, cab, avail in results:
            key = f"{orig}-{dst}|{cab}|pax{px}"
            current.setdefault(key, []).extend(avail)

        # Merge into existing dataset
        for k, v in current.items():
            old_map = {item["date"]: item for item in existing.get(k, []) if item["date"][:7] not in set(months)}
            for item in v:
                old_map[item["date"]] = item
            existing[k] = [old_map[d] for d in sorted(old_map.keys())]

        scan_file.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[+] Completed in {time.time()-t0:.1f}s. Updated {scan_file}")

        for k, v in sorted(current.items()):
            dates_str = ", ".join(f"{x['date']}({x['points']//1000}k)" for x in v[:15])
            more = f" ... (+{len(v)-15} more)" if len(v) > 15 else ""
            print(f"  {k:26s}: {len(v):3d} days | {dates_str}{more}")

        if args.full:
            print("[*] Fetching Finnair Plus native T-60 inventory from Seats.aero...")
            sa_rows = await fetch_finnair_native_60d(context)
            sa_file = DATA_DIR / "seats_aero_finnair_asia_eu.json"
            sa_file.write_text(json.dumps(sa_rows, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"[+] Saved {len(sa_rows)} Finnair Plus native records to {sa_file}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())

