import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import os

SCRIPT_DIR = 'C:\\Users\\faria\\yw\\data'
#SCRIPT_DIR = '/Users/marinabosque/Documents/yw/data'

def extract_info_from_page(url):
    result = {"text": "", "emails": [], "socials": {}}
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return result
        soup = BeautifulSoup(response.text, "lxml")
        result["text"] = soup.get_text(separator=' ', strip=True)
        result["emails"] = re.findall(
            r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
            result["text"]
        )

        # Social links
        result["socials"] = {
            "instagram": None,
            "twitter": None,
            "facebook": None,
            "youtube": None,
            "whatsapp": None
        }

        for a in soup.find_all("a", href=True):
            href = a["href"].lower()
            if "instagram.com" in href and not result["socials"]["instagram"]:
                result["socials"]["instagram"] = href
            elif "twitter.com" in href and not result["socials"]["twitter"]:
                result["socials"]["twitter"] = href
            elif "facebook.com" in href and not result["socials"]["facebook"]:
                result["socials"]["facebook"] = href
            elif "youtube.com" in href or "youtu.be" in href:
                if not result["socials"]["youtube"]:
                    result["socials"]["youtube"] = href
            elif "wa.me" in href or "whatsapp.com" in href:
                if not result["socials"]["whatsapp"]:
                    result["socials"]["whatsapp"] = href

    except Exception:
        pass
    return result

def extract_info_from_website(base_url):
    combined_text = ""
    emails_set = set()

    # Initialize all social platforms
    socials = {
        "instagram": None,
        "twitter": None,
        "facebook": None,
        "youtube": None,
        "whatsapp": None
    }

    # Step 1: Visit base page
    main = extract_info_from_page(base_url)
    combined_text += " " + main["text"]
    emails_set.update(main["emails"])
    socials.update({k: v or socials[k] for k, v in main["socials"].items()})

    # Step 2: Visit contact/about subpages
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        soup = BeautifulSoup(requests.get(base_url, headers=headers, timeout=10).text, "lxml")
        anchors = soup.find_all("a", href=True)
        keywords = ["contact", "about", "quienes", "nosotros", "clases","clases-yoga",
                    "clases-de-yoga","clase-de-yoga-y-pilates"," contacto","contactanos","contact-us","el-estudio",
                    " sobre-mi"," actividades"," quienes-somos","que-ofrecemos"," precios-y-horarios","membership",
                    " precios-y-horarios"," tarifas","horarios-y-tarifas","suscripciones","horarios","tarifas-estudio", "precios"] 
        
        subpages = set()

        for a in anchors:
            href = a["href"].lower()
            text = a.get_text(strip=True).lower()
            if any(k in href or k in text for k in keywords):
                full_url = urljoin(base_url, a["href"])
                subpages.add(full_url)

        for sub_url in subpages:
            sub = extract_info_from_page(sub_url)
            combined_text += " " + sub["text"]
            emails_set.update(sub["emails"])
            socials.update({k: v or socials[k] for k, v in sub["socials"].items()})
    except Exception:
        pass

    # Step 3: Extract yoga styles and price info
    style_keywords = ["hatha", "vinyasa", "yin", "ashtanga", "kundalini", "iyengar", "prenatal", "restorative", 
                      "jivamukti", "rocket", "awakening", "raja", "bhakti", "karma", "jnana", "acroyoga", "aeroyoga",
                      "nidra", "hot", "bikram", "power", "restaurativo", "aerial", "postnatal", "embarazadas", 
                      "yoga para niños", "terapeutico", "navakarana", "soma yoga"]
    found_styles = [s for s in style_keywords if s in combined_text.lower()]
    price_matches = re.findall(r"(€\s?\d+|\d+\s?€)", combined_text)

    return {
        "email": list(emails_set)[0] if emails_set else None,
        "instagram": socials["instagram"],
        "twitter": socials["twitter"],
        "facebook": socials["facebook"],
        "youtube": socials["youtube"],
        "whatsapp": socials["whatsapp"],
        "styles": ", ".join(found_styles) if found_styles else None,
        "price_info": ", ".join(price_matches) if price_matches else None
    }

# === Load Excel ===
INPUT_EXCEL_PATH = os.path.join(SCRIPT_DIR, "centers_with_google_maps_information.xlsx")
df = pd.read_excel(INPUT_EXCEL_PATH)  # Must contain a "website" column

# keep the columns place_id and website
#df = df[["place_id", "website"]]

# === Enrich each row ===
info_list = []
for _, row in df.iterrows():
    website = row.get("website")
    print(f"🔍 Processing website: {website}")  # <--- ADD THIS LINE
    if pd.notna(website):
        info = extract_info_from_website(website)
    else:
        info = {
            "email": None, "instagram": None, "twitter": None,
            "facebook": None, "youtube": None, "whatsapp": None,
            "styles": None, "price_info": None
        }
    info_list.append(info)

# === Combine and Save ===
info_df = pd.DataFrame(info_list)
final_df = pd.concat([df.reset_index(drop=True), info_df], axis=1)
OUTPUT_EXCEL_PATH = os.path.join(SCRIPT_DIR, "centers_with_google_maps_and_website_information.xlsx")
final_df.to_excel(OUTPUT_EXCEL_PATH, index=False)
print("✅ Saved to centers_with_google_maps_and_website_information.xlsx")



# # woking to find info from websites stored in an excel
# import pandas as pd
# import requests
# from bs4 import BeautifulSoup
# import re

# def extract_info_from_website(url):
#     result = {"email": None, "instagram": None, "twitter": None, "styles": None, "price_info": None}
#     try:
#         headers = {'User-Agent': 'Mozilla/5.0'}
#         response = requests.get(url, headers=headers, timeout=10)
#         if response.status_code != 200:
#             return result
#         soup = BeautifulSoup(response.text, "lxml")
#         text = soup.get_text(separator=' ', strip=True)

#         # Email
#         emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
#         result["email"] = emails[0] if emails else None

#         # Instagram & Twitter
#         for a in soup.find_all("a", href=True):
#             href = a["href"]
#             if "instagram.com" in href and not result["instagram"]:
#                 result["instagram"] = href
#             elif "twitter.com" in href and not result["twitter"]:
#                 result["twitter"] = href

#         # Yoga Styles (simple keyword scan)
#         styles = ["Hatha", "Vinyasa", "Yin", "Ashtanga", "Kundalini", "Iyengar", "Prenatal", "Restorative"]
#         found_styles = [style for style in styles if style.lower() in text.lower()]
#         result["styles"] = ", ".join(found_styles) if found_styles else None

#         # Price info
#         price_matches = re.findall(r"(€\s?\d+|\d+\s?€)", text)
#         result["price_info"] = ", ".join(price_matches) if price_matches else None

#     except Exception as e:
#         pass  # You could log this if needed

#     return result

# # === Load Excel ===
# df = pd.read_excel("places.xlsx")  # Ensure 'website' column is present

# # === Enrich each row ===
# info_list = []
# for _, row in df.iterrows():
#     website = row.get("website")
#     if pd.notna(website):
#         info = extract_info_from_website(website)
#     else:
#         info = {"email": None, "instagram": None, "twitter": None, "styles": None, "price_info": None}
#     info_list.append(info)

# # === Merge and Save ===
# info_df = pd.DataFrame(info_list)
# final_df = pd.concat([df.reset_index(drop=True), info_df], axis=1)
# final_df.to_excel("places_enriched.xlsx", index=False)
# print("✅ Enriched data saved to 'places_enriched.xlsx'")
