import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

# Konfigurasi halaman
st.set_page_config(
    page_title="Bike Sharing Analytics Dashboard",
    page_icon="🚲",
    layout="wide",
)


# Load data
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "main_data.csv")
    df = pd.read_csv(file_path)
    df["dteday"] = pd.to_datetime(df["dteday"])
    return df


df = load_data()

# --- SIDEBAR FILTER ---
st.sidebar.header("Filter Data")

min_date = df["dteday"].min().date()
max_date = df["dteday"].max().date()

start_date, end_date = st.sidebar.date_input(
    label="Rentang Tanggal",
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date],
)

selected_seasons = st.sidebar.multiselect(
    label="Pilih Musim",
    options=df["season"].unique().tolist(),
    default=df["season"].unique().tolist(),
)

selected_weathers = st.sidebar.multiselect(
    label="Pilih Kondisi Cuaca",
    options=df["weather"].unique().tolist(),
    default=df["weather"].unique().tolist(),
)

# Terapkan filter
main_df = df[
    (df["dteday"].dt.date >= start_date)
    & (df["dteday"].dt.date <= end_date)
    & (df["season"].isin(selected_seasons))
    & (df["weather"].isin(selected_weathers))
]

# --- HEADER & KPI METRICS ---
st.title("🚲 Bike Sharing Analytics Dashboard (2011–2012)")
st.markdown(
    "Dashboard interaktif untuk mengeksplorasi pola penyewaan sepeda berdasarkan jam operasional, kondisi cuaca/musim, dan pertumbuhan tahunan."
)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Penyewaan", f"{int(main_df['cnt_hour'].sum()):,}")
with col2:
    st.metric("Pengguna Registered", f"{int(main_df['registered_hour'].sum()):,}")
with col3:
    st.metric("Pengguna Casual", f"{int(main_df['casual_hour'].sum()):,}")

st.markdown("---")

# --- VISUALISASI 1: POLA JAM & TIPE HARI ---
st.subheader("1. Pola Penyewaan per Jam: Hari Kerja vs Akhir Pekan/Libur")
hourly_df = (
    main_df.groupby(["hr", "day_type"])["cnt_hour"].mean().reset_index()
)

fig1, ax1 = plt.subplots(figsize=(12, 4))
sns.lineplot(
    data=hourly_df,
    x="hr",
    y="cnt_hour",
    hue="day_type",
    marker="o",
    ax=ax1,
    palette=["#ff7f0e", "#1f77b4"],
)
ax1.axvspan(7, 9, color="gray", alpha=0.15, label="Jam Sibuk Pagi (07–09)")
ax1.axvspan(17, 19, color="gray", alpha=0.15, label="Jam Sibuk Sore (17–19)")
ax1.set_xticks(range(0, 24))
ax1.set_xlabel("Jam (00:00 - 23:00)")
ax1.set_ylabel("Rata-rata Penyewaan")
ax1.set_title(
    "Lonjakan Penyewaan Terjadi pada Jam Komuter (08:00 & 17:00–18:00) di Hari Kerja"
)
ax1.legend()
st.pyplot(fig1)

# --- VISUALISASI 2: PENGARUH MUSIM & CUACA ---
st.subheader("2. Pengaruh Musim dan Kondisi Cuaca terhadap Rata-rata Penyewaan")
col_a, col_b = st.columns(2)

with col_a:
    season_df = (
        main_df.groupby("season")["cnt_hour"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    sns.barplot(
        data=season_df,
        x="season",
        y="cnt_hour",
        palette="Blues_d",
        ax=ax2,
    )
    ax2.set_xlabel("Musim")
    ax2.set_ylabel("Rata-rata Penyewaan per Jam")
    ax2.set_title("Rata-rata Penyewaan Tertinggi di Musim Gugur (Fall)")
    st.pyplot(fig2)

with col_b:
    weather_df = (
        main_df.groupby("weather")["cnt_hour"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    sns.barplot(
        data=weather_df,
        x="weather",
        y="cnt_hour",
        palette="Oranges_d",
        ax=ax3,
    )
    ax3.set_xlabel("Kondisi Cuaca")
    ax3.set_ylabel("Rata-rata Penyewaan per Jam")
    ax3.set_title("Cuaca Buruk Menurunkan Minat Penyewaan Secara Drastis")
    plt.xticks(rotation=15)
    st.pyplot(fig3)

# --- VISUALISASI 3: TREN PERTUMBUHAN 2011 VS 2012 ---
st.subheader("3. Tren Pertumbuhan Penyewaan Bulanan (2011 vs 2012)")
main_df = main_df.copy()
main_df["year_month"] = main_df["dteday"].dt.to_period("M").astype(str)
monthly_df = (
    main_df.groupby("year_month")[["casual_hour", "registered_hour"]]
    .sum()
    .reset_index()
)

fig4, ax4 = plt.subplots(figsize=(12, 4))
ax4.plot(
    monthly_df["year_month"],
    monthly_df["registered_hour"],
    marker="o",
    label="Registered",
    color="#1f77b4",
)
ax4.plot(
    monthly_df["year_month"],
    monthly_df["casual_hour"],
    marker="s",
    label="Casual",
    color="#ff7f0e",
)
ax4.set_xlabel("Bulan")
ax4.set_ylabel("Total Penyewaan")
ax4.set_title(
    "Pertumbuhan Konsisten di Tahun 2012 Didominasi Segmen Registered"
)
plt.xticks(rotation=45)
ax4.legend()
st.pyplot(fig4)

st.caption("Copyright © 2026 - Jovan Bagas Pangestu")