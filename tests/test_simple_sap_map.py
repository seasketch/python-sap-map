from sapmap import genSapMap
import os.path

def test_simple_sap_map():
    INPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "input")
    OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

    shapes = os.path.join(INPUT, 'simple-polygon.shp')
    raster = os.path.join(OUTPUT, 'simple-polygon.tif')

    assert(os.path.isfile(shapes))
    genSapMap(shapes, raster, cellSize=100)
    assert(os.path.isfile(raster))

if __name__ == "__main__":
    test_simple_sap_map()