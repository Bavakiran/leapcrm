from playwright.sync_api import Page

def login(page: Page, email: str, password: str):
    print("👉 Logging in...")
    page.goto("https://leap.intermesh.net/index.php")
    page.fill("input#emp_email", email)
    page.fill("input#emp_pass", password)
    page.keyboard.press("Enter")

    # wait until dashboard loads
    page.wait_for_load_state("networkidle")
    print("✅ Logged in successfully")
    return page
