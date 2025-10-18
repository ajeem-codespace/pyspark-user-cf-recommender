import streamlit as st
import pandas as pd
import requests
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, count, sqrt, sum as ssum, abs as sabs, first

st.set_page_config(page_title="MiniFlix", page_icon="🎬", layout="wide")

# Load CSVs with pandas for small UI pieces
movies_pd = pd.read_csv("data/movies.csv")
links_pd  = pd.read_csv("data/links.csv")
ratings_pd = pd.read_csv("data/ratings.csv")

# Choose 1–2 users from dataset
candidate_users = ratings_pd["userId"].drop_duplicates().sample(2, random_state=7).tolist()
st.sidebar.header("Choose a profile")
selected_user = st.sidebar.radio("Profiles", candidate_users)

# Spark for computing recommendations quickly (same logic as notebook)
spark = (SparkSession.builder.appName("MiniFlix").master("local[*]").getOrCreate())

ratings = (spark.createDataFrame(ratings_pd[["userId","movieId","rating"]])
           .select("userId","movieId","rating"))
movies  = spark.createDataFrame(movies_pd[["movieId","title","genres"]])

user_mean = ratings.groupBy("userId").agg(avg("rating").alias("mu"))
r1 = (ratings.join(user_mean, "userId")
      .withColumn("rc", col("rating") - col("mu"))
      .select(col("userId").alias("u"), "movieId", col("rc").alias("ru")))
r2 = r1.select(col("u").alias("v"), "movieId", col("ru").alias("rv"))

pairs = r1.join(r2, "movieId").where(col("u") < col("v"))
sim = (pairs.groupBy("u","v")
       .agg(ssum(col("ru")*col("rv")).alias("num"),
            sqrt(ssum(col("ru")*col("ru"))).alias("du"),
            sqrt(ssum(col("rv")*col("rv"))).alias("dv"),
            count("*").alias("n_common"))
       .withColumn("sim", col("num")/(col("du")*col("dv")))
       .select("u","v","sim"))
sim_sym = sim.select(col("u").alias("user1"), col("v").alias("user2"), "sim").unionByName(
         sim.select(col("v").alias("user1"), col("u").alias("user2"), "sim"))

# Build predictions for selected user
target = int(selected_user)
seen = ratings.filter(col("userId")==target).select("movieId").distinct()
candidates = movies.join(seen, "movieId", "left_anti").select("movieId")

neighbors = (ratings.alias("r")
             .join(user_mean.alias("umv"), col("r.userId")==col("umv.userId"))
             .join(candidates, "movieId")
             .select(col("r.userId").alias("v"), col("r.movieId").alias("movieId"),
                     col("r.rating").alias("rv"), col("umv.mu").alias("mv")))
sims_u = sim_sym.filter(col("user1")==target).select(col("user2").alias("v"), "sim")
neigh = neighbors.join(sims_u, "v", "inner")

mu_u = user_mean.filter(col("userId")==target).select("mu").first()[0]

preds = (neigh
         .withColumn("numt", col("sim")*(col("rv")-col("mv")))
         .withColumn("dent", sabs(col("sim")))
         .groupBy("movieId")
         .agg(ssum("numt").alias("num"), ssum("dent").alias("den"))
         .withColumn("pred", (col("num")/col("den")) + mu_u)
         .na.fill({"pred": mu_u})
         .orderBy(col("pred").desc()))

topN = preds.join(movies, "movieId").limit(10).toPandas()

# Join IMDb ids
topN = topN.merge(links_pd[["movieId","imdbId"]], on="movieId", how="left")

# Poster fetch helper
OMDB_API_KEY = st.secrets.get("OMDB_API_KEY", "")
def get_poster(imdb_id):
    if pd.isna(imdb_id) or not OMDB_API_KEY:
        return None
    # IMDb id in links.csv often has no 'tt' prefix; add it
    imdb_id_str = f"tt{int(imdb_id):07d}"
    try:
        r = requests.get("https://www.omdbapi.com/", params={"i": imdb_id_str, "apikey": OMDB_API_KEY}, timeout=6)
        j = r.json()
        return None if j.get("Poster") in (None, "N/A") else j["Poster"]
    except Exception:
        return None

st.title("🎬 MiniFlix")
st.subheader(f"Welcome, User {target}")

cols = st.columns(5)
for i, (_, row) in enumerate(topN.iterrows()):
    poster = get_poster(row["imdbId"])
    with cols[i % 5]:
        if poster:
            st.image(poster, use_column_width=True)
        st.caption(f"{row['title']}\n\n⭐ {row['pred']:.2f}")
