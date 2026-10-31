import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Penjualan", layout="wide")

# ================= FUNGSI BANTU =================
def format_rupiah_singkat(n):
    if n >= 1_000_000_000:
        return f"Rp {n/1_000_000_000:.2f} M"
    elif n >= 1_000_000:
        return f"Rp {n/1_000_000:.2f} Jt"
    elif n >= 1_000:
        return f"Rp {n/1_000:.2f} Rb"
    else:
        return f"Rp {n:,.0f}"

# ================= LOAD DATA =================
@st.cache_data
def load_data():
    df = pd.read_csv("data_penjualan_sintesis.csv", parse_dates=["Tanggal"])
    df["Total_Penjualan"] = df["Harga"] * df["Jumlah_Terjual"]
    return df

df = load_data()

st.title("📊 Dashboard Operasional Penjualan")
st.markdown("Bedah Kasus 1: Dataset Operasional Penjualan")

# ================= SIDEBAR FILTER =================
st.sidebar.header("Filter Data")

kategori = st.sidebar.multiselect(
    "Pilih Kategori",
    options=df["Kategori"].unique(),
    default=df["Kategori"].unique()
)

produk = st.sidebar.multiselect(
    "Pilih Produk",
    options=df["Produk"].unique(),
    default=df["Produk"].unique()
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
    df_filtered = df[mask & df["Kategori"].isin(kategori) & df["Produk"].isin(produk)]
else:
    df_filtered = df[df["Kategori"].isin(kategori) & df["Produk"].isin(produk)]

# ================= METRICS =================
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Transaksi", f"{len(df_filtered):,}")
col2.metric("Total Unit Terjual", f"{df_filtered['Jumlah_Terjual'].sum():,}")
col3.metric("Total Pendapatan", format_rupiah_singkat(df_filtered['Total_Penjualan'].sum()))
col4.metric("Rata-rata per Transaksi", format_rupiah_singkat(df_filtered['Total_Penjualan'].mean()))

# ================= CHART =================
col1, col2 = st.columns(2)

with col1:
    rev_prod = df_filtered.groupby("Produk")["Total_Penjualan"].sum().reset_index().sort_values("Total_Penjualan", ascending=False)
    fig = px.bar(rev_prod, x="Produk", y="Total_Penjualan", title="Total Pendapatan per Produk", text_auto='.2s')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    rev_cat = df_filtered.groupby("Kategori")["Total_Penjualan"].sum().reset_index()
    fig = px.pie(rev_cat, names="Kategori", values="Total_Penjualan", title="Proporsi Pendapatan per Kategori")
    st.plotly_chart(fig, use_container_width=True)

# Tren bulanan
df_filtered["Bulan"] = df_filtered["Tanggal"].dt.to_period("M").astype(str)
monthly = df_filtered.groupby("Bulan")["Total_Penjualan"].sum().reset_index()
fig = px.line(monthly, x="Bulan", y="Total_Penjualan", title="Tren Pendapatan Bulanan", markers=True)
st.plotly_chart(fig, use_container_width=True)

# Histogram & Boxplot
col1, col2 = st.columns(2)

with col1:
    fig = px.histogram(df_filtered, x="Jumlah_Terjual", nbins=30, title="Distribusi Jumlah Terjual")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.box(df_filtered, x="Kategori", y="Total_Penjualan", title="Sebaran Pendapatan per Kategori")
    st.plotly_chart(fig, use_container_width=True)

# ================= DATA TABLE =================
st.subheader("Data Transaksi")
st.dataframe(df_filtered.sort_values("Tanggal", ascending=False), use_container_width=True)

# Download
csv = df_filtered.to_csv(index=False).encode('utf-8')
st.download_button("Download Data Filtered (CSV)", csv, "data_filtered.csv", "text/csv")