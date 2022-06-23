from sapmap import genSapMap
import os.path
import rasterio
import numpy as np

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
resolution = 100
pixelArea = resolution * resolution

def test_outer_bounds():
    """ Test bounds larger than the input features
    """
    infile = os.path.join(DATA, 'simple-polygon.geojson')
    outfile = os.path.join(DATA, 'simple-polygon.tif')

    assert(os.path.isfile(infile))
    manifest = genSapMap(infile, outResolution=resolution, bounds=[-400, -400, 400, 400], areaFactor=pixelArea, overwrite=True)
    assert(os.path.isfile(outfile))
    assert(len(manifest['included']) == 5)

    with rasterio.open(os.path.join(DATA, 'simple-polygon.tif')) as reader:
        assert(manifest['outBounds'][0] == reader.bounds.left)
        assert(manifest['outBounds'][1] == reader.bounds.bottom)
        assert(manifest['outBounds'][2] == reader.bounds.right)
        assert(manifest['outBounds'][3] == reader.bounds.top)
        
        assert(manifest['height'] == reader.height == 8)
        assert(manifest['width'] == reader.width == 8)
        assert(manifest['params']['outResolution'] == reader.res[0] == reader.res[1])
        assert(reader.nodata == 0.0)

        arr = reader.read()
        # Extent is that of simple-polygon.shp with additional 200 meters on each side
        # Hand verified values, should be same as simple with two additional cells of zeroes around it
        # view simple-polygon.tif in qgis using the tests/base/testdata.qgz project to verify
        checkArr = np.array([[
            [0, 0, 0,   0,   0,    0, 0, 0],
            [0, 0, 0,   0,   0,    0, 0, 0],
            [0, 0, 1,   0.5, 0,    0, 0, 0],
            [0, 0, 0.5, 0,   0.5,  0, 0, 0],
            [0, 0, 0,   0.5, 1.25, 0.25, 0, 0],
            [0, 0, 0,   0,   0.25, 0.25, 0, 0],
            [0, 0, 0,   0,   0,    0, 0, 0],
            [0, 0, 0,   0,   0,    0, 0, 0]
        ]], dtype=np.float32)
        np.testing.assert_array_equal(arr, checkArr)


def test_inner_bounds():
    """ Test bounds larger than the input features
    """
    infile = os.path.join(DATA, 'simple-polygon.geojson')
    outfile = os.path.join(DATA, 'simple-polygon.tif')

    assert(os.path.isfile(infile))
    manifest = genSapMap(
        infile,
        outResolution=resolution,
        bounds=[-100, -100, 100, 100],
        areaFactor=pixelArea,
        overwrite=True
    )
    assert(os.path.isfile(outfile))
    assert(len(manifest['included']) == 5)

    with rasterio.open(outfile) as reader:
        assert(manifest['outBounds'][0] == reader.bounds.left)
        assert(manifest['outBounds'][1] == reader.bounds.bottom)
        assert(manifest['outBounds'][2] == reader.bounds.right)
        assert(manifest['outBounds'][3] == reader.bounds.top)
        
        assert(manifest['height'] == reader.height == 2)
        assert(manifest['width'] == reader.width == 2)
        assert(manifest['params']['outResolution'] == reader.res[0] == reader.res[1])
        assert(reader.nodata == 0.0)

        arr = reader.read()
        # Extent is that of simple-polygon.shp with additional 200 meters on each side
        # Hand verified values, should be same as simple with two additional cells of zeroes around it
        # view simple-polygon.tif in qgis using the tests/base/testdata.qgz project to verify
        checkArr = np.array([[
            [0,   0.5],
            [0.5, 1.25],
        ]], dtype=np.float32)

        np.testing.assert_array_equal(arr, checkArr)

# Used for debugging
if __name__ == "__main__":
    test_inner_bounds()