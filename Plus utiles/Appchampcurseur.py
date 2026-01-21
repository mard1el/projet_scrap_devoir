import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import joblib

    # Mapping des rôles
    roles_mapping = {
        0: "Combattant",
        1: "Tireur",
        2: "Mage",
        3: "Support",
        4: "Assassin",
        5: "Tank"
    }
    return joblib, mo, pl, roles_mapping


@app.cell
def _(pl):
    class Statchamp:
        def __init__(self, AttackRange, MoveSpeed, HP, HPperLevel, hpregen, 
                     hpregenperlevel, Armor, ArmorperLevel, AttackDamage, 
                     AttackDamageperLevel, attackspeed, attackspeedperlevel, 
                     Spellblock, spellblockperlevel, Prv_attack, Prv_defense, Prv_magic):

            # Stockage des données brutes
            self.raw_data = {
                "AttackRange": [AttackRange],
                "MoveSpeed": [MoveSpeed],
                "HP": [HP],
                "HPperLevel": [HPperLevel],
                "hpregen": [hpregen],
                "hpregenperlevel": [hpregenperlevel],
                "Armor": [Armor],
                "ArmorperLevel": [ArmorperLevel],
                "AttackDamage": [AttackDamage],
                "AttackDamageperLevel": [AttackDamageperLevel],
                "attackspeed": [attackspeed],
                "attackspeedperlevel": [attackspeedperlevel],
                "Spellblock": [Spellblock],
                "spellblockperlevel": [spellblockperlevel],
                "Prv_attack": [Prv_attack],
                "Prv_defense": [Prv_defense],
                "Prv_magic": [Prv_magic]
            }

        def get_dataframe(self):
            """Transforme les données, calcule les stats au lvl 10 et nettoie."""
            df = pl.DataFrame(self.raw_data)

            # 1. Calcul des valeurs au niveau 10
            df = df.with_columns(
                (pl.col("Spellblock") + pl.col("spellblockperlevel") * 9).alias("Spellblock_lvl_10"),
                (pl.col("attackspeed") + pl.col("attackspeedperlevel") * 9).alias("attackspeed_lvl_10"),
                (pl.col("AttackDamage") + pl.col("AttackDamageperLevel") * 9).alias("AttackDamage_lvl_10"),
                (pl.col("Armor") + pl.col("ArmorperLevel") * 9).alias("Armor_lvl_10"),
                (pl.col("hpregen") + pl.col("hpregenperlevel") * 9).alias("hpregen_lvl_10"),
                (pl.col("HP") + pl.col("HPperLevel") * 9).alias("hp_lvl_10")
            )

            # 2. Suppression des colonnes "per level"
            cols_to_drop = [
                "spellblockperlevel", "attackspeedperlevel", "AttackDamageperLevel", 
                "ArmorperLevel", "hpregenperlevel", "HPperLevel"
            ]
            df = df.drop(cols_to_drop)

            # Astuce : On s'assure que les colonnes sont dans l'ordre attendu par le modèle
            # (Si ton modèle est sensible à l'ordre, ajoute un .select() ici avec la liste exacte)
            return df
    return (Statchamp,)


@app.cell
def _(joblib, mo):
    # Chargement sécurisé du modèle
    modele_charge = None
    message_etat = ""

    try:
        # Assure-toi que 'mon_modele_lol.pkl' est dans le même dossier
        loaded_obj = joblib.load('mon_modele_lol.pkl')

        # Si c'est un GridSearch, on prend le meilleur estimateur, sinon le modèle direct
        if hasattr(loaded_obj, "best_estimator_"):
            modele_charge = loaded_obj.best_estimator_
        else:
            modele_charge = loaded_obj

        message_etat = mo.md("✅ **Modèle chargé et prêt.**")
    except FileNotFoundError:
        message_etat = mo.callout("❌ Fichier 'mon_modele_lol.pkl' introuvable.", kind="danger")

    message_etat
    return (modele_charge,)


@app.cell
def _(mo):
    # --- Interface Utilisateur (Inputs) ---
    mo.md("### 📊 Entrez les statistiques du Champion")

    # On utilise mo.ui.dictionary pour garantir la mise à jour automatique
    # Groupe 1 : Survie
    ui_base = mo.ui.dictionary({
        "hp": mo.ui.number(label="PV (Base)", value=650, step=10),
        "hp_lvl": mo.ui.number(label="PV / Niv", value=114, step=1),
        "hpregen": mo.ui.number(label="Regen PV", value=3.5, step=0.1),
        "hpregen_lvl": mo.ui.number(label="Regen PV / Niv", value=0.6, step=0.1),
        "armor": mo.ui.number(label="Armure", value=30, step=1),
        "armor_lvl": mo.ui.number(label="Armure / Niv", value=3.5, step=0.1),
        "spellblock": mo.ui.number(label="Rés. Magique", value=30, step=1),
        "spellblock_lvl": mo.ui.number(label="RM / Niv", value=0.5, step=0.1),
    })

    # Groupe 2 : Offensif
    ui_offensif = mo.ui.dictionary({
        "ad": mo.ui.number(label="Dégâts (AD)", value=60, step=1),
        "ad_lvl": mo.ui.number(label="AD / Niv", value=3, step=1),
        "as": mo.ui.number(label="Vitesse Attaque", value=0.625, step=0.001),
        "as_lvl": mo.ui.number(label="AS / Niv (%)", value=2.5, step=0.1),
        "range": mo.ui.number(label="Portée (Range)", value=175, step=25),
        "ms": mo.ui.number(label="Vitesse Dépl. (MS)", value=340, step=5),
    })

    # Groupe 3 : Notes
    ui_notes = mo.ui.dictionary({
        "prv_atk": mo.ui.slider(start=0, stop=10, value=5, label="Note Attaque"),
        "prv_def": mo.ui.slider(start=0, stop=10, value=5, label="Note Défense"),
        "prv_mag": mo.ui.slider(start=0, stop=10, value=5, label="Note Magie"),
    })

    # Affichage visuel (On n'affiche pas le dictionnaire brut, mais ses composants)
    # mo.ui.dictionary se comporte visuellement comme une liste verticale par défaut, 
    # mais ici on veut garder ta mise en page personnalisée, donc on accède aux éléments via ["cle"]
    mo.vstack([
        mo.md("**🛡️ Défense & Vie**"),
        mo.hstack([ui_base["hp"], ui_base["hp_lvl"], ui_base["hpregen"], ui_base["hpregen_lvl"]], wrap=True),
        mo.hstack([ui_base["armor"], ui_base["armor_lvl"], ui_base["spellblock"], ui_base["spellblock_lvl"]], wrap=True),
    
        mo.md("**⚔️ Offensif & Mouvement**"),
        mo.hstack(list(ui_offensif.values()), wrap=True), # .values() marche ici car c'est un objet UI
    
        mo.md("**📝 Notes Riot**"),
        mo.hstack(list(ui_notes.values()))
    ])
    return ui_base, ui_notes, ui_offensif


@app.cell
def _(
    Statchamp,
    mo,
    modele_charge,
    roles_mapping,
    ui_base,
    ui_notes,
    ui_offensif,
):
    # On récupère les dictionnaires de VALEURS (et non plus les objets UI un par un)
    vals_base = ui_base.value
    vals_off = ui_offensif.value
    vals_notes = ui_notes.value

    # Création de l'objet Champion avec les valeurs extraites
    nouveau_champ = Statchamp(
        AttackRange=vals_off["range"],
        MoveSpeed=vals_off["ms"],
        HP=vals_base["hp"],
        HPperLevel=vals_base["hp_lvl"],
        hpregen=vals_base["hpregen"],
        hpregenperlevel=vals_base["hpregen_lvl"],
        Armor=vals_base["armor"],
        ArmorperLevel=vals_base["armor_lvl"],
        AttackDamage=vals_off["ad"],
        AttackDamageperLevel=vals_off["ad_lvl"],
        attackspeed=vals_off["as"],
        attackspeedperlevel=vals_off["as_lvl"],
        Spellblock=vals_base["spellblock"],
        spellblockperlevel=vals_base["spellblock_lvl"],
        Prv_attack=vals_notes["prv_atk"],
        Prv_defense=vals_notes["prv_def"],
        Prv_magic=vals_notes["prv_mag"]
    )

    # Le reste ne change pas...
    df_pret = nouveau_champ.get_dataframe()
    resultat_affichage = mo.md("⏳ En attente...")

    if modele_charge is not None:
        try:
            prediction_index = modele_charge.predict(df_pret)[0]
            role_texte = roles_mapping.get(prediction_index, "Inconnu")

            # J'ajoute un callout dynamique qui change de couleur selon le rôle
            couleur = "success"
            if "Assassin" in role_texte: couleur = "danger"
            elif "Support" in role_texte: couleur = "info"

            resultat_affichage = mo.callout(
                f"# 🎯 Rôle prédit : **{role_texte}**", 
                kind=couleur
            )
        except Exception as e:
            resultat_affichage = mo.callout(f"Erreur : {e}", kind="danger")

    mo.vstack([
        resultat_affichage,
        mo.accordion({"Voir les données calculées (Lvl 10)": df_pret})
    ])
    return


if __name__ == "__main__":
    app.run()
