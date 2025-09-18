from playwright.sync_api import Page

def employee_monitoring(page: Page):
    """
    Handles Employee Sign Out, back button navigation,
    and TEST VANI BOT NEW (handles new tab or iframe).
    Also prints header row + Bavakiran's row if found.
    """
    print("👉 Clicking Employee Sign Out...")
    try:
        signout_btn = page.locator("a[onclick*=\"openCRM('showunassignVIP')\"]")
        signout_btn.click()
        page.wait_for_timeout(2000)
        print("✅ Employee Sign Out clicked")
    except:
        print("⚠️ Employee Sign Out button not found, continuing...")

    # 🔍 Find Bavakiran row and headers
    try:
        # Locate header row (first row with <b> tags)
        header_tr = page.locator("table tr").filter(has=page.locator("td b")).first
        header_texts = header_tr.locator("td").all_inner_texts()
        print("📋 Table Headers:")
        print(" | ".join(header_texts))

        # Locate Bavakiran row
        bav_td = page.locator("td:has-text('Bavakiran Govindharaj')").first
        if bav_td.is_visible(timeout=3000):
            bav_tr = bav_td.locator("xpath=ancestor::tr").first
            row_texts = bav_tr.locator("td").all_inner_texts()
            print(" | ".join(row_texts))
        else:
            print("⚠️ Bavakiran not found on Employee Sign Out page")
    except Exception as e:
        print(f"⚠️ Error while searching table: {e}")

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

        # Print new tab URL
        try:
            tab_url = new_tab.url
            print(f"🌐 New Tab URL: {tab_url}")
        except:
            print("⚠️ Could not fetch new tab URL")

        # 🔍 Check for <h1>Voice Bot Call Interface</h1>
        try:
            h1_el = new_tab.locator("h1:has-text('Voice Bot Call Interface')")
            if h1_el.is_visible(timeout=5000):
                header_text = h1_el.text_content().strip()
                print(f"✅ Header found in new tab: {header_text}")
            else:
                print("❌ 'Voice Bot Call Interface' header NOT found in new tab")
        except:
            print("❌ Error checking for 'Voice Bot Call Interface' header")

        # Close new tab
        new_tab.close()
        print("✅ TEST VANI BOT tab closed")

        # Switch back to parent Dashboard tab
        main_page.bring_to_front()
        print("✅ Switched back to main Dashboard tab")
    except Exception:
        print("⚠️ No new tab opened, maybe it loads in iframe")
        iframe = page.frame(name="iframeReport")
        if iframe:
            print("✅ Found iframeReport after clicking TEST VANI BOT")
        else:
            print("❌ Neither new tab nor iframeReport found")