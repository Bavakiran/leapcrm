from playwright.sync_api import Page

def dashboard_tabs(page: Page):
    """
    Handles clicking menu items on Dashboard that open new tabs, closes them, 
    and returns to the main Dashboard tab.
    """
    main_page = page

    menu_items = ["Latest Briefings", "Training Videos"]

    for item in menu_items:
        print(f"👉 Clicking {item}...")
        try:
            # Wait for new page/tab
            with page.context.expect_page() as new_page_info:
                page.locator(f"li.menuBar-list-item:has-text('{item}')").click()
            new_tab = new_page_info.value
            new_tab.wait_for_load_state("domcontentloaded")
            print(f"✅ {item} tab opened")

            # Close new tab
            new_tab.close()
            print(f"✅ {item} tab closed")

            # Switch back to main tab
            main_page.bring_to_front()
            print(f"✅ Switched back to main Dashboard tab")
        except Exception as e:
            print(f"❌ Error handling {item}: {e}")
