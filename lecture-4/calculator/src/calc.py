import flet as ft
import math  # 科学計算に必要な関数のためにmathモジュールをインポート


class CalcButton(ft.ElevatedButton):
    def __init__(self, text, button_clicked, expand=1):
        super().__init__()
        self.text = text
        self.expand = expand
        self.on_click = button_clicked
        self.data = text


class DigitButton(CalcButton):
    def __init__(self, text, button_clicked, expand=1):
        CalcButton.__init__(self, text, button_clicked, expand)
        self.bgcolor = ft.Colors.WHITE24
        self.color = ft.Colors.WHITE


class ActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.Colors.ORANGE
        self.color = ft.Colors.WHITE


class ExtraActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.Colors.BLUE_GREY_100
        self.color = ft.Colors.BLACK


class ScientificButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.Colors.TEAL_200
        self.color = ft.Colors.BLACK


class CalculatorApp(ft.Container):
    def __init__(self):
        super().__init__()
        self.reset()
        self.scientific_mode = False

        self.result = ft.Text(value="0", color=ft.Colors.WHITE, size=20)
        self.width = 350
        self.bgcolor = ft.Colors.BLACK
        self.border_radius = ft.border_radius.all(20)
        self.padding = 20
        
        # 科学計算ボタン行
        self.scientific_rows = [
            ft.Row(
                controls=[
                    ScientificButton(text="sin", button_clicked=self.button_clicked),
                    ScientificButton(text="cos", button_clicked=self.button_clicked),
                    ScientificButton(text="tan", button_clicked=self.button_clicked),
                ]
            ),
            ft.Row(
                controls=[
                    ScientificButton(text="log", button_clicked=self.button_clicked),
                    ScientificButton(text="ln", button_clicked=self.button_clicked),
                    ScientificButton(text="^", button_clicked=self.button_clicked),
                ]
            ),
            ft.Row(
                controls=[
                    ScientificButton(text="√", button_clicked=self.button_clicked),
                    ScientificButton(text="π", button_clicked=self.button_clicked),
                    ScientificButton(text="e", button_clicked=self.button_clicked),
                ]
            ),
        ]

        # 標準電卓のボタン
        self.standard_rows = [
            ft.Row(controls=[self.result], alignment=ft.MainAxisAlignment.END),
            ft.Row(
                controls=[
                    ExtraActionButton(text="AC", button_clicked=self.button_clicked),
                    ExtraActionButton(text="+/-", button_clicked=self.button_clicked),
                    ExtraActionButton(text="%", button_clicked=self.button_clicked),
                    ActionButton(text="/", button_clicked=self.button_clicked),
                ]
            ),
            ft.Row(
                controls=[
                    DigitButton(text="7", button_clicked=self.button_clicked),
                    DigitButton(text="8", button_clicked=self.button_clicked),
                    DigitButton(text="9", button_clicked=self.button_clicked),
                    ActionButton(text="*", button_clicked=self.button_clicked),
                ]
            ),
            ft.Row(
                controls=[
                    DigitButton(text="4", button_clicked=self.button_clicked),
                    DigitButton(text="5", button_clicked=self.button_clicked),
                    DigitButton(text="6", button_clicked=self.button_clicked),
                    ActionButton(text="-", button_clicked=self.button_clicked),
                ]
            ),
            ft.Row(
                controls=[
                    DigitButton(text="1", button_clicked=self.button_clicked),
                    DigitButton(text="2", button_clicked=self.button_clicked),
                    DigitButton(text="3", button_clicked=self.button_clicked),
                    ActionButton(text="+", button_clicked=self.button_clicked),
                ]
            ),
            ft.Row(
                controls=[
                    DigitButton(text="0", expand=2, button_clicked=self.button_clicked),
                    DigitButton(text=".", button_clicked=self.button_clicked),
                    ActionButton(text="=", button_clicked=self.button_clicked),
                ]
            ),
        ]

        # モード切替ボタン
        self.mode_toggle_button = ft.ElevatedButton(
            text="科学計算モード",
            on_click=self.toggle_mode,
            bgcolor=ft.Colors.BLUE,
            color=ft.Colors.WHITE
        )

        # 初期表示は標準モード
        self.columns = ft.Column(
            controls=[self.mode_toggle_button] + self.standard_rows
        )
        
        self.content = self.columns

    def toggle_mode(self, e):
        self.scientific_mode = not self.scientific_mode
        
        if self.scientific_mode:
            self.mode_toggle_button.text = "標準モード"
            self.columns.controls = [self.mode_toggle_button] + self.scientific_rows + self.standard_rows
        else:
            self.mode_toggle_button.text = "科学計算モード"
            self.columns.controls = [self.mode_toggle_button] + self.standard_rows
            
        self.update()

    def button_clicked(self, e):
        data = e.control.data
        print(f"Button clicked with data = {data, type(data)}")
        if self.result.value == "Error" or data == "AC":
            self.result.value = "0"
            self.reset()

        elif data in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "."):
            if self.result.value == "0" or self.new_operand == True:
                self.result.value = data
                self.new_operand = False
            else:
                self.result.value = str(self.result.value) + str(data)

        elif data in ("+", "-", "*", "/", "^"):
            self.result.value = str(self.calculate(self.operand1, float(str(self.result.value)), self.operator))
            self.operator = data
            if self.result.value == "Error":
                self.operand1 = "0"
            else:
                self.operand1 = float(self.result.value)
            self.new_operand = True

        elif data in ("="):
            self.result.value = str(self.calculate(self.operand1, float(str(self.result.value)), self.operator))
            self.reset()

        elif data in ("%"):
            self.result.value = str(float(str(self.result.value)) / 100)
            self.reset()

        elif data in ("+/-"):
            if float(str(self.result.value)) > 0:
                self.result.value = "-" + str(self.result.value)

            elif float(str(self.result.value)) < 0:
                self.result.value = str(self.format_number(abs(float(str(self.result.value)))))
        
        # 科学計算関数
        elif data == "sin":
            value = float(str(self.result.value))
            self.result.value = str(self.format_number(math.sin(math.radians(value))))
            self.new_operand = True
            
        elif data == "cos":
            value = float(str(self.result.value))
            self.result.value = str(self.format_number(math.cos(math.radians(value))))
            self.new_operand = True
            
        elif data == "tan":
            value = float(str(self.result.value))
            try:
                self.result.value = str(self.format_number(math.tan(math.radians(value))))
            except:
                self.result.value = "Error"
            self.new_operand = True
            
        elif data == "log":
            value = float(str(self.result.value))
            if value <= 0:
                self.result.value = "Error"
            else:
                self.result.value = str(self.format_number(math.log10(value)))
            self.new_operand = True
            
        elif data == "ln":
            value = float(str(self.result.value))
            if value <= 0:
                self.result.value = "Error"
            else:
                self.result.value = str(self.format_number(math.log(value)))
            self.new_operand = True
            
        elif data == "√":
            value = float(str(self.result.value))
            if value < 0:
                self.result.value = "Error"
            else:
                self.result.value = str(self.format_number(math.sqrt(value)))
            self.new_operand = True
            
        elif data == "π":
            self.result.value = str(self.format_number(math.pi))
            self.new_operand = True
            
        elif data == "e":
            self.result.value = str(self.format_number(math.e))
            self.new_operand = True

        self.update()

    def format_number(self, num):
        if num % 1 == 0:
            return int(num)
        else:
            return num

    def calculate(self, operand1, operand2, operator):
        if operator == "+":
            return self.format_number(operand1 + operand2)

        elif operator == "-":
            return self.format_number(operand1 - operand2)

        elif operator == "*":
            return self.format_number(operand1 * operand2)

        elif operator == "/":
            if operand2 == 0:
                return "Error"
            else:
                return self.format_number(operand1 / operand2)
        
        elif operator == "^":
            try:
                return self.format_number(math.pow(operand1, operand2))
            except:
                return "Error"

    def reset(self):
        self.operator = "+"
        self.operand1 = 0
        self.new_operand = True


def main(page: ft.Page):
    page.title = "Scientific Calculator"
    calc = CalculatorApp()
    page.add(calc)


ft.app(main)