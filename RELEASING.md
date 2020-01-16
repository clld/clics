
# CLICS clld app

The database of the CLICS clld app is initialized reading data of a CLICS
dataset via pyclics. To do so, several artifacts must have been created with
the `clics` command before:
- the CLICS sqlite db, running `clics load`
- `subgraph` and `infomap` clusters, running `clics -t 3 cluster (subgraph|infomap)`

To initialize the app db, run
```
clics-app init PATH/TO/CLICS_DATA_REPOS
```

