import sys
import pandas as pd
from PyQt6.QtWidgets import QLabel, QVBoxLayout
from PyQt6.QtCore import QTimer
from datetime import datetime, timedelta
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import (
    QComboBox,
    QSpinBox,
    QPushButton,
    QListWidget,
    QHBoxLayout
)
import json
import os
from PyQt6.QtGui import QFontDatabase, QFont
from matplotlib import font_manager
from PyQt6.QtGui import QPainter, QColor
import random
import matplotlib.patheffects as path_effects


# ===== LOGIN SCREEN CONFIG =====
LOGIN_PANEL_WIDTH = 980
LOGIN_PANEL_HEIGHT = 640
LOGIN_PANEL_PADDING = 40
LOGIN_PANEL_BACKGROUND = "#050505"
LOGIN_PANEL_BORDER_WIDTH = 4
LOGIN_PANEL_BORDER_COLOR = "#00ff88"
LOGIN_PANEL_RADIUS = 8

LOGIN_WIDGET_WIDTH = 750
LOGIN_WIDGET_HEIGHT = 500
LOGIN_WIDGET_BACKGROUND = "transparent"
LOGIN_WIDGET_BORDER_WIDTH = 0
LOGIN_WIDGET_BORDER_COLOR = "transparent"


class MplCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure(figsize=(5, 5))
        self.fig.patch.set_alpha(0)  # прозрачный фон фигуры

        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("none")  # прозрачный фон оси
        self.ax.set_frame_on(False)  # убрать рамку

        super().__init__(self.fig)

        self.setStyleSheet("background: transparent;")


class MatrixBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.columns = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)
        self.scan_y = 0

    def resizeEvent(self, event):
        self.columns = [
            random.randint(0, self.height())
            for _ in range(self.width() // 15)
        ]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 120))

        painter.setPen(QColor(0, 255, 120))

        for i in range(len(self.columns)):
            x = i * 15
            y = self.columns[i]
            char = random.choice("01")
            painter.drawText(x, y, char)
            self.columns[i] += 15

            if self.columns[i] > self.height():
                self.columns[i] = 0

        painter.setPen(QColor(0, 255, 120))
        painter.drawLine(0, self.scan_y, self.width(), self.scan_y)
        self.scan_y += 5
        if self.scan_y > self.height():
            self.scan_y = 0


class LoginWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedSize(LOGIN_WIDGET_WIDTH, LOGIN_WIDGET_HEIGHT)

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {LOGIN_WIDGET_BACKGROUND};
                border: {LOGIN_WIDGET_BORDER_WIDTH}px solid {LOGIN_WIDGET_BORDER_COLOR};
            }}

            QLabel {{
                color: #00ff88;
            }}

            QPushButton {{
                background-color: #001100;
                color: #00ff88;
                border: 3px solid #00ff88;
                padding: 12px;
            }}

            QPushButton:hover {{
                background-color: #00ff88;
                color: black;
            }}

            QPushButton:pressed {{
                background-color: #003300;
            }}
        """)

        layout = QVBoxLayout()
        layout.setSpacing(30)
        self.setLayout(layout)

        self.title = QLabel("SYSTEM AUTHORIZATION")
        self.title.setStyleSheet("font-size: 40px; color: #00ff88;")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title)

        self.user_label = QLabel("ЛОГИН:")
        self.user_label.setStyleSheet("font-size: 26px;")
        layout.addWidget(self.user_label)

        self.user_value = QLabel("")
        self.user_value.setStyleSheet("""
            background:#001100;
            padding:12px;
            font-size: 28px;
        """)
        layout.addWidget(self.user_value)

        self.pass_label = QLabel("ПАРОЛЬ:")
        self.pass_label.setStyleSheet("font-size: 26px;")
        layout.addWidget(self.pass_label)

        self.pass_value = QLabel("")
        self.pass_value.setStyleSheet("""
            background:#001100;
            padding:12px;
            font-size: 28px;
        """)
        layout.addWidget(self.pass_value)

        self.login_button = QPushButton("В О Й Т И")
        self.login_button.setStyleSheet("""
            font-size: 28px;
            padding: 14px;
        """)
        layout.addWidget(self.login_button)

        self.username_text = "Хуесос_Ебаный45"
        self.password_text = "*" * 15

        self.user_index = 0
        self.pass_index = 0

        self.typing_timer = QTimer()
        self.typing_timer.timeout.connect(self.type_text)
        self.typing_timer.start(200)

    def type_text(self):
        if self.user_index < len(self.username_text):
            self.user_value.setText(
                self.user_value.text() + self.username_text[self.user_index]
            )
            self.user_index += 1
            return

        if self.pass_index < len(self.password_text):
            self.pass_value.setText(
                self.pass_value.text() + self.password_text[self.pass_index]
            )
            self.pass_index += 1
            return

        self.typing_timer.stop()


class DebtApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.is_drilled = False

        self.setWindowTitle("ЖИГАЛО-КАЛЬКУЛЯТОР")
        self.setWindowState(Qt.WindowState.WindowMaximized)

        # Серый фон до логина
        self.setStyleSheet("background-color: #2b2b2b;")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.layout = QGridLayout()
        central_widget.setLayout(self.layout)

        self.show_login()

    def show_login(self):
        self.login_panel = QWidget(self.centralWidget())
        self.login_panel.setFixedSize(LOGIN_PANEL_WIDTH, LOGIN_PANEL_HEIGHT)
        self.login_panel.setStyleSheet(f"""
            QWidget {{
                background-color: {LOGIN_PANEL_BACKGROUND};
                border: {LOGIN_PANEL_BORDER_WIDTH}px solid {LOGIN_PANEL_BORDER_COLOR};
                border-radius: {LOGIN_PANEL_RADIUS}px;
            }}
        """)

        panel_layout = QVBoxLayout(self.login_panel)
        panel_layout.setContentsMargins(
            LOGIN_PANEL_PADDING,
            LOGIN_PANEL_PADDING,
            LOGIN_PANEL_PADDING,
            LOGIN_PANEL_PADDING
        )

        self.login_widget = LoginWidget(self.login_panel)
        panel_layout.addWidget(self.login_widget)
        self.center_login()
        self.login_widget.login_button.clicked.connect(self.start_system)

    def center_login(self):
        if hasattr(self, "login_panel") and self.login_panel is not None:
            self.login_panel.move(
                self.width() // 2 - self.login_panel.width() // 2,
                self.height() // 2 - self.login_panel.height() // 2
            )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.center_login()

    def start_system(self):
        self.login_panel.deleteLater()
        self.login_panel = None
        self.login_widget = None
        self.show_loading_animation()

    def show_loading_animation(self):
        # Чистим layout
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.loading_screen = QLabel("")
        self.loading_screen.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_screen.setStyleSheet("""
            font-size: 100px;
            color: #00ff88;
        """)

        self.layout.addWidget(self.loading_screen, 0, 0, 2, 3)

        self.loading_frames = [
            "LOADING/.",
            "LOADING--..",
            "LOADING\\...",
            "LOADING|"
        ]

        self.loading_index = 0
        self.loading_time = 0

        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(self.update_loading_animation)
        self.loading_timer.start(200)  # скорость смены кадров

    def update_loading_animation(self):
        self.loading_screen.setText(self.loading_frames[self.loading_index])
        self.loading_index = (self.loading_index + 1) % len(self.loading_frames)

        self.loading_time += 200

        if self.loading_time >= 3000:  # 3 секунды
            self.loading_timer.stop()
            self.loading_screen.setText("INITIALIZING SYSTEM...")
            QTimer.singleShot(1500, self.init_main_ui)

    def init_main_ui(self):
        if hasattr(self, "loading_screen") and self.loading_screen is not None:
            self.layout.removeWidget(self.loading_screen)
            self.loading_screen.deleteLater()
            self.loading_screen = None

        self.animation_progress = 0

        # ===== ЗАГРУЖАЕМ ШРИФТ HACK =====
        font_id = QFontDatabase.addApplicationFont("Hack-Regular.ttf")
        if font_id != -1:
            family = QFontDatabase.applicationFontFamilies(font_id)[0]
            app_font = QFont(family)
            app_font.setPointSize(11)
            QApplication.instance().setFont(app_font)

        # ===== ТЕРМИНАЛЬНАЯ ТЕМА =====
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QLabel { color: #00ff88; }
            QPushButton {
                background-color: #111111;
                color: #00ff88;
                border: 1px solid #00ff88;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #00ff88;
                color: black;
            }
            QListWidget, QComboBox, QSpinBox {
                background-color: #111111;
                color: #00ff88;
                border: 1px solid #00ff88;
            }
        """)

        central_widget = self.centralWidget()

        # ===== MATRIX BACKGROUND =====
        self.matrix_bg = MatrixBackground(self.centralWidget())
        self.matrix_bg.setGeometry(self.centralWidget().rect())
        self.matrix_bg.raise_()

        # ===== 3x2 СЕТКА =====
        for row in range(2):
            self.layout.setRowStretch(row, 1)

        for col in range(3):
            self.layout.setColumnStretch(col, 1)

        # ===== 1 — ДИАГРАММА =====
        self.chart_container = QWidget()
        self.chart_container.setStyleSheet("background: transparent;")

        chart_layout = QVBoxLayout()
        self.chart_container.setLayout(chart_layout)

        self.canvas = MplCanvas()
        self.canvas.setStyleSheet("background: transparent;")

        chart_layout.addWidget(self.canvas)

        self.layout.addWidget(self.chart_container, 0, 0)

        # ===== 3 — KPI =====
        self.kpi_container = QWidget()
        kpi_layout = QVBoxLayout()
        self.kpi_container.setLayout(kpi_layout)

        self.kpi_total = QLabel()
        self.kpi_total.setStyleSheet("font-size: 50px; font-weight: bold;")
        kpi_layout.addWidget(self.kpi_total)

        self.kpi_count = QLabel()
        kpi_layout.addWidget(self.kpi_count)

        self.kpi_avg = QLabel()
        kpi_layout.addWidget(self.kpi_avg)

        kpi_layout.addSpacing(20)

        self.date_label = QLabel()
        kpi_layout.addWidget(self.date_label)

        self.time_label = QLabel()
        self.time_label.setStyleSheet("font-size: 50px;")
        kpi_layout.addWidget(self.time_label)

        self.week_label = QLabel()
        kpi_layout.addWidget(self.week_label)

        kpi_layout.addStretch()

        self.layout.addWidget(self.kpi_container, 0, 2)

        # ===== 6 — ЗАПАСЫ ЕДЫ =====
        self.food_container = QWidget()
        food_layout = QVBoxLayout()
        self.food_container.setLayout(food_layout)

        title = QLabel("Запасы еды")
        title.setStyleSheet("font-size: 40px; font-weight: bold;")
        food_layout.addWidget(title)

        input_layout = QHBoxLayout()

        self.food_combo = QComboBox()
        self.food_combo.addItems(["Рис", "Макароны", "Мясо", "Молоко", "Яйца"])

        self.food_amount = QSpinBox()
        self.food_amount.setRange(1, 1000)

        self.add_food_button = QPushButton("Добавить")
        self.update_food_button = QPushButton("Обновить")
        self.delete_food_button = QPushButton("Удалить")

        input_layout.addWidget(self.food_combo)
        input_layout.addWidget(self.food_amount)
        input_layout.addWidget(self.add_food_button)
        input_layout.addWidget(self.update_food_button)
        input_layout.addWidget(self.delete_food_button)

        food_layout.addLayout(input_layout)

        self.food_list = QListWidget()
        food_layout.addWidget(self.food_list)

        self.layout.addWidget(self.food_container, 1, 2)

        # ===== ЗАГРУЗКА ДАННЫХ ЕДЫ =====
        self.load_food_data()

        self.add_food_button.clicked.connect(self.add_food)
        self.update_food_button.clicked.connect(self.update_food)
        self.delete_food_button.clicked.connect(self.delete_food)

        # ===== ТАЙМЕР ВРЕМЕНИ =====
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)

        # ===== PULSE KPI =====
        self.pulse_state = True
        self.pulse_timer = QTimer()
        self.pulse_timer.timeout.connect(self.pulse_kpi)
        self.pulse_timer.start(500)

        self.update_datetime()

        # ===== ЗАПУСК ЗАГРУЗКИ =====
        self.show_loading()
        self.matrix_bg.show()

        self.canvas.mpl_connect("button_press_event", self.handle_click)

        chart_layout = QVBoxLayout()
        chart_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

    def update_datetime(self):
        now = datetime.now()

        # Русские названия дней недели
        weekdays = [
            "Понедельник",
            "Вторник",
            "Среда",
            "Четверг",
            "Пятница",
            "Суббота",
            "Воскресенье"
        ]

        # Русские названия месяцев
        months = [
            "января",
            "февраля",
            "марта",
            "апреля",
            "мая",
            "июня",
            "июля",
            "августа",
            "сентября",
            "октября",
            "ноября",
            "декабря"
        ]

        # ===== Дата =====
        day = now.day
        month = months[now.month - 1]
        year = now.year

        self.date_label.setText(f"{day} {month} {year}")

        # ===== Время =====
        self.time_label.setText(now.strftime("%H:%M:%S"))

        # ===== Оставшиеся дни недели =====
        today_weekday = now.weekday()  # 0 = Пн, 6 = Вс

        days = []

        if today_weekday < 6:
            for i in range(1, 7 - today_weekday):
                next_day = now + timedelta(days=i)
                next_weekday = weekdays[next_day.weekday()]
                next_month = months[next_day.month - 1]

                days.append(
                    f"{next_weekday} — {next_day.day} {next_month}"
                )
        else:
            days.append("Неделя завершена")

        self.week_label.setText(
            "Оставшиеся дни недели:\n\n" + "\n".join(days)
        )

    def load_and_plot(self):
        df = pd.read_excel("долги.xlsx")
        df = df.sort_values(by="Amount", ascending=False)

        total = df["Amount"].sum()

        df["Percent"] = df["Amount"] / total * 100

        # --- делим на основные и маленькие ---
        main_df = df[df["Percent"] >= 2].copy()
        small_df = df[df["Percent"] < 2].copy()

        # --- если есть мелкие ---
        if not small_df.empty:
            others_sum = small_df["Amount"].sum()
            others_percent = others_sum / total * 100

            others_row = pd.DataFrame([{
                "Name": "Остальные",
                "Amount": others_sum,
                "Percent": others_percent
            }])

            # добавляем "Остальные" В КОНЕЦ
            main_df = pd.concat([main_df, others_row], ignore_index=True)

        self.main_df = main_df.reset_index(drop=True)
        self.small_df = small_df.reset_index(drop=True)
        self.total_sum = total

        # KPI
        count = len(df)
        avg = int(total / count) if count > 0 else 0

        self.kpi_total.setText(f"Общий долг: {total:,} ₽")
        self.kpi_count.setText(f"Количество людей: {count}")
        self.kpi_avg.setText(f"Средний долг: {avg:,} ₽")

        self.animate_chart()

    def on_hover(self, event):
        if event.inaxes != self.canvas.ax:
            if self.annotation.get_visible():
                self.annotation.set_visible(False)
                self.canvas.draw_idle()
            return

        for i, wedge in enumerate(self.wedges):
            if wedge.contains_point([event.x, event.y]):

                # если мы уже на этом же секторе — не перерисовываем
                if hasattr(self, "current_index") and self.current_index == i:
                    return

                self.current_index = i

                name = self.names.iloc[i]
                amount = self.amounts.iloc[i]

                self.annotation.xy = (event.xdata, event.ydata)
                self.annotation.set_text(f"{name}\n{amount} ₽")
                self.annotation.set_visible(True)

                self.canvas.draw_idle()
                return

        # если вышли из сектора
        if self.annotation.get_visible():
            self.annotation.set_visible(False)
            self.current_index = None
            self.canvas.draw_idle()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.showNormal()

    def add_food(self):
        product = self.food_combo.currentText()
        amount = self.food_amount.value()

        if product in self.food_storage:
            self.food_storage[product] += amount
        else:
            self.food_storage[product] = amount

        self.update_food_list()
        self.save_food_data()

    def update_food_list(self):
        self.food_list.clear()

        for product, amount in self.food_storage.items():
            self.food_list.addItem(f"{product}: {amount}")

    def save_food_data(self):
        with open("food_data.json", "w", encoding="utf-8") as f:
            json.dump(self.food_storage, f, ensure_ascii=False, indent=4)

    def load_food_data(self):
        if os.path.exists("food_data.json"):
            with open("food_data.json", "r", encoding="utf-8") as f:
                self.food_storage = json.load(f)
        else:
            self.food_storage = {}

        self.update_food_list()

    def update_food(self):
        selected_item = self.food_list.currentItem()

        if not selected_item:
            return

        product = selected_item.text().split(":")[0]
        new_amount = self.food_amount.value()

        self.food_storage[product] = new_amount

        self.update_food_list()
        self.save_food_data()

    def delete_food(self):
        selected_item = self.food_list.currentItem()

        if not selected_item:
            return

        product = selected_item.text().split(":")[0]

        if product in self.food_storage:
            del self.food_storage[product]

        self.update_food_list()
        self.save_food_data()

    def pulse_kpi(self):
        if self.pulse_state:
            self.kpi_total.setStyleSheet("font-size: 50px; font-weight: bold; color: #00ff88;")
        else:
            self.kpi_total.setStyleSheet("font-size: 50px; font-weight: bold; color: #00cc66;")
        self.pulse_state = not self.pulse_state

    def animate_chart(self):
        if self.main_df.empty:
            return

        self.canvas.ax.clear()

        names = self.main_df["Name"]
        amounts = self.main_df["Amount"]

        font_path = "Hack-Regular.ttf"
        hack_font = font_manager.FontProperties(fname=font_path)

        colors = [
            "#00ff88",
            "#00cc66",
            "#009944",
            "#006633",
            "#003322",
            "#001a11"
        ]

        def autopct_format(pct):
            return f"{pct:.1f}%"

        wedges, texts, autotexts = self.canvas.ax.pie(
            amounts,
            labels=names,
            autopct=autopct_format,
            startangle=90,
            colors=colors,
            wedgeprops=dict(width=0.75, edgecolor="#0a0a0a")
        )

        # сохраняем wedges для клика
        self.wedges = wedges

        self.canvas.ax.axis("off")

        for text in texts + autotexts:
            text.set_fontproperties(hack_font)
            text.set_color("#00ff88")
            text.set_fontsize(9)

        self.canvas.draw()

    def show_loading(self):
        self.loading_label = QLabel("INITIALIZING SYSTEM...")
        self.loading_label.setStyleSheet("font-size: 30px; color: #00ff88;")
        self.layout.addWidget(self.loading_label, 0, 1)

        QTimer.singleShot(2000, self.finish_loading)

    def finish_loading(self):
        self.loading_label.deleteLater()
        self.load_and_plot()

    def resizeEvent(self, event):
        super().resizeEvent(event)

        if hasattr(self, "login_widget"):
            self.center_login()

        if hasattr(self, "matrix_bg"):
            self.matrix_bg.resize(self.centralWidget().size())

    def handle_click(self, event):
        if event.inaxes != self.canvas.ax:
            return

        for i, wedge in enumerate(self.wedges):
            if wedge.contains_point([event.x, event.y]):
                name = self.main_df.iloc[i]["Name"]

                if name == "Остальные" and not self.small_df.empty:
                    self.drill_down()
                break

    def drill_down(self):
        self.is_drilled = True
        self.canvas.ax.clear()

        names = self.small_df["Name"]
        amounts = self.small_df["Amount"]

        font_path = "Hack-Regular.ttf"
        hack_font = font_manager.FontProperties(fname=font_path)

        def autopct_format(pct):
            absolute = pct / 100 * sum(amounts)
            percent_total = absolute / self.total_sum * 100
            return f"{percent_total:.1f}%"

        wedges, texts, autotexts = self.canvas.ax.pie(
            amounts,
            labels=names,
            autopct=autopct_format,
            startangle=90,
            wedgeprops=dict(width=0.75, edgecolor="#0a0a0a")
        )

        for text in texts + autotexts:
            text.set_fontproperties(hack_font)
            text.set_color("#00ff88")
            text.set_fontsize(9)

        self.canvas.ax.axis("off")
        self.canvas.draw()

        self.show_back_button()

    def show_back_button(self):

        # если уже есть — не создаём вторую
        if hasattr(self, "back_button"):
            return

        self.back_button = QPushButton("←")
        self.back_button.setFixedSize(40, 30)
        self.back_button.setStyleSheet("""
            font-size: 16px;
            padding: 2px;
        """)

        # добавляем в контейнер диаграммы
        self.chart_container.layout().addWidget(self.back_button)

        self.back_button.clicked.connect(self.go_back)

    def go_back(self):
        self.is_drilled = False

        if hasattr(self, "back_button"):
            self.back_button.deleteLater()
            del self.back_button

        self.animate_chart()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DebtApp()
    window.show()
    sys.exit(app.exec())
