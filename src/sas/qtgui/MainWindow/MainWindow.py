# UNLESS EXEPTIONALLY REQUIRED TRY TO AVOID IMPORTING ANY MODULES HERE
# ESPECIALLY ANYTHING IN SAS, SASMODELS NAMESPACE
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMdiArea
from PyQt5.QtWidgets import QSplashScreen
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import os
import sys
# Local UI
from sas.qtgui.UI import main_resources_rc
from .UI.MainWindowUI import Ui_MainWindow

class MainSasViewWindow(QMainWindow, Ui_MainWindow):
    # Main window of the application
    def __init__(self, parent=None):
        super(MainSasViewWindow, self).__init__(parent)
        self.setupUi(self)

        # define workspace for dialogs.
        self.workspace = QMdiArea(self)
        self.setCentralWidget(self.workspace)

        # Temporary solution for problem with menubar on Mac
        if sys.platform == "darwin":  # Mac
            self.menubar.setNativeMenuBar(False)

        # Create the gui manager
        from .GuiManager import GuiManager
        try:
            self.guiManager = GuiManager(self)
        except Exception as ex:
            import logging
            logging.error("Application failed with: "+str(ex))

    def closeEvent(self, event):
        if self.guiManager.quitApplication():
            event.accept()
        else:
            event.ignore()

def SplashScreen():
    """
    Displays splash screen as soon as humanely possible.
    The screen will disappear as soon as the event loop starts.
    """
    pixmap_path = "images/SVwelcome_mini.png"
    if os.path.splitext(sys.argv[0])[1].lower() == ".py":
        pixmap_path = "src/sas/qtgui/images/SVwelcome_mini.png"
    pixmap = QPixmap(pixmap_path)
    splashScreen = QSplashScreen(pixmap)
    return splashScreen

def run_sasview():
    app = QApplication([])

    # Main must have reference to the splash screen, so making it explicit
    splash = SplashScreen()
    splash.show()
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    # fix for pyinstaller packages app to avoid ReactorAlreadyInstalledError
    import sys
    if 'twisted.internet.reactor' in sys.modules:
        del sys.modules['twisted.internet.reactor']

    # DO NOT move the following import to the top!
    # (unless you know what you're doing)
    import qt5reactor
    # Using the Qt5 reactor wrapper from https://github.com/ghtdak/qtreactor
    qt5reactor.install()

    # DO NOT move the following import to the top!
    from twisted.internet import reactor

    # Show the main SV window
    mainwindow = MainSasViewWindow()
    mainwindow.showMaximized()

    # no more splash screen
    splash.finish(mainwindow)

    # Time for the welcome window
    mainwindow.guiManager.showWelcomeMessage()

    # No need to .exec_ - the reactor takes care of it.
    reactor.run()

if __name__ == "__main__":
    run_sasview()
