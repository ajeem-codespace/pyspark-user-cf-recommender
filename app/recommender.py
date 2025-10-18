from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, sqrt, sum as ssum, abs as sabs, count
import pandas as pd

def build_spark():
    return (SparkSession.builder
            .appName("MiniFlix-Recommender")
            .master("local[*]")
            .getOrCreate())

def get_recommendations(target_user: int, ratings_path: str, movies_path: str, links_path: str):
    spark = build_spark()
    ratings = (spark.read.option("header", True).option("inferSchema", True).csv(ratings_path)
               .select("userId", "movieId", "rating"))
    movies = spark.read.option("header", True).option("inferSchema", True).csv(movies_path)
    links = spark.read.option("header", True).option("inferSchema", True).csv(links_path)

    user_mean = ratings.groupBy("userId").agg(avg("rating").alias("mu"))
    r1 = (ratings.join(user_mean, "userId")
          .withColumn("rc", col("rating") - col("mu"))
          .select(col("userId").alias("u"), "movieId", col("rc").alias("ru")))
    r2 = r1.select(col("u").alias("v"), "movieId", col("ru").alias("rv"))
    pairs = r1.join(r2, "movieId").where(col("u") < col("v"))

    sim = (pairs.groupBy("u", "v")
           .agg(ssum(col("ru") * col("rv")).alias("num"),
                sqrt(ssum(col("ru") * col("ru"))).alias("du"),
                sqrt(ssum(col("rv") * col("rv"))).alias("dv"),
                count("*").alias("n_common"))
           .withColumn("sim", col("num") / (col("du") * col("dv")))
           .select("u", "v", "sim"))
    sim_sym = sim.select(col("u").alias("user1"), col("v").alias("user2"), "sim").unionByName(
             sim.select(col("v").alias("user1"), col("u").alias("user2"), "sim"))

    seen = ratings.filter(col("userId") == target_user).select("movieId").distinct()
    candidates = movies.join(seen, "movieId", "left_anti").select("movieId")
    neighbors = (ratings.alias("r")
                 .join(user_mean.alias("umv"), col("r.userId") == col("umv.userId"))
                 .join(candidates, "movieId")
                 .select(col("r.userId").alias("v"),
                         col("r.movieId").alias("movieId"),
                         col("r.rating").alias("rv"),
                         col("umv.mu").alias("mv")))
    sims_u = sim_sym.filter(col("user1") == target_user).select(col("user2").alias("v"), "sim")
    neigh = neighbors.join(sims_u, "v", "inner")

    mu_u = user_mean.filter(col("userId") == target_user).select("mu").first()[0]

    preds = (neigh
             .withColumn("numt", col("sim") * (col("rv") - col("mv")))
             .withColumn("dent", sabs(col("sim")))
             .groupBy("movieId")
             .agg(ssum("numt").alias("num"), ssum("dent").alias("den"))
             .withColumn("pred", (col("num") / col("den")) + mu_u)
             .na.fill({"pred": mu_u})
             .orderBy(col("pred").desc()))

    topN = preds.join(movies, "movieId").limit(10).toPandas()
    topN = topN.merge(links.toPandas()[["movieId", "imdbId"]], on="movieId", how="left")

    spark.stop()
    return topN
