#!/usr/bin/env python

import numpy as np
import scipy.signal as ss
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.exporters
from template_file_viewer import Ui_Form
import os, datetime

os.chdir(os.path.dirname(__file__))

num_points = 0

UNIX_EPOCH = datetime.datetime(1970, 1, 1, 0, 0)

def now_timestamp(epoch=UNIX_EPOCH):
	return(int((datetime.datetime.now() - epoch).total_seconds()*1e6))

class QtPlotter:
	def __init__(self):
		self.app = QtGui.QApplication([])
		self.win = QtGui.QWidget()
		self.ui = Ui_Form()
		self.ui.setupUi(self.win)
		self.win.setWindowTitle('static file viewer')
		self.win.show()
		self.ui_plot = self.ui.plot
		self.plt = self.ui_plot.plot()
		# self.ui_plot.setRange(xRange=[-100, 100], yRange=[0, 2100])
		self.ui_plot.showGrid(x=True, y=True)
		self.ui.loadDataBtn.clicked.connect(self.load_data)
		self.ui.exportImgBtn.clicked.connect(self.export_image)
		self.ui.windowLenSpin.valueChanged.connect(self.win_len_change)
		self.ui.winTypeComboBox.currentIndexChanged.connect(self.win_len_change)
		self.point_num = 0
		self.max_num_points = 50000
		self.data_x = []
		self.raw_data = np.zeros(self.max_num_points)
		self.sum_data = np.zeros((self.max_num_points, 16))
		# self.ui_plot.setAspectLocked(True)

	def load_data(self):
		filename = QtGui.QFileDialog.getOpenFileName(self.win, 'Open File', os.path.dirname(os.path.abspath(__file__)))
		data = np.load(str(filename))
		self.raw_data = data['count']
		self.data_x = data['time']
		start_time = datetime.datetime.utcfromtimestamp(float(data['time'][0])/1e6)
		end_time = datetime.datetime.utcfromtimestamp(float(data['time'][-1])/1e6)
		self.plt.setData(self.data_x, self.raw_data, pen='g')
		time_info = 'start time '+start_time.strftime("%d.%m.%y %H:%M:%S")+'; end time '+end_time.strftime("%d.%m.%y %H:%M:%S")
		self.title = time_info+'; threshold value = '+str(data['threshold'])+'mV'
		self.ui_plot.setTitle(self.title, color='w', size='15pt')
		self.ui.windowLenSpin.setValue(1)

	def export_image(self):
		self.plt.setData(self.data_x, self.raw_data, pen=(0, 0, 0))
		self.ui_plot.setTitle(self.title, color=(0, 0, 0), size='15pt')
		exporter = pg.exporters.ImageExporter(self.ui_plot.plotItem)
		exporter.parameters()['background'] = 'w'
		self.app.processEvents()
		filename = QtGui.QFileDialog.getSaveFileName(self.win, 'Export image', os.getenv("HOME"))
		exporter.export(str(filename)+'.png')
		self.ui_plot.setTitle(self.title, color='w', size='15pt')
		self.plt.setData(self.data_x, self.raw_data, pen='g')

	def win_len_change(self):
		if str(self.ui.winTypeComboBox.currentText()) == 'rectangular':
			window = ss.boxcar(self.ui.windowLenSpin.value())
		elif str(self.ui.winTypeComboBox.currentText()) == 'tukey':
			window = ss.tukey(self.ui.windowLenSpin.value())
		elif str(self.ui.winTypeComboBox.currentText()) == 'hann':
			window = ss.hann(self.ui.windowLenSpin.value())
		data_conv = ss.convolve(self.raw_data, window, mode='same')
		self.plt.setData(self.data_x, data_conv, pen='g')

plotter = QtPlotter()


if __name__ == '__main__':
	import sys
	if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
		QtGui.QApplication.instance().exec_()
