from playwright.sync_api import Page
import re

def handle_dnc_pools(page: Page):
    # ---------------- Pools ----------------
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

    # Pool → OfferId locators
    offer_id_locators = {
        "India Pool 1 (Vkalp)": ["b:has-text('Offer Id') span", "b span[style*='color:#A5110A;']"],
        "Ban Review Pool": ["#offerid", "span#offerid"],
        "Photo Review Pool": ["span.header-central-heading", "span.header-central-heading-value"],
        "MCAT Review Pool": ["span.tal.titlemargin:has-text('Offer ID')", "span.tal.titlemargin"],
        "WHATSAPP Review Pool": ["p.card-text.subheading a"],
    }

    # Pools where OfferId is NOT available
    no_offer_id_pools = {"Email BL Campaign", "Self Evaluation Pool"}

    # ---------------- Helper Functions ----------------
    def extract_offer_id(raw_text: str) -> str | None:
        if not raw_text:
            return None
        match = re.search(r"\d{6,}", raw_text)
        return match.group(0) if match else None

    def print_offer_id(pool_name: str):
        """Fetch and print OfferId based on pool-specific locator(s)."""
        if pool_name in no_offer_id_pools:
            print(f"ℹ️ Skipping OfferId fetch for {pool_name} (not applicable)")
            return

        if pool_name == "MergePool":
            # MergePool → search across all pools' locators
            found = False
            for name, locator_list in offer_id_locators.items():
                for locator in locator_list:
                    try:
                        el = page.locator(locator).first
                        if el.is_visible(timeout=1500):
                            raw = el.text_content().strip()
                            offer_id = extract_offer_id(raw)
                            if offer_id:
                                print(f"📌 OfferId found in {name} (inside MergePool): {offer_id}")
                                found = True
                                break
                    except:
                        continue
                if found:
                    break
            if not found:
                print("⚠️ No OfferId found in MergePool")
            return

        # Normal pools
        locators = offer_id_locators.get(pool_name, [])
        for locator in locators:
            try:
                el = page.locator(locator).first
                if el.is_visible(timeout=2000):
                    raw = el.text_content().strip()
                    offer_id = extract_offer_id(raw)
                    if offer_id:
                        print(f"📌 OfferId found on {pool_name}: {offer_id}")
                        return
            except:
                continue

        # Only print warning if it's not a skipped pool
        if pool_name not in no_offer_id_pools:
            print(f"⚠️ No OfferId found on {pool_name}")

    def safe_go_back(pool_name: str):
        print(f"↩️ Returning to Dashboard from {pool_name}...")
        for attempt in range(10):
            try:
                page.go_back(wait_until="domcontentloaded", timeout=5000)
                page.locator("a[onclick*='Logoff']").wait_for(state="visible", timeout=3000)
                print("✅ Back on Dashboard (Sign Out visible)")
                return
            except:
                print(f"↩️ Back attempt {attempt+1} failed, retrying...")

    # ---------------- Pool Handling ----------------
    for i, pool_name in enumerate(dnc_pools, start=1):
        print(f"👉 Clicking {pool_name}...")

        if pool_name == "MergePool":
            with page.expect_navigation(timeout=60000):
                page.locator("a[href*='mergePool/index.php']").click()
            print("✅ MergePool page loaded")
            print_offer_id(pool_name)
            safe_go_back(pool_name)
            continue

        # Other pools
        with page.expect_navigation(timeout=60000):
            page.locator(f"a:has-text('{pool_name}')").click()
        print(f"✅ {pool_name} page loaded")

        # Foreign Pool special handling
        if pool_name == "Foreign Pool":
            print("⚠️ Foreign Pool detected → handling popup and GLID...")
            handled = False
            try:
                warning_el = page.locator("#warningDiv")
                if warning_el.is_visible(timeout=3000):
                    print(f"⚠️ Warning message from #warningDiv: {warning_el.text_content().strip()}")
                    page.locator("#warningDiv input[value='OK, I understand']").click()
                    handled = True
            except:
                pass
            try:
                limit_el = page.locator("#limitDiv")
                if limit_el.is_visible(timeout=3000):
                    print(f"⚠️ Warning message from #limitDiv: {limit_el.text_content().strip()}")
                    page.locator("#limitDiv input[value='OK, I understand']").click()
                    handled = True
            except:
                pass

            # Fetch GLID if present
            try:
                glid_el = page.locator("span:has-text('GLID')")
                if glid_el.is_visible(timeout=2000):
                    raw = glid_el.text_content().strip()
                    glid_match = re.search(r"\d{5,}", raw)
                    if glid_match:
                        print(f"📌 GLID found in Foreign Pool: {glid_match.group(0)}")
            except:
                print("⚠️ No GLID found in Foreign Pool")

            if not handled:
                print("❌ Could not handle any popup in Foreign Pool")

            safe_go_back(pool_name)
            continue

        # Normal pools → OfferId search (skips excluded pools automatically)
        print_offer_id(pool_name)
        safe_go_back(pool_name)
