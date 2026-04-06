# Buscador IT Remote

Sistema automatizado de búsqueda y postulación de trabajos IT/remoto.

## Descripción

Proyecto similar a "Job Search Automation" pero orientado específicamente a:
- Trabajos remotos de IT
- Postulación vía portal (sin email directo)
- Empresas tecnológicas regionales y multinacionales

## Características

- Scraping de portales remote (RemoteOK, WeWorkRemotely, LinkedIn)
- Cooldown por empresa (evitar spam)
- Fallback a empresas tecnológicas locales/regionales
- Registro SQLite del historial de postulaciones
- Plantillas de email adaptadas a IT

## Estructura

```
buscador-it-remote/
├── main.py
├── config.py
├── .env
├── scrapers/
│   ├── base.py
│   ├── remote_ok.py
│   ├── we_work_remotely.py
│   └── linkedin.py
├── core/
│   ├── models.py
│   ├── history_manager.py
│   ├── job_filter.py
│   ├── email_sender.py
│   ├── fallback.py
│   └── reporter.py
├── templates/
├── data/
│   ├── tech_companies.json
│   └── blacklist.txt
└── logs/
```

## Configuración

1. Copiar `.env` y configurar credenciales SMTP
2. Agregar CV en `assets/cv.pdf`
3. Ajustar `data/tech_companies.json` con empresas target

## Uso

```bash
python main.py
```

## Estado

Proyecto en desarrollo.
