import time
import json

from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup, NavigableString
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


# Przewija stronę w dół, aż cała zawartość zostanie załadowana
# Na niektórych stronach treść ładuję się po zjechaniu niżej
def scroll_to_bottom(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")        # Wysokość strony

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")    # Przewiń na dół strony
        time.sleep(1)                                                               # Czekaj na załadowanie treści
        new_height = driver.execute_script("return document.body.scrollHeight")     # Nowa wysokość strony po przewinięciu

        # Przerwanie, jeśli osiągnięto koniec strony
        if new_height == last_height:
            break
        last_height = new_height


# Szukanie i kliknięcie przycisku 'zgadzam sie', jeśli istnieje
# Na 2 stronach (spidersweb i chip) okna dialogowe powodowały niepoprawne czytanie danych
def click_popup_button(driver):
    try:
        consent_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button.fc-button.fc-cta-consent"))
        )
        consent_button.click()      # Kliknięcie przycisku
        time.sleep(3)               # Krótkie opóźnienie po kliknięciu w celu załadowania strony
    except Exception as e:
        print("Brak przycisku zgody lub wystąpił inny błąd:", e)


# Pobieranie kodu źródłowego strony
def fetch_page(url):
    driver = None
    page_source = ""

    try:
        # Konfiguracja opcji przeglądarki
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")      # Uruchamienie przeglądraki w tle
        driver = Chrome(options=options)
        driver.get(url)

        click_popup_button(driver)              # Kliknięcie przycisku 'zgadzam sie', jeśli istnieje
        scroll_to_bottom(driver)                # Orzewijanie strony w dół

        page_source = driver.page_source

    except Exception as e:
        print(f"Błąd podczas pobierania strony: {url}, błąd: {e}")

    finally:
        if driver:
            driver.quit()

    return page_source


# Funkcja wyodrębniająca zawartość z wybranych tagów HTML na danej stronie
def extract_tags(url):
    page_content = fetch_page(url)                              # Pobranie kodu HTML
    soup = BeautifulSoup(page_content, 'html.parser')   # Parsowanie strony za pomocą BeautifulSoup

    # Filtoranie wybranych tagów
    allowed_tags = ['h2', 'h3', 'p', 'strong']
    filtered_content = soup.find_all(allowed_tags)

    results = []
    for tag in filtered_content:
        results.append({
            'tag': tag.name,
            'content': tag.get_text(strip=True)
        })

    return results


# Funkcja, która iteruje po liście z linkami URL, pobiera treść z każdej strony i zapisuje dane w pliku JSON
def scrape_pages(urls):
    data = []

    for url in urls:
        tags = extract_tags(url)
        data.append({
            'url': url,
            'tags': tags
        })

    with open('response.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# Lista stron do scrapowania
urls = [
    'https://bistrolubie.pl/pierniki-z-miodem-tradycyjny-przepis-na-swiateczne-ciasteczka-pelne-aromatu',
    'https://bistrolubie.pl/piernik-z-mascarpone-kremowy-i-pyszny-przepis-na-deser-idealny-na-swieta',
    'https://spidersweb.pl/2024/07/metamorfoza-w-centrum-warszawy.html',
    'https://spidersweb.pl/2024/07/kontrolery-na-steam-rosnie-popularnosc.html',
    'https://www.chip.pl/2024/06/wtf-obalamy-mity-poprawnej-pozycji-przy-biurku',
    'https://www.chip.pl/2024/07/sony-xperia-1-vi-test-recenzja-opinia',
    'https://newonce.net/artykul/chief-keef-a-sprawa-polska-opowiadaja-benito-gicik-crank-all',
    'https://newonce.net/artykul/glosna-gra-ktorej-akcja-toczy-sie-w-warszawie-1905-roku-gralismy-w-the-thaumaturge',
]

# Wywołanie głównej funkcji scrapującej
scrape_pages(urls)


