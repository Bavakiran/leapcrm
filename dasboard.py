from playwright.sync_api import Page

def dashboard_tabs(page: Page):
    """
    Handles clicking menu items on Dashboard that open new tabs, 
    verifies their content, closes them, 
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

            # Print new tab URL
            try:
                tab_url = new_tab.url
                print(f"🌐 {item} Tab URL: {tab_url}")
            except:
                print(f"⚠️ Could not fetch {item} tab URL")

            # Handle per item logic
            if item == "Latest Briefings":
                try:
                    h1_el = new_tab.locator("h1:has-text('Briefing Of The Day')")
                    if h1_el.is_visible(timeout=5000):
                        header_text = h1_el.text_content().strip()
                        print(f"✅ Header found in {item} tab: {header_text}")
                    else:
                        print(f"❌ Expected header NOT found in {item} tab")
                except Exception as e:
                    print(f"⚠️ Error checking header in {item} tab: {e}")

            elif item == "Training Videos":
                try:
                    links = new_tab.locator("a").all_inner_texts()
                    print("📋 Links found in Training Videos tab:")
                    for link in links:
                        print(f"- {link.strip()}")
                except Exception as e:
                    print(f"⚠️ Error fetching links in Training Videos tab: {e}")

            # Close new tab
            new_tab.close()
            print(f"✅ {item} tab closed")

            # Switch back to main tab
            main_page.bring_to_front()
            print("✅ Switched back to main Dashboard tab")

        except Exception as e:
            print(f"❌ Error handling {item}: {e}")
