from sapmap import genSapMap
import os.path
import rasterio
import numpy as np

def test_simple_sap_map():
    INPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "input")
    OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

    shapes = os.path.join(INPUT, 'simple-polygon.geojson')
    raster = os.path.join(OUTPUT, 'simple-polygon.tif')

    assert(os.path.isfile(shapes))
    manifest = genSapMap(shapes, raster, outResolution=100)
    assert(os.path.isfile(raster))
    assert(len(manifest['included']) == 5)

    with rasterio.open(raster) as reader:
        assert(manifest['outBounds'][0] == reader.bounds.left)
        assert(manifest['outBounds'][1] == reader.bounds.bottom)
        assert(manifest['outBounds'][2] == reader.bounds.right)
        assert(manifest['outBounds'][3] == reader.bounds.top)
        
        assert(manifest['height'] == reader.height == 4)
        assert(manifest['width'] == reader.width == 4)
        assert(manifest['params']['outResolution'] == reader.res[0] == reader.res[1])
        assert(reader.nodata == 0.0)

        arr = reader.read()
        # Hand verified values, view simple-polygon.tif in qgis using the tests/base/testdata.qgz project to verify
        checkArr = np.array([[
            [1,   0.5, 0,    0],
            [0.5, 0,   0.5,  0],
            [0,   0.5, 1.25, 0.25],
            [0,   0,   0.25, 0.25]
        ]], dtype=np.float32)
        np.testing.assert_array_equal(arr, checkArr)
        

# Used for debugging
if __name__ == "__main__":
    test_simple_sap_map()