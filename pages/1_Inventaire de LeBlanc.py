import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Base de Données", page_icon="📊", layout="wide")

st.title("La Bibliothèque d'Objets")
st.write("Voici la liste des objets actuellement disponibles en jeu.")

fichier_csv = "présentation_objets_complets.csv" 

# On vérifie que le fichier existe pour éviter un crash
if os.path.exists(fichier_csv):
    df = pd.read_csv(fichier_csv, sep=";") 
    
    # 1. Quelques détails sympas en haut
    col1, col2 = st.columns(2)
    col1.metric("Nombre d'objets", len(df))
    col2.metric("Prix Moyen", f"{df['Price'].mean():.0f} Gold")

    st.divider()

    # 2. Filtres interactifs (classe de zinzin)
    st.subheader(" Filtrer les données")
    recherche = st.text_input("Rechercher un objet par nom :", "")
    
    if recherche:
        df_affiche = df[df["Name"].str.contains(recherche, case=False, na=False)]
    else:
        df_affiche = df


    # Préparation et Affichage du tableau


    
    # 1. On sépare les colonnes
    autres_colonnes = [col for col in df_affiche.columns if col not in ["ID", "ImageURL","tag2", "tag3"]]
    colonnes_ordonnees = ["ImageURL"] + autres_colonnes
    
    # 2. On crée le DataFrame final
    df_final = df_affiche[colonnes_ordonnees].copy() # 

    # vasy bref
    if "AttackSpeed" in df_final.columns:
        df_final["AttackSpeed"] = df_final["AttackSpeed"] * 100

    # 3. L'affichage
    st.dataframe(
        df_final,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ImageURL": st.column_config.ImageColumn(
                "Aperçu", 
                width="small"
            ),
            "Price": st.column_config.NumberColumn(
                "Prix d'achat", 
                format="%d "
            ),
            
            "Sell_Price": st.column_config.NumberColumn(
                "Prix de Revente", 
                format="%d "
            ),
            
            "AttackSpeed": st.column_config.NumberColumn(
                "Vitesse d'Attaque",
                format="%.0f %%", 
                help="Bonus de vitesse d'attaque"
            )
        }
    )
else:
    st.error(f" Le fichier '{fichier_csv}' est introuvable à la racine du projet.")
    st.info("Vérifiez que vous avez bien généré le CSV depuis votre Notebook.")