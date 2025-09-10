from playwright.sync_api import Page

def employee_monitoring(page: Page):
    """
    Handles Employee Sign Out, back button navigation,
    and TEST VANI BOT NEW (handles new tab or iframe).
    """
    print("👉 Clicking Employee Sign Out...")
    try:
        signout_btn = page.locator("a[onclick*=\"openCRM('showunassignVIP')\"]")
        signout_btn.click()
        page.wait_for_timeout(2000)
        print("✅ Employee Sign Out clicked")
    except:
        print("⚠️ Employee Sign Out button not found, continuing...")

    # Go back until Dashboard is visible
    print("↩️ Returning to Dashboard using back button...")
    for attempt in range(10):
        try:
            page.go_back(wait_until="domcontentloaded", timeout=5000)
            page.locator("a[onclick*='Logoff']").wait_for(state="visible", timeout=3000)
            print("✅ Back on Dashboard (Sign Out visible)")
            break
        except:
            print(f"↩️ Back attempt {attempt+1} failed, retrying...")

    # Wait until Dashboard fully loaded
    page.locator("a[onclick*='Logoff']").wait_for(state="visible", timeout=5000)

    # Click TEST VANI BOT NEW
    print("👉 Clicking TEST VANI BOT NEW...")
    try:
        main_page = page
        with page.context.expect_page() as new_page_info:
            page.locator("a:has-text('TEST VANI BOT')").click()
        new_tab = new_page_info.value
        new_tab.wait_for_load_state("domcontentloaded")
        print("✅ TEST VANI BOT opened in new tab/window")

        # Close new tab
        new_tab.close()
        print("✅ TEST VANI BOT tab closed")

        # Switch back to parent Dashboard tab
        main_page.bring_to_front()
        print("✅ Switched back to main Dashboard tab")
    except Exception:
        print("⚠️ No new tab opened, maybe it loads in iframe")

        # fallback check for iframe
        iframe = page.frame(name="iframeReport")
        if iframe:
            print("✅ Found iframeReport after clicking TEST VANI BOT")
        else:
            print("❌ Neither new tab nor iframeReport found")
