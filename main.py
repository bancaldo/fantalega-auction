import os
import wx

# Django specific settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

import sys
import os
import platform

# add the project path into the sys.path
working_dir = os.getcwd()
sys.path.append(working_dir)

# add the virtualenv site-packages path to the sys.path
VENV_PATH = '/venv/Lib/site-packages' if platform.system() == 'Linux' else\
             r'\venv\Lib\site-packages'
sys.path.append(os.getcwd() + VENV_PATH)

# noinspection PyUnresolvedReferences
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# noinspection PyPep8
from auction.controller import Controller


class App(wx.App):
    # noinspection PyPep8Naming,PyMethodMayBeStatic
    def OnInit(self):
        from settings import DATABASES
        db = DATABASES.get('default').get('NAME')
        if not db in os.listdir(os.getcwd()):
            from django.core.management import call_command
            print("INFO: db 'auction.db' not found")
            print("INFO: invoking django 'makemigrations' command...")
            call_command("makemigrations", interactive=False)
            print("INFO: invoking django 'migrate' command...")
            call_command("migrate", interactive=False)
        Controller()
        return True


if __name__ == '__main__':
    app = App(False)
    app.MainLoop()
