import logging
from datetime import date
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper
from core.models import JobOffer

logger = logging.getLogger(__name__)


class ScraperRemoteOK(BaseScraper):
    BASE_URL = "https://remoteok.com"

    def scrape(self) -> list[JobOffer]:
        ofertas = []
        url = f"{self.BASE_URL}/remote-dev-jobs"
        
        response = self._get(url)
        if not response:
            logger.warning("No se pudo obtener respuesta de RemoteOK")
            return ofertas
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        for item in soup.select("tr.job"):
            try:
                title_elem = item.select_one("h2")
                company_elem = item.select_one("h3")
                apply_elem = item.select_one("a")
                
                if not title_elem or not apply_elem:
                    continue
                
                titulo = title_elem.get_text(strip=True)
                empresa = company_elem.get_text(strip=True) if company_elem else "desconocida"
                
                url_oferta = self.BASE_URL + apply_elem.get("href", "")
                oferta_id = url_oferta.split("-")[-1] if url_oferta else titulo
                
                salary_elem = item.select_one(".salary")
                salary = salary_elem.get_text(strip=True) if salary_elem else None
                
                ciudad = "Remoto"
                
                ofertas.append(JobOffer(
                    id=f"remoteok-{oferta_id}",
                    titulo=titulo,
                    empresa=empresa,
                    email_contacto=None,
                    url_oferta=url_oferta,
                    portal_origen="RemoteOK",
                    fecha_publicacion=date.today(),
                    descripcion=f"Trabajo remoto - {salary}" if salary else "Trabajo remoto",
                    ciudad=ciudad,
                    categoria="IT / Desarrollo",
                    salary=salary
                ))
            except Exception as e:
                logger.debug(f"Error parseando oferta RemoteOK: {e}")
                continue
        
        logger.info(f"RemoteOK: {len(ofertas)} ofertas extraídas")
        return ofertas
