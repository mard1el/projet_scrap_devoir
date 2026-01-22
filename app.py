import streamlit as st

# Configuration de la page (si c'est ta page principale app.py)
st.set_page_config(
    page_title="Présentation - LoL Data",
    page_icon="🏠",
    layout="wide"
)

# bannière
BANNER_URL = "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/dcf7c948-8cc2-4b45-af94-df8a20542c55/dc7rff7-dcf8d220-54a7-4e49-8400-1964bd075bd0.jpg/v1/fill/w_1024,h_400,q_75,strp/league_of_legends_banner_by_milesports_dc7rff7-fullview.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7ImhlaWdodCI6Ijw9NDAwIiwicGF0aCI6Ii9mL2RjZjdjOTQ4LThjYzItNGI0NS1hZjk0LWRmOGEyMDU0MmM1NS9kYzdyZmY3LWRjZjhkMjIwLTU0YTctNGU0OS04NDAwLTE5NjRiZDA3NWJkMC5qcGciLCJ3aWR0aCI6Ijw9MTAyNCJ9XV0sImF1ZCI6WyJ1cm46c2VydmljZTppbWFnZS5vcGVyYXRpb25zIl19.UD-p07Au2Pf9nJcjKjxA1j4TWSbbHoyUQk-sXZdcZzo"

st.image(BANNER_URL, use_container_width=True)

st.title("Bienvenue dans la Faille de la Data")
st.markdown("""
**Ce projet a pour but d'analyser les champions de League of Legends à travers la Data Science.**
Que vous soyez un invocateur vétéran ou un fer V, 
cette application vous permet d'explorer les données du jeu, 
de comparer les statistiques et même de tester des intelligence artificielle prédictive.
""")

st.divider()

#kesakoi lol
col_text, col_logo = st.columns([3, 1])

with col_text:
    st.header(" Le Jeu en bref")
    st.write("""
    **League of Legends (LoL)** est un jeu de stratégie en équipe (MOBA) où deux équipes de cinq champions s'affrontent pour détruire la base adverse (le Nexus).
    
    Il existe plus de **160 champions**, chacun possédant :
    * Une histoire unique (Lore)
    * Des compétences spéciales
    * Des **statistiques mathématiques** qui définissent leur rôle (Tank, Mage, Assassin, etc.).
    
    *C'est sur ces statistiques que ce projet se concentre.*
    """)

with col_logo:
    # Logo officiel LoL propre
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/League_of_Legends_2019_vector.svg/1200px-League_of_Legends_2019_vector.svg.png", use_container_width=True)

st.divider()

#lexique des stats
st.header("Comprendre les Données")
st.markdown("Voici les définitions des variables utilisées dans nos analyses et nos modèles prédictifs.")


c1, c2, c3 = st.columns(3)

with c1:
    st.subheader("🛡️ Résistance (Défense)")
    with st.container(border=True):
        st.markdown("""
        **HP (Health Points)** *La vie du champion.* Si elle tombe à 0, il meurt.
        
        **HP per Level** *Le gain de vie* naturel à chaque passage de niveau.
        
        **Armor (Armure)** Réduit les dégâts **physiques** reçus.
        
        **Spellblock (Résistance Magique)** Réduit les dégâts **magiques** reçus.
        """)

with c2:
    st.subheader("⚔️ Offensive (Attaque)")
    with st.container(border=True):
        st.markdown("""
        **Attack Damage (AD)** La puissance des attaques de base (coups blancs) et de certains sorts physiques.
        
        **Attack Speed (AS)** Le nombre d'attaques qu'un champion peut lancer par seconde.
        
        **Attack Range (Portée)** La distance à laquelle un champion peut frapper.  
        *< 150 : Corps à corps (Mêlée)* *> 500 : Distance (Range)*
        """)

with c3:
    st.subheader("⚡ Utilitaire & Ressources")
    with st.container(border=True):
        st.markdown("""
        **Move Speed (Vitesse)** La rapidité de déplacement du champion sur la carte.
        
        **MP (Mana Points)** L'énergie pour lancer des sorts. Certains champions n'en ont pas (énergie, rage, ou rien).
        
        **Regeneration (HP/MP Regen)** La vitesse à laquelle la vie ou le mana remonte tout seul hors combat.
        """)

#provenance des données
st.divider()
with st.expander("D'où viennent ces chiffres ?"):
    st.markdown("""
    Les données proviennent de l'API officielle de Riot Games (**Data Dragon**).
    
    * **Version du Patch :** Dernière version récupérée automatiquement.
    * **Traitement :** Les données ont été nettoyées avec Python (Pandas/Polars).
    * **Machine Learning :** Le modèle de devinette utilise un algorithme **Random Forest** entraîné sur ces statistiques.
    """) 

#bouton suite
if st.button("Commencer l'exploration", use_container_width=True):
    st.switch_page("pages/1_Inventaire de LeBlanc.py")