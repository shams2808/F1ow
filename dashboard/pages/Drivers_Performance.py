import streamlit as st
import plotly.express as px
import boto3
import pandas as pd
from io import BytesIO

BUCKET_NAME = "f1ow-data-417521971713"

TEAM_COLORS = {
    'Red Bull': '#3671C6',
    'McLaren': '#FF8000',
    'Ferrari': '#E8002D',
    'Mercedes': '#27F4D2',
    'Aston Martin': '#229971',
    'Alpine F1 Team': '#FF87BC',
    'Williams': '#64C4FF',
    'RB F1 Team': '#6692FF',
    'Haas F1 Team': '#B6BABD',
    'Sauber': '#52E252',
    'AlphaTauri': '#5E8FAA',
    'Alfa Romeo': '#C92D4B',
    'Kick Sauber': '#52E252',
    'Visa Cash App RB': '#6692FF',
}

NATIONALITY_FLAGS = {
    'British': '🇬🇧', 'Dutch': '🇳🇱', 'Spanish': '🇪🇸',
    'Mexican': '🇲🇽', 'Monegasque': '🇲🇨', 'Australian': '🇦🇺',
    'German': '🇩🇪', 'French': '🇫🇷', 'Finnish': '🇫🇮',
    'Canadian': '🇨🇦', 'Thai': '🇹🇭', 'Japanese': '🇯🇵',
    'Danish': '🇩🇰', 'American': '🇺🇸', 'Chinese': '🇨🇳',
    'New Zealander': '🇳🇿', 'Italian': '🇮🇹', 'Brazilian': '🇧🇷',
    'Austrian': '🇦🇹', 'Argentinian': '🇦🇷'
}

@st.cache_data
def load_driver_performance():
    s3 = boto3.client('s3')
    response = s3.get_object(
        Bucket=BUCKET_NAME,
        Key="gold/driver_performance/driver_performance.parquet"
    )
    return pd.read_parquet(BytesIO(response['Body'].read()))

@st.cache_data
def load_race_data():
    s3 = boto3.client('s3')
    all_dfs = []
    for season in [2023, 2024, 2025]:
        for round_num in range(1, 25):
            try:
                response = s3.get_object(
                    Bucket=BUCKET_NAME,
                    Key=f"silver/{season}/race_results/round_{round_num}.parquet"
                )
                all_dfs.append(pd.read_parquet(BytesIO(response['Body'].read())))
            except:
                pass
    return pd.concat(all_dfs, ignore_index=True)

df = load_driver_performance()
race_df = load_race_data()

# fix data types
df['total_points'] = pd.to_numeric(df['total_points'], errors='coerce').fillna(0)
df['total_wins'] = pd.to_numeric(df['total_wins'], errors='coerce').fillna(0)
df['podiums'] = pd.to_numeric(df['podiums'], errors='coerce').fillna(0)
race_df['points'] = pd.to_numeric(race_df['points'], errors='coerce').fillna(0)

st.title("🏆 Driver Performance")
st.divider()

season = st.selectbox("Select Season", [2023, 2024, 2025])

# filter race data for selected season
season_race_df = race_df[race_df['season'] == season].copy()
season_race_df = season_race_df.sort_values(['driver_name', 'round'])
season_race_df['cumulative_points'] = season_race_df.groupby('driver_name')['points'].cumsum()

# get constructor per driver for this season
driver_constructor = season_race_df.groupby('driver_name')['constructor_name'].first().reset_index()

# filter aggregated df for this season
filtered_df = df[df['season'] == season].copy()
filtered_df = filtered_df.merge(driver_constructor, on='driver_name', how='inner')
filtered_df = filtered_df.drop_duplicates('driver_name')
filtered_df['team_color'] = filtered_df['constructor_name'].map(TEAM_COLORS).fillna('#FFFFFF')
filtered_df = filtered_df.sort_values('total_points', ascending=False).reset_index(drop=True)

# KPI metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("🏁 Races", int(filtered_df['total_races'].max()))
with col2:
    top_driver_wins = filtered_df.iloc[filtered_df['total_wins'].argmax()]
    st.metric("🏆 Most Wins", f"{top_driver_wins['driver_name']} ({int(top_driver_wins['total_wins'])})")
with col3:
    top_driver_pts = filtered_df.iloc[0]
    st.metric("⭐ Most Points", f"{top_driver_pts['driver_name']} ({int(top_driver_pts['total_points'])})")

st.divider()

# All drivers points progression
st.markdown("### 📈 All Drivers Points Progression")

driver_color_map = {}
for driver_name in season_race_df['driver_name'].unique():
    constructor = season_race_df[season_race_df['driver_name'] == driver_name]['constructor_name'].iloc[0]
    driver_color_map[driver_name] = TEAM_COLORS.get(constructor, '#FFFFFF')

fig_all = px.line(
    season_race_df,
    x='round',
    y='cumulative_points',
    color='driver_name',
    color_discrete_map=driver_color_map,
    title=f'All Drivers Points Progression — {season}',
    markers=True,
    labels={'round': 'Race Round', 'cumulative_points': 'Cumulative Points', 'driver_name': 'Driver'}
)
fig_all.update_layout(
    legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.01),
    height=600
)
st.plotly_chart(fig_all, use_container_width=True)

st.divider()

# Individual driver points progression
st.markdown("### 📈 Individual Driver Points Progression")
season_drivers = sorted(season_race_df['driver_name'].unique())
driver = st.selectbox("Select Driver", season_drivers)

driver_races = season_race_df[season_race_df['driver_name'] == driver].copy()
constructor = driver_races['constructor_name'].iloc[0] if len(driver_races) > 0 else 'Unknown'
line_color = TEAM_COLORS.get(constructor, '#E8002D')

fig_individual = px.line(
    driver_races, x='round', y='cumulative_points',
    title=f'{driver} ({constructor}) — Points Progression {season}',
    markers=True,
    labels={'round': 'Race Round', 'cumulative_points': 'Cumulative Points'}
)
fig_individual.update_traces(line_color=line_color, marker_color=line_color)
st.plotly_chart(fig_individual, use_container_width=True)

st.divider()

# Bar charts
col1, col2 = st.columns(2)

with col1:
    top_points = filtered_df.nlargest(10, 'total_points')
    fig1 = px.bar(
        top_points, x='driver_name', y='total_points',
        title=f'Top 10 Drivers by Points — {season}',
        color='constructor_name',
        color_discrete_map=TEAM_COLORS,
        labels={'driver_name': 'Driver', 'total_points': 'Points', 'constructor_name': 'Team'}
    )
    fig1.update_layout(xaxis_tickangle=-45,  xaxis={'categoryorder': 'total descending'})
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    top_wins = filtered_df.nlargest(10, 'total_wins')
    fig2 = px.bar(
        top_wins, x='driver_name', y='total_wins',
        title=f'Top 10 Drivers by Wins — {season}',
        color='constructor_name',
        color_discrete_map=TEAM_COLORS,
        labels={'driver_name': 'Driver', 'total_wins': 'Wins', 'constructor_name': 'Team'}
    )
    fig2.update_layout(xaxis_tickangle=-45, xaxis={'categoryorder': 'total descending'})
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# Podiums
st.markdown("### 🥇 Podiums Comparison")
top_podiums = filtered_df.nlargest(10, 'podiums')
fig4 = px.bar(
    top_podiums, x='driver_name', y='podiums',
    title=f'Top 10 Drivers by Podiums — {season}',
    color='constructor_name',
    color_discrete_map=TEAM_COLORS,
    labels={'driver_name': 'Driver', 'podiums': 'Podiums', 'constructor_name': 'Team'}
)
fig4.update_layout(xaxis_tickangle=-45,  xaxis={'categoryorder': 'total descending'})
st.plotly_chart(fig4, use_container_width=True)

st.divider()

# Driver cards
st.markdown("### 👤 All Drivers")
for _, row in filtered_df.iterrows():
    flag = NATIONALITY_FLAGS.get(row.get('driver_nationality', ''), '🏁')
    team_color = row['team_color']
    st.markdown(
        f"""<div style='padding:10px; margin:5px; border-left: 5px solid {team_color}; background-color:#1E1E1E; border-radius:5px'>
        {flag} <b>{row['driver_name']}</b> — {row.get('constructor_name', '')} | 
        🏆 Wins: {int(row['total_wins'])} | 
        ⭐ Points: {int(row['total_points'])} | 
        🥇 Podiums: {int(row['podiums'])}
        </div>""",
        unsafe_allow_html=True
    )