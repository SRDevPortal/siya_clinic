import frappe

DIVISOR = 5000.0

def _f(v):
    try:
        if v is None:
            return 0.0
        if isinstance(v, str):
            v = v.replace(",", "").strip()
        return float(v or 0)
    except Exception:
        return 0.0

def calculate_pkg_weights(doc, method=None):
    """
    Calculates volumetric & applied package weight for Item.
    """

    L = _f(doc.get("sr_pkg_length"))
    W = _f(doc.get("sr_pkg_width"))
    H = _f(doc.get("sr_pkg_height"))
    dead = _f(doc.get("sr_pkg_dead_weight"))

    vol = 0.0
    if L and W and H:
        vol = (L * W * H) / DIVISOR

    applied = max(dead, vol)

    doc.sr_pkg_vol_weight = round(vol, 3)
    doc.sr_pkg_applied_weight = round(applied, 3)