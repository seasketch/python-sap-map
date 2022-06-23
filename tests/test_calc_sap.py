from heatmap import calcSap
from shapely.geometry import shape
import json

# geometry is a rectangle that is 100m x 200m = 20,000m^2 area
geometry = shape({
    "type":"Polygon",
    "coordinates":[[[0, 0],[0, 100],[200, 100],[200, 0],[0,0]]]
})
importance = 20

def test_calc_sap_no_importance():
    # Calculation without importance (will use value of 1)
    # 1 importance / 20,000m^2 = .00005
    sap1 = calcSap(
        geometry
    )
    assert(sap1 == .00005)

def test_calc_sap():
    # Basic calculation without area scale factor
    # 20 importance / 20,000m^2 = .001
    sap1 = calcSap(
        geometry,
        importance
    )
    assert(sap1 == .001)

def test_calc_sap_areaFactor():
    # Use areaFactor to match 1km planning unit size. 1000m x 10000m = area of 1,000,000m^2.
    # Geometry now has area 1/50th of the size of a planning unit
    # 20 importance / (20,000 / 1,000,000) = 1000 SAP
    # Now we can say that the shape, with a SAP of 1000 per km^2 represents 1/1000 of a respondent
    sap2 = calcSap(
        geometry,
        importance,
        1000000
    )
    assert(sap2 == 1000)

    # Use areaFactor to match 100m planning unit size. 100m x 100m = area of 10,000m^2.
    # Geometry now has area the size of 2 planning units
    # 20 importance / (20,000 / 10,000) = 10 SAP
    # Now we can say that the shape, with a SAP of 10 per 100 km^2 represents 1/1000 of a respondent
    sap3 = calcSap(
        geometry,
        importance,
        10000
    )
    assert(sap3 == 10)

def test_calc_sap_importance_factor():
    # Assume the geometry represents the value for a group of 3000 people.
    # Use the importanceFactor to scale the SAP up, so that each of those people get
    # their 20 importance applied to the area of the shape
    # 3000 people * 20 importance / 20,000 m^2
    sap1 = calcSap(
        geometry,
        importance,
        importanceFactor=3000
    )
    assert(sap1 == 3)

if __name__ == "__main__":
    test_calc_sap()