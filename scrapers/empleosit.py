import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from scrapers.base import BaseScraper
from core.models import JobOffer


logger = logging.getLogger(__name__)


class ScraperEmpleosIT(BaseScraper):
    def __init__(self, email: str, password: str, ciudad: str = "Remoto", provincia: str = "Argentina"):
        super().__init__(ciudad, provincia)
        self.email = email
        self.password = password
        
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.wait = WebDriverWait(self.driver, 15)

    def login(self) -> bool:
        try:
            self.driver.get("https://www.empleosit.com.ar/login")
            time.sleep(2)
            email_field = self.wait.until(EC.presence_of_element_located((By.ID, "email")))
            email_field.send_keys(self.email)
            time.sleep(1)
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(self.password)
            password_field.send_keys(Keys.RETURN)
            time.sleep(3)
            return "login" not in self.driver.current_url.lower()
        except Exception as e:
            logger.warning(f"Login EmpleosIT falló: {e}")
            return False

    def scrape(self) -> list[JobOffer]:
        if not self.login():
            return []
        
        try:
            self.driver.get("https://www.empleosit.com.ar/empleos?q=desarrollador+IT&l=Argentina")
            time.sleep(3)
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            ofertas = []
            for item in soup.select(".job-card, .job-listing, .offer"):
                try:
                    titre = item.select_one("h2, .title, .job-title")
                    empresa = item.select_one(".company, .company-name")
                    link = item.select_one("a")
                    titulo_txt = titre.get_text(strip=True) if titre else "Sin título"
                    empresa_txt = empresa.get_text(strip=True) if empresa else "desconocida"
                    url = link.get("href", "") if link else ""
                    oferta = JobOffer(
                        id=f"ei-{hash(url)}",
                        titulo=titulo_txt,
                        empresa=empresa_txt,
                        ubicacion=self.ciudad,
                        url_oferta=url,
                        portal_origen="EmpleosIT",
                        categoria="IT / Desarrollo"
                    )
                    ofertas.append(oferta)
                except Exception:
                    pass
            return ofertas
        except Exception as e:
            logger.error(f"Error scrape EmpleosIT: {e}")
            return []

    def __del__(self):
        if hasattr(self, "driver"):
            try:
                self.driver.quit()
            except Exception:
                pass