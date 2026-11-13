import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Dashboard Pengamatan Cuaca", layout="wide")

@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "data_cuaca_sintesis.csv")
    df = pd.read_csv(file_path, parse_dates=["Tanggal"])
    return df

df = load_data()

st.title("🌤️ Dashboard Pengamatan Cuaca")
st.markdown("Bedah Kasus 3: Dataset Pengamatan Cuaca")

# ================= SIDEBAR FILTER =================
st.sidebar.header("Filter Data")

kota = st.sidebar.multiselect(
    "Pilih Kota",
    options=sorted(df["Kota"].unique()),
    default=sorted(df["Kota"].unique())
)

kondisi = st.sidebar.multiselect(
    "Pilih Kondisi",
    options=sorted(df["Kondisi"].unique()),
    default=sorted(df["Kondisi"].unique())
)

min_date = df["Tanggal"].min().date()
max_date = df["Tanggal"].max().date()

date_range = st.sidebar.date_input(
    "Rentang Tanggal",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date, end_date = date_range
    mask = (df["Tanggal"].dt.date >= start_date) & (df["Tanggal"].dt.date <= end_date)
    df_filtered = df[mask & df["Kota"].isin(kota) & df["Kondisi"].isin(kondisi)]
else:
    df_filtered = df[df["Kota"].isin(kota) & df["Kondisi"].isin(kondisi)]

# ================= METRICS =================
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Pengamatan", f"{len(df_filtered):,}")
col2.metric("Rata-rata Suhu", f"{df_filtered['Suhu_C'].mean():.1f} °C")
col3.metric("Rata-rata Kelembaban", f"{df_filtered['Kelembaban_Persen'].mean():.1f} %")
col4.metric("Jumlah Kota", f"{df_filtered['Kota'].nunique()}")

# ================= CHART 1: Kategorik Nominal =================
st.subheader("🏙️ Analisis Kategorik (Nominal)")
col1, col2 = st.columns(2)

with col1:
    kota_count = df_filtered["Kota"].value_counts().reset_index()
    kota_count.columns = ["Kota", "Jumlah"]
    fig = px.bar(kota_count, x="Jumlah", y="Kota", orientation="h",
                 title="Jumlah Pengamatan per Kota",
                 text="Jumlah", color="Jumlah",
                 color_continuous_scale="Blues")
    fig.update_layout(yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    kondisi_count = df_filtered["Kondisi"].value_counts().reset_index()
    kondisi_count.columns = ["Kondisi", "Jumlah"]
    fig = px.pie(kondisi_count, names="Kondisi", values="Jumlah",
                 title="Proporsi Kondisi Cuaca", hole=0.4,
                 color="Kondisi",
                 color_discrete_map={"Cerah": "#FFD700", "Berawan": "#A9A9A9", "Hujan": "#4682B4"})
    st.plotly_chart(fig, use_container_width=True)

# ================= CHART 2: Numerik Interval & Rasio =================
st.subheader("🌡️ Analisis Numerik Interval & Rasio")
col1, col2 = st.columns(2)

with col1:
    fig = px.histogram(df_filtered, x="Suhu_C", nbins=25,
                       title="Distribusi Suhu (°C) — Interval",
                       marginal="box",
                       color_discrete_sequence=["#EF553B"])
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.histogram(df_filtered, x="Kelembaban_Persen", nbins=25,
                       title="Distribusi Kelembaban (%) — Rasio",
                       marginal="box",
                       color_discrete_sequence=["#00CC96"])
    st.plotly_chart(fig, use_container_width=True)

# ================= CHART 3: Perbandingan Suhu & Kelembaban per Kota =================
st.subheader("📊 Perbandingan Suhu & Kelembaban per Kota")
col1, col2 = st.columns(2)

with col1:
    suhu_kota = df_filtered.groupby("Kota")["Suhu_C"].mean().reset_index().sort_values("Suhu_C", ascending=False)
    fig = px.bar(suhu_kota, x="Kota", y="Suhu_C",
                 title="Rata-rata Suhu per Kota",
                 text=suhu_kota["Suhu_C"].round(1),
                 color="Suhu_C", color_continuous_scale="OrRd")
    fig.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    lembab_kota = df_filtered.groupby("Kota")["Kelembaban_Persen"].mean().reset_index().sort_values("Kelembaban_Persen", ascending=False)
    fig = px.bar(lembab_kota, x="Kota", y="Kelembaban_Persen",
                 title="Rata-rata Kelembaban per Kota",
                 text=lembab_kota["Kelembaban_Persen"].round(1),
                 color="Kelembaban_Persen", color_continuous_scale="Blues")
    fig.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)

# ================= CHART 4: Box Plot Suhu & Kelembaban per Kondisi =================
st.subheader("📦 Sebaran Suhu & Kelembaban per Kondisi Cuaca")
col1, col2 = st.columns(2)

with col1:
    fig = px.box(df_filtered, x="Kondisi", y="Suhu_C", color="Kondisi",
                 title="Sebaran Suhu per Kondisi")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.box(df_filtered, x="Kondisi", y="Kelembaban_Persen", color="Kondisi",
                 title="Sebaran Kelembaban per Kondisi")
    st.plotly_chart(fig, use_container_width=True)

# ================= CHART 5: Scatter Suhu vs Kelembaban =================
st.subheader("🔍 Hubungan Suhu dan Kelembaban")
fig = px.scatter(df_filtered, x="Suhu_C", y="Kelembaban_Persen",
                 color="Kondisi", symbol="Kota",
                 title="Suhu vs Kelembaban (diwarnai Kondisi)",
                 color_discrete_map={"Cerah": "#FFD700", "Berawan": "#A9A9A9", "Hujan": "#4682B4"},
                 opacity=0.7)
st.plotly_chart(fig, use_container_width=True)

# ================= CHART 6: Tren Bulanan =================
st.subheader("📈 Tren Suhu & Kelembaban Bulanan")
df_filtered["Bulan"] = df_filtered["Tanggal"].dt.to_period("M").astype(str)
monthly = df_filtered.groupby("Bulan").agg(
    Suhu_Rata=("Suhu_C", "mean"),
    Kelembaban_Rata=("Kelembaban_Persen", "mean")
).reset_index()

fig = go.Figure()
fig.add_trace(go.Scatter(x=monthly["Bulan"], y=monthly["Suhu_Rata"],
                         mode="lines+markers", name="Suhu (°C)",
                         yaxis="y1", line=dict(color="#EF553B")))
fig.add_trace(go.Scatter(x=monthly["Bulan"], y=monthly["Kelembaban_Rata"],
                         mode="lines+markers", name="Kelembaban (%)",
                         yaxis="y2", line=dict(color="#00CC96")))
fig.update_layout(
    title="Tren Bulanan Suhu & Kelembaban",
    yaxis=dict(title="Suhu (°C)", side="left"),
    yaxis2=dict(title="Kelembaban (%)", overlaying="y", side="right"),
    hovermode="x unified"
)
st.plotly_chart(fig, use_container_width=True)

# ================= DATA TABLE =================
st.subheader("📋 Data Pengamatan Cuaca")
st.dataframe(df_filtered.sort_values("Tanggal", ascending=False), use_container_width=True)

csv = df_filtered.to_csv(index=False).encode("utf-8")
st.download_button("Download Data Filtered (CSV)", csv, "data_cuaca_filtered.csv", "text/csv")
