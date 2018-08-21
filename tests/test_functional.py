import pytest


@pytest.mark.parametrize(
    "method,path",
    [
        ('get_html', '/'),
        ('get_html', '/legal'),
        ('get_html', '/about'),
        ('get_html', '/download'),
        ('get_html', '/contributions'),
        ('get_html', '/contributions/lexibank-northeuralex'),
    ])
def test_pages(app, method, path):
    getattr(app, method)(path)
