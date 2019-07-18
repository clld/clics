
# CLICS clld app

The database of the CLICS clld app is initialized reading data of a CLICS
dataset via pyclics. To do so, several artifacts must have been created with
the `clics` command before:
- the CLICS sqlite db, running `clics load`
- `subgraph` and `infomap` clusters, running `clics -t 3 cluster (subgraph|infomap)`

The initialization script will look for these artifacts in a directory `clics3` parallel
to the clone of the web app repository. So the directory layout should look like this
```
+- clics
+- clics3
 +- app
 | +- cluster
 |   +- infomap
 |   +- subgraph
 +- clics.sqlite
```
