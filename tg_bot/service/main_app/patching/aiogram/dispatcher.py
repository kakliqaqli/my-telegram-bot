from aiogram import Dispatcher


class PatchedDispatcher(Dispatcher):
    def __int__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def app(self):
        return self.app

    @app.setter
    def app(self, value):
        self.app = value
