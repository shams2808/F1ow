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

@st.cache_data
def load_constructor_performance():
    s3 = boto3.client('s3')
    response = s3.get_object(
        Bucket=BUCKET_NAME,
        Key="gold/constructor_performance/constructor_performance.parquet"
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

df = load_constructor_performance()
race_df = load_race_data()

df['total_points'] = pd.to_numeric(df['total_points'], errors='coerce').fillna(0)
df['total_wins'] = pd.to_numeric(df['total_wins'], errors='coerce').fillna(0)
race_df['points'] = pd.to_numeric(race_df['points'], errors='coerce').fillna(0)

st.title("🏎️ Constructor Performance")
st.divider()

season = st.selectbox("Select Season", [2023, 2024, 2025])

# filter by season
filtered_df = df[df['season'] == season].copy()
filtered_df = filtered_df.drop_duplicates('constructor_name')
filtered_df = filtered_df.sort_values('total_points', ascending=False).reset_index(drop=True)
filtered_df['team_color'] = filtered_df['constructor_name'].map(TEAM_COLORS).fillna('#FFFFFF')

# season race data
season_race_df = race_df[race_df['season'] == season].copy()

# constructor cumulative points per round
constructor_round_points = season_race_df.groupby(['constructor_name', 'round'])['points'].sum().reset_index()
constructor_round_points = constructor_round_points.sort_values(['constructor_name', 'round'])
constructor_round_points['cumulative_points'] = constructor_round_points.groupby('constructor_name')['points'].cumsum()

# KPI metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("🏁 Races", int(filtered_df['total_races'].max()))
with col2:
    top_wins = filtered_df.loc[filtered_df['total_wins'].idxmax()]
    st.metric("🏆 Most Wins", f"{top_wins['constructor_name']} ({int(top_wins['total_wins'])})")
with col3:
    top_pts = filtered_df.iloc[0]
    st.metric("⭐ Most Points", f"{top_pts['constructor_name']} ({int(top_pts['total_points'])})")

st.divider()

# All constructors points progression
st.markdown("### 📈 All Constructors Points Progression")

fig_all = px.line(
    constructor_round_points,
    x='round',
    y='cumulative_points',
    color='constructor_name',
    color_discrete_map=TEAM_COLORS,
    title=f'All Constructors Points Progression — {season}',
    markers=True,
    labels={'round': 'Race Round', 'cumulative_points': 'Cumulative Points', 'constructor_name': 'Constructor'}
)
fig_all.update_layout(
    legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.01),
    height=600
)
st.plotly_chart(fig_all, use_container_width=True)

st.divider()

# Individual constructor points progression
st.markdown("### 📈 Individual Constructor Points Progression")
season_constructors = sorted(constructor_round_points['constructor_name'].unique())
constructor = st.selectbox("Select Constructor", season_constructors)

constructor_races = constructor_round_points[constructor_round_points['constructor_name'] == constructor].copy()
line_color = TEAM_COLORS.get(constructor, '#E8002D')

fig_individual = px.line(
    constructor_races, x='round', y='cumulative_points',
    title=f'{constructor} — Points Progression {season}',
    markers=True,
    labels={'round': 'Race Round', 'cumulative_points': 'Cumulative Points'}
)
fig_individual.update_traces(line_color=line_color, marker_color=line_color)
st.plotly_chart(fig_individual, use_container_width=True)

st.divider()

# Bar charts
col1, col2 = st.columns(2)

with col1:
    fig1 = px.bar(
        filtered_df, x='constructor_name', y='total_points',
        title=f'Constructors by Points — {season}',
        color='constructor_name',
        color_discrete_map=TEAM_COLORS,
        labels={'constructor_name': 'Constructor', 'total_points': 'Points'}
    )
    fig1.update_layout(xaxis_tickangle=-45, showlegend=False,  xaxis={'categoryorder': 'total descending'})
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.bar(
        filtered_df, x='constructor_name', y='total_wins',
        title=f'Constructors by Wins — {season}',
        color='constructor_name',
        color_discrete_map=TEAM_COLORS,
        labels={'constructor_name': 'Constructor', 'total_wins': 'Wins'}
    )
    fig2.update_layout(xaxis_tickangle=-45, showlegend=False,  xaxis={'categoryorder': 'total descending'})
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# Constructor cards
st.markdown("### 🏢 All Constructors")
for _, row in filtered_df.iterrows():
    team_color = row['team_color']
    st.markdown(
        f"""<div style='padding:10px; margin:5px; border-left: 5px solid {team_color}; background-color:#1E1E1E; border-radius:5px'>
        <b>{row['constructor_name']}</b> | 
        🏆 Wins: {int(row['total_wins'])} | 
        ⭐ Points: {int(row['total_points'])} | 
        🏁 Races: {int(row['total_races'])}
        </div>""",
        unsafe_allow_html=True
    )
