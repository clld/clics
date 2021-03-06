import pytest


@pytest.mark.parametrize(
    "method,path",
    [
        ('get_html', '/'),
        ('get_html', '/legal'),
        ('get_html', '/about'),
        ('get_html', '/download'),
        ('get_html', '/contributions/northeuralex'),
        ('get_dt', '/contributions'),
        ('get_dt', '/contributions?sSearch_1=madang'),
        ('get_json', '/parameters/5.geojson'),
        ('get_json', '/graphs/infomap_11_GRAIN.json'),
    ])
def test_pages(app, method, path):
    getattr(app, method)(path)
