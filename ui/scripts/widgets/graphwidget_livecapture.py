# ------------------------------------------------------
# -------------------- mplwidget.py --------------------
# ------------------------------------------------------

### START IMPORTS ###
## PyQt5 imports ##
from PyQt5.QtWidgets import *
from matplotlib import patches
from skimage import io, img_as_float

## Matplotlib imports ##
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.ticker import StrMethodFormatter
### END IMPORTS ###


class GraphWidgetLiveCapture(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.figure = plt.figure()
        self.figure.subplots_adjust(left=-0,
                                    right=1.0,
                                    bottom=-0.00,
                                    top=1.00)
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)

        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.canvas.axes.set_axis_off()
        self.canvas.axes.get_xaxis().set_visible(False)
        self.canvas.axes.get_yaxis().set_visible(False)

        self.setLayout(layout)

    def refresh_UI(self, image):
        self.canvas.axes.clear()
        image_float = img_as_float(image)
        self.canvas.axes.imshow(image_float, interpolation='nearest', aspect='auto')

        # Get the size of the figure in inches
        fig_size_inches = self.figure.get_size_inches()

        # Convert the size from inches to pixels
        fig_size_pixels = fig_size_inches * self.figure.dpi
        print(fig_size_pixels)

        rect = patches.Rectangle((fig_size_pixels[0], fig_size_pixels[1]), 200, 200, linewidth=2, edgecolor='r', facecolor='none')

        # Add the patch to the Axes
        self.canvas.axes.add_patch(rect)

        self.canvas.draw()
