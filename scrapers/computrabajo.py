import time
import random
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


class ScraperComputrabajo(BaseScraper):
    def __init__(self, email: str, password: str, ciudad: str = "Remoto", provincia: str = "Argentina"):
        super().__init__(ciudad, provincia)
        self.email = email
        self.password = password
        
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.wait = WebDriverWait(self.driver, 15)

    def _tipear(self, campo, texto: str):
        campo.clear()
        for char in texto:
            campo.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))

    def login(self) -> bool:
        max_intentos = 2
        for intento in range(max_intentos):
            try:
                logger.info(f"Computrabajo login intento {intento + 1}/{max_intentos}")
                self.driver.get("https://candidato.ar.computrabajo.com/acceso/")
                time.sleep(3)
                
                email_field = self.wait.until(EC.presence_of_element_located((By.ID, "email")))
                self._tipear(email_field, self.email)
                
                continue_btn = self.wait.until(EC.element_to_be_clickable((By.ID, "continueWithMailButton")))
                self.driver.execute_script("arguments[0].click();", continue_btn)
                
                password_field = self.wait.until(EC.presence_of_element_located((By.ID, "password")))
                self._tipear(password_field, self.password)
                
                password_field.send_keys(Keys.RETURN)
                time.sleep(3)
                
                current_url = self.driver.current_url
                if "login" not in current_url and "acceso" not in current_url:
                    logger.info("Login exitoso en Computrabajo")
                    return True
                else:
                    logger.warning(f"Login fallo, URL: {current_url}")
                    
            except Exception as e:
                logger.warning(f"Error en login intento {intento + 1}: {e}")
            
            if intento < max_intentos - 1:
                time.sleep(30)
        
        return False

    def scrape(self) -> list[JobOffer]:
        if not self.login():
            logger.warning("Login computrabajo falló, retornando lista vacía")
            return []
        
        try:
            self.driver.get("https://candidato.ar.computrabajo.com/trabajo/?q=desarrollador+IT&l=Argentina")
            time.sleep(3)
            
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            ofertas = []
            
            for card in soup.select(".card"):
                try:
                    titulo = card.select_one(".title, h2, .job-title")
                    empresa = card.select_one(".company, .company-name")
                    lugar = card.select_one(".location, .city")
                    link = card.select_one("a")
                    
                    titulo_txt = titulo.get_text(strip=True) if titulo else "Sin título"
                    empresa_txt = empresa.get_text(strip=True) if empresa else "desconocida"
                    lugar_txt = lugar.get_text(strip=True) if lugar else self.ciudad
                    url = link.get("href", "") if link else ""
                    url = f"https://candidato.ar.computrabajo.com{url}" if url.startswith("/") else url
                    
                    oferta = JobOffer(
                        id=f"ct-{hash(url)}",
                        titulo=titulo_txt,
                        empresa=empresa_txt,
                        ubicacion=lugar_txt,
                        url_oferta=url,
                        portal_origen="Computrabajo",
                        categoria="IT / Desarrollo"
                    )
                    ofertas.append(oferta)
                except Exception as e:
                    logger.debug(f"Error parseando oferta: {e}")
            
            logger.info(f"Computrabajo: {len(ofertas)} ofertas encontradas")
            return ofertas
            
        except Exception as e:
            logger.error(f"Error en scrape computrabajo: {e}")
            return []

    def __del__(self):
        if hasattr(self, "driver"):
            try:
                self.driver.quit()
            except Exception:
                pass