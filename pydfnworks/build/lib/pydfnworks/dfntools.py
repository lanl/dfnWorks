""" Tools for dfnworks data """

class Frozen(object):
	"""
	Prevents adding new attributes to classes once _freeze() is called on the class.
	"""
	__frozen = False

	def __setattr__(self, key, value):
	    """
            Set attribute to a value.
            Args:
                key (string): the key of the attribute being set.
                value : the value of the attribute being set. 
            """
            if not self.__frozen or hasattr(self, key):
		object.__setattr__(self, key, value)
	    else:
		raise AttributeError(str(key) + ' is not a valid attribute for ' + self.__class__.__name__)

	def _freeze(self):
            """
            Prevents adding new attributes to a class.
            """
            self.__frozen = True

	def _unfreeze(self):
	    """
            Allows adding new attributes to classes.
            """
            self.__frozen = False

