import pytest


@pytest.mark.parametrize(
    "method,path",
    [
        ('get_html', '/'),
        ('get_html', '/legal'),
        ('get_html', '/download'),
    ])
def test_pages(app, method, path):
    getattr(app, method)(path)
