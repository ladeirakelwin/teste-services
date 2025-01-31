# install_service.py
import sys
import win32serviceutil
import win32service
import win32event
import servicemanager
import threading
import os
from app.wsgi import application
from waitress import create_server


class DjangoService(win32serviceutil.ServiceFramework):
    _svc_name_ = "DjangoService"
    _svc_display_name_ = "Django Service"
    _svc_description_ = "Serviço para rodar a Orquestração"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.server = None
        self.server_thread = None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        if self.server:
            self.server.close()

    def SvcDoRun(self):
        try:
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
            self.server = create_server(
                application,
                host="0.0.0.0",
                port=8000,
                threads=2,
                url_scheme='http'
            )
            self.server_thread = threading.Thread(target=self.server.run)
            self.server_thread.start()
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
            self.server.close()
            self.server_thread.join()
        except Exception as e:
            servicemanager.LogErrorMsg(str(e))
        finally:
            self.ReportServiceStatus(win32service.SERVICE_STOPPED)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(DjangoService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(DjangoService)