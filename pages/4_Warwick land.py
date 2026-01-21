import streamlit as st
import joblib
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Devinette de Classe", page_icon="🔮")

# Format : "NomColonne": (Min, Max, Pas, Défaut)
STATS_CONFIG = {
    "HP":               (300.0, 700.0, 10.0,  650.0),
    "HPperLevel":       (50.0,  150.0,  1.0,   114.0),
    "MoveSpeed":        (300.0, 450.0,  5.0,   345.0),
    "Armor":            (15.0,  50.0,  1.0,   38.0),
    "ArmorperLevel":    (0.0,   10.0,   0.1,   3.5),
    "Spellblock":       (20.0,  100.0,  1.0,   30.0), # C'est la Magic Resist
    "SpellblockperLevel":(0.0,   5.0,    0.1,   0.5),
    "AttackRange":      (100.0, 850.0,  25.0,  175.0),
    "hpregen":          (0.0,   20.0,   0.1,   5.0),
    "hpregenperlevel":  (0.0,   5.0,    0.1,   0.5),
    "AttackDamage":     (40.0,  100.0,  1.0,   60.0),
    "AttackDamageperLevel":(0.0, 10.0,   0.1,   3.0),
    "attackspeed":      (0.4,   1.5,    0.001, 0.625), # Très précis pour l'AS
    "attackspeedperlevel":(0.0, 6.0,    0.1,   2.5),
    'Prv_attack':(0.0, 10.0,   1.0,   5.0),
    'Prv_defense':(0.0, 10.0,   1.0,   5.0),
    'Prv_magic':(0.0, 10.0,   1.0,   5.0)
}

#modèle
@st.cache_resource
def load_model():
    try:
        return joblib.load("lol_champ_model.pkl")
    except FileNotFoundError:
        return None

data = load_model()

if data is None:
    st.error("❌ Le fichier 'lol_champ_model.pkl' est introuvable.")
    st.stop()

model = data["pipeline"]
features = data["features"]
classes_noms = model.classes_ 

st.title("🔮 Le Choixpeau Magique de LoL")
st.markdown("Entrez les statistiques, et l'IA devinera la classe du champion.")

#inputs
with st.form("form_prediction"):
    st.write("### 🎚️ Ajustez les statistiques")
    
    user_inputs = {}
    cols = st.columns(3) 
    
    for i, feature_name in enumerate(features):
        col = cols[i % 3]
        

        cfg = STATS_CONFIG.get(feature_name, (0.0, 100.0, 1.0, 50.0))
        
        v_min, v_max, v_step, v_default = cfg
        
        with col:
            val = st.slider(
                label=feature_name,
                min_value=float(v_min),
                max_value=float(v_max),
                value=float(v_default),
                step=float(v_step)
            )
            user_inputs[feature_name] = val
    
    submitted = st.form_submit_button("✨ Deviner la Classe", use_container_width=True)

#final
if submitted:

    X_user = pd.DataFrame([user_inputs])
    X_user = X_user[features] 

    # B. Prédiction
    prediction_label = model.predict(X_user)[0]
    probas = model.predict_proba(X_user)[0]
    
    df_resultats = pd.DataFrame({"Classe": classes_noms, "Probabilité": probas})
    df_resultats = df_resultats.sort_values(by="Probabilité", ascending=False)
    
    #Affichage
    st.divider()
    col_g, col_d = st.columns([1, 2])
    
    with col_g:
        st.subheader("Verdict")
        st.success(f"C'est un **{prediction_label}** !")
        
        st.write("---")
        st.caption("Top 3 Probabilités :")
        for index, row in df_resultats.head(3).iterrows():
            st.write(f"**{row['Classe']}** : {row['Probabilité']:.1%}")

    with col_d:
        st.subheader("Analyse de certitude")
        fig = px.pie(
            df_resultats, 
            values='Probabilité', 
            names='Classe', 
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)