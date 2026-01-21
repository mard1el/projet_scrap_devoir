import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Champions LoL", page_icon="🏆", layout="wide")

#chargement
file_path = "présentation_champions_complets.csv"

if not os.path.exists(file_path):
    st.error(f" Le fichier '{file_path}' est introuvable")
    st.stop()

df = pd.read_csv(file_path, sep=";")

#titre et description
st.title("🏆 Encyclopédie des Champions")
st.markdown("Explorez les statistiques, les compétences et l'histoire des champions.")

# filtrage des champions
col_filter1, col_filter2 = st.columns(2)
with col_filter1:
    classes_dispo = ["Tous"] + sorted(list(df["Class"].unique()))
    choix_classe = st.selectbox("Filtrer par Classe :", classes_dispo)

with col_filter2:
    search_term = st.text_input("Rechercher un champion :", "")

# Application des filtres
df_filtered = df.copy()
if choix_classe != "Tous":
    df_filtered = df_filtered[df_filtered["Class"] == choix_classe]

if search_term:
    df_filtered = df_filtered[df_filtered["Name"].str.contains(search_term, case=False)]

# 2 Onglets
tab1, tab2 = st.tabs(["Tableau Comparatif", "Fiche Détaillée"])

# Le tableau
with tab1:
    st.caption(f"{len(df_filtered)} champions trouvés.")
    
    # Configuration des colonnes pour afficher les images
    st.dataframe(
        df_filtered[["Name", "Title", "Class", "ImageURL", "HP", "MoveSpeed", "AttackRange", "AttackDamage", "Armor"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "ImageURL": st.column_config.ImageColumn("Aperçu", width="small"),
            "HP": st.column_config.ProgressColumn("PV de base", min_value=400, max_value=700, format="%d"),
            "MoveSpeed": st.column_config.NumberColumn("Vitesse", format="%d"),
            "Name": "Nom",
            "Title": "Titre",
            "Class": "Classe"
        }
    )

# fiche détaillée
with tab2:
    # Sélecteur pour choisir un champion spécifique parmi ceux filtrés
    if not df_filtered.empty:
        selected_champ_name = st.selectbox("Sélectionnez un champion pour voir les détails :", df_filtered["Name"].unique())
        
        # Récupération de la ligne unique du champion
        champ = df_filtered[df_filtered["Name"] == selected_champ_name].iloc[0]
        
        st.divider()
        
        #imaaaaaaaaaage
        c1, c2 = st.columns([1, 2])
        
        with c1:
            # Affiche l'image de chargement (format portrait)
            st.image(champ["Image_Loading"], use_container_width=True)
            
        with c2:
            st.header(f"{champ['Name']} - {champ['Title']}")
            st.caption(f"Classe : {champ['Class']}")
            
            # Affichage du Lore dans une boite déroulante
            with st.expander(" Lire l'histoire", expanded=True):
                st.write(f"_{champ['Lore']}_")
            
            # Stats principales en métriques
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("PV Base", champ["HP"], f"+{champ['HPperLevel']}/lvl")
            m2.metric("Attaque (AD)", champ["AttackDamage"], f"+{champ['AttackDamageperLevel']}/lvl")
            m3.metric("Armure", champ["Armor"], f"+{champ['ArmorperLevel']}/lvl")
            m4.metric("Portée", champ["AttackRange"])

        st.divider()
        
        # --- Les sorts (image) ---
        st.subheader("Compétences")
        cols_spells = st.columns(5)
        
        # Liste des sorts à itérer pour éviter de copier-coller le code
        spells_info = [
            ("Passif", "Passive_Name", "Passive_Desc", "Passive_Icon"),
            ("Q", "Spell_Q_Name", "Spell_Q_Desc", "Spell_Q_Icon"),
            ("W", "Spell_W_Name", "Spell_W_Desc", "Spell_W_Icon"),
            ("E", "Spell_E_Name", "Spell_E_Desc", "Spell_E_Icon"),
            ("R", "Spell_R_Name", "Spell_R_Desc", "Spell_R_Icon"),
        ]

        for i, (key, name_col, desc_col, icon_col) in enumerate(spells_info):
            with cols_spells[i]:
                st.markdown(f"**{key}**")
                # Affichage de l'icône du sort
                st.image(champ[icon_col], width=50)
                # Nom du sort en gras
                st.markdown(f"**{champ[name_col]}**")
                # Description en petit avec popover
                with st.popover("Description"):
                    st.write(champ[desc_col])

    else:
        st.warning("Aucun champion ne correspond aux filtres actuels.")