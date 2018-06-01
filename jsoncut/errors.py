from boltons.iterutils import PathAccessError


class PathAssignmentError(IndexError, TypeError):
    """An amalgamation of KeyError, IndexError, and TypeError,
    representing what can occur when assign a value to a path in a
    nested object.
    """
    def __init__(self, exc, seg, path, val=None):
        self.exc = exc
        self.seg = seg
        self.path = path
        self.val = val

    def __repr__(self):
        cn = self.__class__.__name__
        return '%s(%r, %r, %r, %r)' % (
            cn, self.exc, self.seg, self.path, self.val
        )

    def __str__(self):
        return ('could not set %r in path %r to %r, got error: %r'
                % (self.seg, self.path, self.val, self.exc))


class JsonCutError(PathAccessError, PathAssignmentError):
    """Exception for Json Cut."""
