import geopandas as gpd
import folium

# ─────────────────────────────────────────
# STEP 1 — Load all data
# ─────────────────────────────────────────
lakes = gpd.read_file("data/processed/lakes_cleaned.gpkg")
buffers = gpd.read_file("data/processed/lake_buffers_30m.gpkg")
flagged = gpd.read_file("data/processed/ndbi_diff_flagged.gpkg")

# Convert all to lat/lon for folium
lakes = lakes.to_crs(epsg=4326)
buffers = buffers.to_crs(epsg=4326)
flagged = flagged.to_crs(epsg=4326)

print(f"Lakes loaded: {len(lakes)}")
print(f"Buffer zones loaded: {len(buffers)}")
print(f"Flagged zones loaded: {len(flagged)}")

# ─────────────────────────────────────────
# STEP 2 — Create base map
# ─────────────────────────────────────────
m = folium.Map(location=[11.0168, 76.9558], zoom_start=11)

# ─────────────────────────────────────────
# STEP 3 — Draw lakes in blue
# ─────────────────────────────────────────
for _, row in lakes.iterrows():
    if row.geometry is not None:
        folium.GeoJson(
            row.geometry.__geo_interface__,
            style_function=lambda x: {
                "fillColor": "blue",
                "color": "blue",
                "weight": 1,
                "fillOpacity": 0.5
            }
        ).add_to(m)

print("Lakes drawn!")

# ─────────────────────────────────────────
# STEP 4 — Draw buffer zones in orange
# ─────────────────────────────────────────
for _, row in buffers.iterrows():
    if row.geometry is not None:
        folium.GeoJson(
            row.geometry.__geo_interface__,
            style_function=lambda x: {
                "fillColor": "orange",
                "color": "orange",
                "weight": 1,
                "fillOpacity": 0.15
            }
        ).add_to(m)

print("Buffer zones drawn!")

# ─────────────────────────────────────────
# STEP 5 — Draw flagged zones
# ─────────────────────────────────────────
for _, row in flagged.iterrows():
    if row.geometry is None:
        continue

    flag = row.get("Change_Flag", "")

    if flag == "High Change":
        color = "red"
    elif flag == "Moderate Change":
        color = "yellow"
    else:
        continue  # skip no change zones

    folium.GeoJson(
        row.geometry.__geo_interface__,
        style_function=lambda x, c=color: {
            "fillColor": c,
            "color": c,
            "weight": 2,
            "fillOpacity": 0.6
        },
        tooltip=f"Flag: {flag} | NDBI diff: {row.get('NDBI_Diff_Mean', 'N/A'):.3f}"
    ).add_to(m)

print("Flagged zones drawn!")

# ─────────────────────────────────────────
# STEP 6 — Add legend
# ─────────────────────────────────────────
legend_html = """
<div style="position: fixed; bottom: 40px; left: 40px; z-index: 1000;
     background-color: white; padding: 15px; border-radius: 8px;
     border: 2px solid grey; font-size: 14px;">
  <b>Lake Buffer Encroachment Detector</b><br>
  <i style="background:blue;width:12px;height:12px;display:inline-block;opacity:0.6"></i> Lake boundary<br>
  <i style="background:orange;width:12px;height:12px;display:inline-block;opacity:0.4"></i> 30m buffer zone<br>
  <i style="background:yellow;width:12px;height:12px;display:inline-block;opacity:0.8"></i> Moderate change<br>
  <i style="background:red;width:12px;height:12px;display:inline-block;opacity:0.8"></i> High confidence change<br>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

# ─────────────────────────────────────────
# STEP 7 — Save map
# ─────────────────────────────────────────
m.save("output/flagged_zones.html")
print("\nMap saved to output/flagged_zones.html")
print("Open it in your browser to explore!")