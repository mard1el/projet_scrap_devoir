import streamlit as st
import pandas as pd
import os
from streamlit_extras.metric_cards import style_metric_cards 
import plotly.graph_objects as go

st.set_page_config(page_title="Champions LoL", page_icon="🏆", layout="wide")

# Chargement
file_path = "présentation_champions_complets.csv"

if not os.path.exists(file_path):
    st.error(f" Le fichier '{file_path}' est introuvable")
    st.stop()

df = pd.read_csv(file_path, sep=";")

# Titre et description
st.title(" Encyclopédie des Champions")
st.markdown("Explorez les statistiques, les compétences et l'histoire des champions.")

# Filtrage des champions
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

# Fiche détaillée
with tab2:
    if not df_filtered.empty:
        selected_champ_name = st.selectbox("Sélectionnez un champion :", df_filtered["Name"].unique())
        
        champ = df_filtered[df_filtered["Name"] == selected_champ_name].iloc[0]
        
        st.divider()
        
        # Mise en page : Image à gauche, Radar et Infos à droite
        c1, c2 = st.columns([1, 2])
        
        with c1:
            st.image(champ["Image_Loading"], use_container_width=True)
            
            # Petit bloc de Lore sous l'image
            with st.expander("📖 Lire l'histoire", expanded=False):
                st.write(f"_{champ['Lore']}_")
            
        with c2:
            st.header(f"{champ['Name']} - {champ['Title']}")
            st.caption(f"Classe : {champ['Class']}")
            
            # --- CRÉATION DU SPIDER CHART (RADAR) ---
            
            # 1. Normalisation (Pour que tout soit sur une échelle de 0 à 100)
            # On définit des "Max" arbitraires pour le niveau 1
            # Ex: 700 PV est considéré comme 100/100 pour un niveau 1
            values = [
                (champ["HP"] / 700) * 100,           # PV
                (champ["AttackDamage"] / 70) * 100,  # Attaque
                (champ["Armor"] / 40) * 100,         # Armure
                (champ["Spellblock"] / 40) * 100,    # Res. Magique
                (champ["AttackRange"] / 650) * 100,  # Portée
                (champ["MoveSpeed"] / 355) * 100     # Vitesse
            ]
            
            # On s'assure que ça ne dépasse pas 100 (pour les cas extrêmes)
            values = [min(v, 100) for v in values]
            
            # On boucle la liste pour fermer le graphique
            categories = ['PV', 'Attaque', 'Armure', 'Res. Magique', 'Portée', 'Vitesse']
            
            # 2. Construction du Graphique
            fig = go.Figure()

            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=champ['Name'],
                line_color='#C89B3C', # Or Hextech
                fillcolor='rgba(200, 155, 60, 0.5)' # Or semi-transparent
            ))

            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100], # L'échelle fixe est importante pour comparer !
                        showticklabels=False, # On cache les chiffres 0, 20, 40... pour le look
                        linecolor='#444'
                    ),
                    bgcolor='rgba(0,0,0,0)' # Fond transparent
                ),
                showlegend=False,
                margin=dict(l=40, r=40, t=20, b=20), # Marges réduites
                height=300, # Hauteur compacte
                paper_bgcolor='rgba(0,0,0,0)', # Fond général transparent
                font=dict(color='white') # Texte en blanc
            )

            st.plotly_chart(fig, use_container_width=True)
            
            # On affiche quand même les vraies valeurs en petit dessous
            cols_stats = st.columns(6)
            stats_raw = [
                ("PV", champ["HP"]), 
                ("AD", champ["AttackDamage"]), 
                ("ARM", champ["Armor"]), 
                ("MR", champ["Spellblock"]),
                ("Range", champ["AttackRange"]), 
                ("MS", champ["MoveSpeed"])
            ]
            
            for i, (label, val) in enumerate(stats_raw):
                cols_stats[i].metric(label, int(val))

        st.divider()
        
        # --- Les sorts ---
        st.subheader("Compétences")
        cols_spells = st.columns(5)
        
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
                # Gestion d'erreur si l'image manque
                if pd.notna(champ[icon_col]):
                     st.image(champ[icon_col], width=50)
                st.markdown(f"**{champ[name_col]}**")
                with st.popover("Description"):
                    st.write(champ[desc_col])

    else:
        st.warning("Aucun champion ne correspond aux filtres actuels.")