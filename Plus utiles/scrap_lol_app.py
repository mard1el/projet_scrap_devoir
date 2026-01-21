import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import requests
    import polars as pl
    return mo, pl, requests


@app.cell
def _(pl, requests):
    url = "https://ddragon.leagueoflegends.com/cdn/15.24.1/data/en_US/champion.json"
    response = requests.get(url)
    data = response.json()

    # On accède au dictionnaire des champions
    champions_dict = data['data']

    rows = []
    for champ_name, details in champions_dict.items():
        stats = details['stats']
        info = details['info']
        rows.append({
            "Name": champ_name,
            "Class": details['tags'][0],
            "AttackRange": stats['attackrange'],
            "MoveSpeed": stats['movespeed'],
            "HP": stats['hp'],
            "HPperLevel": stats['hpperlevel'],
            "HPRegen": stats['hpregen'],
            "HPRegenperLevel": stats['hpregenperlevel'],
            "Armor": stats['armor'],
            "ArmorperLevel": stats['armorperlevel'],
            "AttackDamage": stats['attackdamage'],
            "AttackDamageperLevel": stats['attackdamageperlevel'],
            "AttackSpeed": stats['attackspeed'],
            "AttackSpeedperLevel": stats['attackspeedperlevel'],
            "Spellblock": stats['spellblock'],
            "SpellblockperLevel": stats['spellblockperlevel'],
            "Prv_attack": info['attack'],
            "Prv_defense": info['defense'],
            "Prv_magic": info['magic']
        })
    
        tableau_champ = pl.DataFrame(rows)
    return (tableau_champ,)


@app.cell
def _(mo, tableau_champ):
    # On récupère la liste de toutes les classes uniques (Mage, Fighter, etc.)
    liste_classes = sorted(tableau_champ["Class"].unique().to_list())

    # Création du champ de texte
    recherche = mo.ui.text(label="Nom du champion :", placeholder="Ex: Ahri...")

    # Création du bouton de sélection de classe (on ajoute "Toutes" par défaut)
    filtre_classe = mo.ui.dropdown(
        options=["Toutes"] + liste_classes, 
        value="Toutes", 
        label="Filtrer par Classe :"
    )

    # On affiche les deux côte à côte
    mo.hstack([recherche, filtre_classe])
    return filtre_classe, recherche


@app.cell
def _(filtre_classe, mo, pl, recherche, tableau_champ):
    # 1. On commence par filtrer selon le texte
    df_final = tableau_champ.filter(
        pl.col("Name").str.to_lowercase().str.contains(recherche.value.lower())
    )

    # 2. On ajoute le filtre de classe si une classe spécifique est choisie
    if filtre_classe.value != "Toutes":
        df_final = df_final.filter(pl.col("Class") == filtre_classe.value)

    # 3. Affichage final
    mo.vstack([
        mo.md(f"#  Database ({len(df_final)} champions trouvés)"),
        df_final
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Préparation pour la classification
    """)
    return


@app.cell
def _(mo, pl, tableau_champ):
    # 1. On crée une liste des classes uniques
    classes_uniques = tableau_champ["Class"].unique().to_list()

    # 2. On crée un dictionnaire de correspondance
    mapping_classes = {nom: i for i, nom in enumerate(classes_uniques)}

    # 3. On ajoute une colonne numérique au tableau
    df_prepare = tableau_champ.with_columns(
        pl.col("Class").replace(mapping_classes).alias("Class_ID")
    )

    # On affiche la correspondance pour s'en souvenir
    mo.md(f"**Correspondance :** {mapping_classes}")
    return (df_prepare,)


@app.cell
def _(df_prepare):
    df_prepare
    return


if __name__ == "__main__":
    app.run()
