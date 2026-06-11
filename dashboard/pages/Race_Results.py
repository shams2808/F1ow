import streamlit as st
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

ROUNDS = {
    2023: 22,
    2024: 24,
    2025: 24
}

@st.cache_data
def load_all_races(season):
    s3 = boto3.client('s3')
    all_dfs = []
    for round_num in range(1, ROUNDS[season] + 1):
        try:
            response = s3.get_object(
                Bucket=BUCKET_NAME,
                Key=f"silver/{season}/race_results/round_{round_num}.parquet"
            )
            df = pd.read_parquet(BytesIO(response['Body'].read()))
            df['round_num'] = round_num
            all_dfs.append(df)
        except:
            pass
    return pd.concat(all_dfs, ignore_index=True)

@st.cache_data
def load_race(season, round_num):
    s3 = boto3.client('s3')
    response = s3.get_object(
        Bucket=BUCKET_NAME,
        Key=f"silver/{season}/race_results/round_{round_num}.parquet"
    )
    return pd.read_parquet(BytesIO(response['Body'].read()))

st.title("🏁 Race Results")
st.divider()

# season selector
col1, col2 = st.columns(2)
with col1:
    season = st.selectbox("Select Season", [2023, 2024, 2025])

# load all races for season to build round labels
all_races = load_all_races(season)
round_names = all_races.groupby('round_num')['racename'].first().to_dict()
round_options = {f"Round {r} — {name}": r for r, name in sorted(round_names.items())}

with col2:
    selected_label = st.selectbox("Select Round", list(round_options.keys()))
    round_num = round_options[selected_label]

df = load_race(season, round_num)
df['finish_position'] = pd.to_numeric(df['finish_position'], errors='coerce')
df['points'] = pd.to_numeric(df['points'], errors='coerce').fillna(0)
df['grid_position'] = pd.to_numeric(df['grid_position'], errors='coerce')
df['fastest_lap_rank'] = pd.to_numeric(df['fastest_lap_rank'], errors='coerce')
df = df.sort_values('finish_position')

# race info
race_info = df.iloc[0]
st.markdown(f"## 🏎️ {race_info['racename']}")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"📍 **Circuit:** {race_info['circuitname']}")
with col2:
    st.markdown(f"🌍 **Country:** {race_info['country']}")
with col3:
    st.markdown(f"📅 **Date:** {race_info['date']}")

st.divider()

# podium
st.markdown("### 🥇 Podium")
podium = df[df['finish_position'] <= 3].sort_values('finish_position')
col1, col2, col3 = st.columns(3)

with col1:
    if len(podium) >= 1:
        p1 = podium.iloc[0]
        color = TEAM_COLORS.get(p1['constructor_name'], '#FFD700')
        st.markdown(f"""<div style='padding:15px; border-left: 5px solid {color}; 
        background-color:#1E1E1E; border-radius:5px; text-align:center'>
        🥇 <b style='font-size:18px'>{p1['driver_name']}</b><br>
        <span style='color:{color}'>{p1['constructor_name']}</span><br>
        ⭐ {int(p1['points'])} pts
        </div>""", unsafe_allow_html=True)

with col2:
    if len(podium) >= 2:
        p2 = podium.iloc[1]
        color = TEAM_COLORS.get(p2['constructor_name'], '#C0C0C0')
        st.markdown(f"""<div style='padding:15px; border-left: 5px solid {color}; 
        background-color:#1E1E1E; border-radius:5px; text-align:center'>
        🥈 <b style='font-size:18px'>{p2['driver_name']}</b><br>
        <span style='color:{color}'>{p2['constructor_name']}</span><br>
        ⭐ {int(p2['points'])} pts
        </div>""", unsafe_allow_html=True)

with col3:
    if len(podium) >= 3:
        p3 = podium.iloc[2]
        color = TEAM_COLORS.get(p3['constructor_name'], '#CD7F32')
        st.markdown(f"""<div style='padding:15px; border-left: 5px solid {color}; 
        background-color:#1E1E1E; border-radius:5px; text-align:center'>
        🥉 <b style='font-size:18px'>{p3['driver_name']}</b><br>
        <span style='color:{color}'>{p3['constructor_name']}</span><br>
        ⭐ {int(p3['points'])} pts
        </div>""", unsafe_allow_html=True)

st.divider()

# fastest lap highlight
fastest_lap_driver = df[df['fastest_lap_rank'] == 1]
if len(fastest_lap_driver) > 0:
    fl = fastest_lap_driver.iloc[0]
    fl_color = TEAM_COLORS.get(fl['constructor_name'], '#9B59B6')
    st.markdown(f"""<div style='padding:10px; border-left: 5px solid #9B59B6; 
    background-color:#1E1E1E; border-radius:5px'>
    ⚡ <b>Fastest Lap:</b> {fl['driver_name']} ({fl['constructor_name']}) — 
    <span style='color:#9B59B6'>{fl['fastest_lap_time']}</span>
    </div>""", unsafe_allow_html=True)
    st.markdown("")

st.divider()

# full results table with colored rows
st.markdown("### 📋 Full Results")

for _, row in df.iterrows():
    pos = row['finish_position']
    constructor = row['constructor_name']
    team_color = TEAM_COLORS.get(constructor, '#FFFFFF')
    is_fastest = row['fastest_lap_rank'] == 1

    # position emoji
    if pos == 1:
        pos_display = "🥇 1"
    elif pos == 2:
        pos_display = "🥈 2"
    elif pos == 3:
        pos_display = "🥉 3"
    elif pd.isna(pos):
        pos_display = "DNF"
    else:
        pos_display = f"{int(pos)}"

    # background color for points positions
    if not pd.isna(pos) and pos <= 10:
        bg_color = "#1E1E1E"
    else:
        bg_color = "#141414"

    fastest_badge = " ⚡" if is_fastest else ""

    st.markdown(f"""
    <div style='display:flex; align-items:center; padding:8px 12px; margin:3px 0; 
    background-color:{bg_color}; border-radius:5px; border-left: 4px solid {team_color}'>
        <span style='width:50px; font-weight:bold; color:{"#FFD700" if pos==1 else "#FFFFFF"}'>{pos_display}</span>
        <span style='width:200px; font-weight:bold'>{row['driver_name']}{fastest_badge}</span>
        <span style='width:200px; color:{team_color}'>■ {constructor}</span>
        <span style='width:80px; text-align:center; color:#888'>Grid: {int(row['grid_position']) if not pd.isna(row['grid_position']) else '-'}</span>
        <span style='width:80px; text-align:center; font-weight:bold; color:#FFD700'>{int(row['points'])} pts</span>
        <span style='width:80px; text-align:center; color:#888'>{int(row['laps']) if not pd.isna(row['laps']) else '-'} laps</span>
        <span style='width:100px; text-align:center; color:{"#888" if row["status"] == "Finished" else "#E8002D"}'>{row['status']}</span>
        <span style='width:120px; text-align:right; color:#9B59B6'>{row['fastest_lap_time'] if pd.notna(row['fastest_lap_time']) else ''}</span>
    </div>
    """, unsafe_allow_html=True)