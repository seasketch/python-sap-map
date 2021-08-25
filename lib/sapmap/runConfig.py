class RunConfig(object):
    cellSize = 100
    infile = './input.shp'
    outfile = './output.tif'
    importanceField = 'weight'
    maxArea = None
    maxSap = None

    def __init__(self, dictionary):
        self.__dict__.update(dictionary)