"""Module dashboard : affiche les résultats (texte + graphiques matplotlib)."""

import os

import matplotlib.pyplot as plt

from logger import get_logger

logger = get_logger("dashboard")


def print_report(results: dict, top_n: int = 10) -> None:
    """Affiche les résultats dans le terminal."""
    print("\n===== DASHBOARD =====")
    print(f"\nTentatives échouées avec un invalid user : {results['invalid_user_count']}")

    print(f"\nTentatives échouées par pays (top {top_n}) :")
    for country, count in results["failed_by_country"].most_common(top_n):
        print(f"  {country:<25} {count}")

        print(f"\nTentatives réussies par utilisateur (top {top_n}) :")
    if not results["success_by_user"]:
        print("  Aucune connexion réussie dans les logs analysés")
    for user, count in results["success_by_user"].most_common(top_n):
        print(f"  {user:<25} {count}")
    print()


def show_dashboard(results: dict, top_n: int = 10, output_dir: str = "output") -> None:
    """Affiche le rapport texte puis les graphiques."""
    try:
        print_report(results, top_n)

        failed = results["failed_by_country"].most_common(top_n)
        success = results["success_by_user"].most_common(top_n)

        if not failed and not success:
            logger.warning("Aucune donnée à afficher dans les graphiques")
            return

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        if failed:
            ax1.barh([c for c, _ in failed][::-1], [n for _, n in failed][::-1], color="tab:red")
        ax1.set_title("Tentatives échouées par pays")
        ax1.set_xlabel("Nombre de tentatives")

        if success:
            ax2.barh([u for u, _ in success][::-1], [n for _, n in success][::-1], color="tab:green")
            ax2.set_xlabel("Nombre de connexions")
        else:
            ax2.text(0.5, 0.5, "Aucune connexion réussie\ndans les logs analysés",
                     ha="center", va="center", fontsize=14)
            ax2.set_axis_off()
        ax2.set_title("Tentatives réussies par utilisateur")

        fig.suptitle(f"Invalid user : {results['invalid_user_count']} tentatives échouées")
        fig.tight_layout()

        try:
            os.makedirs(output_dir, exist_ok=True)
            image_path = os.path.join(output_dir, "dashboard.png")
            fig.savefig(image_path)
            logger.info("Graphique sauvegardé : %s", image_path)
        except OSError as error:
            logger.error("Impossible de sauvegarder l'image : %s", error)

        plt.show()

    except KeyError as error:
        logger.error("Résultat manquant dans les données : %s", error)
    except Exception as error:
        logger.exception("Erreur d'affichage du dashboard : %s", error)


if __name__ == "__main__":
    from collections import Counter

    show_dashboard({
        "failed_by_country": Counter({"FR": 5, "CN": 12, "RU": 8}),
        "success_by_user": Counter({"alice": 3, "root": 1}),
        "invalid_user_count": 9,
    })