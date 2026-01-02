import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import requests
    from bs4 import BeautifulSoup
    import time

    mo.md("# 📊 Projet : Création d'app sous fond de web scrapping 🏠")
    return (mo,)


@app.cell
def _(mo):
    # On crée des curseurs pour simuler les entrées de ton futur modèle
    surface = mo.ui.slider(start=10, stop=150, value=40, label="Surface (m²)")
    pieces = mo.ui.number(start=1, stop=10, value=2, label="Nombre de pièces")
    return pieces, surface


@app.cell
def _(mo, pieces, surface):
    # Une formule simple pour illustrer la "rationalité" avant d'avoir ton IA
    # (Prix de base + prix au m2 - malus petite surface)
    prix_estime = (surface.value * 3000) + (pieces.value * 5000)

    mo.vstack([
        mo.md(f"### Paramètres du bien :"),
        surface,
        pieces,
        mo.md(f"## 💰 Prix Rationnel Estimé : {prix_estime:,} €".replace(',', ' '))
    ])
    return


@app.cell
def _(mo):
    mo.md(r"""
    C'était grave du blabal
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    création du bouton de scrapp ??
    """)
    return


@app.cell
def _(mo):
    # On crée un bouton pour ne pas scraper par erreur en boucle
    run_scraping = mo.ui.run_button(label="Lancer le Scraping 🚀")
    run_scraping
    return (run_scraping,)


@app.cell
def _(mo, run_scraping):
    # Cette cellule ne s'exécutera QUE si on clique sur le bouton
    mo.stop(not run_scraping.value)

    def scraper_prix(url):
        # Simulation de scraping (remplace par ton vrai code beautifulsoup)
        # headers = {'User-Agent': 'Mozilla/5.0'}
        # response = requests.get(url, headers=headers)
        return {"titre": "Appartement test", "prix": 250000}

    # Exemple de résultat
    donnees = scraper_prix("https://un-site-immobilier.com")
    mo.md(f"Données récupérées : {donnees}")
    return


if __name__ == "__main__":
    app.run()
