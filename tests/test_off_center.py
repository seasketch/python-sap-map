from sapmap import genSapMap
import os.path
import rasterio
import numpy as np

def test_off_center():
    INPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "input")
    OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

    shapes = os.path.join(INPUT, 'off-center-polygon.geojson')
    raster = os.path.join(OUTPUT, 'off-center-polygon.tif')

    assert(os.path.isfile(shapes))
    manifest = genSapMap(shapes, raster, outResolution=100, bounds=[-100, -100, 100, 100])
    assert(os.path.isfile(raster))
    assert(len(manifest['included']) == 1)

    with rasterio.open(raster) as reader:
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

def test_all_touched():
    INPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "input")
    OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

    shapes = os.path.join(INPUT, 'off-center-polygon.geojson')
    raster = os.path.join(OUTPUT, 'off-center-polygon.tif')

    assert(os.path.isfile(shapes))
    manifest = genSapMap(shapes, raster, outResolution=100, bounds=[-100, -100, 100, 100], allTouched=True)
    assert(os.path.isfile(raster))
    assert(len(manifest['included']) == 1)

    with rasterio.open(raster) as reader:
        assert(manifest['outBounds'][0] == reader.bounds.left)
        assert(manifest['outBounds'][1] == reader.bounds.bottom)
        assert(manifest['outBounds'][2] == reader.bounds.right)
        assert(manifest['outBounds'][3] == reader.bounds.top)
        
        assert(manifest['height'] == reader.height == 2)
        assert(manifest['width'] == reader.width == 2)
        assert(manifest['params']['outResolution'] == reader.res[0] == reader.res[1])
        assert(reader.nodata == 0.0)

        arr = reader.read()
        # all_touched will pick up the small polygon
        checkArr = np.array([[
            [0,  32],
            [0, 0],
        ]], dtype=np.float32)

        np.testing.assert_array_equal(arr, checkArr)

# Used for debugging
if __name__ == "__main__":
    test_all_touched()