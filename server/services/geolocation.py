import math


def haversine(lat1, lng1, lat2, lng2):
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


HAVERSINE_SQL = """
CREATE OR REPLACE FUNCTION haversine(lat1 float, lng1 float, lat2 float, lng2 float)
RETURNS float AS $$
DECLARE
    R float := 6371.0;
    phi1 float := radians(lat1);
    phi2 float := radians(lat2);
    dphi float := radians(lat2 - lat1);
    dlambda float := radians(lng2 - lng1);
    a float := sin(dphi/2)^2 + cos(phi1) * cos(phi2) * sin(dlambda/2)^2;
    c float := 2 * atan2(sqrt(a), sqrt(1-a));
BEGIN
    RETURN R * c;
END;
$$ LANGUAGE plpgsql IMMUTABLE;
"""
