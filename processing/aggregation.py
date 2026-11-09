"""Module d'agrégation : calcule les statistiques demandées par le sujet."""

from collections import Counter

from logger import get_logger

logger = get_logger("aggregation")


def aggregate(events: list[dict], ip_to_country: dict[str, str]) -> dict:
    """Calcule les 3 résultats du dashboard.

    Returns:
        {"failed_by_country": Counter, "success_by_user": Counter,
         "invalid_user_count": int}
    """
    failed_by_country: Counter = Counter()
    success_by_user: Counter = Counter()
    invalid_user_count = 0

    if not events:
        logger.warning("Aucun événement à agréger")

    for event in events:
        try:
            kind = event["event"]

            if kind == "invalid_user":
                invalid_user_count += 1
                failed_by_country[ip_to_country.get(event["ip"], "Unknown")] += 1

            elif kind == "failed" and not event["invalid"]:
                # Les "failed" sur invalid user sont déjà comptés via "invalid_user"
                failed_by_country[ip_to_country.get(event["ip"], "Unknown")] += 1

            elif kind == "accepted":
                success_by_user[event["user"]] += 1

        except KeyError as error:
            logger.error("Événement incomplet (clé manquante %s) : %s", error, event)

    logger.info(
        "Agrégation : %d pays, %d utilisateurs, %d invalid user",
        len(failed_by_country), len(success_by_user), invalid_user_count,
    )
    return {
        "failed_by_country": failed_by_country,
        "success_by_user": success_by_user,
        "invalid_user_count": invalid_user_count,
    }


if __name__ == "__main__":
    fake_events = [
        {"event": "failed", "user": "root", "ip": "1.1.1.1", "invalid": False},
        {"event": "invalid_user", "user": "admin", "ip": "2.2.2.2", "invalid": True},
        {"event": "failed", "user": "admin", "ip": "2.2.2.2", "invalid": True},
        {"event": "accepted", "user": "alice", "ip": "1.1.1.1", "invalid": False},
        {"event": "accepted", "user": "alice", "ip": "1.1.1.1", "invalid": False},
        {"event": "failed"},  # incomplet : doit être logué sans planter
    ]
    print(aggregate(fake_events, {"1.1.1.1": "FR", "2.2.2.2": "CN"}))