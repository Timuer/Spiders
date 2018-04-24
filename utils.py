import time

class Model(object):
	def __repr__(self):
		cls_name = self.__class__.__name__
		props = ["{}: ({})".format(k, v) for k, v in self.__dict__.items()]
		return cls_name + "\n" + "\n".join(props)


def reconnect(fn):
	def func(*args, **kwargs):
		limit = 301
		step = 30
		for t in range(1, limit, step):
			try:
				return fn(*args, **kwargs)
			except Exception as ex:
				print(ex, "{}秒后重新连接".format(t))
				time.sleep(t)
				continue
	return func
