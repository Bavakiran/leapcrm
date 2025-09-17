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

    no_offer_id_pools = {"Email BL Campaign", "Self Evaluation Pool"}

    # ---------------- State Storage ----------------
    india_glid = None  # Save India Pool GLID for comparison later

    # ---------------- Helper Functions ----------------
    def extract_offer_id(raw_text: str) -> str | None:
        if not raw_text:
            return None
        match = re.search(r"\d{6,}", raw_text)
        return match.group(0) if match else None

    def extract_glid(raw_text: str) -> str | None:
        if not raw_text:
            return None
        match = re.search(r"\d{6,}", raw_text)
        return match.group(0) if match else None

    def print_offer_id(pool_name: str):
        nonlocal india_glid

        if pool_name in no_offer_id_pools:
            print(f"ℹ️ Skipping OfferId fetch for {pool_name} (not applicable)")
            return

        if pool_name == "MergePool":
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
                print("⚠️ Lead is not assigned and no offer id found")
            return

        # India Pool special handling → fetch OfferId + GLID
        if pool_name == "India Pool 1 (Vkalp)":
            try:
                # OfferId
                locators = offer_id_locators.get(pool_name, [])
                for locator in locators:
                    el = page.locator(locator).first
                    if el.is_visible(timeout=2000):
                        raw = el.text_content().strip()
                        offer_id = extract_offer_id(raw)
                        if offer_id:
                            print(f"📌 Lead assigned and OfferId found on India Pool 1 (Vkalp): {offer_id}")
                            break

                # GLID inside modal-header
                glid_el = page.locator("h4.modal-header span:has-text('')").nth(0)
                if glid_el.is_visible(timeout=2000):
                    raw_glid = glid_el.text_content().strip()
                    india_glid = extract_glid(raw_glid)
                    if india_glid:
                        print(f"📌 GLID found in India Pool 1 (Vkalp): {india_glid}")

            except:
                print("⚠️ Could not fetch GLID from India Pool 1 (Vkalp)")
            return

        # Photo Review Pool special handling
        if pool_name == "Photo Review Pool":
            offer_id = None
            locators = offer_id_locators.get(pool_name, [])
            for locator in locators:
                try:
                    el = page.locator(locator).first
                    if el.is_visible(timeout=2000):
                        raw = el.text_content().strip()
                        offer_id = extract_offer_id(raw)
                        if offer_id:
                            print(f"📌 Lead assigned and OfferId found on {pool_name}: {offer_id}")
                            break
                except:
                    continue

            if not offer_id:
                print(f"⚠️ No OfferId found on {pool_name}")

            # ✅ Verify Buyer Submitted Photo
            try:
                photo = page.locator("img#editImage.buyer-photo")
                if photo.is_visible(timeout=3000):
                    photo_src = photo.get_attribute("src")
                    print(f"🖼️ Buyer Submitted Photo found: {photo_src}")
                else:
                    print("⚠️ No Buyer Submitted Photo found in Photo Review Pool")
            except:
                print("⚠️ Error checking Buyer Submitted Photo in Photo Review Pool")
            return

        # WhatsApp Review Pool special handling
        if pool_name == "WHATSAPP Review Pool":
            offer_id = None
            locators = offer_id_locators.get(pool_name, [])
            for locator in locators:
                try:
                    el = page.locator(locator).first
                    if el.is_visible(timeout=2000):
                        raw = el.text_content().strip()
                        offer_id = extract_offer_id(raw)
                        if offer_id:
                            print(f"📌 Lead assigned and OfferId found on {pool_name}: {offer_id}")
                            break
                except:
                    continue

            if not offer_id:
                print(f"⚠️ No OfferId found on {pool_name}")

            # ✅ Verify Product Image
            try:
                product_img = page.locator("img.prodImg[alt='Product Image']")
                if product_img.is_visible(timeout=3000):
                    img_src = product_img.get_attribute("src")
                    print(f"🖼️ Product Image found in WhatsApp Review Pool: {img_src}")
                else:
                    print("⚠️ No Product Image found in WhatsApp Review Pool")
            except:
                print("⚠️ Error checking Product Image in WhatsApp Review Pool")
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
                        print(f"📌 Lead assigned and OfferId found on {pool_name}: {offer_id}")
                        return
            except:
                continue

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

        with page.expect_navigation(timeout=60000):
            page.locator(f"a:has-text('{pool_name}')").click()
        print(f"✅ {pool_name} page loaded")

        if pool_name == "Foreign Pool":
            print("⚠️ Foreign Pool detected → handling popup and GLID...")
            handled = False
            try:
                warning_el = page.locator("#warningDiv")
                if warning_el.is_visible(timeout=3000):
                    warning_text = warning_el.text_content().strip()
                    print(f"⚠️ Warning message from #warningDiv: {warning_text}")

                    # Extract GLID directly from warning text
                    foreign_glid = extract_glid(warning_text)
                    if foreign_glid:
                        print(f"📌 GLID found in Foreign Pool warning: {foreign_glid}")
                        if india_glid:
                            if india_glid == foreign_glid:
                                print("✅ GLID in India Pool 1 matches Foreign Pool")
                            else:
                                print(f"❌ GLID mismatch! India Pool 1: {india_glid}, Foreign Pool: {foreign_glid}")
                        else:
                            print("⚠️ No India Pool GLID stored for comparison")
                    else:
                        print("⚠️ No GLID found in Foreign Pool warning")

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

            if not handled:
                print("❌ Could not handle any popup in Foreign Pool")

            safe_go_back(pool_name)
            continue

        print_offer_id(pool_name)
        safe_go_back(pool_name)
