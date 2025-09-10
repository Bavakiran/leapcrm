from playwright.sync_api import Page

def handle_pool(page: Page, pool_name: str):
    print(f"👉 Clicking {pool_name}...")

    with page.expect_navigation(timeout=60000):
        page.locator(f"a:has-text('{pool_name}')").click()

    print(f"✅ {pool_name} page loaded")

    try:
        signout_btn = page.locator("a.signout:has-text('Sign Out')")
        signout_btn.wait_for(state="visible", timeout=5000)
        signout_btn.click()
        print(f"✅ Signed out from {pool_name}")

        # After signout → login page should appear
        page.locator("input#emp_email").wait_for(state="visible", timeout=10000)
        print("✅ Back on Login Page after signing out")

    except:
        print(f"⚠️ Sign Out not found in {pool_name}, going back...")

        for i in range(10):
            try:
                page.go_back(wait_until="domcontentloaded", timeout=5000)

                # Check if dashboard signout is visible
                page.locator("a.signout:has-text('Sign Out')").wait_for(
                    state="visible", timeout=3000
                )
                print("✅ Dashboard visible, Sign Out found")
                break
            except Exception as e:
                print(f"↩️ Back attempt {i+1} failed ({str(e)[:60]}...), retrying...")


def handle_brf(page: Page):
    """Special case for Go to BRF → only back navigation until dashboard Sign Out is visible"""
    pool_name = "Go to BRF"
    print(f"👉 Clicking {pool_name}...")

    with page.expect_navigation(timeout=60000):
        page.locator(f"a:has-text('{pool_name}')").click()

    print(f"✅ {pool_name} page loaded")

    print("↩️ Going back until Dashboard Sign Out is visible...")
    for i in range(10):
        try:
            page.go_back(wait_until="domcontentloaded", timeout=5000)

            page.locator("a.signout:has-text('Sign Out')").wait_for(
                state="visible", timeout=3000
            )
            print("✅ Dashboard visible, Sign Out found")
            break
        except Exception as e:
            print(f"↩️ Back attempt {i+1} failed ({str(e)[:60]}...), retrying...")
