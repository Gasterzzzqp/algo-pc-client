import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineUrlRequestInfo
from PyQt5.QtCore import QUrl, QObject, pyqtSlot

class URLInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, blocked_urls):
        super().__init__()
        self.blocked_urls = blocked_urls
    
    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        

        for blocked_url in self.blocked_urls:
            if blocked_url in url:
                
                info.block(True)


class SimpleIFrame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("algoritmika pc client")
        self.setGeometry(100, 100, 1000, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        

        blocked_urls = [
            "https://learn.algoritmika.org/colect_info",
            "trackVisitedSite",
            "mindbox",
            "analytics",
            "tracking",
            "collect_info",
            "https://log-collector.algoritmika.su/",
            "https://sentry.algoritmika.su/api/8/envelope/?sentry_key=8fc299642da8bf575c646243c166e768&sentry_version=7&sentry_client=sentry.javascript.browser%2F7.120.1",
            "https://mc.yandex.ru/metrika/tag.js",
            "https://api.mindbox.ru/scripts/v1/tracker.js",
            "https://api.mindbox.ru/v1.1/customer/track-visit?version=1.0.737&transport=beacon",
            "https://web-static.mindbox.ru/js/byendpoint/algoritmika.website.js?_=5870116",
            "https://mc.yandex.com/",
            "https://learn.algoritmika.org/api/v1/projects/track-view/",
            "https://insights-collector.newrelic.com/v1/accounts/"
        ]
        
       
        self.web_view = QWebEngineView()
        
       
        profile = QWebEngineProfile.defaultProfile()
        interceptor = URLInterceptor(blocked_urls)
        profile.setUrlRequestInterceptor(interceptor)
        
        
        url = "https://learn.algoritmika.org/"
        self.web_view.setUrl(QUrl(url))
        
        layout.addWidget(self.web_view)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleIFrame()
    window.show()
    sys.exit(app.exec_())
