import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Profil Mahasiswa", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("data_mahasiswa_sintesis.csv")
    return df

df = load_data()

st.title("🎓 Dashboard Profil Mahasiswa")
st.markdown("Bedah Kasus 2: Dataset Profil Mahasiswa")

# ================= SIDEBAR FILTER =================
st.sidebar.header("Filter Data")

fakultas = st.sidebar.multiselect(
    "Pilih Fakultas",
    options=sorted(df["Fakultas"].unique()),
    default=sorted(df["Fakultas"].unique())
)

jurusan = st.sidebar.multiselect(
    "Pilih Jurusan",
    options=sorted(df["Jurusan"].unique()),
    default=sorted(df["Jurusan"].unique())
)

gender = st.sidebar.multiselect(
    "Pilih Gender",
    options=sorted(df["Gender"].unique()),
    default=sorted(df["Gender"].unique())
)

semester_range = st.sidebar.slider(
    "Rentang Semester",
    min_value=int(df["Semester"].min()),
    max_value=int(df["Semester"].max()),
    value=(int(df["Semester"].min()), int(df["Semester"].max()))
)

df_filtered = df[
    df["Fakultas"].isin(fakultas) &
    df["Jurusan"].isin(jurusan) &
    df["Gender"].isin(gender) &
    (df["Semester"] >= semester_range[0]) &
    (df["Semester"] <= semester_range[1])
]

# ================= METRICS =================
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Mahasiswa", f"{len(df_filtered):,}")
col2.metric("Rata-rata IPK", f"{df_filtered['IPK'].mean():.2f}")
col3.metric("Rata-rata Usia", f"{df_filtered['Usia'].mean():.1f} thn")
col4.metric("Jumlah Jurusan", f"{df_filtered['Jurusan'].nunique()}")

# ================= CHART 1: Kategorik =================
st.subheader("📊 Analisis Kategorik")
col1, col2 = st.columns(2)

with col1:
    jur = df_filtered["Jurusan"].value_counts().reset_index()
    jur.columns = ["Jurusan", "Jumlah"]
    fig = px.bar(jur, x="Jumlah", y="Jurusan", orientation="h",
                 title="Jumlah Mahasiswa per Jurusan",
                 text="Jumlah", color="Jumlah",
                 color_continuous_scale="Blues")
    fig.update_layout(yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    sem = df_filtered["Semester"].value_counts().sort_index().reset_index()
    sem.columns = ["Semester", "Jumlah"]
    sem["Semester"] = sem["Semester"].astype(str)
    fig = px.bar(sem, x="Semester", y="Jumlah",
                 title="Distribusi Semester (Ordinal)",
                 text="Jumlah", color="Jumlah",
                 color_continuous_scale="Greens")
    st.plotly_chart(fig, use_container_width=True)

# ================= CHART 2: Numerik Kontinu =================
st.subheader("📈 Analisis Numerik Kontinu")
col1, col2 = st.columns(2)

with col1:
    fig = px.histogram(df_filtered, x="IPK", nbins=25,
                       title="Distribusi IPK",
                       marginal="box",
                       color_discrete_sequence=["#636EFA"])
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.histogram(df_filtered, x="Usia", nbins=15,
                       title="Distribusi Usia",
                       marginal="box",
                       color_discrete_sequence=["#EF553B"])
    st.plotly_chart(fig, use_container_width=True)

# ================= CHART 3: Box Plot =================
st.subheader("📦 Sebaran IPK per Kategori")
col1, col2 = st.columns(2)

with col1:
    fig = px.box(df_filtered, x="Fakultas", y="IPK", color="Fakultas",
                 title="Sebaran IPK per Fakultas")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.box(df_filtered, x="Gender", y="IPK", color="Gender",
                 title="Sebaran IPK per Gender")
    st.plotly_chart(fig, use_container_width=True)

# ================= CHART 4: Komposisi =================
st.subheader("🥧 Komposisi & Perbandingan")
col1, col2 = st.columns([1, 2])

with col1:
    gen = df_filtered["Gender"].value_counts().reset_index()
    gen.columns = ["Gender", "Jumlah"]
    fig = px.pie(gen, names="Gender", values="Jumlah",
                 title="Komposisi Gender", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    ipk_jur = df_filtered.groupby("Jurusan")["IPK"].mean().reset_index().sort_values("IPK", ascending=False)
    fig = px.bar(ipk_jur, x="Jurusan", y="IPK",
                 title="Rata-rata IPK per Jurusan",
                 text=ipk_jur["IPK"].round(2), color="IPK",
                 color_continuous_scale="RdYlGn")
    fig.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)

# ================= DATA TABLE =================
st.subheader("📋 Data Mahasiswa")
st.dataframe(df_filtered, use_container_width=True)

csv = df_filtered.to_csv(index=False).encode("utf-8")
st.download_button("Download Data Filtered (CSV)", csv, "data_mahasiswa_filtered.csv", "text/csv")