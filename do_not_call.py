from playwright.sync_api import Page

def handle_dnc_pools(page: Page):
    """
    Automates Do Not Call pools in sequence:
    MergePool → India Pool 1 (Vkalp) → Foreign Pool → Ban Review Pool → ...
    Uses browser back button until 'Sign Out' is visible to confirm Dashboard.
    """
    dnc_pools = [
        "MergePool",   
        "India Pool 1 (Vkalp)",
        "Foreign Pool",
        "Ban Review Pool",
        "Photo Review Pool",
        "MCAT Review Pool",
        "Email BL Campaign",
        "WHATSAPP Review Pool",
        "Self Evaluation Pool",
    ]

    for i, pool_name in enumerate(dnc_pools, start=1):
        print(f"👉 ({i}/{len(dnc_pools)}) Clicking {pool_name}...")

        # Handle MergePool separately (direct href instead of :has-text)
        if pool_name == "MergePool":
            with page.expect_navigation(timeout=60000):
                page.locator("a[href='https://leap.intermesh.net/mergePool/index.php']").click()
            print("✅ MergePool page loaded")

            # Go back to Dashboard
            print("↩️ Returning to Dashboard from MergePool...")
            for attempt in range(10):
                try:
                    page.go_back(wait_until="domcontentloaded", timeout=5000)
                    page.locator("a[onclick*='Logoff']").wait_for(state="visible", timeout=3000)
                    print("✅ Back on Dashboard (Sign Out visible)")
                    break
                except:
                    print(f"↩️ Back attempt {attempt+1} failed, retrying...")
            continue  # Skip to next pool after MergePool

        # Normal pools
        with page.expect_navigation(timeout=60000):
            page.locator(f"a:has-text('{pool_name}')").click()
        print(f"✅ {pool_name} page loaded")

        if pool_name == "Foreign Pool":
            print("⚠️ Foreign Pool detected → handling popup...")
            handled = False

            try:
                ok_button = page.locator("#warningDiv input[value='OK, I understand']")
                ok_button.wait_for(state="visible", timeout=3000)
                ok_button.click()
                print("✅ Handled popup from #warningDiv")
                handled = True
            except:
                try:
                    ok_button = page.locator("#limitDiv input[value='OK, I understand']")
                    ok_button.wait_for(state="visible", timeout=3000)
                    ok_button.click()
                    print("✅ Handled popup from #limitDiv")
                    handled = True
                except:
                    print("❌ Could not handle popup in Foreign Pool")

            if not handled:
                continue  # Skip to next pool if popup fails
        else:
            # Keep going back until Sign Out is visible (Dashboard indicator)
            print(f"↩️ Returning to Dashboard from {pool_name}...")
            for attempt in range(10):  # try max 10 back presses
                try:
                    page.go_back(wait_until="domcontentloaded", timeout=5000)

                    # Dashboard check = Sign Out link visible
                    page.locator("a[onclick*='Logoff']").wait_for(state="visible", timeout=3000)
                    print("✅ Back on Dashboard (Sign Out visible)")
                    break
                except:
                    print(f"↩️ Back attempt {attempt+1} failed, retrying...")
