import time
import logging

from PIL.ImageQt import QPixmap
from PyQt6.QtCore import Qt
from qasync import asyncSlot
from PIL.ImageQt import ImageQt
from core.utils.win32.media import MediaOperations
from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.media import VALIDATION_SCHEMA
from PyQt6.QtWidgets import QLabel, QGridLayout

from core.widgets.yasb.applications import ClickableLabel


class MediaWidget(BaseWidget):
    validation_schema = VALIDATION_SCHEMA

    def __init__(self, label: str, label_alt: str, update_interval: int, callbacks: dict[str, str],
                 max_field_size: dict[str, int], show_thumbnail: bool, controls_only: bool, controls_left: bool,
                 thumbnail_alpha: int,
                 thumbnail_padding: int,
                 icons: dict[str, str]):
        super().__init__(update_interval, class_name="media-widget")
        self._label_content = label
        self._label_alt_content = label_alt

        self._max_field_size = max_field_size
        self._show_thumbnail = show_thumbnail
        self._thumbnail_alpha = thumbnail_alpha
        self._media_button_icons = icons
        self._controls_only = controls_only
        self._thumbnail_padding = thumbnail_padding

        # Make a grid box to overlay the text and thumbnail
        self.thumbnail_box = QGridLayout()

        if controls_left:
            self._prev_label, self._play_label, self._next_label = self._create_media_buttons()
            if not controls_only:
                self.widget_layout.addLayout(self.thumbnail_box)
        else:
            if not controls_only:
                self.widget_layout.addLayout(self.thumbnail_box)
            self._prev_label, self._play_label, self._next_label = self._create_media_buttons()

        self._label = QLabel()
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label_alt = QLabel()
        self._label_alt.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._thumbnail_label = QLabel()
        self._thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._label.setProperty("class", "label")
        self._label_alt.setProperty("class", "label alt")

        self.thumbnail_box.addWidget(self._thumbnail_label, 0, 0)
        self.thumbnail_box.addWidget(self._label, 0, 0)
        self.thumbnail_box.addWidget(self._label_alt, 0, 0)

        self.register_callback("update_label", self._update_label)

        self.callback_left = callbacks['on_left']
        self.callback_right = callbacks['on_right']
        self.callback_middle = callbacks['on_middle']
        self.callback_timer = "update_label"

        if not self._controls_only:
            self.register_callback("toggle_label", self._toggle_label)
            self._label.show()

        self._label_alt.hide()
        self._show_alt_label = False

        self.start_timer()

        self._last_title = None
        self._last_artist = None

    def start_timer(self):
        if self.timer_interval and self.timer_interval > 0:
            self.timer.timeout.connect(self._timer_callback)
            self.timer.start(self.timer_interval)

    def _toggle_label(self):
        self._show_alt_label = not self._show_alt_label

        if self._show_alt_label:
            self._label.hide()
            self._label_alt.show()
        else:
            self._label.show()
            self._label_alt.hide()
        self._update_label(is_toggle=True)

    @staticmethod
    def _refresh_css(label: QLabel):
        label.style().unpolish(label)
        label.style().polish(label)
        label.update()

    @asyncSlot()
    async def _update_label(self, is_toggle=False):
        active_label = self._label_alt if self._show_alt_label else self._label
        active_label_content = self._label_alt_content if self._show_alt_label else self._label_content

        # Get media info
        try:
            media_info = await MediaOperations.get_media_properties()
        except Exception as e:
            logging.error(f"Error fetching media properties: {e}")
            return  # Exit early if there's an error

        # If no media is playing, set disable class on all buttons
        # Give next/previous buttons a different css class based on whether they are available

        disabled_if = lambda disabled: "disabled" if disabled else ""
        self._prev_label.setProperty("class", f'btn prev {disabled_if(media_info is None or
                                                                      not media_info['prev_available'])}')
        self._play_label.setProperty("class", f'btn play {disabled_if(media_info is None)}')
        self._next_label.setProperty("class", f'btn next {disabled_if(media_info is None or 
                                                                      not media_info['next_available'])}')
        self._refresh_css(self._prev_label)
        self._refresh_css(self._play_label)
        self._refresh_css(self._next_label)

        # If nothing playing, hide thumbnail and empty text, stop here
        if media_info is None:
            # Hide thumbnail and label fields
            self._thumbnail_label.hide()
            active_label.hide()
            active_label.setText('')
            return

        # Change icon based on if song is playing
        self._play_label.setText(self._media_button_icons['pause' if media_info['playing'] else 'play'])

        # If we only have controls, stop update here
        if self._controls_only:
            return

        # If we are playing, make sure the label field is showing
        active_label.show()

        # Shorten fields if necessary with ...
        media_info = {k: self._format_max_field_size(v) if isinstance(v, str) else v for k, v in
                      media_info.items()}

        # Format the label
        format_label_content = active_label_content.format(**media_info)
        active_label.setText(format_label_content)

        # If we don't want the thumbnail, stop here
        if not self._show_thumbnail:
            return

        # Only update the thumbnail if the title/artist changes or if we did a toggle (resize)
        if is_toggle or not (self._last_title == media_info['title'] and self._last_artist == media_info['artist']):
            if media_info['thumbnail'] is not None:
                self._thumbnail_label.show()
                self._last_title = media_info['title']
                self._last_artist = media_info['artist']

                thumbnail = await MediaOperations.get_thumbnail(media_info['thumbnail'])
                thumbnail.putalpha(self._thumbnail_alpha)

                size = active_label.sizeHint().width() + self._thumbnail_padding

                thumbnail = thumbnail.resize((size, size))
                qim = ImageQt(thumbnail)
                pixmap = QPixmap.fromImage(qim)
                self._thumbnail_label.setPixmap(pixmap)

    def _format_max_field_size(self, text: str):
        max_field_size = self._max_field_size['label_alt' if self._show_alt_label else 'label']
        if len(text) > max_field_size:
            return text[:max_field_size - 3] + '...'
        else:
            return text

    def _create_media_button(self, icon, action):
        label = ClickableLabel(self)
        label.setProperty("class", "btn")
        label.setText(icon)
        label.data = action
        self.widget_layout.addWidget(label)
        return label

    def _create_media_buttons(self):
        return self._create_media_button(self._media_button_icons['prev_track'],
                                         MediaOperations.prev), self._create_media_button(
            self._media_button_icons['play'], MediaOperations.play_pause), self._create_media_button(
            self._media_button_icons['next_track'], MediaOperations.next)

    def execute_code(self, func):
        func()
        time.sleep(0.1)
        self._update_label()
