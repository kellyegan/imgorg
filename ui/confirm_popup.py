from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty

Builder.load_file("ui/confirm_popup.kv")

class ConfirmPopup(Popup):
    title_text = StringProperty("Confirm")
    message = StringProperty("Are you sure?")
    on_confirm = ObjectProperty(None)
    on_cancel = ObjectProperty(None)

    def confirm(self):
        if self.on_confirm:
            self.on_confirm()
        self.dismiss()

    def cancel(self):
        if self.on_cancel:
            self.on_cancel()
        self.dismiss()
