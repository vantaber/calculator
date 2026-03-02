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

        self.setFixedSize(750, 500)

        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
                border: 3px solid #00ff88;
            }

            QLabel {
                color: #00ff88;
            }

            QPushButton {
                background-color: #001100;
                color: #00ff88;
                border: 3px solid #00ff88;
                padding: 12px;
            }

            QPushButton:hover {
                background-color: #00ff88;
                color: black;
            }

            QPushButton:pressed {
                background-color: #003300;
            }
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
        self.login_widget = LoginWidget(self.centralWidget())
        self.center_login()
        self.login_widget.login_button.clicked.connect(self.start_system)

    def center_login(self):
        self.login_widget.move(
            self.width() // 2 - self.login_widget.width() // 2,
            self.height() // 2 - self.login_widget.height() // 2
        )

    def start_system(self):
        self.login_widget.deleteLater()
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

        self.animation_progress = 0

        self.names = df["Name"].reset_index(drop=True)
        self.amounts = df["Amount"].reset_index(drop=True)

        total = self.amounts.sum()
        count = len(self.amounts)
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
        if not hasattr(self, "amounts") or len(self.amounts) == 0:
            return
        self.animation_progress += 0.05

        if self.animation_progress > 1:
            self.animation_progress = 1

        self.canvas.ax.clear()

        self.canvas.ax.set_facecolor("none")
        self.canvas.ax.set_frame_on(False)

        self.canvas.ax.set_position([0, 0, 1, 1])
        self.canvas.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

        font_path = "Hack-Regular.ttf"
        hack_font = font_manager.FontProperties(fname=font_path)

        colors = [
            "#00ff88",
            "#00cc66",
            "#009944",
            "#006633",
            "#003322"
        ]

        animated_values = self.amounts * self.animation_progress

        def autopct_format(pct):
            return f"{pct:.1f}%"

        wedges, texts, autotexts = self.canvas.ax.pie(
            animated_values,
            labels=self.names,
            autopct=autopct_format,
            startangle=90,
            colors=colors,
            wedgeprops=dict(width=0.75, edgecolor="#0a0a0a")
        )

        self.canvas.ax.set_xticks([])
        self.canvas.ax.set_yticks([])
        self.canvas.ax.axis("off")

        for wedge in wedges:
            wedge.set_path_effects([
                path_effects.Stroke(linewidth=6, foreground="#003300"),
                path_effects.Normal()
            ])

        for text in texts + autotexts:
            text.set_fontproperties(hack_font)
            text.set_color("#00ff88")
            text.set_path_effects([
                path_effects.Stroke(linewidth=2, foreground="#003300"),
                path_effects.Normal()
            ])
            text.set_fontsize(9)

        self.canvas.ax.set_title("", color="#00ff88")
        self.canvas.ax.title.set_fontproperties(hack_font)

        self.canvas.ax.set_facecolor("#1e1e1e")
        self.canvas.fig.patch.set_facecolor("#1e1e1e")

        self.canvas.draw()

        if self.animation_progress < 1:
            QTimer.singleShot(30, self.animate_chart)

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DebtApp()
    window.show()
    sys.exit(app.exec())