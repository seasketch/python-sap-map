from sapmap import genSapMap
import os.path
import rasterio
import numpy as np

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
resolution = 100
pixelArea = resolution * resolution

def test_small_polygon_lost():
    infile = os.path.join(DATA, 'off-center-polygon.geojson')
    outfile = os.path.join(DATA, 'off-center-polygon.tif')

    assert(os.path.isfile(infile))
    manifest = genSapMap(
        infile,
        outResolution=resolution,
        bounds=[-100, -100, 100, 100],
        areaFactor=pixelArea
    )
    assert(os.path.isfile(outfile))
    assert(len(manifest['included']) == 1)

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
        # Bresenham centerline algorithm will miss the small polygon and get zero
        assert(np.all((arr == 0)))

def test_small_polygon_found():
    infile = os.path.join(DATA, 'off-center-polygon.geojson')
    outfile = os.path.join(DATA, 'off-center-polygon.tif')

    assert(os.path.isfile(infile))
    manifest = genSapMap(
        infile,
        outResolution=resolution,
        bounds=[-100, -100, 100, 100],
        areaFactor=pixelArea,
        allTouchedSmall=True
    )
    assert(os.path.isfile(outfile))
    assert(len(manifest['included']) == 1)

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
        # should pick up polygon smaller than pixel resolution
        checkArr = np.array([[
            [0,  32],
            [0, 0],
        ]], dtype=np.float32)

        np.testing.assert_array_equal(arr, checkArr)

# Used for debugging
if __name__ == "__main__":
    test_small_polygon_lost()
    test_small_polygon_found()