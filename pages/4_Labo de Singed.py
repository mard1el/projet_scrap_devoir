import streamlit as st
import joblib
import pandas as pd
import plotly.express as px
import os # Nécessaire pour vérifier le fichier

st.set_page_config(page_title="Devinette de Classe", page_icon="🔮", layout="wide")

# Format : "NomColonne": (Min, Max, Pas, Défaut)
STATS_CONFIG = {
    "HP":                   (300.0, 700.0, 10.0,   630.0),  # Jinx
    "HPperLevel":           (50.0,  150.0,  1.0,   105.0),
    "MoveSpeed":            (300.0, 450.0,  5.0,   325.0),  # Lente sans passif
    "Armor":                (15.0,  50.0,  1.0,    26.0),   # Très fragile
    "ArmorperLevel":        (0.0,   10.0,   0.1,    4.7),
    "Spellblock":           (20.0,  100.0,  1.0,   30.0), 
    "spellblockperlevel":   (0.0,   5.0,    0.1,    1.3),
    "AttackRange":          (100.0, 850.0,  25.0,  525.0),  # Portée standard ADC
    "hpregen":              (0.0,   20.0,   0.1,    3.75),
    "hpregenperlevel":      (0.0,   5.0,    0.1,    0.5),
    "AttackDamage":         (40.0,  100.0,  1.0,   59.0),
    "AttackDamageperLevel": (0.0,   10.0,   0.1,    3.15),
    "attackspeed":          (0.4,   1.5,    0.001, 0.625), 
    "attackspeedperlevel":  (0.0,   6.0,    0.1,    1.0),
    'Prv_attack':           (0.0,   10.0,   1.0,    9.0),   # Jinx tape fort
    'Prv_defense':          (0.0,   10.0,   1.0,    2.0),   # Défense en carton
    'Prv_magic':            (0.0,   10.0,   1.0,    4.0)
}

# --- CHARGEMENT DES MODÈLES ---

@st.cache_resource
def load_rf_model():
    try:
        return joblib.load("lol_champ_model.pkl")
    except FileNotFoundError:
        return None

@st.cache_resource
def load_knn_model():
    path = "knn_data.pkl"
    if os.path.exists(path):
        return joblib.load(path)
    return None

data_rf = load_rf_model()
data_knn = load_knn_model()

if data_rf is None:
    st.error("Le fichier 'lol_champ_model.pkl' est introuvable.")
    st.stop()

model_rf = data_rf["pipeline"]
features_rf = data_rf["features"]
classes_noms = model_rf.classes_ 

# ==============================================================================
# 1. NOUVELLE LOGIQUE : PRÉ-REMPLISSAGE (CALLBACK & SESSION STATE)
# ==============================================================================

# On récupère le dataframe de référence s'il existe
df_ref = data_knn['data'] if data_knn else None

def charger_stats_champion():
    """Fonction appelée automatiquement quand on change le champion dans la liste"""
    choix = st.session_state.selected_champ_name
    
    if choix != "Personnalisé" and df_ref is not None:
        # On trouve la ligne du champion
        row = df_ref[df_ref['Name'] == choix].iloc[0]
        
        # On met à jour chaque stat dans le session_state
        for feature in features_rf:
            if feature in row:
                valeur = float(row[feature])
                
                # IMPORTANT : On vérifie que la valeur est dans les bornes du slider
                cfg = STATS_CONFIG.get(feature, (0.0, 100.0, 1.0, 50.0))
                v_min, v_max, _, _ = cfg
                
                # On "clip" la valeur entre min et max pour éviter les erreurs
                if valeur < v_min: valeur = v_min
                if valeur > v_max: valeur = v_max
                
                # Mise à jour de la mémoire de l'app
                st.session_state[feature] = valeur

# Liste des noms pour le menu déroulant
liste_champions = ["Personnalisé"]
if df_ref is not None:
    liste_champions += sorted(df_ref['Name'].unique().tolist())

# 2. interface utilisateur

st.title("🧪 Le Labo de Singed")
st.markdown("Ajustez les statistiques ci-dessous. L'IA devinera la classe et trouvera les champions existants similaires.")

# LE MENU DÉROULANT (NOUVEAU)
st.selectbox(
    "Charger un spécimen connu (Optionnel) :",
    options=liste_champions,
    key="selected_champ_name",
    on_change=charger_stats_champion # Déclenche la mise à jour des sliders
)

# formulaire
with st.form("form_prediction"):
    st.write("### Paramètres du champion")
    
    user_inputs = {}
    cols = st.columns(3) 
    
    # On utilise les clés de STATS_CONFIG pour être sûr de tout afficher
    for i, feature_name in enumerate(features_rf):
        col = cols[i % 3]
        
        # Récupération config ou valeurs par défaut
        cfg = STATS_CONFIG.get(feature_name, (0.0, 100.0, 1.0, 50.0))
        v_min, v_max, v_step, v_default = cfg
        
        # --- MODIFICATION IMPORTANTE ICI ---
        # 1. Si la variable n'existe pas encore en mémoire, on la crée avec la valeur par défaut
        if feature_name not in st.session_state:
            st.session_state[feature_name] = float(v_default)

        with col:
            # 2. On ajoute 'key=feature_name' pour lier le slider à la mémoire (Session State)
            val = st.slider(
                label=feature_name,
                min_value=float(v_min),
                max_value=float(v_max),
                step=float(v_step),
                key=feature_name #Permet au menu déroulant de changer le slider
            )
            user_inputs[feature_name] = val
    
    st.markdown("---")
    submitted = st.form_submit_button("✨ Analyser le Specimen", use_container_width=True)

# --- RÉSULTATS (CODE D'ORIGINE) ---
if submitted:
    # 1. PRÉDICTION CLASSE (Random Forest)
    X_user = pd.DataFrame([user_inputs])
    # On s'assure de l'ordre pour le RF
    X_user_rf = X_user[features_rf] 

    prediction_label = model_rf.predict(X_user_rf)[0]
    probas = model_rf.predict_proba(X_user_rf)[0]
    
    df_resultats = pd.DataFrame({"Classe": classes_noms, "Probabilité": probas})
    df_resultats = df_resultats.sort_values(by="Probabilité", ascending=False)
    
    st.divider()
    
    # Affichage RF
    col_g, col_d = st.columns([1, 2])
    with col_g:
        st.subheader("Verdict")
        st.success(f"C'est un **{prediction_label}** !")
        st.caption("Certitude :")
        for index, row in df_resultats.head(3).iterrows():
            st.write(f"**{row['Classe']}** : {row['Probabilité']:.1%}")

    with col_d:
        fig = px.pie(
            df_resultats,
            values='Probabilité',
            names='Classe', 
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

    # 2. RECHERCHE DE SOSIES (KNN)
    if data_knn:
        st.divider()
        st.subheader("🧬 Champions Génétiquement Proches")
        st.caption("Basé sur la proximité statistique des individus.")
        
        knn_model = data_knn['model']
        knn_scaler = data_knn['scaler']
        df_ref = data_knn['data']
        knn_features_order = data_knn['features'] # L'ordre CRUCIAL
        
        try:
            # A. On reconstruit la liste dans le bon ordre pour le KNN
            # On pioche dans le dictionnaire user_inputs
            knn_values = [user_inputs[f] for f in knn_features_order]
            
            # B. On scale
            knn_scaled = knn_scaler.transform([knn_values])
            
            # C. On prédit (4 voisins)
            distances, indices = knn_model.kneighbors(knn_scaled, n_neighbors=4)
            
            # D. Affichage
            cols_knn = st.columns(4)
            
            for i, idx in enumerate(indices[0]):
                champion = df_ref.iloc[idx]
                dist = distances[0][i]
                
                with cols_knn[i]:
                    # Image
                    if pd.notna(champion.get('Image_Loading')):
                        st.image(champion['Image_Loading'], use_container_width=True)
                    
                    st.markdown(f"**{champion['Name']}**")
                    st.caption(f"Classe réelle : {champion['Class']}")
                    
                    # Score de ressemblance
                    score = max(0, 100 - (dist * 10))
                    st.progress(int(score)/100, text=f"Similarité : {int(score)}%")
                    
        except KeyError as e:
            st.error(f"Erreur de configuration : Le KNN attend la colonne {e} qui manque dans les sliders.")
    else:
        st.warning("Fichier 'knn_data.pkl' manquant. Lancez 'train_knn.py' pour activer les recommandations.")