
# sapmap

[DEPRECATED] This has become a more general purpose heatmap tool and is maintained at https://github.com/seasketch/heatmap

![sapmap package](https://github.com/seasketch/python-sap-map/actions/workflows/test-sapmap.yml/badge.svg)

`sapmap` takes the areas that a group identifies as important and combines them into a map of `spatial access priorities (SAP)`

![example polygon](docs/img/survey-sap-start-end.png)

This aggregate map is used in area-based planning exercises for identifying where important areas exist and measuring the impact if changes in access are made.

Common questions it can answer include:
```
Which geographic areas are most important to the group?  The least most important?

Is area A of more value to the group than area B?  How much more?

If the use of a given area is changed, will the group be impacted?  How much importance does the group place within this area?
```

## Documentation

Detailed docs for installation and usage can be found at [https://seasketch.github.io/python-sap-map/](https://seasketch.github.io/python-sap-map/)

# Publications

This module is an implementation of previously published work, specifically the Spatial Access Priority Mapping (SAPM) framework.  It is designed for simplicity with relatively minimal input requirements, and flexibility to support more complex use cases including scaling up to represent larger populations.

Yates KL, Schoeman DS (2013) Spatial Access Priority Mapping (SAPM) with Fishers: A Quantitative GIS Method for Participatory Planning. PLoS ONE 8(7): e68424. [https://doi.org/10.1371/journal.pone.0068424](https://doi.org/10.1371/journal.pone.0068424)

Additional notable work includes:

Klein CJ, Steinback C, Watts M, Scholz AJ, Possingham HP (2010) Spatial marine zoning for fisheries and conservation. Frontiers in Ecology and the Environment 8: 349–353. Available: [https://doi.org/10.1890/090047](https://doi.org/10.1890/090047)