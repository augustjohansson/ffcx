__author__ = "Anders Logg (logg@tti-c.org)"
__date__ = "2004-10-07"
__copyright__ = "Copyright (c) 2004 Anders Logg"
__license__  = "GNU GPL Version 2"

# FFC modules
from index import Index

class Transform:

    """A Transform represents an element of the inverse Jacobian
    matrix of the affine map from the reference cell. With X the
    coordinates on the reference cell mapped to real coordinates x by
    an affine map x = F(X), a Transform represents the partial
    derivative dX/dx."""
    
    def __init__(self, index0 = None, index1 = None):
        "Create Transform."
        if isinstance(index0, Transform):
            self.index0 = Index(index0.index0)
            self.index1 = Index(index0.index1)
        else:
            self.index0 = Index(index0)
            self.index1 = Index(index1)
        return

    def __repr__(self):
        "Print nicely formatted representation of Factor."
        return "(dX" + self.index0.__repr__() + "/" + "dx" + self.index1.__repr__() + ")"
