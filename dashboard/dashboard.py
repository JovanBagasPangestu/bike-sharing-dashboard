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

ORDER_MUSIM = ["Winter", "Spring", "Summer", "Fall"]
ORDER_CUACA = ["Clear", "Mist/Cloudy", "Light Rain/Snow", "Heavy Rain/Snow"]
WARNA_HARI = {"Hari kerja": "#1f77b4", "Akhir pekan / libur": "#ff7f0e"}


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

date_range = st.sidebar.date_input(
    label="Rentang Tanggal",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
)
# date_input mengembalikan 1 tanggal saja jika pengguna baru memilih tanggal awal
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    st.sidebar.warning("Pilih tanggal awal dan tanggal akhir.")
    st.stop()

opsi_musim = [m for m in ORDER_MUSIM if m in df["season"].unique()]
opsi_cuaca = [c for c in ORDER_CUACA if c in df["weather"].unique()]

selected_seasons = st.sidebar.multiselect(
    label="Pilih Musim",
    options=opsi_musim,
    default=opsi_musim,
)

selected_weathers = st.sidebar.multiselect(
    label="Pilih Kondisi Cuaca",
    options=opsi_cuaca,
    default=opsi_cuaca,
)

# Terapkan filter
main_df = df[
    (df["dteday"].dt.date >= start_date)
    & (df["dteday"].dt.date <= end_date)
    & (df["season"].isin(selected_seasons))
    & (df["weather"].isin(selected_weathers))
]

if main_df.empty:
    st.warning("Tidak ada data untuk filter yang dipilih. Ubah filter di sidebar.")
    st.stop()

# --- HEADER & KPI METRICS ---
st.title("🚲 Bike Sharing Analytics Dashboard (2011–2012)")
st.markdown(
    "Dashboard interaktif untuk mengeksplorasi pola penyewaan sepeda berdasarkan "
    "jam operasional, musim dan cuaca, serta pertumbuhan bulanan."
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
st.subheader("1. Rata-rata Penyewaan per Jam: Hari Kerja vs Akhir Pekan/Libur")
hourly_df = main_df.groupby(["hr", "day_type"])["cnt_hour"].mean().reset_index()
urutan_hari = [h for h in WARNA_HARI if h in hourly_df["day_type"].unique()]

fig1, ax1 = plt.subplots(figsize=(12, 4))
sns.lineplot(
    data=hourly_df,
    x="hr",
    y="cnt_hour",
    hue="day_type",
    hue_order=urutan_hari,
    palette=WARNA_HARI,
    marker="o",
    ax=ax1,
)
ax1.axvspan(6.5, 9.5, color="gray", alpha=0.15, label="Jam sibuk pagi (07.00–09.59)")
ax1.axvspan(15.5, 19.5, color="gray", alpha=0.15, label="Jam sibuk sore (16.00–19.59)")
ax1.set_xticks(range(0, 24))
ax1.set_xlabel("Jam (00–23)")
ax1.set_ylabel("Rata-rata penyewaan per jam")
ax1.set_title("Rata-rata Penyewaan per Jam: Hari Kerja vs Akhir Pekan/Libur")
ax1.legend(title="")
st.pyplot(fig1)
plt.close(fig1)

# --- VISUALISASI 2: MUSIM & CUACA ---
st.subheader("2. Rata-rata Penyewaan per Jam Berdasarkan Musim dan Kondisi Cuaca")
col_a, col_b = st.columns(2)

with col_a:
    season_avg = (
        main_df.groupby("season")["cnt_hour"].mean().reindex(ORDER_MUSIM).dropna()
    )
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    batang = ax2.bar(season_avg.index, season_avg.values, color="#1f77b4")
    ax2.bar_label(batang, fmt="%.0f")
    ax2.set_xlabel("Musim")
    ax2.set_ylabel("Rata-rata penyewaan per jam")
    ax2.set_title("Rata-rata Penyewaan per Jam Berdasarkan Musim")
    st.pyplot(fig2)
    plt.close(fig2)

with col_b:
    weather_avg = (
        main_df.groupby("weather")["cnt_hour"].mean().reindex(ORDER_CUACA).dropna()
    )
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    batang = ax3.bar(weather_avg.index, weather_avg.values, color="#ff7f0e")
    ax3.bar_label(batang, fmt="%.0f")
    ax3.set_xlabel("Kondisi cuaca")
    ax3.set_ylabel("Rata-rata penyewaan per jam")
    ax3.set_title("Rata-rata Penyewaan per Jam Berdasarkan Kondisi Cuaca")
    ax3.tick_params(axis="x", rotation=15)
    st.pyplot(fig3)
    plt.close(fig3)

st.caption(
    "Catatan: grafik ini memakai rata-rata per jam dari data jam (hour.csv), "
    "sehingga angkanya berbeda dari rata-rata per hari di notebook. "
    "Kategori Heavy Rain/Snow hanya tercatat 3 jam, jadi rata-ratanya kurang representatif."
)

# --- VISUALISASI 3: TOTAL PENYEWAAN BULANAN ---
st.subheader("3. Total Penyewaan Bulanan 2011–2012: Registered vs Casual")
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
ax4.set_ylabel("Total penyewaan per bulan")
ax4.set_title("Total Penyewaan Bulanan: Registered vs Casual")
ax4.tick_params(axis="x", rotation=45)
ax4.legend()
st.pyplot(fig4)
plt.close(fig4)

st.caption("Copyright © 2026 - Jovan Bagas Pangestu")