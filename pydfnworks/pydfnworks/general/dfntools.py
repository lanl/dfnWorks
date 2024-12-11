""" Tools for dfnworks data """


class Frozen(object):
    """
    Prevents adding new attributes to classes once _freeze() is called on the class.

    Parameters
    ----------
    None

    Returns
    -------
    None

    Notes
    -----
    None

    """
    frozen = False

    def __setattr__(self, key, value):
        """
        Set attribute to a value.


        Parameters
        ----------
            self : object
                DFN Class

            key : string
                the key of the attribute being set.

            value : the value of the attribute being set. 

        Returns
        -------
            None

        Notes
        -----
            None

        """
        if not self.frozen or hasattr(self, key):
            object.__setattr__(self, key, value)
        else:
            raise AttributeError(
                str(key) + ' is not a valid attribute for ' +
                self._class__.__name__)

    def _freeze(self):
        """
        Prevents adding new attributes to a class.


        Parameters
        ----------
            self : object
                DFN Class

        Returns
        -------
            Return True to freeze attributes

        Notes
        -----
            None

        """
    
        self.frozen = True

    def _unfreeze(self):
        """
        Allows adding new attributes to a class.


        Parameters
        ----------
            self : object
                DFN Class

        Returns
        -------
            Return False to un-freeze attributes

        Notes
        -----
            None

        """
        self.frozen = False
