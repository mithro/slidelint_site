import unittest
from pyramid import testing
from testfixtures import compare


class CounterModelTests(unittest.TestCase):

    def test_constructor(self):
        from slidelint_site.models import Counter
        instance = Counter()
        compare(instance.count, 0)
        rez = instance.increment()
        compare(rez, 1)
        compare(instance.count, 1)


class AppmakerTests(unittest.TestCase):

    def _callFUT(self, zodb_root):
        from slidelint_site.models import appmaker
        return appmaker(zodb_root)

    def test_it(self):
        root = {}
        self._callFUT(root)
        compare(root['app_root'].count, 0)


class ViewMainTests(unittest.TestCase):
    def test_it(self):
        from slidelint_site.views import main_view
        context = testing.DummyResource()
        context.count = 0
        request = testing.DummyRequest()
        response = main_view(context, request)
        compare(response, {'count': 0})
