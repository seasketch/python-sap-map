from sapmap import calcSap
import json


def test_calc_sap():
    # geometry is a rectangle that is 100m x 200m = 20,000m^2
    feature = json.loads('{"type":"Feature","properties":{"weight":20},"geometry":{"type":"Polygon","coordinates":[[[0, 0],[0, 100],[200, 100],[200, 0],[0,0]]]}}')
    
    # cellSize is 100m x 100m = area of 10,000m^2. shape has an area the size of 2 cells, yielding a sap of 10 which is half.
    # Think of it as splitting the importance in half between the two cells worth of area
    sap1 = calcSap(feature['geometry'], feature['properties']['weight'], 100)
    assert(sap1 == 10)

    # shape has an area of half of a cell, giving it a sap that is 2x the importance
    sap2 = calcSap(feature['geometry'], feature['properties']['weight'], 200)
    assert(sap2 == 40)

if __name__ == "__main__":
    test_calc_sap()