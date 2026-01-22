import streamlit as st
import joblib
import pandas as pd


# 1. Chargement du "Package"
# Le @st.cache_resource évite de recharger le fichier à chaque clic
@st.cache_resource
def load_model():
    return joblib.load("lol_price_model.pkl")

data = load_model()
pipeline = data["pipeline"]
features_order = data["features"] # C'est ta liste ["AD", "AP", "HP", ...]

#st.title(" LoL Price Estimator")
col1, col2 = st.columns([1, 5])

with col1:
    st.image("https://ddragon.leagueoflegends.com/cdn/16.1.1/img/profileicon/588.png", width=80)

with col2:
    st.title("Estiamateur de Prix d'Objets")

#1. Dictionnaire des Images

stat_icons = {
    "AD": "https://ddragon.leagueoflegends.com/cdn/16.1.1/img/item/1038.png",
    "AP": "https://ddragon.leagueoflegends.com/cdn/16.1.1/img/item/1026.png",
    "HP": "https://ddragon.leagueoflegends.com/cdn/16.1.1/img/item/1028.png",
    "Armor": "https://ddragon.leagueoflegends.com/cdn/16.1.1/img/item/1029.png",
    "MR": "https://ddragon.leagueoflegends.com/cdn/16.1.1/img/item/1057.png",
    "Mana": "https://ddragon.leagueoflegends.com/cdn/16.1.1/img/item/1027.png",
    "AttackSpeed": "https://ddragon.leagueoflegends.com/cdn/16.1.1/img/item/1042.png",
    "MoveSpeed": "https://ddragon.leagueoflegends.com/cdn/16.1.1/img/item/1001.png",
    "CritChance": "https://ddragon.leagueoflegends.com/cdn/16.1.1/img/item/3031.png",
    "AbilityHaste": "https://ddragon.leagueoflegends.com/cdn/16.1.1/img/item/6675.png",
    "Lethality": "https://ddragon.leagueoflegends.com/cdn/16.1.1/img/item/3134.png",
    "MagicPen": "https://ddragon.leagueoflegends.com/cdn/16.1.1/img/item/4645.png",
    "Omnivamp": "https://ddragon.leagueoflegends.com/cdn/16.1.1/img/item/4633.png",
    "LifeSteal": "https://ddragon.leagueoflegends.com/cdn/16.1.1/img/item/1053.png"
}

# --- 2. Initialisation ---
user_inputs = {} # On stocke les valeurs ici
cols = st.columns(3) # Grille de 3 colonnes

# --- 3. La Boucle d'affichage ---
for i, feature_name in enumerate(features_order):
    col = cols[i % 3] # On alterne entre colonne 1, 2 et 3
    
    with col:
        # A. En-tête : Image + Nom de la stat
        # On divise la colonne en deux petites sous-parties (Image | Texte)
        sub_col1, sub_col2 = st.columns([1, 4])
        
        with sub_col1:
            # On affiche l'image si on l'a, sinon un emoji
            img_url = stat_icons.get(feature_name)
            if img_url:
                st.image(img_url, width=35) # width=35 pixels est idéal
            else:
                st.write("❓") 
        
        with sub_col2:
            # On écrit le nom de la stat verticalement centré
            # Le HTML/CSS ici sert à aligner le texte proprement avec l'image
            st.markdown(f"<h5 style='margin-top: 5px;'>{feature_name}</h5>", unsafe_allow_html=True)

        # B. La zone de saisie (Input)
        # On cache le label ("label_visibility") car on a déjà mis le titre au-dessus
        val = st.number_input(
            label=feature_name, # Sert juste pour l'accessibilité ici
            label_visibility="collapsed", # On cache le titre intégré
            value=0.0,
            step=1.0 if "Speed" in feature_name else 5.0, # Pas de 0.1 pour la vitesse d'attaque, on met des %
            key=feature_name # Indispensable pour que Streamlit ne s'embrouille pas
        )
        
        # C. On sauvegarde la valeur
        user_inputs[feature_name] = val
    
    # Un petit espacement vertical pour aérer les lignes
    if (i + 1) % 3 == 0:
        st.write("")

# 3. Prédiction
if st.button(" Estimer le Prix"):
    # C'est ici que la magie opère :
    # On transforme le dictionnaire {'AD': 50, 'AP': 0...} en DataFrame
    df_predict = pd.DataFrame([user_inputs])
    
    # Sécurité : On s'assure que les colonnes sont dans le BON ORDRE (celui du pickle)
    # Même si le dictionnaire le gère souvent bien, c'est une sécurité vitale.
    df_predict = df_predict[features_order]
    
    # Le Pipeline s'occupe de tout (Scaling + Huber)
    prediction = pipeline.predict(df_predict)[0]
    
    st.success(f"Prix estimé : **{prediction:.0f} Gold**")
    
    # Petit bonus visuel
    if prediction > 10000:
        st.info("ça fait beaucoup là non ?")
    elif prediction > 3000:
        st.warning("C'est un objet Legendaire !")
    elif prediction < 0:
        st.info("cette abomination ne devrait pas exister...")
    