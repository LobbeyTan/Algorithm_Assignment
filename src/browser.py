from cefpython3.cefpython_py39 import PyBrowser
from cefpython3 import cefpython as cef
import threading
import tkinter
import sys


class WebBrowser:
    def __init__(self, browserFrame=tkinter.Frame,
                 browserSetting=dict, url=str, window_title=str, rect=None):

        if rect is None:
            rect = [0, 0, 810, 500]

        self.browser = PyBrowser
        self.webThread = threading.Thread

        self.browserFrame = browserFrame
        self.url = url
        self.window_title = window_title
        self.browserSetting = browserSetting
        self.rect = rect

        self.cefSettings = {
            "multi_threaded_message_loop": True
        }

    def __createBrowser(self, withLoadHandler):
        sys.excepthook = cef.ExceptHook
        window_info = cef.WindowInfo(self.browserFrame.winfo_id())
        window_info.SetAsChild(self.browserFrame.winfo_id(), self.rect)
        self.browser = cef.CreateBrowserSync(window_info, self.browserSetting, self.url, self.window_title)
        if withLoadHandler:
            self.browser.SetClientHandler(LoadHandler())

    def __browserThread(self, withLoadHandler):
        cef.Initialize(settings=self.cefSettings)
        print("CEF Initialized")
        cef.PostTask(cef.TID_UI, self.__createBrowser, *[withLoadHandler])
        print("Browser created")

    def start(self, withLoadHandler=False):
        self.webThread = threading.Thread(target=self.__browserThread, args=(withLoadHandler, ))
        self.webThread.setName("Web Browser Thread Page 1")
        self.webThread.start()

    def getUrl(self):
        return self.browser.GetUrl()

    def loadUrl(self, url):
        self.browser.LoadUrl(url)

    def close(self):
        self.browser.CloseBrowser()
        cef.Shutdown()
        print("Browser closed")


class LoadHandler(object):
    def OnLoadingStateChange(self, browser, is_loading, can_go_back, can_go_forward, *args, **kwargs):
        print("On Loading State Change")

    def OnLoadStart(self, browser, frame, *args, **kwargs):
        print("On Load Start")

    def OnLoadEnd(self, browser, frame, *args, **kwargs):
        print("On Load End")

    def OnLoadError(self, browser, frame, error_code, error_text_out, failed_url, *args, **kwargs):
        print("On Load Error")
