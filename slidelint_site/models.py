from persistent import Persistent


class Counter(Persistent):
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1
        return self.count


def appmaker(zodb_root):
    if not 'app_root' in zodb_root:
        app_root = Counter()
        zodb_root['app_root'] = app_root
        import transaction
        transaction.commit()
    return zodb_root['app_root']
