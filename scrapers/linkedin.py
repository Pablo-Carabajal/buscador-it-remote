import logging
from datetime import date
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper
from core.models import JobOffer

logger = logging.getLogger(__name__)


class ScraperLinkedIn(BaseScraper):
    BASE_URL = "https://www.linkedin.com"

    def scrape(self) -> list[JobOffer]:
        ofertas = []
        url = f"{self.BASE_URL}/jobs/search/?geoId=90000000&keywords=remote%20developer"
        
        response = self._get(url)
        if not response:
            logger.warning("No se pudo obtener respuesta de LinkedIn")
            return ofertas
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        for item in soup.select(".job-card-container"):
            try:
                title_elem = item.select_one(".job-card-list__title")
                company_elem = item.select_one(".job-card-container__company-name")
                link_elem = item.select_one("a.job-card-list__title")
                
                if not title_elem:
                    continue
                
                titulo = title_elem.get_text(strip=True)
                empresa = company_elem.get_text(strip=True) if company_elem else "desconocida"
                
                url_oferta = link_elem.get("href", "") if link_elem else ""
                if url_oferta and not url_oferta.startswith("http"):
                    url_oferta = self.BASE_URL + url_oferta
                
                oferta_id = titulo.replace(" ", "-").lower()[:30]
                
                ciudad = "Remoto"
                
                ofertas.append(JobOffer(
                    id=f"linkedin-{oferta_id}",
                    titulo=titulo,
                    empresa=empresa,
                    email_contacto=None,
                    url_oferta=url_oferta,
                    portal_origen="LinkedIn",
                    fecha_publicacion=date.today(),
                    descripcion="Trabajo remoto IT",
                    ciudad=ciudad,
                    categoria="IT / Desarrollo"
                ))
            except Exception as e:
                logger.debug(f"Error parseando oferta LinkedIn: {e}")
                continue
        
        logger.info(f"LinkedIn: {len(ofertas)} ofertas extraídas")
        return ofertas
