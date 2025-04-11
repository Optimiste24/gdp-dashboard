import streamlit as st
import pandas as pd
import math
from pathlib import Path
import plotly.express as px

# Configuration de la page
st.set_page_config(
    page_title='GDP Dashboard',
    page_icon=':earth_americas:',
    layout='wide',
    initial_sidebar_state='expanded'
)

# -----------------------------------------------------------------------------
# Fonctions utilitaires avec cache

@st.cache_data
def load_raw_data():
    """Charge les données brutes depuis le fichier CSV"""
    DATA_FILENAME = Path(__file__).parent/'data/gdp_data.csv'
    return pd.read_csv(DATA_FILENAME)

@st.cache_data
def get_gdp_data(raw_df):
    """Transforme les données GDP avec mise en cache"""
    MIN_YEAR = 1960
    MAX_YEAR = 2022

    gdp_df = raw_df.melt(
        ['Country Name', 'Country Code'],
        [str(x) for x in range(MIN_YEAR, MAX_YEAR + 1)],
        'Year',
        'GDP',
    )

    gdp_df['Year'] = pd.to_numeric(gdp_df['Year'])
    gdp_df['GDP (Billion $)'] = gdp_df['GDP'] / 1e9
    return gdp_df

# -----------------------------------------------------------------------------
# Chargement des données et affichage initial

st.title(':earth_americas: GDP Dashboard - GitHub Workflow')

# Section d'aperçu des données
st.header('📊 Data Preview')
st.write("Voici les 5 premières lignes du dataset brut:")

# Chargement des données brutes
try:
    raw_df = load_raw_data()
    st.dataframe(raw_df.head(5), use_container_width=True)
    
    # Transformation des données
    gdp_df = get_gdp_data(raw_df)
    country_names = dict(zip(raw_df['Country Code'], raw_df['Country Name']))
    
except FileNotFoundError:
    st.error("Erreur: Le fichier de données n'a pas été trouvé. Vérifiez le chemin dans GitHub.")
    st.stop()

# -----------------------------------------------------------------------------
# Interface utilisateur principale

st.divider()
st.header('🔍 Data Exploration')

with st.sidebar:
    st.header('Filters')
    
    # Sélection des années
    year_range = st.slider(
        'Select year range',
        min_value=gdp_df['Year'].min(),
        max_value=gdp_df['Year'].max(),
        value=(gdp_df['Year'].min(), gdp_df['Year'].max())
    
    # Sélection des pays avec recherche
    default_countries = ['DEU', 'FRA', 'GBR', 'USA', 'CHN']
    selected_countries = st.multiselect(
        'Select countries',
        options=gdp_df['Country Code'].unique(),
        default=default_countries,
        format_func=lambda x: f"{x} - {country_names.get(x, '?')}"
    )

# Filtrage des données
if not selected_countries:
    st.warning("Veuillez sélectionner au moins un pays")
    st.stop()

filtered_df = gdp_df[
    (gdp_df['Country Code'].isin(selected_countries)) &
    (gdp_df['Year'].between(*year_range))
].copy()

# -----------------------------------------------------------------------------
# Visualisations

st.header('📈 GDP Evolution')
fig = px.line(
    filtered_df,
    x='Year',
    y='GDP (Billion $)',
    color='Country Code',
    hover_name='Country Name',
    labels={'GDP (Billion $)': 'GDP (in Billion USD)'}
)
st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------------------------
# Pied de page avec info GitHub

st.divider()
st.caption("""
**GitHub Workflow Tips:**
- Le fichier de données doit être dans le dossier `data/`
- Vérifiez les chemins d'accès relatifs
- Commit + push pour mettre à jour l'application
""")
