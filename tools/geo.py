"""Longitude / latitude -> pixel on the Ante Imperium map (3328 x 3072, y counted from the top).

The map is a 2.4x zoom of a crop of the vanilla HoI4 map, which is not a clean map projection (Europe
is stretched). So the conversion is FITTED: islands and lakes whose real extent is known were measured
on the province bitmap (their bounding boxes), and two cubic surfaces x(lon, lat) and y(lon, lat) are
fitted through those points. Typical error: 10-15 pixels, i.e. about a third of a degree.

usage in code:  from geo import to_xy;  x, y = to_xy(12.48, 41.89)      # Rome
check:          python tools/geo.py                                      # residuals of the fit
"""
import numpy as np

MAP_W, MAP_H = 3328, 3072

# (longitude, latitude, x) - west / east ends of islands and lakes measured on map/provinces.bmp
X_ANCHORS = [
    (-13.50, 65.0, 155),   # Iceland, east end
    (-10.48, 52.1, 247),   # Ireland, west end
    (-5.43, 54.6, 433),    # Ireland, east end
    (-6.23, 56.7, 407),    # Great Britain, west end (Ardnamurchan)
    (1.76, 52.5, 705),     # Great Britain, east end (Lowestoft)
    (-6.9, 62.0, 380),     # Faroe
    (-1.3, 60.3, 593),     # Shetland
    (2.34, 39.6, 751), (3.48, 39.6, 792),        # Mallorca
    (8.13, 40.0, 967), (9.83, 40.0, 1029),       # Sardinia
    (8.54, 42.2, 984), (9.56, 42.2, 1021),       # Corsica
    (12.43, 37.6, 1129), (15.65, 37.6, 1242),    # Sicily
    (9.70, 55.3, 1030), (10.85, 55.3, 1077),     # Funen
    (10.87, 55.5, 1073), (12.65, 55.5, 1134),    # Zealand
    (16.40, 56.7, 1277), (17.10, 56.7, 1305),    # Oland
    (21.83, 58.4, 1483), (23.30, 58.4, 1537),    # Saaremaa
    (23.51, 35.2, 1543), (26.32, 35.2, 1648),    # Crete
    (32.27, 35.0, 1870), (34.60, 35.0, 1960),    # Cyprus
    (46.70, 44.5, 2424), (54.00, 40.5, 2713),    # Caspian Sea
    (58.20, 45.0, 2844), (61.60, 45.0, 2991),    # Aral Sea
    (53.90, 12.5, 2681),                         # Socotra
]
# (longitude, latitude, y) - north / south ends
Y_ANCHORS = [
    (-18.0, 66.5, 262), (-18.0, 63.4, 433),      # Iceland
    (-6.9, 62.0, 597),                           # Faroe
    (-1.3, 60.35, 699),                          # Shetland
    (-3.4, 58.67, 794), (-5.2, 49.96, 1242),     # Great Britain
    (-7.4, 55.38, 973), (-9.6, 51.42, 1169),     # Ireland
    (11.8, 56.13, 960), (11.8, 54.96, 1021),     # Zealand
    (9.4, 43.01, 1603), (9.2, 41.37, 1673),      # Corsica
    (9.2, 41.26, 1680), (8.9, 38.86, 1786),      # Sardinia
    (15.5, 38.30, 1817), (15.1, 36.65, 1885),    # Sicily
    (3.0, 39.96, 1742), (3.0, 39.26, 1768),      # Mallorca
    (24.9, 35.70, 1930), (24.8, 34.92, 1962),    # Crete
    (33.6, 35.70, 1927), (33.0, 34.56, 1976),    # Cyprus
    (50.0, 47.10, 1414), (52.0, 36.55, 1890),    # Caspian Sea
    (60.0, 46.80, 1428), (59.5, 43.40, 1571),    # Aral Sea
    (53.9, 12.50, 2873),                         # Socotra
]


def _terms(lon, lat):
    lon, lat = np.asarray(lon, float) / 30.0, (np.asarray(lat, float) - 40.0) / 20.0
    return np.stack([np.ones_like(lon), lon, lat, lon * lon, lon * lat, lat * lat, lon ** 3, lat ** 3], -1)


def _fit(anchors):
    a = np.array(anchors, float)
    coef, *_ = np.linalg.lstsq(_terms(a[:, 0], a[:, 1]), a[:, 2], rcond=None)
    return coef


_CX, _CY = _fit(X_ANCHORS), _fit(Y_ANCHORS)


def to_xy(lon, lat):
    """-> (x, y) in map pixels, y from the top; not clipped to the map"""
    t = _terms(lon, lat)
    return float(t @ _CX), float(t @ _CY)


def on_map(lon, lat, margin=0):
    x, y = to_xy(lon, lat)
    return margin <= x < MAP_W - margin and margin <= y < MAP_H - margin


if __name__ == "__main__":
    for name, anchors, coef in (("x", X_ANCHORS, _CX), ("y", Y_ANCHORS, _CY)):
        a = np.array(anchors, float)
        res = _terms(a[:, 0], a[:, 1]) @ coef - a[:, 2]
        print(f"{name}: {len(a)} anchors, rms {np.sqrt((res ** 2).mean()):.1f} px, worst {np.abs(res).max():.1f} px")
    for name, lon, lat in (("Rome", 12.48, 41.89), ("Athens", 23.72, 37.97), ("Carthage", 10.32, 36.85),
                           ("Babylon", 44.42, 32.54), ("Persepolis", 52.89, 29.93), ("Gades", -6.29, 36.53),
                           ("Byzantion", 28.98, 41.01), ("Memphis", 31.25, 29.85), ("Londinium", -0.09, 51.51)):
        x, y = to_xy(lon, lat)
        print(f"{name:12s} {lon:7.2f} {lat:6.2f} -> x {x:7.1f}  y {y:7.1f}")
