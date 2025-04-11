# gdp_dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Configuration de la page
st.set_page_config(
    page_title="Dashboard PIB Mondial",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Chemin local vers les données (adaptez-le à votre structure)
DATA_PATH = "data/gdp_data.csv"

@st.cache_data
def load_data():
    """Charge les données depuis le fichier local"""
    try:
        df = pd.read_csv(DATA_PATH)
        
        # Transformation des données (format wide to long)
        years = [str(y) for y in range(1960, 2023)]
        df_melted = df.melt(
            id_vars=["Country Name", "Country Code", "Indicator Name", "Indicator Code"],
            value_vars=years,
            var_name="Year",
            value_name="GDP"
        )
        
        df_melted["Year"] = pd.to_numeric(df_melted["Year"])
        df_melted["GDP (Milliards $)"] = df_melted["GDP"] / 1e9
        
        return df, df_melted
    
    except FileNotFoundError:
        st.error(f"Fichier introuvable : {DATA_PATH}")
        st.stop()
    except Exception as e:
        st.error(f"Erreur de chargement : {str(e)}")
        st.stop()

# Interface utilisateur
def main():
    st.title("🌍 Analyse du PIB Mondial")
    st.markdown("""
    **Dashboard interactif** utilisant des données locales de la Banque Mondiale.
    """)
    
    # Chargement des données
    raw_df, processed_df = load_data()
    
    # Section d'exploration
    with st.expander("🔍 Aperçu des données brutes (5 premières lignes)"):
        st.dataframe(raw_df.head(), use_container_width=True)
        st.download_button(
            label="Télécharger les données brutes",
            data=raw_df.to_csv(index=False).encode('utf-8'),
            file_name="gdp_data_raw.csv",
            mime="text/csv"
        )
    
    # Sidebar avec filtres
    with st.sidebar:
        st.header("Filtres")
        
        # Sélection des pays
        available_countries = processed_df["Country Name"].unique()
        selected_countries = st.multiselect(
            "Pays",
            options=available_countries,
            default=["France", "Germany", "United States", "China", "Japan"],
            max_selections=10
        )
        
        # Sélection des années
        min_year = int(processed_df["Year"].min())
        max_year = int(processed_df["Year"].max())
        year_range = st.slider(
            "Période",
            min_year, max_year,
            (2000, max_year)
        )
        
        # Options d'affichage
        st.header("Options")
        log_scale = st.checkbox("Échelle logarithmique", False)
        show_raw = st.checkbox("Afficher données filtrées", False)
    
    # Filtrage des données
    filtered_df = processed_df[
        (processed_df["Country Name"].isin(selected_countries)) &
        (processed_df["Year"].between(*year_range))
    ]
    
    if filtered_df.empty:
        st.warning("Aucune donnée disponible avec ces filtres")
        return
    
    # Visualisation principale
    st.header("Évolution du PIB")
    fig = px.line(
        filtered_df,
        x="Year",
        y="GDP (Milliards $)",
        color="Country Name",
        hover_name="Country Name",
        log_y=log_scale,
        labels={"GDP (Milliards $)": "PIB (en milliards USD)"}
    )
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistiques comparatives
    st.header("Comparaison entre pays")
    
    # Calcul des indicateurs
    pivot_df = filtered_df.pivot_table(
        index="Country Name",
        columns="Year",
        values="GDP (Milliards $)",
        aggfunc="sum"
    )
    
    # Affichage des métriques
    cols = st.columns(4)
    for idx, country in enumerate(selected_countries):
        with cols[idx % 4]:
            if country in pivot_df.index:
                latest_year = pivot_df.columns[-1]
                prev_year = pivot_df.columns[0]
                
                current_gdp = pivot_df.loc[country, latest_year]
                previous_gdp = pivot_df.loc[country, prev_year]
                
                growth = (current_gdp / previous_gdp - 1) * 100
                
                st.metric(
                    label=country,
                    value=f"{current_gdp:,.0f} Md$",
                    delta=f"{growth:.1f}%",
                    help=f"De {prev_year} à {latest_year}"
                )
    
    # Données filtrées
    if show_raw:
        st.header("Données filtrées")
        st.dataframe(
            filtered_df[["Country Name", "Year", "GDP (Milliards $)"]],
            column_config={
                "GDP (Milliards $)": st.column_config.NumberColumn(format="%.2f Md$")
            },
            hide_index=True,
            use_container_width=True
        )

if __name__ == "__main__":
    main()
