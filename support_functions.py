# Creating a Perl Hash using Python
# reference: https://stackoverflow.com/questions/2435989/how-do-i-do-advanced-python-hash-autovivification
class AutoVivification(dict):
    """Implementation of perl's autovivification feature. Has features from both dicts and lists,
    dynamically generates new subitems as needed, and allows for working (somewhat) as a basic type.
    """
    def __getitem__(self, item):
        if isinstance(item, slice):
            d = AutoVivification()
            items = sorted(self.iteritems(), reverse=True)
            k,v = items.pop(0)
            while 1:
                if (item.start < k < item.stop):
                    d[k] = v
                elif k > item.stop:
                    break
                if item.step:
                    for x in range(item.step):
                        k,v = items.pop(0)
                else:
                    k,v = items.pop(0)
            return d
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

    def __add__(self, other):
        """If attempting addition, use our length as the 'value'."""
        return len(self) + other

    def __radd__(self, other):
        """If the other type does not support addition with us, this addition method will be tried."""
        return len(self) + other

    def append(self, item):
        """Add the item to the dict, giving it a higher integer key than any currently in use."""
        largestKey = sorted(self.keys())[-1]
        if isinstance(largestKey, str):
            self.__setitem__(0, item)
        elif isinstance(largestKey, int):
            self.__setitem__(largestKey+1, item)

    def count(self, item):
        """Count the number of keys with the specified item."""
        return sum([1 for x in self.items() if x == item])

    def __eq__(self, other):
        """od.__eq__(y) <==> od==y. Comparison to another AV is order-sensitive
        while comparison to a regular mapping is order-insensitive. """
        if isinstance(other, AutoVivification):
            return len(self)==len(other) and self.items() == other.items()
        return dict.__eq__(self, other)

    def __ne__(self, other):
        """od.__ne__(y) <==> od!=y"""
        return not self == other

