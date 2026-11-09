"""Module de parsing : transforme une ligne de log SSH en dictionnaire."""

import re

from logger import get_logger

logger = get_logger("parsing")

# Début commun : "May 24 00:26:51 ns sshd[1350968]: "
HEADER = (
    r"^(?P<month>\w{3})\s+(?P<day>\d{1,2})\s+(?P<time>\d{2}:\d{2}:\d{2})"
    r"\s+\S+\s+sshd\[\d+\]:\s+"
)
IP = r"(?P<ip>[0-9a-fA-F.:]+)"

# "Failed password for root from 1.2.3.4" / "Failed password for invalid user x from ..."
FAILED = re.compile(
    HEADER + r"Failed \S+ for (?P<invalid>invalid user )?(?P<user>\S*)\s+from " + IP
)
# "Accepted password for alice from 1.2.3.4"
ACCEPTED = re.compile(HEADER + r"Accepted \S+ for (?P<user>\S+) from " + IP)
# "Invalid user admin from 1.2.3.4"
INVALID = re.compile(HEADER + r"Invalid user (?P<user>\S*)\s+from " + IP)


def extract(row: str) -> dict | None:
    """Analyse une ligne et retourne un dictionnaire, ou None si elle ne nous intéresse pas.

    Clés : month, day, time, event ("failed", "accepted", "invalid_user"),
    user, ip, invalid (True si la ligne mentionne un invalid user).
    """
    if not row or not row.strip():
        return None

    try:
        match = INVALID.search(row)
        if match:
            data = match.groupdict()
            data.update(event="invalid_user", invalid=True)
            return data

        match = FAILED.search(row)
        if match:
            data = match.groupdict()
            data.update(event="failed", invalid=bool(data["invalid"]))
            return data

        match = ACCEPTED.search(row)
        if match:
            data = match.groupdict()
            data.update(event="accepted", invalid=False)
            return data
    except Exception as error:  # sécurité : une ligne ne doit jamais tout arrêter
        logger.error("Erreur de parsing sur la ligne %r : %s", row, error)

    return None


def parse_all(lines: list[str]) -> list[dict]:
    """Analyse toutes les lignes et retourne la liste des événements trouvés."""
    events: list[dict] = []
    ignored = 0

    for line in lines:
        event = extract(line)
        if event:
            events.append(event)
        else:
            ignored += 1

    logger.info("Parsing terminé : %d événements, %d lignes ignorées", len(events), ignored)
    if not events:
        logger.warning("Aucun événement reconnu : vérifie le format des logs")
    return events


if __name__ == "__main__":
    from collections import Counter

    from ingestion.read import ingest

    result = parse_all(ingest("data"))
    print(Counter(e["event"] for e in result))
    for e in result[:3]:
        print(e)