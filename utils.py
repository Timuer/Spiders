class Model(object):
	def __repr__(self):
		cls_name = self.__class__.__name__
		props = ["{}: ({})".format(k, v) for k, v in self.__dict__.items()]
		return cls_name + "\n" + "\n".join(props)
