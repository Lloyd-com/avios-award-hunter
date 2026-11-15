#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Chrome Persistent Login & T-360 Direct Award Checker (Finnair & Qatar)
=============================================================================
Uses your local Google Chrome (channel="chrome") with a persistent profile directory
(`data/chrome_profile`, excluded from Git) so you only need to log in once.

Usage:
  1. First-time login (opens real Chrome window for you to sign in):
     python scripts/chrome_360d_login_and_check.py --site qatar --login
     python scripts/chrome_360d_login_and_check.py --site finnair --login

  2. Check T-360 / specific date award availability using saved Chrome profile:
     python scripts/chrome_360d_login_and_check.py --site qatar --origin PVG --dest CDG --date 2027-11-10 --pax 2
     python scripts/chrome_360d_login_and_check.py --site finnair --origin PVG --dest HEL --date 2027-11-10 --pax 2
"""

import argparse
import asyncio
import datetime
from pathlib import Path
from playwright.async_api import async_playwright

ROOT_DIR = Path(__file__).resolve().parent.parent
PROFILE_DIR = ROOT_DIR / "data" / "chrome_profile"
STATE_FILE = ROOT_DIR / "data" / "chrome_auth_state.json"


async def main():
    parser = argparse.ArgumentParser(description="Chrome T-360 Award Checker for Finnair & Qatar")
    parser.add_argument("--site", choices=["qatar", "finnair", "ba"], default="qatar", help="Target airline site")
    parser.add_argument("--login", action="store_true", help="Open Chrome interactively to log in and save session")
    parser.add_argument("--origin", type=str, default="PVG", help="Origin airport code")
    parser.add_argument("--dest", type=str, default="CDG", help="Destination airport code")
    parser.add_argument("--date", type=str, default="", help="Target YYYY-MM-DD (default: today + 360 days)")
    parser.add_argument("--pax", type=int, default=2, help="Number of adult passengers")
    parser.add_argument("--wait-seconds", type=int, default=120, help="Seconds to keep interactive login window open")
    args = parser.parse_args()

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    target_date = args.date or (datetime.date.today() + datetime.timedelta(days=360)).strftime("%Y-%m-%d")

    async with async_playwright() as p:
        print(f"[*] Launching Google Chrome (channel='chrome') with persistent profile: {PROFILE_DIR}")
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            channel="chrome",
            headless=False,
            viewport={"width": 1366, "height": 860},
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = context.pages[0] if context.pages else await context.new_page()

        if args.site == "qatar":
            if args.login:
                url = "https://www.qatarairways.com/en/Privilege-Club/loginpage.html"
            else:
                url = (
                    f"https://www.qatarairways.com/app/booking/flight-selection?"
                    f"widget=QR&searchType=F&addTaxToFare=Y&minPurTime=0&upsellCallId=&allowRedemption=Y"
                    f"&flexibleDate=off&bookingClass=B&tripType=O&selLang=en"
                    f"&fromStation={args.origin}&toStation={args.dest}&departing={target_date}"
                    f"&adults={args.pax}&children=0&infants=0&ofw=0&teenager=0"
                )
        elif args.site == "finnair":
            if args.login:
                url = "https://www.finnair.com/en/book-flights-with-avios"
            else:
                url = (
                    f"https://www.finnair.com/en/book/flights-selection?"
                    f"Json=%7B%22flights%22:%5B%7B%22origin%22:%22{args.origin}%22,"
                    f"%22destination%22:%22{args.dest}%22,%22departureDate%22:%22{target_date}%22%7D%5D,"
                    f"%22passengers%22:%5B%7B%22type%22:%22ADT%22,%22count%22:{args.pax}%7D%5D,"
                    f"%22isAward%22:true%7D"
                )
        else:
            url = "https://www.britishairways.com/travel/redeem/execclub/_gf/en_gb"

        print(f"[*] Navigating Chrome to: {url}")
        await page.goto(url, wait_until="domcontentloaded", timeout=45000)

        if args.login:
            print(
                f"[!] Please complete login in the opened Chrome window. "
                f"Waiting up to {args.wait_seconds}s (or close the browser window when done)..."
            )
            try:
                await page.wait_for_timeout(args.wait_seconds * 1000)
            except Exception:
                pass
        else:
            await page.wait_for_timeout(12000)
            try:
                body_txt = await page.inner_text("body")
                lines = [l.strip() for l in body_txt.split("\n") if l.strip()]
                print(f"=== Page Snapshot ({args.site.upper()} {args.origin}->{args.dest} on {target_date}) ===")
                print(" | ".join(lines[:60]))
            except Exception as e:
                print(f"[!] Could not read page text: {e}")

        try:
            await context.storage_state(path=str(STATE_FILE))
            print(f"[+] Saved Chrome auth state to {STATE_FILE}")
        except Exception:
            pass
        await context.close()


if __name__ == "__main__":
    asyncio.run(main())
