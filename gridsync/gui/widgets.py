# -*- coding: utf-8 -*-

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QComboBox, QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QMessageBox, QPlainTextEdit, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

from gridsync import resource
from gridsync.config import Config
from gridsync.tahoe import is_valid_furl


class GridComboBox(QWidget):
    def __init__(self):
        super(self.__class__, self).__init__()

        #self.label = QLabel('Storage provider:')
        #self.label.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, 0))

        self.combo_box = QComboBox(self)

        hbox = QHBoxLayout(self)
        hbox.addItem(QSpacerItem(100, 0, QSizePolicy.Preferred, 0))
        #hbox.addWidget(self.label)
        hbox.addWidget(self.combo_box)
        hbox.addItem(QSpacerItem(100, 0, QSizePolicy.Preferred, 0))


class GridDescription(QWidget):
    def __init__(self):
        super(self.__class__, self).__init__()

        self.image = QLabel()

        self.description = QLabel('', self)
        self.description.setWordWrap(True)
        self.description.setOpenExternalLinks(True)

        form = QFormLayout()
        form.setWidget(0, QFormLayout.LabelRole, self.image)
        form.setWidget(0, QFormLayout.FieldRole, self.description)

        hbox = QHBoxLayout(self)
        hbox.addItem(QSpacerItem(30, 0, QSizePolicy.Preferred, 0))
        hbox.addLayout(form)
        hbox.addItem(QSpacerItem(30, 0, QSizePolicy.Preferred, 0))


class GridForm(QWidget):
    def __init__(self):
        super(self.__class__, self).__init__()

        self.name_label = QLabel("Name (optional):")

        self.name_line_edit = QLineEdit()

        self.introducer_label = QLabel("Introducer fURL:")

        self.introducer_text_edit = QPlainTextEdit()
        self.introducer_text_edit.setMaximumHeight(70)
        self.introducer_text_edit.setTabChangesFocus(True)

        self.description_label = QLabel("Description (optional):")

        self.description_text_edit = QPlainTextEdit()
        self.description_text_edit.setMaximumHeight(70)
        self.description_text_edit.setTabChangesFocus(True)

        self.push_button = QPushButton("Save")

        form = QFormLayout()
        form.setWidget(0, QFormLayout.LabelRole, self.name_label)
        form.setWidget(0, QFormLayout.FieldRole, self.name_line_edit)
        form.setWidget(1, QFormLayout.LabelRole, self.introducer_label)
        form.setWidget(1, QFormLayout.FieldRole, self.introducer_text_edit)
        #form.setWidget(2, QFormLayout.LabelRole, self.description_label)
        #form.setWidget(2, QFormLayout.FieldRole, self.description_text_edit)
        form.setWidget(3, QFormLayout.FieldRole, self.push_button)

        hbox = QHBoxLayout(self)
        #hbox.addItem(QSpacerItem(100, 0, QSizePolicy.Preferred, 0))
        hbox.addLayout(form)
        #hbox.addItem(QSpacerItem(100, 0, QSizePolicy.Preferred, 0))


class GridSelector(QWidget):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.resize(800, 500)
        self.introducer_furl = None
        self.storage_providers = None

        self.grid_combo_box = GridComboBox()
        self.grid_combo_box.combo_box.activated[str].connect(self.on_selected)

        self.grid_description = GridDescription()
        self.grid_description.hide()

        self.grid_form = GridForm()
        self.grid_form.push_button.clicked.connect(self.on_save)
        self.grid_form.hide()

        gbox = QGroupBox(self)
        gbox.setTitle("Select a storage grid:")
        gbox_layout = QVBoxLayout(gbox)
        gbox_layout.addWidget(self.grid_combo_box)
        gbox_layout.addWidget(self.grid_description)
        gbox_layout.addWidget(self.grid_form)
        #gbox_layout.addItem(QSpacerItem(0, 0, 0, QSizePolicy.Expanding))

        vbox = QVBoxLayout(self)
        #vbox.addItem(QSpacerItem(0, 60, 0, QSizePolicy.Minimum))
        #vbox.addWidget(self.grid_selector)
        #vbox.addWidget(self.grid_description)
        #vbox.addWidget(self.new_grid_form)
        #vbox.addItem(QSpacerItem(0, 0, 0, QSizePolicy.Expanding))
        vbox.addWidget(gbox)

        self.combo_box = self.grid_combo_box.combo_box
        self.image = self.grid_description.image
        self.description = self.grid_description.description

        self.populate_combo_box()

    def populate_combo_box(self):
        self.storage_providers = Config(
            resource('storage_providers.txt')).load()
        self.combo_box.clear()
        self.combo_box.addItem(" ")
        for name in sorted(self.storage_providers.keys(), reverse=True):
            self.combo_box.addItem(name)
        self.combo_box.insertSeparator(
            self.combo_box.count())
        self.combo_box.addItem("Add new...")

    def on_selected(self, name):
        if self.combo_box.itemText(0) == " ":
            self.combo_box.removeItem(0)
        if name == " ":
            return
        elif name == "Add new...":
            self.grid_description.hide()
            self.grid_form.show()
        else:
            provider = self.storage_providers[name]
            self.introducer_furl = provider['introducer']
            description = provider['description']
            try:
                description += '<p>Homepage: <a href="{}">{}</a>'.format(
                    provider['homepage'], provider['homepage'])
            except KeyError:
                pass
            self.description.setText(description)
            try:
                pixmap = QPixmap(resource(provider['icon'])).scaled(64, 64)
                self.image.setPixmap(pixmap)
                self.image.show()
            except KeyError:
                self.image.hide()
            self.grid_form.hide()
            self.grid_description.show()

    def on_save(self):
        introducer_furl = self.grid_form.introducer_text_edit.toPlainText()
        introducer_furl = introducer_furl.lower().strip().strip('"').strip("'")
        #name = self.grid_form.name_line_edit.text()
        if not introducer_furl:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Gridsync")
            msg.setText("Please enter an Introducer fURL.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        elif is_valid_furl(introducer_furl):
            self.introducer_furl = introducer_furl
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Gridsync")
            msg.setText("Please enter a valid Introducer fURL.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()