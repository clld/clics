import pytest


@pytest.mark.parametrize(
    "method,path",
    [
        ('get_html', '/'),
        ('get_html', '/legal'),
        ('get_html', '/about'),
        ('get_html', '/download'),
        ('get_html', '/contributions/lexibank-northeuralex'),
        ('get_dt', '/contributions'),
        ('get_dt', '/contributions?sSearch_1=madang')
    ])
def test_pages(app, method, path):
    getattr(app, method)(path)
