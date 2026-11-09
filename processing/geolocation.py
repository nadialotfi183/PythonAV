"""Module de géolocalisation : IP -> pays, via la base IPinfo Lite locale (data/geo)."""

import bisect
import csv
import gzip
import ipaddress
import os

from logger import get_logger

logger = get_logger("geolocation")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEO_DIR = os.path.join(PROJECT_ROOT, "data", "geo")

# Pour chaque version d'IP (4 ou 6) : listes triées de débuts, fins et pays
_db: dict[int, dict[str, list]] = {
    4: {"starts": [], "ends": [], "countries": []},
    6: {"starts": [], "ends": [], "countries": []},
}
_loaded = False
_cache: dict[str, str] = {}


def _find_database_file() -> str | None:
    """Cherche le premier fichier .csv ou .csv.gz dans data/geo."""
    try:
        for name in sorted(os.listdir(GEO_DIR)):
            if name.endswith((".csv", ".csv.gz")):
                return os.path.join(GEO_DIR, name)
    except FileNotFoundError:
        logger.error("Dossier introuvable : %s", GEO_DIR)
    except PermissionError:
        logger.error("Permission refusée sur le dossier : %s", GEO_DIR)
    return None


def _row_to_range(row: dict, country_key: str) -> tuple[int, int, int, str]:
    """Transforme une ligne du CSV en (version, début, fin, pays)."""
    if "network" in row:
        network = ipaddress.ip_network(row["network"].strip(), strict=False)
        start, end = network.network_address, network.broadcast_address
    else:
        start = ipaddress.ip_address(row["start_ip"].strip())
        end = ipaddress.ip_address(row["end_ip"].strip())
    return start.version, int(start), int(end), row[country_key].strip()


def load_database() -> bool:
    """Charge la base IPinfo en mémoire. Retourne True si le chargement a réussi."""
    global _loaded
    if _loaded:
        return True

    path = _find_database_file()
    if path is None:
        logger.error("Aucun fichier .csv trouvé dans %s : géolocalisation impossible", GEO_DIR)
        return False

    rows: dict[int, list[tuple[int, int, str]]] = {4: [], 6: []}
    bad_rows = 0

    try:
        opener = gzip.open if path.endswith(".gz") else open
        with opener(path, "rt", encoding="utf-8", errors="replace", newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                logger.error("Fichier vide : %s", path)
                return False

            reader.fieldnames = [name.strip().lower() for name in reader.fieldnames]
            fields = set(reader.fieldnames)

            if "network" not in fields and not {"start_ip", "end_ip"} <= fields:
                logger.error("Colonnes d'IP introuvables (trouvées : %s)", reader.fieldnames)
                return False
            country_key = "country_code" if "country_code" in fields else "country"
            if country_key not in fields:
                logger.error("Colonne pays introuvable (trouvées : %s)", reader.fieldnames)
                return False

            for row in reader:
                try:
                    version, start, end, country = _row_to_range(row, country_key)
                    rows[version].append((start, end, country))
                except (ValueError, KeyError, AttributeError):
                    bad_rows += 1

    except PermissionError:
        logger.error("Permission refusée sur le fichier : %s", path)
        return False
    except (gzip.BadGzipFile, EOFError):
        logger.error("Fichier .gz corrompu : %s", path)
        return False
    except OSError as error:
        logger.error("Erreur de lecture sur %s : %s", path, error)
        return False
    except csv.Error as error:
        logger.error("Fichier CSV invalide %s : %s", path, error)
        return False

    for version, items in rows.items():
        items.sort()
        _db[version]["starts"] = [item[0] for item in items]
        _db[version]["ends"] = [item[1] for item in items]
        _db[version]["countries"] = [item[2] for item in items]

    if bad_rows:
        logger.warning("%d lignes invalides ignorées dans %s", bad_rows, os.path.basename(path))
    total = len(rows[4]) + len(rows[6])
    if total == 0:
        logger.error("Aucune plage d'IP chargée depuis %s", path)
        return False

    logger.info("Base IPinfo chargée : %d plages (%s)", total, os.path.basename(path))
    _loaded = True
    return True


def geo_location(ip: str) -> str:
    """Retourne le code pays d'une IP ("Local" ou "Unknown" si impossible à trouver)."""
    if ip in _cache:
        return _cache[ip]

    try:
        address = ipaddress.ip_address(ip)
    except ValueError:
        logger.warning("IP invalide : %r", ip)
        return "Unknown"

    if address.is_private or address.is_loopback:
        _cache[ip] = "Local"
        return "Local"

    if not load_database():
        return "Unknown"

    table = _db[address.version]
    value = int(address)
    index = bisect.bisect_right(table["starts"], value) - 1

    country = "Unknown"
    if index >= 0 and value <= table["ends"][index]:
        country = table["countries"][index] or "Unknown"
    else:
        logger.debug("IP absente de la base : %s", ip)

    _cache[ip] = country
    return country


def resolve_countries(ips) -> dict[str, str]:
    """Retourne un dictionnaire {ip: pays} pour un ensemble d'IP."""
    result = {ip: geo_location(ip) for ip in ips}
    logger.info("Géolocalisation terminée pour %d IP", len(result))
    return result


if __name__ == "__main__":
    for test_ip in ["88.147.152.239", "127.0.0.1", "pas-une-ip"]:
        print(test_ip, "->", geo_location(test_ip))