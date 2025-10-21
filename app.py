import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineUrlRequestInfo
from PyQt5.QtCore import QUrl, QTimer

class URLInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, blocked_urls):
        super().__init__()
        self.blocked_urls = blocked_urls
    
    def interceptRequest(self, info):
        url = info.requestUrl().toString().lower()
        
        # Блокируем определенные URL
        for blocked_url in self.blocked_urls:
            if blocked_url.lower() in url:
                print(f"🚫 Блокируем: {url}")
                info.block(True)
                return

class SecureWebPage(QWebEnginePage):
    def __init__(self, profile=None):
        super().__init__(profile)
    
    def featurePermissionRequested(self, securityOrigin, feature):
        """Блокируем запросы разрешений"""
        if feature in [
            QWebEnginePage.Geolocation,
            QWebEnginePage.MediaAudioCapture,
            QWebEnginePage.MediaVideoCapture,
            QWebEnginePage.MediaAudioVideoCapture,
            QWebEnginePage.DesktopVideoCapture,
            QWebEnginePage.DesktopAudioVideoCapture,
            QWebEnginePage.Notifications,
            QWebEnginePage.MouseLock
        ]:
            print(f"🚫 Блокируем запрос разрешения: {self.featureToString(feature)}")
            self.setFeaturePermission(securityOrigin, feature, QWebEnginePage.PermissionDeniedByUser)
        else:
            self.setFeaturePermission(securityOrigin, feature, QWebEnginePage.PermissionDeniedByUser)
    
    def featureToString(self, feature):
        """Конвертируем тип разрешения в строку"""
        features = {
            QWebEnginePage.Geolocation: "Geolocation",
            QWebEnginePage.MediaAudioCapture: "Microphone",
            QWebEnginePage.MediaVideoCapture: "Camera",
            QWebEnginePage.MediaAudioVideoCapture: "Microphone + Camera",
            QWebEnginePage.Notifications: "Notifications",
            QWebEnginePage.MouseLock: "Mouse Lock"
        }
        return features.get(feature, f"Unknown ({feature})")

class SVGModifierWebView(QWebEngineView):
    def __init__(self):
        super().__init__()
        
        # Устанавливаем безопасную страницу
        self.setPage(SecureWebPage())
        
        self.loadFinished.connect(self.on_page_loaded)
        
        # Таймер для периодической проверки SVG
        self.modification_timer = QTimer()
        self.modification_timer.timeout.connect(self.modify_svg_icons)
        self.modification_timer.start(1000)
    
    def on_page_loaded(self, ok):
        """Вызывается когда страница загружена"""
        if ok:
            print("🌐 Страница загружена, запускаем модификацию SVG")
            self.modify_svg_icons()
            self.inject_geolocation_blocker()
    
    def modify_svg_icons(self):
        """Изменяет SVG иконки на странице"""
        js_code = """
        (function() {
            try {
                let modifiedCount = 0;
                
                // Меняем цвет SVG иконок
                const blueCircles = document.querySelectorAll('circle[fill="#00ABEE"]');
                blueCircles.forEach(circle => {
                    circle.setAttribute('fill', '#FFA500');
                    modifiedCount++;
                });
                
                if (modifiedCount > 0) {
                    console.log('🎨 Изменено SVG элементов: ' + modifiedCount);
                }
                return modifiedCount;
                
            } catch (error) {
                console.error('Ошибка при модификации SVG:', error);
                return -1;
            }
        })();
        """
        
        self.page().runJavaScript(js_code, self.on_svg_modification_result)
    
    def on_svg_modification_result(self, result):
        """Обработчик результата модификации"""
        if isinstance(result, int) and result > 0:
            print(f"✅ Изменено SVG иконок: {result}")
    
    def inject_geolocation_blocker(self):
        """Внедряем JavaScript для блокировки геолокации на стороне клиента"""
        blocker_js = """
        // Блокировка Geolocation API
        if (navigator.geolocation) {
            const originalGetCurrentPosition = navigator.geolocation.getCurrentPosition;
            const originalWatchPosition = navigator.geolocation.watchPosition;
            
            navigator.geolocation.getCurrentPosition = function(success, error, options) {
                console.log('🚫 Geolocation.getCurrentPosition заблокирован');
                if (error) error({ code: 1, message: 'Geolocation blocked by security policy' });
            };
            
            navigator.geolocation.watchPosition = function(success, error, options) {
                console.log('🚫 Geolocation.watchPosition заблокирован');
                if (error) error({ code: 1, message: 'Geolocation blocked by security policy' });
                return -1;
            };
            
            // Блокируем clearWatch тоже для полноты
            navigator.geolocation.clearWatch = function() {
                console.log('🚫 Geolocation.clearWatch заблокирован');
            };
        }
        
        // Блокируем доступ к координатам через другие API
        Object.defineProperty(navigator, 'geolocation', {
            value: undefined,
            writable: false
        });
        
        console.log('🔒 Геолокация заблокирована на уровне браузера');
        """
        
        self.page().runJavaScript(blocker_js)

class SimpleIFrame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Algoritmika PC Client - Secure")
        self.setGeometry(100, 100, 1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Список блокируемых URL
        blocked_urls = [
            "https://learn.algoritmika.org/colect_info",
            "trackvisitedsite",
            "mindbox",
            "analytics",
            "tracking",
            "collect_info",
            "log-collector.algoritmika.su",
            "sentry.algoritmika.su",
            "mc.yandex.ru",
            "api.mindbox.ru",
            "web-static.mindbox.ru",
            "mc.yandex.com",
            "learn.algoritmika.org/api/v1/projects/track-view",
            "insights-collector.newrelic.com",
            "google-analytics",
            "doubleclick",
            "googlesyndication",
            "beacon",
            "telemetry",
            "geolocation",
            "location",
            "gps",
            "geo"
        ]
        
        # Создаем и настраиваем веб-вью
        self.web_view = SVGModifierWebView()
        
        # Настраиваем перехватчик URL
        profile = QWebEngineProfile.defaultProfile()
        interceptor = URLInterceptor(blocked_urls)
        profile.setUrlRequestInterceptor(interceptor)
        
        # Добавляем JavaScript для блокировки трекеров
        self.web_view.loadFinished.connect(self.inject_tracker_blocker)
        
        # Загружаем URL
        url = "https://learn.algoritmika.org/"
        self.web_view.setUrl(QUrl(url))
        
        layout.addWidget(self.web_view)
    
    def inject_tracker_blocker(self, ok):
        """Внедряем JavaScript для блокировки трекеров на стороне клиента"""
        if ok:
            blocker_js = """
            // Блокировка Mindbox
            if (typeof window.mindbox !== 'undefined') {
                window.mindbox.trackVisitedSite = function() { 
                    console.log('🚫 Mindbox trackVisitedSite заблокирован');
                };
                window.mindbox.track = function() {
                    console.log('🚫 Mindbox track заблокирован');
                };
            }
            
            // Блокировка Яндекс.Метрики
            if (typeof window.ym !== 'undefined') {
                window.ym = function() { 
                    console.log('🚫 Яндекс.Метрика заблокирована');
                };
            }
            
            // Блокировка Google Analytics
            if (typeof window.ga !== 'undefined') {
                window.ga = function() { 
                    console.log('🚫 Google Analytics заблокирован');
                };
            }
            
            console.log('🔒 Блокировщик трекеров активирован');
            """
            
            self.web_view.page().runJavaScript(blocker_js)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Устанавливаем атрибуты для уменьшения предупреждений
    QApplication.setAttribute(0x00000004, True)  # AA_ShareOpenGLContexts
    
    window = SimpleIFrame()
    window.show()
    sys.exit(app.exec_())
