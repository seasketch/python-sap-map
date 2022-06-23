from sapmap import genHeatMap
import os.path
import rasterio
import numpy as np

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
resolution = 100
pixelArea = (resolution * resolution)
infile = os.path.join(DATA, 'simple-polygon.geojson')
outfile = os.path.join(DATA, 'simple-polygon.tif')

def test_simple_sap_map():
    assert(os.path.isfile(infile))
    manifest = genHeatMap(infile, outResolution=resolution, areaFactor=pixelArea, overwrite=True)
    assert(os.path.isfile(outfile))
    assert(len(manifest['included']) == 5)

    with rasterio.open(outfile) as reader:
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

def test_importance_sap_map():
    """Includes importanceField
    """
    assert(os.path.isfile(infile))
    manifest = genHeatMap(infile, outResolution=resolution, areaFactor=pixelArea, importanceField='importance', overwrite=True)
    assert(os.path.isfile(outfile))
    assert(len(manifest['included']) == 5)

    with rasterio.open(outfile) as reader:
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
            [20., 10.,  0.,  0.],
            [10.,  0., 10.,  0.],
            [ 0., 10., 30., 10.],
            [ 0.,  0., 10., 10.]
        ]], dtype=np.float32)
        np.testing.assert_array_equal(arr, checkArr)

# Used for debugging
if __name__ == "__main__":
    test_simple_sap_map()
    test_importance_sap_map()