__all__ = ["QThreadedFunctionWrapper"]


from qtpy import QtCore


class QTask(QtCore.QRunnable):
    def __init__(self, function, signal, args, kwargs):
        super().__init__()
        self._function = function
        self._args = args
        self._kwargs = kwargs
        self._signal = signal
        self.setAutoDelete(True)
        self.finished = False

    def run(self):
        self.result = self._function(*self._args, **self._kwargs)
        self.finished = True
        self._signal.emit(self.result)


class QThreadedFunctionWrapper(QtCore.QObject):
    finished = QtCore.Signal(object)

    def __init__(self, function):
        """
        function must be threadsafe
        """
        super().__init__()
        self._function = function
        self._current_task = None

    def __call__(self, *args, **kwargs):
        if self._current_task is None or self._current_task.finished:
            task = QTask(function=self._function, signal=self.finished, args=args, kwargs=kwargs)
            QtCore.QThreadPool.globalInstance().start(task)
            self._current_task = task
        return self._current_task
