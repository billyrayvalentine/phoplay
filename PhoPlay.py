# PhoPlay.py
# Copyright (c) <2012, 2015>, <Ben Sampson> All rights reserved.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.

"""PhoPlay.py Entry point for the application"""
import signal
import sys
import os
import argparse
from PyQt4.QtGui import QMainWindow, QApplication, QFileDialog, qApp
from PyQt4.QtGui import QFileDialog, QMessageBox
from PyQt4.phonon import Phonon
from ui_MainWindow import Ui_MainWindow


class PhoPlay(QMainWindow, Ui_MainWindow):
    """Main class for the application, inherits class genrated from pyuic"""

    AUDIO_FILE_TYPES = '*.aac *.aiff *.au *.bwf *.flac *.m4a *.m4p *.mp4 \
        *.mp3 *.ogg *.ra *.raw *.rm *.wav *.wma *.wv'

    def __init__(self, fileName=None, disableGui=False, quitOnFinish=False):
        super().__init__()
        super().setupUi(self)

        # Copy config option to object
        self.fileName = fileName
        self.disableGui = disableGui
        self.quitOnFinish = quitOnFinish

        # Setup the GUI
        self.setupGui()

        # Process commandline args
        if self.fileName:
            self.playNew(self.fileName)

    def setupGui(self):
        """Setup the Gui"""
        self.setWindowTitle('PhoPlay')

        # Print availble mime types
        self.availableMimeTypes = \
          Phonon.BackendCapabilities.availableMimeTypes()
        #print(type(self.availableMimeTypes))
        #print("Available Mime Types")
        #print(self.availableMimeTypes)

        # Print availble Audio Output Devices
        #for device in Phonon.BackendCapabilities.availableAudioOutputDevices():
          #print("Available Output Devices")
          #print(device.index(), device.name(), device.description())

        # Connect some slots
        # Menus and buttons
        self.openAction.triggered.connect(self.openFile)
        self.exitAction.triggered.connect(qApp.quit)
        self.infoAction.triggered.connect(self.showInfoDialog)
        self.aboutAction.triggered.connect(self.showAboutDialog)
        self.stopButton.clicked.connect(self.stop)
        self.playButton.clicked.connect(self.play)
        self.pauseButton.clicked.connect(self.pause)

        # Setup phonon player
        self.mediaObject = Phonon.MediaObject(self)
        self.mediaObject.setTickInterval(100)
        self.mediaObject.tick.connect(self.tick)
        self.mediaObject.finished.connect(self.finished)
        self.mediaObject.stateChanged.connect(self.catchStateChanged)
        self.mediaObject.totalTimeChanged.connect(self.totalTime)

        # bind AudioOutput with MediaObject
        self.audioOutput = Phonon.AudioOutput(Phonon.MusicCategory, self)
        Phonon.createPath(self.mediaObject, self.audioOutput)

        # Setup the seek slider
        self.seekSlider.setMediaObject(self.mediaObject)

        # Setup the volume slider
        self.volumeSlider.setAudioOutput(self.audioOutput)

        #self.statusbar.showMessage('hello')

        # Dont show the GUI if called that way AKA cli mode
        if not self.disableGui:
            self.show()

    def openFile(self):
        """Open the file browser"""
        fileName = QFileDialog.getOpenFileName(self, 'Open File', \
            os.getcwd(), 'Audio (' + self.AUDIO_FILE_TYPES + ');; \
            All Files (*.*)')
        if fileName:
            print('Atempting to play' + str(fileName))
            self.playNew(fileName)

    def stop(self):
        """Stop playing"""
        #print('Calling stop')
        self.mediaObject.stop()

    def playNew(self, url):
        """Play a new track"""
        # Set media object to play url
        # Set window title to URL
        # Update track time
        self.mediaObject.setCurrentSource(Phonon.MediaSource(url))
        self.setWindowTitle(os.path.basename(url))
        self.mediaObject.play()
        #print(self.mediaObject.metaData())

    def play(self):
        """Play / Resume Current playback"""
        #print('Calling play')
        self.mediaObject.play()

    def pause(self):
        """Pause current playback"""
        #print('Calling pause')
        self.mediaObject.pause()

    def tick(self, time):
        """Catch the signal from the media object and update the time"""
        # time is received as time in milliseconds, convert to h m s
        h, m, s = self.msToHms(time)
        self.timeLabel.setText('%02d:%02d:%02d' %(h, m, s))

    def finished(self):
        """Catch the signal emitted when the track has finished
        if the app is in cli mode then quit after the track has finished
        """
        #print('Caught finished')
        if self.disableGui or self.quitOnFinish:
            qApp.quit()

    def totalTime(self, newTotalTime):
        """Catch the signal emitted when the total time is know or
        updated and update the totalLabel
        """
        h, m, s = self.msToHms(newTotalTime)
        self.totalLabel.setText('%02d:%02d:%02d' %(h, m, s))

    def catchStateChanged(self, newstate, oldstate):
        """Catch the stateChanged signal to check for errors quit app
        if in CLI mode
        """
        #print('State = ' + str(newstate))
        #print('Meta Info')
        #print(self.mediaObject.metaData())
        if newstate == Phonon.ErrorState:
            print('Error playing back file')
            if self.disableGui:
                qApp.quit()

    def showInfoDialog(self):
        """Show the Mime types dialog"""
        #print('Info Button Clicked')
        QMessageBox.information(self, 'Available Mime Types',
            str(self.availableMimeTypes))

    def showAboutDialog(self):
        """Show the about application dialog"""
        QMessageBox.about(self, 'About PhoPlay', 'PhoPlay\n \
            (c) 2012, 2015 Ben Sampson\n \
            License: BSD (http://www.opensource.org/licenses/bsd-license.php) \n \
            Icons (c) Jojo Mendoza (http://www.deleket.com)')

    def msToHms(self, timeMs):
        """Convert timeMS in milliseconds to h m s format"""
        s = timeMs / 1000
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        return h, m, s


if __name__ == "__main__":

    # Catch ctl-c and kill the app
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Setup the commandline args
    parser = argparse.ArgumentParser(description='Simple Audio Player')
    parser.add_argument('fileName', metavar='file', nargs='?', \
        help='filename to play')
    parser.add_argument('-x, --no-gui', dest='nogui', action='store_true', \
        help='disable the GUI / CLI mode (requires a file)')
    parser.add_argument('-q, --quit-finished', dest='quitOnFinish', \
        action='store_true', \
        help='quit when finished playing (no effect when used with -x)')
    args = parser.parse_args()

    # Check that if CLI mode is enabled and a filename is also provided
    if not args.fileName and args.nogui:
        parser.error('fileName must be specified with -x, --no-gui mode')

    app = QApplication(sys.argv)
    #Need this for dbus on linux
    app.setApplicationName('PhoPlay')
    main = PhoPlay(args.fileName, args.nogui, args.quitOnFinish)
    sys.exit(app.exec_())
