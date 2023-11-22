import pandas as pd

path = "../blammo-bot-private/user_data.csv"
df = pd.read_csv(path, index_col=False, header=0)
print(df.head())
# df = df.sort_values(by="gamble_loss", ascending=False)
# df = df.reset_index(drop=True)
print(df.head())
print("----------------------------")
df["points_rank"] = df["points"].rank(ascending=0)
index = df.index[df["username"] == "docclaremore"].tolist()
rank = int(df.iloc[index]["points_rank"])
print(df)
print(index)
print(rank)
