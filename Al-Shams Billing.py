# Al-Shams Karakri Billing App - Kivy Version

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.properties import NumericProperty
from kivy.uix.image import Image
from fpdf import FPDF
import os
import datetime

ITEMS = [
    ("Trays", 30), ("Glasses", 5), ("Tables", 50), ("Jugs", 10),
    ("Chairs", 12), ("Plates (Small)", 5), ("Plates (Large)", 5),
    ("Gwari", 7), ("Dastarkhwan", 30),
    ("Kandol (Small)", 5), ("Kandol (Medium)", 5), ("Kandol (Large)", 5)
]

class ItemRow(BoxLayout):
    subtotal = NumericProperty(0.0)

    def __init__(self, item_name, price, update_total_callback, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=40, **kwargs)
        self.update_total_callback = update_total_callback
        self.item_name = item_name
        self.price = price

        self.add_widget(Label(text=item_name, size_hint_x=0.25))
        self.add_widget(Label(text=f"{price:.2f}", size_hint_x=0.2))

        self.qty_input = TextInput(text='', multiline=False, input_filter='int', size_hint_x=0.2)
        self.qty_input.bind(text=self.on_qty_changed)
        self.qty_input.bind(on_text_validate=self.focus_next)
        self.add_widget(self.qty_input)

        self.subtotal_label = Label(text="0.00", size_hint_x=0.35)
        self.add_widget(self.subtotal_label)

    def on_qty_changed(self, instance, value):
        try:
            qty = int(value)
        except:
            qty = 0
        self.subtotal = qty * self.price
        self.subtotal_label.text = f"{self.subtotal:.2f}"
        self.update_total_callback()

    def focus_next(self, instance):
        parent = self.parent
        index = parent.children[::-1].index(self)  # children list is reversed
        if index + 1 < len(parent.children):
            next_row = parent.children[::-1][index + 1]
            next_row.qty_input.focus = True

class AlShamsLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=10, **kwargs)

        self.add_widget(Image(source='logo.png', size_hint_y=None, height=120, allow_stretch=True, keep_ratio=True))

        self.biller_name = TextInput(hint_text="Enter Biller Name", size_hint_y=None, height=40)
        self.add_widget(self.biller_name)

        self.grid_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.grid_layout.bind(minimum_height=self.grid_layout.setter('height'))

        self.rows = []
        for item, price in ITEMS:
            row = ItemRow(item, price, self.update_total)
            self.rows.append(row)
            self.grid_layout.add_widget(row)

        scroll = ScrollView(size_hint=(1, None), size=(Window.width, 400))
        scroll.add_widget(self.grid_layout)
        self.add_widget(scroll)

        self.total_label = Label(text="Total: 0.00", size_hint_y=None, height=30)
        self.add_widget(self.total_label)

        self.days_input = TextInput(hint_text="Days", multiline=False, input_filter='int', size_hint_y=None, height=35)
        self.days_input.bind(text=self.update_grand_total)
        self.add_widget(self.days_input)

        self.grand_total_label = Label(text="Grand Total: Rs. 0.00", size_hint_y=None, height=40)
        self.add_widget(self.grand_total_label)

        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        btn_layout.add_widget(Button(text="Generate PDF", on_press=self.generate_pdf))
        self.add_widget(btn_layout)

        self.output_dir = os.path.dirname(os.path.abspath(__file__))

    def update_total(self):
        total = sum([row.subtotal for row in self.rows])
        self.total_label.text = f"Total: {total:.2f}"
        self.update_grand_total()

    def update_grand_total(self, *args):
        try:
            total = sum([row.subtotal for row in self.rows])
            days = int(self.days_input.text or 0)
            grand_total = total * days
        except:
            grand_total = 0
        self.grand_total_label.text = f"Grand Total: Rs. {grand_total:.2f}"

    def generate_pdf(self, instance):
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "Al-Shams Karakri Billing", ln=True, align="C")
            pdf.set_font("Arial", size=12)
            pdf.cell(0, 10, f"Biller: {self.biller_name.text}", ln=True)
            pdf.cell(0, 10, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d')}", ln=True)
            pdf.ln(5)

            pdf.set_font("Arial", "B", 12)
            for w, title in zip([60, 40, 40, 50], ["Item", "Price", "Qty", "Sub Total"]):
                pdf.cell(w, 10, title, 1)
            pdf.ln()

            total = 0
            for row in self.rows:
                qty = int(row.qty_input.text or 0)
                subtotal = row.subtotal
                total += subtotal
                for w, val in zip([60, 40, 40, 50], [row.item_name, f"{row.price:.2f}", f"{qty}", f"{subtotal:.2f}"]):
                    pdf.cell(w, 10, val, 1)
                pdf.ln()

            days = int(self.days_input.text or 0)
            grand_total = total * days
            pdf.ln(5)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, f"Total: Rs. {total:.2f}", ln=True)
            pdf.cell(0, 10, f"Days: {days}", ln=True)
            pdf.cell(0, 10, f"Grand Total: Rs. {grand_total:.2f}", ln=True)

            filename = f"alshams_bill_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            full_path = os.path.join(self.output_dir, filename)
            pdf.output(full_path)
        except Exception as e:
            print("Error generating PDF:", e)

class AlShamsApp(App):
    def build(self):
        Window.clearcolor = (0.18, 0.18, 0.18, 1)
        return AlShamsLayout()

if __name__ == "__main__":
    AlShamsApp().run()
