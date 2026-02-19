"""
Minimal stub of pkg_resources for compatibility with apscheduler in Python 3.14.
Provides get_distribution() and DistributionNotFound.
"""
class DistributionNotFound(Exception):
    pass

def get_distribution(name):
    """
    Return a dummy distribution object with a version attribute.
    This is a stub used when pkg_resources is unavailable.
    """
    class DummyDist:
        version = "0.0"
    return DummyDist()


def iter_entry_points(group, name=None):
    """
    Return an empty list of entry points.
    """
    return []
