import logging
from datetime import date
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper
from core.models import JobOffer

logger = logging.getLogger(__name__)


class ScraperWeWorkRemotely(BaseScraper):
    BASE_URL = "https://weworkremotely.com"

    def scrape(self) -> list[JobOffer]:
        ofertas = []
        url = f"{self.BASE_URL}/remote-jobs"
        
        response = self._get(url)
        if not response:
            logger.warning("No se pudo obtener respuesta de WeWorkRemotely")
            return ofertas
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        for item in soup.select("li.job-listing"):
            try:
                title_elem = item.select_one(".title")
                company_elem = item.select_one(".company")
                link_elem = item.select_one("a")
                
                if not title_elem or not link_elem:
                    continue
                
                titulo = title_elem.get_text(strip=True)
                empresa = company_elem.get_text(strip=True) if company_elem else "desconocida"
                
                url_oferta = self.BASE_URL + link_elem.get("href", "")
                oferta_id = url_oferta.split("/")[-1] if url_oferta else titulo
                
                ciudad = "Remoto"
                
                ofertas.append(JobOffer(
                    id=f"weworkremotely-{oferta_id}",
                    titulo=titulo,
                    empresa=empresa,
                    email_contacto=None,
                    url_oferta=url_oferta,
                    portal_origen="WeWorkRemotely",
                    fecha_publicacion=date.today(),
                    descripcion="Trabajo remoto",
                    ciudad=ciudad,
                    categoria="IT / Desarrollo"
                ))
            except Exception as e:
                logger.debug(f"Error parseando oferta WeWorkRemotely: {e}")
                continue
        
        logger.info(f"WeWorkRemotely: {len(ofertas)} ofertas extraídas")
        return ofertas
