from PyQt6.QtCore import QThread, pyqtSignal, QObject

class WorkerSignals(QObject):
    """Signals for thread workers."""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)

class DataLoaderWorker(QThread):
    """Background worker for loading narrator data."""
    
    signals = WorkerSignals()

    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager

    def run(self):
        """Execute loading logic."""
        try:
            narrators = self.db.get_all_narrators()
            self.signals.result.emit(narrators)
            self.signals.finished.emit()
        except Exception as e:
            self.signals.error.emit(str(e))