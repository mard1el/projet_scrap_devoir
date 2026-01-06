import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium")


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
 
    """)
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    On va tenter de mettre le fichier de bookstoscrap sous forme d'app sous marimo
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    importation
    """)
    return


@app.cell
def _():
    import requests
    from bs4 import BeautifulSoup
    import re
    import time
    import polars as pl
    return BeautifulSoup, pl, re, requests


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    choix du nombre de pages
    """)
    return


@app.cell
def _(mo):
    nombre_pages = mo.ui.slider(1, 50, label="Nombre de pages à scraper", value=5)
    return (nombre_pages,)


@app.cell
def _(mo, nombre_pages):

    mo.vstack([
        mo.md("### Choix du nombre de pages :"),
        nombre_pages,
        mo.md(f"## Le nombre de pages est de : {nombre_pages.value}")
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    on commence
    """)
    return


@app.cell
def _(BeautifulSoup, nombre_pages, pl, re, requests):
    def scrapper_donnees(nb):
        base_url = "https://books.toscrape.com/catalogue/page-{}.html"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0'}
        tous_les_produits = []

        for numero_page in range(1, nb + 1):
            reponse = requests.get(base_url.format(numero_page), headers=headers)
            if reponse.status_code != 200:
                break
        
            soup = BeautifulSoup(reponse.text, 'html.parser')
            for produit in soup.select(".product_pod"):
                balise_titre = produit.select_one("h3 a")
                titre = balise_titre["title"] if balise_titre else "Inconnu"
            
                balise_prix = produit.select_one(".price_color")
                if balise_prix:
                    chiffres = re.findall(r"[0-9.]+", balise_prix.text)
                    if chiffres:
                        tous_les_produits.append({
                            "titre": titre, 
                            "prix": float(chiffres[0]),
                            "page": numero_page
                        })
        return pl.from_dicts(tous_les_produits) if tous_les_produits else pl.DataFrame()

    # On exécute la fonction avec la valeur du curseur
    df = scrapper_donnees(nombre_pages.value)
    return (df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    cellule d'affichage
    """)
    return


@app.cell
def _(df, mo):
    if not df.is_empty():
        # Affichage du tableau interactif
        table = mo.ui.table(df)
    
        # Calcul de statistiques
        stats = mo.md(f"""
        ### Statistiques
        - **Total :** {len(df)} livres
        - **Prix moyen :** {df['prix'].mean():.2f} £
        """)
    
        mo.vstack([stats, table])
    else:
        mo.md("Aucune donnée chargée. Modifiez le curseur pour lancer le scraping.")
    return


if __name__ == "__main__":
    app.run()
