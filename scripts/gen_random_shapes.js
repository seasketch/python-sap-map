const turf = require('@turf/turf')
const fs = require('fs')

const randPolys = turf.randomPolygon(10000, {bbox: [ -141.002725124365, 40.0511489973286, -47.6941470240656, 86.4318731326392 ], max_radial_length: 0.5})

const proppedPolys = turf.featureReduce(randPolys, (previousValue, currentFeature, featureIndex) => {
  return previousValue.concat({ 
    ...currentFeature,
    id: featureIndex,
    properties: { id: featureIndex, importance: Math.floor(Math.random() * 100) }
  })
}, []);

const fc = turf.featureCollection(proppedPolys)

let data = JSON.stringify(fc, null, 2);

fs.writeFile('testPolygons.geojson', data, (err) => {
  if (err) throw err;
  console.log('Data written to file');
});