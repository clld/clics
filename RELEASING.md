# CLICS clld app

```shell
git clone https://github.com/clld/clics
git clone --branch v1.0 --depth 1 https://github.com/clics/clics4
cd clics4
pip install -e .
cldfbench download lexibank_clics4.py
cd ../clics
pip install -e .[test]
```

```shell
clld initdb development.ini --cldf ../clics4/cldf/StructureDataset-metadata.json
```

```shell
pytest
```

Store the tested requirements:
```shell
pip freeze > requirements.txt
```

Store a db dump:
```shell
pg_dump -xO --compress gzip:9 clics > clics.sql.gz
```

