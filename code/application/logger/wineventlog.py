import win32api
import win32con
import win23evtlog
import win32evtlogutil
import win32security

class WinEventLog:
    def __init__(self):
        self.ph = win32api.GetCurrentProcess()
        self.th = win32security.OpenProcessToken(self.ph, win32con.TOKEN_READ)
        self.sid = win32security.GetTokenInformation(self.th, win32security.TokenUse)[0]
        self.app_name = "win-hourse"
        self.data = "Application\0Data".encode("ascii")
        
    def info(self, event_id, message):
        self.write_event_log(event_id, win32evtlog.EVENTLOG_WARNING_TYPE, message)
        
    def warning(self, event_id, message):
        self.write_event_log(event_id, win32evtlog.EVENTLOG_WARNING_TYPE, message)
    
    def error(self, event_id, message):
        self.write_event_log(event_id, win32evtlog.EVENTLOG_ERROR_TYPE, message)
        
    def write_event_log(self, event_id, level, message):
        win32evtlogutil.ReportEvent(
            self.app_name,
            int(event_id),
            event_type=level,
            strings=[message],
            data=self.data,
            sid=self.sid
        )