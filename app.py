import streamlit as st

st.set_page_config(
    page_title="Accueil",
    page_icon="🏠",
)

st.title("Bienvenu dans le labo")

st.image("https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Ornn_0.jpg", use_container_width=True)

st.markdown("""
### À propos de cet outil
Ce projet sur League of Legends permet un accès facile à une base de données complète des objets et champions du jeu.
Il met aussi à disposition un outil d'aide à la création d'objets et de champion pour ne pas ruiner la méta déjà fragile



---
*Créé avec Python, Scikit-Learn et Streamlit.*
""")