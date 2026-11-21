# Schemas for checking exports

Copies of the schemas a Camtrap DP 1.0.1 package is checked against, so that the tests check an
export without a network connection:

| File | Source | Licence |
|---|---|---|
| `camtrap-dp-profile.json`, `*-table-schema.json` | https://github.com/tdwg/camtrap-dp, tag 1.0.1 | MIT, see `LICENSE-camtrap-dp` |
| `data-package.json` | https://specs.frictionlessdata.io/schemas/data-package.json | Unlicense |
| `GeoJSON.json` | https://geojson.org/schema/GeoJSON.json (https://github.com/geojson/schema) | MIT |

The profile refers to GeoJSON through http://json.schemastore.org/geojson.json, which only points
on to `GeoJSON.json`; the tests resolve that address to `GeoJSON.json` directly.
