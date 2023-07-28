import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QSizeGrip, QMessageBox, QPushButton
from PyQt5.QtCore import QDate, Qt, QUrl, QTimer, QTime, QDate, QDateTime, QThread, pyqtSignal
from PyQt5.QtGui import QDesktopServices, QIntValidator, QRegExpValidator
import time
from time import sleep
from gui import Ui_MainWindow
import sqlite3
import pyautogui
from pyscreeze import PyScreezeException
import pyperclip

class SendMessage(QThread):
    update_signal = pyqtSignal(str, str)
    finished_signal = pyqtSignal()
    wp_signal = pyqtSignal()
    theme_durum = pyqtSignal()

    def __init__(self, giris_saati, anliksaat, tema):
        super().__init__()
        self.giris_saati = giris_saati
        self.anliksaat = anliksaat
        self.running = True
        self.tema = tema
        
    def run(self):
        while True:
            self.xx = QDateTime.currentDateTime()
            self.yy = self.xx.toString('dd.MM.yyyy-hh:mm')
            
            if self.running == True and self.tema == True:
                if self.giris_saati != self.yy:
                    self.update_signal.emit(self.giris_saati, self.anliksaat)
                    time.sleep(0.5)
                else:
                    self.finished_signal.emit()
                    break

            elif self.running == False:
                self.wp_signal.emit()
                break

            else:
                self.theme_durum.emit()
                break

class script(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        global x,y
        self.loadcount = False
        self.webcheck = False
        self.appcheck = False
        self.zamancheck = False
        self.rehbercheck = False
        self.grupcheck = False
        self.gruplist = []
        self.rehberlist = []
        self.durum = ['DURUM:']
        self.message = ''
        self.liste_ = False
        self.ikonun_yeri = None
        self.ikon_check = False
        self.tb = False
        self.iptaldurum = False

        self.setupUi(self)
        
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint) #bar delete
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground,on=True)

        self.head.mouseMoveEvent = self.moveWindow
        QSizeGrip(self.size_frame)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.saat)
        self.timer.start(100)
        self.show()

        ### REGEX ###
        reg_ex_name = QtCore.QRegExp('^[a-z 0-9 A-Z öçşğüÖÇŞİÜĞ]+$')
        reg_ex_number = QtCore.QRegExp('[0-9]*')
        self.yeniKayit_Name_lineEdit.setValidator(QRegExpValidator(reg_ex_name))
        self.yeniKayit_Surname_lineEdit.setValidator(QRegExpValidator(reg_ex_number))
        self.grup_lineEdit.setValidator(QIntValidator())
        self.rehber_lineEdit.setValidator(QIntValidator())
        ### REGEX ###

        ### BUTTON ###
        self.close_Button.clicked.connect(self.closeapp)
        self.minimize_Button.clicked.connect(self.minimized)
        self.github_Label.linkActivated.connect(self.github)
        self.github_Label.setText('<a href="https://github.com/cyberfloki"><img src="{}"></a>'.format('Icons\\github.png'))
        self.site_Label.setText('alpayozturk.net')
        self.send_Button.clicked.connect(self.start_thread)
        self.db_rehber_LoadButton.clicked.connect(self.dbButton_rehber)
        self.db_grup_LoadButton.clicked.connect(self.dbButton_grup)
        self.yeniKayit_Button.clicked.connect(self.newPerson)
        self.rehber_delete.clicked.connect(self.rehberDelete)
        self.grupEkle_Button.clicked.connect(self.grupEkle)
        self.grupSil_Button.clicked.connect(self.grupDelete)
        self.web_Checkbox.stateChanged.connect(self.webcheckbox)
        self.app_Checkbox.stateChanged.connect(self.appcheckbox)
        self.zaman_Checkbox.stateChanged.connect(self.zamancheckbox)
        self.rehber_Checkbox.stateChanged.connect(self.rehbercheckbox)
        self.grup_Checkbox.stateChanged.connect(self.grupcheckbox)
        ### BUTTON ###
        
    ### EVENT ###
    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()

    def moveWindow(self, e):
        if self.isMaximized() == False:
            if e.buttons() == Qt.LeftButton:
                self.move(self.pos() + e.globalPos() - self.clickPosition)
                self.clickPosition = e.globalPos()
                e.accept()

    def closeapp(self):
        sys.exit(0)

    def minimized(self):
        self.showMinimized()

    def github(self, linkStr):
        QDesktopServices.openUrl(QUrl(linkStr))

    def durumLabel(self): #*durumlar
        metin = " ".join(str(durum) for durum in self.durum)
        self.durum_Label.setText(metin)
    ### EVENT ###


    ### DIALOG ###
    def dialog(self, notification_type, notification_message, notification_title):
        self.msgBox = QMessageBox()
        self.msgBox.resize(200, 100)
        self.msgBox.setIcon(notification_type)
        self.msgBox.setWindowIcon(QtGui.QIcon('Icons\\app_icon.png'))
        self.msgBox.setText(notification_message)
        self.msgBox.setWindowTitle(notification_title)
        self.msgBox.exec()
    ### DIALOG ###

    ### ZAMAN ###
    def saat(self):
        current_time = QTime.currentTime()
        display_text = current_time.toString("hh:mm")
        self.saat_Label.setText(display_text)

        current_date = QDate.currentDate()
        displayDate = current_date.toString('dd.MM.yyyy')
        self.tarih_Label.setText(displayDate)

        self.anliksaat = (displayDate+'-'+display_text)

        script.tarih_giris(self)
        script.listeolustur_(self)

        ### TARİH GİRİŞ ###

    def tarih_giris(self):
        self.tarih_saat = self.dateTimeEdit.text()
        self.tarih_saat = self.tarih_saat.split()
        self.giris_tarih = self.tarih_saat[0]
        self.giris_saat = self.tarih_saat[1]
        self.tarih_saat_text = (self.giris_tarih+'-'+self.giris_saat)

    def zaman_fark(self, end_date_str):
        current_date = QDateTime.currentDateTime()
        end_date = QDateTime.fromString(end_date_str, "dd.MM.yyyy-HH:mm")

        if current_date <= end_date:
            time_difference = current_date.secsTo(end_date)
            days, time_difference = divmod(time_difference, 86400)
            hours, time_difference = divmod(time_difference, 3600)
            minutes, seconds = divmod(time_difference, 60)
            result_str = f"{int(days):02} gün, {int(hours):02}:{int(minutes):02}:{int(seconds):02}"
            uyarı = '\nSüre bitene kadar bu pencereye ve Whatsapp penceresine dokunmayın.'
            i_iptal = '\nİşlemi iptal etmek için `İptal Et` butonuna basınız.'
            return result_str + uyarı + i_iptal
        else:
            return "\nGeçerli tarih, bitiş tarihinden daha ileri bir tarih olmalı."
        ### TARİH GİRİŞ ###
    ### ZAMAN ###

    def iptal(self):
        self.iptaldurum = True

    ### THREAD
    def start_thread(self):
        self.dd = False
        if self.zamancheck == False:
            script.Whatsapp(self)
        elif self.webcheck == False and self.appcheck == False:
            script.dialog(self, notification_type=QMessageBox.Warning, notification_title='HATA', notification_message='Uygulama ya da Webden birini seçiniz.')
        elif self.zamancheck == False and self.grupcheck == False and self.rehbercheck == False:
            script.dialog(self, notification_type=QMessageBox.Warning, notification_title='HATA', notification_message='Rehber ya da grup seçilmedi.')
        elif self.zamancheck == True and self.grupcheck == False and self.rehbercheck == False:
            script.dialog(self, notification_type=QMessageBox.Warning, notification_title='HATA', notification_message='Zaman seçtikten sonra Rehber ya da grup seçmelisiniz.')

        elif self.giris_saat != self.anliksaat and self.zamancheck == True:
            script.tema_bulucu(self, dark_icon='Icons\\plus_dark.png', white_icon='Icons\\plus.png', web_icon='Icons\\web.png')
            self.worker_thread = SendMessage(giris_saati=self.tarih_saat_text, anliksaat=self.anliksaat, tema=self.tb)
            self.worker_thread.running = True
            self.worker_thread.update_signal.connect(self.update_label)
            self.worker_thread.wp_signal.connect(self.wp_)
            self.worker_thread.theme_durum.connect(self.theme)
            self.worker_thread.finished_signal.connect(self.thread_finished)
            self.worker_thread.start()
            time.sleep(0.1)
            self.box = QMessageBox()
            self.box.resize(200, 100)
            self.box.setIcon(QMessageBox.Information)
            self.box.setWindowIcon(QtGui.QIcon('Icons\\app_icon.png'))
            self.box.setWindowTitle('BİLGİ')
            self.okButton = QPushButton('Tamam', self.box)
            self.iptalButton = QPushButton('İptal Et')
            self.box.addButton(self.okButton, QMessageBox.YesRole)
            self.box.addButton(self.iptalButton, QMessageBox.YesRole)
            self.iptalButton.clicked.connect(self.iptal)
            self.box.exec()
            script.checkbox_reset(self)

    def update_label(self):
        if self.iptaldurum == True:
            self.iptaldurum = False
            self.tb = False
            self.worker_thread.running = False
        
        else:
            remaining_time = self.zaman_fark(self.tarih_saat_text)
            self.box.setText(f"Mesajın gönderilmesine kalan süre: {remaining_time}.")

    def wp_(self):
        self.tb = False
        self.worker_thread.quit()
        self.worker_thread.wait()

    def theme(self):
        self.box.setText('Whatsapp ekranı bulunamadı. Ekranda üste taşıyın.\nUygulama Whatsapp web koyu tema üzerinde çalışmamaktadır.')
        self.tb = False
        self.worker_thread.quit()
        self.worker_thread.wait()

    def thread_finished(self):
        self.okButton.click()
        script.Whatsapp(self)
        script.checkbox_reset(self)
    ### THREAD

    ### DATABASE ###
    def dbConnection(self):
        self.connect = sqlite3.connect('.\\data.db')
        self.connect.commit()

    def dbClose(self):
        self.connect.commit()
        self.connect.close()

    def db_query_rehber_grup(self, text, query):
        self.rehbergrupliste_Label.setText(text)
        script.dbConnection(self)
        self.table.setRowCount(0)

        query_execute = self.connect.execute(query)

        for row_number, row_data in enumerate(query_execute):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))
        script.dbClose(self)
        self.loadcount = True

    def db_query(self, query_):
        script.dbConnection(self)
        self.connect.execute(query_)
        self.connect.commit()
        self.connect.close()

    def listeolustur(self, databasename):
        script.dbConnection(self)
        query = self.connect.execute(f'SELECT isim,numara FROM {databasename}')
        if databasename == 'rehber':
            for row in query:
                if row[1] not in self.rehberlist:
                    self.rehberlist.append(row[1])

        elif databasename == 'grup':
            for row in query:
                if row[1] not in self.gruplist:
                    self.gruplist.append(row[1])

        script.dbClose(self)

    def dbButton_rehber(self):
        script.db_query_rehber_grup(self, text='REHBER', query='SELECT kayit_no,isim,numara FROM rehber')

    def dbButton_grup(self):
        script.db_query_rehber_grup(self, text='GRUP', query='SELECT kayit_no,isim,numara FROM grup')

    def rehberDelete(self):
        script.removePerson(self, liste='rehber', lineEdit=self.rehber_lineEdit)

    def grupDelete(self):
        script.removePerson(self, liste='grup', lineEdit=self.grup_lineEdit)
        
        ### NEW RECORD ###
    def newPerson(self):
        self.isim = self.yeniKayit_Name_lineEdit.text()
        self.number = self.yeniKayit_Surname_lineEdit.text()
        if len(self.isim) == 0 or len(self.number) == 0:
            self.yeniKayit_Name_lineEdit.clear()
            self.yeniKayit_Surname_lineEdit.clear()
        else:
            script.dbConnection(self)
            self.connect.execute('INSERT INTO rehber(isim,numara) VALUES(?,?)',(self.isim,self.number))
            self.connect.commit()            
            self.connect.close()
            self.yeniKayit_Name_lineEdit.clear()
            self.yeniKayit_Surname_lineEdit.clear()
            if self.loadcount != False:
                script.dbButton_rehber(self)

    def removePerson(self, liste, lineEdit):
        self.removeid = lineEdit.text()

        if len(self.removeid) == 0:
            lineEdit.clear()

        elif self.loadcount != False:
            script.dbConnection(self)
            self.removeid = lineEdit.text()
            script.db_query(self, query_='DELETE FROM {} WHERE kayit_no={}'.format(liste,self.removeid))
            script.dbButton_rehber(self)
            lineEdit.clear()

    def grupEkle(self):
        self.grupID = self.grup_lineEdit.text()
        if len(self.grupID) == 0:
            self.grup_lineEdit.clear()
        elif self.loadcount != False:
            try:
                script.dbConnection(self)
                query = self.connect.execute('SELECT kayit_no,isim,numara FROM rehber WHERE kayit_no={}'.format(self.grupID))
                self.connect.commit()
                for row in query:
                    name = row[1]
                    number = row[2]

                self.connect.execute('INSERT INTO grup(isim,numara) VALUES(?,?)',(name,number))
                script.dbClose(self)
                self.grup_lineEdit.clear()
            except UnboundLocalError:
                self.grup_lineEdit.clear()
                script.dialog(self, notification_type=QMessageBox.Warning, notification_message='Rehberde bu numaraya ait kişi yok.', notification_title='HATA')
    ### DATABASE ###

    ### CHECKBOX ###
    def webcheckbox(self, state):
        if state == Qt.Checked:
            self.durum.append('WEB')
            script.durumLabel(self)
            self.webcheck = True
        else:
            self.durum.remove('WEB')
            script.durumLabel(self)
            self.webcheck = False

    def appcheckbox(self, state):
        if state == Qt.Checked:
            self.durum.append('APP')
            script.durumLabel(self)
            self.appcheck = True
        else:
            self.durum.remove('APP')
            script.durumLabel(self)
            self.appcheck = False

    def zamancheckbox(self, state):
        if state == Qt.Checked:
            self.durum.append('ZAMANLI')
            script.durumLabel(self)
            self.zamancheck = True
        else:
            self.durum.remove('ZAMANLI')
            script.durumLabel(self)
            self.zamancheck = False

    def rehbercheckbox(self, state):
        if state == Qt.Checked:
            self.durum.append('REHBER')
            script.durumLabel(self)
            self.rehbercheck = True
        else:
            self.durum.remove('REHBER')
            script.durumLabel(self)
            self.rehbercheck = False

    def grupcheckbox(self, state):
        if state == Qt.Checked:
            self.durum.append('GRUP')
            script.durumLabel(self)
            self.grupcheck = True
        else:
            self.durum.remove('GRUP')
            script.durumLabel(self)
            self.grupcheck = False
    ### CHECKBOX ###
    
    def listeolustur_(self):
        if self.rehbercheck == True and self.grupcheck == True:
            script.listeolustur(self, databasename='rehber')
            script.listeolustur(self, databasename='grup')

        if self.rehbercheck == True:
            script.listeolustur(self, databasename='rehber')

        if self.grupcheck == True:
            script.listeolustur(self, databasename='grup')

        if self.rehbercheck == False and self.grupcheck == False:
            self.rehberlist.clear()
            self.gruplist.clear()

        if self.rehbercheck == False:
            self.rehberlist.clear()

        if self.gruplist == False:
            self.gruplist.clear()
            
    ### PROGRAM ###    
    def sendMessage(self, listeismi, message):
        checklist = list(set(listeismi))
        for ch in checklist:
            pyautogui.click(self.ikonun_yeri)
            sleep(2)
            pyautogui.write(ch)
            x = self.ikonun_yeri[0]
            y = self.ikonun_yeri[1]
            sleep(0.7)
            pyautogui.moveTo(x, y, duration=.05)
            pyautogui.moveTo(x+30, y+210, duration=.4)
            pyautogui.click()
            sleep(2)
            pyperclip.copy(message)
            sleep(0.7)
            pyautogui.hotkey('ctrl', 'v')
            sleep(2)
            pyautogui.press('enter')
        self.ikonun_yeri = None

    def mesaj_gönderici(self, durum):
        self.message = self.mesaj.toPlainText()
        self.mesaj.clear()
        self.durum_Label.setText(durum)

    def rehber_bosliste_check(self):
        if len(self.rehberlist) == 0:
            self.rehber_liste_ = False
        else:
            self.rehber_liste_ = True

    def grup_bosliste_check(self):
        if len(self.gruplist) == 0:
            self.grup_liste_ = False
        else:
            self.grup_liste_ = True

    

    def checkbox_reset(self):
        self.zaman_Checkbox.setChecked(False)
        self.rehber_Checkbox.setChecked(False)
        self.grup_Checkbox.setChecked(False)
        self.tb = False

    def Whatsapp(self):
        try:
            ### HATA ###
            if self.webcheck == True and self.appcheck == True:
                script.dialog(self, notification_type=QMessageBox.Warning, notification_title='HATA', notification_message='Uygulama ve Web aynı anda seçilemez.')
            elif self.webcheck == False and self.appcheck == False:
                script.dialog(self, notification_type=QMessageBox.Warning, notification_title='HATA', notification_message='Uygulama ya da Webden birini seçiniz.')
            elif self.zamancheck == False and self.grupcheck == False and self.rehbercheck == False:
                script.dialog(self, notification_type=QMessageBox.Warning, notification_title='HATA', notification_message='Rehber ya da grup seçilmedi.')
            elif self.zamancheck == True and self.grupcheck == False and self.rehbercheck == False:
                script.dialog(self, notification_type=QMessageBox.Warning, notification_title='HATA', notification_message='Zaman seçtikten sonra Rehber ya da grup seçmelisiniz.')
            ### HATA ###
            
            elif self.appcheck == True or self.webcheck == True:
                script.tema_bulucu(self, dark_icon='Icons\\plus_dark.png', white_icon='Icons\\plus.png', web_icon='Icons\\web.png')
                if self.tb == False:
                    script.dialog(self, notification_type=QMessageBox.Warning, notification_title='HATA', notification_message='Whatsapp`ı ekranda görünür hale getirin.\nUygulama Whatsapp web koyu tema üzerinde çalışmamaktadır.')
                    self.tb = False
                    script.checkbox_reset(self)

                elif self.rehbercheck == True and self.grupcheck == True:
                    script.rehber_bosliste_check(self)
                    script.grup_bosliste_check(self)
                    if self.grup_liste_ == 0 or self.rehber_liste_ == 0:
                        script.dialog(self, notification_type=QMessageBox.Warning, notification_title='HATA', notification_message='Rehber ya da grup listesi boş.')
                        script.checkbox_reset(self)
                    else:
                        script.mesaj_gönderici(self, durum='Mesajınız gruba ve rehbere gönderildi.')
                        script.sendMessage(self,listeismi=self.rehberlist,message=self.message)
                        sleep(0.2)
                        script.sendMessage(self,listeismi=self.gruplist,message=self.message)
                        script.dialog(self, notification_type=QMessageBox.Information, notification_title='BİLDİRİM', notification_message='Mesajınız rehbere ve gruba gönderilmiştir.')
                        script.checkbox_reset(self)
                        self.rehber_liste_ = False
                        self.grup_liste_ = False
                        self.tb = False

                elif self.rehbercheck == True:
                    script.rehber_bosliste_check(self)
                    if self.rehber_liste_ == False:
                        script.dialog(self, notification_type=QMessageBox.Warning, notification_title='HATA', notification_message='Rehber listesi boş.')
                        script.checkbox_reset(self)
                    elif self.rehber_liste_ == True:
                        script.mesaj_gönderici(self, durum='Mesajınız rehbere gönderildi.')
                        script.sendMessage(self,listeismi=self.rehberlist,message=self.message)
                        script.dialog(self, notification_type=QMessageBox.Information, notification_title='BİLDİRİM', notification_message='Mesajınız rehbere gönderilmiştir.')
                        script.checkbox_reset(self)
                        self.rehber_liste_ = False
                        self.tb = False

                elif self.grupcheck == True:
                    script.grup_bosliste_check(self)
                    if self.grup_liste_ == False:
                        script.dialog(self, notification_type=QMessageBox.Warning, notification_title='HATA', notification_message='Grup listesi boş.')
                        script.checkbox_reset(self)
                    elif self.grup_liste_ == True:
                        script.mesaj_gönderici(self, durum='Mesajınız gruba gönderildi.')
                        script.sendMessage(self,listeismi=self.gruplist,message=self.message)
                        script.dialog(self, notification_type=QMessageBox.Information, notification_title='BİLDİRİM', notification_message='Mesajınız gruba gönderilmiştir.')
                        script.checkbox_reset(self)
                        self.grup_liste_ = False
                        self.tb = False

        except PyScreezeException:
            script.dialog(self, notification_type=QMessageBox.Warning, notification_title='HATA', notification_message='WhatsApp penceresini üste taşıyıp tekrar deneyiniz.\nUygulama Whatsapp web koyu tema üzerinde çalışmamaktadır.')
        
        except Exception as e:
            print(e)
    
    def tema_bulucu(self, dark_icon, white_icon, web_icon):
        result = pyautogui.locateOnScreen(dark_icon, confidence=.6)
        if result is not None:
            self.ikonun_yeri = result
            self.tb = True
        
        result = pyautogui.locateOnScreen(white_icon, confidence=.6)
        if result is not None:
            self.ikonun_yeri = result
            self.tb = True

        result = pyautogui.locateOnScreen(web_icon, confidence=.6)
        if result is not None:
            self.ikonun_yeri = result
            self.tb = True
    ### PROGRAM ###