import sys
from PyQt5.QtWidgets import QApplication
from script import script

uygulama = QApplication(sys.argv)

script = script()

sys.exit(uygulama.exec_())