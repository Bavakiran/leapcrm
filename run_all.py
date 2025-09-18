import subprocess
import os
import sys
from collections import defaultdict
from google_logger import GoogleSheetLogger
from mailer import send_summary_email

sys.stdout.reconfigure(encoding='utf-8')

# Google Sheet details
SHEET_NAME = "LEAP_CRM"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1C1zjuN4P503xHjoGv-l31wTPpqN6gLsqwdb3BlttFv0/edit?gid=0#gid=0"

# Scripts and their corresponding Google Sheet tab names
scripts_to_run = [
    ("login.py", None)
    ("dasboard.py", "dashboard"),
    ("do_not_call.py", "DNC"),
    ("employee_monitoring.py", "employeemonitoring"),
    
    
]

folder_path = os.path.dirname(os.path.abspath(__file__))

browser_results = defaultdict(lambda: {"Pass": 0, "Fail": 0})
tab_summaries = {}
latest_run_times = {}

# --- Step 1: Run all scripts ---
for script_name, tab_name in scripts_to_run:
    print(f"\n=== Running {script_name} ===")
    result = subprocess.run(
        [sys.executable, os.path.join(folder_path, script_name)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONUTF8": "1"}
    )

    print(result.stdout)
    if result.stderr:
        print(f"Error in {script_name}:\n{result.stderr}")

# --- Step 2: Get latest run time for each tab ---
print("\n🔍 Detecting latest run timestamp for each tab...")
for _, tab_name in scripts_to_run:
    if tab_name:
        try:
            logger = GoogleSheetLogger(SHEET_NAME, tab_name)
            latest_time = logger.get_latest_run_time()
            if latest_time:
                latest_run_times[tab_name] = latest_time
                print(f"✅ {tab_name} latest run time: {latest_time}")
            else:
                print(f"⚠ No run time found in {tab_name}")
        except Exception as e:
            print(f"❌ Could not fetch latest run time from {tab_name}: {e}")

if not latest_run_times:
    print("❌ No run times found in any sheet tab. Cannot fetch summary.")
    sys.exit(1)

# --- Step 3: Fetch summaries for each tab ---
for _, tab_name in scripts_to_run:
    if tab_name and tab_name in latest_run_times:
        try:
            logger = GoogleSheetLogger(SHEET_NAME, tab_name)
            passed, failed, total = logger.get_summary_counts(run_time=latest_run_times[tab_name])
            tab_summaries[tab_name] = (passed, failed, total)
            print(f"📊 {tab_name} - Passed: {passed}, Failed: {failed}, Total: {total}")

            if hasattr(logger, "get_browser_wise_counts"):
                tab_browser_counts = logger.get_browser_wise_counts(run_time=latest_run_times[tab_name])
                for browser, counts in tab_browser_counts.items():
                    browser_results[browser]["Pass"] += counts.get("Pass", 0)
                    browser_results[browser]["Fail"] += counts.get("Fail", 0)

        except Exception as e:
            print(f"❌ Could not fetch summary for {tab_name}: {e}")

# --- Step 4: Send summary email ---
if tab_summaries:
    total_passed = sum(p for p, _, _ in tab_summaries.values())
    total_failed = sum(f for _, f, _ in tab_summaries.values())
    total_total = sum(t for _, _, t in tab_summaries.values())

    send_summary_email(
        passed=total_passed,
        failed=total_failed,
        total=total_total,
        sheet_url=SHEET_URL,
        tab_name="LEAP",
        browser_results=browser_results,
        tab_summaries=tab_summaries
    )