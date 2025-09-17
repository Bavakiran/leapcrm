from playwright.sync_api import sync_playwright
from login import login
from do_not_call import handle_dnc_pools
from employee_monitoring import employee_monitoring
from dasboard import dashboard_tabs  # Import your dashboard module

EMAIL = "bavakiran@indiamart.com"
PASSWORD = "@Indiamart25"

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=800)
        page = browser.new_page()

        # 1️⃣ Login
        login(page, EMAIL, PASSWORD)
        
        # 2️⃣ Handle Dashboard Tabs (Latest Briefings & Training Videos)
        dashboard_tabs(page)
        
        # 3️⃣ Handle DNC pools (with Foreign Pool logic merged)
        handle_dnc_pools(page)

        # 4️⃣ Run Employee Monitoring (Sign Out + TEST VANI BOT iframe)
        employee_monitoring(page)

        # 5️⃣ Stay on Dashboard until user manually clicks Sign Out
        print("✅ Script finished. Browser will stay open until you click Sign Out on Dashboard.")
        try:
            # Wait until Sign Out is clicked (detached from DOM)
            page.locator("a[onclick*='Logoff']").wait_for(state="detached", timeout=0)
            print("✅ Sign Out detected, browser will close and land on login page.")
        except:
            print("⚠️ Sign Out not detected, closing browser anyway...")

        browser.close()

if __name__ == "__main__":
    run()
