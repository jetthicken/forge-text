// Build geo assets for the Forge ops dashboard.
// - State outline SVG paths from us-atlas states-albers-10m (pre-projected, 975x610)
// - Zip centroid coordinates projected with the matching d3.geoAlbersUsa()
import { readFileSync, writeFileSync } from "node:fs";
import * as topojson from "topojson-client";
import { geoAlbersUsa, geoPath } from "d3-geo";

const topo = JSON.parse(
  readFileSync("node_modules/us-atlas/states-albers-10m.json", "utf8")
);
const states = topojson.feature(topo, topo.objects.states);
const path = geoPath(); // identity: coordinates already projected

const fmt = (d) => d.replace(/(\.\d)\d+/g, "$1"); // trim precision
const statePaths = states.features.map((f) => ({
  id: f.id,
  name: f.properties.name,
  d: fmt(path(f)),
}));

// Same projection used by us-atlas prebuilt files
const proj = geoAlbersUsa().scale(1300).translate([487.5, 305]);

// zip: [lat, lng] centroids (2013 Census gazetteer values, city-level accuracy)
const zips = {
  "16033": [40.7686, -80.0623],
  "17225": [39.7887, -77.7379],
  "17257": [40.0453, -77.5188],
  "22901": [38.0879, -78.5569],
  "22902": [37.9856, -78.4703],
  "22903": [38.0303, -78.5299],
  "22932": [38.1442, -78.6963],
  "25703": [38.4137, -82.4249],
  "27812": [35.8069, -77.3843],
  "27828": [35.5875, -77.5813],
  "27834": [35.6272, -77.3948],
  "27858": [35.5713, -77.3229],
  "28513": [35.4692, -77.4176],
  "28530": [35.3760, -77.4322],
  "28532": [34.8905, -76.8887],
  "28590": [35.5296, -77.4033],
  "29902": [32.4104, -80.6963],
  "29906": [32.4457, -80.7440],
  "29935": [32.3830, -80.6970],
  "43064": [40.1096, -83.2842],
  "43302": [40.5959, -83.1330],
  "43315": [40.4988, -82.8908],
  "43338": [40.5528, -82.8232],
  "43410": [41.3070, -82.9788],
  "43725": [40.0329, -81.5914],
  "43907": [40.2657, -81.0037],
  "44288": [41.2358, -81.0454],
  "44444": [41.1849, -80.9772],
  "44483": [41.2624, -80.8178],
  "44484": [41.2320, -80.7566],
  "44485": [41.2394, -80.8595],
  "44663": [40.4787, -81.4441],
  "44820": [40.8107, -82.9720],
  "44857": [41.2404, -82.6110],
  "44890": [41.0620, -82.7195],
  "45810": [40.7695, -83.8221],
  "49401": [42.9764, -85.9553],
  "54601": [43.7942, -91.2011],
  "54603": [43.8598, -91.2405],
  "54650": [43.8938, -91.2110],
  "65201": [38.9349, -92.3079],
  "65202": [39.0043, -92.3092],
  "65619": [37.1188, -93.4030],
  "65804": [37.1509, -93.2519],
  "65807": [37.1600, -93.3313],
  "65809": [37.1743, -93.2028],
  "65810": [37.1174, -93.3080],
  "70586": [30.6942, -92.2827],
  "71378": [31.9678, -91.6540],
  "71465": [31.9028, -92.2276],
};

const zipXY = {};
for (const [z, [lat, lng]] of Object.entries(zips)) {
  const p = proj([lng, lat]);
  if (!p) throw new Error("projection failed for " + z);
  zipXY[z] = [Math.round(p[0] * 10) / 10, Math.round(p[1] * 10) / 10];
}

writeFileSync("geo_states.json", JSON.stringify(statePaths));
writeFileSync("geo_zips.json", JSON.stringify(zipXY));
console.log("states:", statePaths.length, "zips:", Object.keys(zipXY).length);
console.log(
  "states bytes:",
  JSON.stringify(statePaths).length,
  "sample zip 54601 ->",
  zipXY["54601"]
);
