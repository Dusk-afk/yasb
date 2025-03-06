import os
from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.applications import VALIDATION_SCHEMA
from PyQt6.QtWidgets import QLabel, QHBoxLayout, QWidget
from PyQt6.QtGui import QCursor, QPixmap
from PyQt6.QtCore import Qt
import subprocess
import logging
from core.utils.win32.system_function import function_map
from core.utils.widgets.animation_manager import AnimationManager

class ApplicationsWidget(BaseWidget):
    validation_schema = VALIDATION_SCHEMA

    def __init__(
            self,
            label: str,
            class_name: str,
            app_list:  list[str, dict[str]],
            image_icon_size: int,
            animation: dict[str, str],
            container_padding: dict[str, int],
        ):
        super().__init__(class_name=f"apps-widget {class_name}")
        self._label = label
        self._apps = app_list
        self._padding = container_padding
        self._image_icon_size = image_icon_size
        self._animation = animation
        # Construct container
        self._widget_container_layout: QHBoxLayout = QHBoxLayout()
        self._widget_container_layout.setSpacing(0)
        self._widget_container_layout.setContentsMargins(self._padding['left'],self._padding['top'],self._padding['right'],self._padding['bottom'])
        # Initialize container
        self._widget_container: QWidget = QWidget()
        self._widget_container.setLayout(self._widget_container_layout)
        self._widget_container.setProperty("class", "widget-container")
        # Add the container to the main widget layout
        self.widget_layout.addWidget(self._widget_container)
        self._update_label()

    def _update_label(self):
        if isinstance(self._apps, list):
            for app_data in self._apps:
                if 'icon' in app_data and 'launch' in app_data:
                    label = ClickableLabel(self)
                    label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                    label.setProperty("class", "label")
                    icon = app_data['icon']
                    if os.path.isfile(icon):
                        pixmap = QPixmap(icon).scaled(self._image_icon_size, self._image_icon_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        label.setPixmap(pixmap)
                    else:
                        label.setText(icon)
                    label.data = app_data['launch']
                    self._widget_container_layout.addWidget(label)
        else:
            logging.error(f"Expected _apps to be a list but got {type(self._apps)}")

    def execute_code(self, data):
        try:
            if data in function_map:
                function_map[data]()
            else:    
                try:
                    if not any(param in data for param in ['-new-tab', '-new-window','-private-window']):
                        data = data.split()
                    subprocess.Popen(data, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
                except Exception as e:
                    logging.error(f"Error starting app: {str(e)}")
        except Exception as e:
            logging.error(f"Exception occurred: {str(e)} \"{data}\"")
 
        
class ClickableLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.data = None 

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.data:
            if self.parent_widget._animation['enabled']:
                AnimationManager.animate(self, self.parent_widget._animation['type'], self.parent_widget._animation['duration'])
            self.parent_widget.execute_code(self.data)
 
            