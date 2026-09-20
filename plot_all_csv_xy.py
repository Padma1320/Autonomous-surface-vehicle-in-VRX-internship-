import os
import pandas as pd
import matplotlib.pyplot as plt
import utm

folder = os.path.expanduser("~/Downloads")

files = [
    "fix_40_tc_35.csv",
    "fix_50_tc_35_r1.csv",
    "fix_80_tc_35.csv",
    "fix_90_tc_35.csv"
]

figures = []

for file in files:

    filepath = os.path.join(folder, file)

    df = pd.read_csv(filepath)

    lat_col = [c for c in df.columns if "lat" in c.lower()][0]
    lon_col = [c for c in df.columns if ("lon" in c.lower() or "long" in c.lower())][0]

    lat0 = float(df[lat_col].iloc[0])
    lon0 = float(df[lon_col].iloc[0])

    e0, n0, zone_num, zone_letter = utm.from_latlon(lat0, lon0)

    x = []
    y = []

    for lat, lon in zip(df[lat_col], df[lon_col]):

        easting, northing, _, _ = utm.from_latlon(
            float(lat),
            float(lon)
        )

        x.append(easting - e0)
        y.append(northing - n0)

    df["x_m"] = x
    df["y_m"] = y

    fig = plt.figure(figsize=(8,6))

    plt.plot(
        df["x_m"].to_numpy(),
        df["y_m"].to_numpy(),
        linewidth=2
    )

    plt.scatter(
        df["x_m"].iloc[0],
        df["y_m"].iloc[0],
        s=80,
        label="Start"
    )

    plt.scatter(
        df["x_m"].iloc[-1],
        df["y_m"].iloc[-1],
        s=80,
        label="End"
    )

    plt.xlabel("X Position (m)")
    plt.ylabel("Y Position (m)")
    plt.title(file.replace(".csv",""))
    plt.grid(True)
    plt.axis("equal")
    plt.legend()

    figures.append(fig)

# Opens all four windows together
plt.show(block=False)

input("Press ENTER to close all plots...")
