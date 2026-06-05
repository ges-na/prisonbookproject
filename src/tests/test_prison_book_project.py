from django.test import TestCase

from prisonbookproject import __version__


def test_version():
    assert __version__ == "0.1.0"


class TestAdminEndpoints(TestCase):
    pass
