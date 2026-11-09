"""Point d'entrée : exécute le pipeline complet."""

from dashboard.dashboard import show_dashboard
from ingestion.read import ingest
from logger import get_logger
from processing.aggregation import aggregate
from processing.extract_transform import parse_all
from processing.geolocation import resolve_countries

logger = get_logger("main")


def main() -> None:
    logger.info("=== Démarrage du pipeline ===")
    try:
        lines = ingest("data")                                   # 1. Ingestion
        if not lines:
            logger.error("Aucune ligne lue : arrêt du pipeline")
            return

        events = parse_all(lines)                                # 2. Parsing

        failed_ips = {
            e["ip"] for e in events if e["event"] in ("failed", "invalid_user")
        }
        ip_to_country = resolve_countries(failed_ips)            # 3. Géolocalisation

        results = aggregate(events, ip_to_country)               # 4. Agrégation
        show_dashboard(results)                                  # 5. Dashboard
        logger.info("=== Pipeline terminé avec succès ===")
    except Exception:
        logger.exception("Erreur fatale dans le pipeline")


if __name__ == "__main__":
    main()