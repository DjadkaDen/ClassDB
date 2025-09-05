import os
import sys
import json
from PyQt5.QtWidgets import QMessageBox
from db_migrator import ensure_db_structure
from git_updater import self_update

SCRIPT_PATH = os.path.abspath(__file__)
PROJECT_DIR = os.path.dirname(SCRIPT_PATH)
CONFIG_PATH = os.path.join(PROJECT_DIR, "config.json")

# --- Проверка обновлений ---
try:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    if config.get("auto_update", False):
        repo_url = config.get("repo_url")
        branch = config.get("branch", "main")
        if repo_url:
            self_update(repo_url, branch, PROJECT_DIR)

except Exception as e:
    print(f"Не удалось загрузить config.json для автообновления: {e}")


import pyodbc
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QDialog, QTextEdit, QDoubleSpinBox,
    QVBoxLayout, QHBoxLayout, QListWidget, QLabel, QTableWidget, QHeaderView,
    QTableWidgetItem, QCheckBox, QListWidgetItem, QSplitter,
    QPushButton, QInputDialog, QLineEdit
)

class GoalDialog(QDialog):
    def __init__(self, parent=None, title=""):
        super().__init__(parent)
        self.setWindowTitle("Новая цель")

        self.title_edit = QLineEdit(title)
        self.chk_for_all = QCheckBox("Для всех")

        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Отмена")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Название цели:"))
        layout.addWidget(self.title_edit)
        layout.addWidget(self.chk_for_all)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def getValues(self):
        return self.title_edit.text().strip(), self.chk_for_all.isChecked()
class PlanFactDialog(QDialog):
    def __init__(self, parent=None, details='', cost=0.0):
        super().__init__(parent)
        self.setWindowTitle("Новый")
        self.details_edit = QTextEdit()
        self.details_edit.setPlainText(details)
        self.cost_spin = QDoubleSpinBox()
        self.cost_spin.setRange(-1000000, 1000000)
        self.cost_spin.setDecimals(2)
        self.cost_spin.setValue(cost)

        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Отмена")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Детализация:"))
        layout.addWidget(self.details_edit)
        layout.addWidget(QLabel("Стоимость:"))
        layout.addWidget(self.cost_spin)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def getValues(self):
        return self.details_edit.toPlainText(), float(self.cost_spin.value())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Class DB")
        QTimer.singleShot(0, self.showMaximized)

        # Загружаем конфиг
        with open(os.path.join(os.path.dirname(__file__), "config.json"), "r", encoding="utf-8") as f:
            config = json.load(f)

        conn_str = (
            f"DRIVER={{{config['driver']}}};"
            f"SERVER={config['server']};"
            f"PORT={config['port']};"
            f"DATABASE={config['database']};"
            f"UID={config['user']};"
            f"PWD={config['password']};"
        )

        # Подключение к PostgreSQL
        self.conn = pyodbc.connect(conn_str)
        self.cursor = self.conn.cursor()
        # проверка и миграции
        ensure_db_structure(self, self.cursor, self.conn, os.path.dirname(__file__))

        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        # --- Вкладка Люди ---
        people_tab = QWidget()
        people_layout = QHBoxLayout()
        people_tab.setLayout(people_layout)

        # Левый блок
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)

        # Список людей
        self.people_list = QListWidget()
        self.people_list.currentItemChanged.connect(self.load_person_data)
        left_layout.addWidget(self.people_list, 1)

        # Кнопки для списка людей
        people_btns = QHBoxLayout()
        btn_people_add = QPushButton("Добавить человека")
        btn_people_edit = QPushButton("Редактировать")
        btn_people_del = QPushButton("Удалить")
        people_btns.addWidget(btn_people_add)
        people_btns.addWidget(btn_people_edit)
        people_btns.addWidget(btn_people_del)
        btn_people_add.clicked.connect(self.add_person)
        btn_people_edit.clicked.connect(self.edit_person)
        btn_people_del.clicked.connect(self.delete_person)
        left_layout.addLayout(people_btns)

        # Правый блок
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)

        # Подписки
        self.subscriptions_list = QListWidget()
        right_layout.addWidget(QLabel("Подписки"))
        right_layout.addWidget(self.subscriptions_list, 3)

        # Деньги
        right_layout.addWidget(QLabel("Деньги"))
        self.money_table = QTableWidget()
        self.money_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.money_table.cellDoubleClicked.connect(self.edit_money)
        right_layout.addWidget(self.money_table, 5)

        # Кнопки CRUD для денег
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Добавить")
        btn_add.clicked.connect(self.add_money)
        btn_edit = QPushButton("Редактировать")
        btn_edit.clicked.connect(self.edit_money_btn)
        btn_delete = QPushButton("Удалить")
        btn_delete.clicked.connect(self.delete_money)
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_edit)
        btn_layout.addWidget(btn_delete)
        right_layout.addLayout(btn_layout)

        # Добавляем splitter
        splitter = QSplitter()
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)

        # начальные пропорции (2:5)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 5)

        people_layout.addWidget(splitter)
        tabs.addTab(people_tab, "Люди")

        # Загружаем список людей
        self.load_people()

        # Вкладка "Цели"
        goals_tab = QWidget()
        goals_layout = QHBoxLayout()
        goals_tab.setLayout(goals_layout)

        # --- Новый слой слева ---
        goals_left_widget = QWidget()
        goals_left = QVBoxLayout()
        goals_left_widget.setLayout(goals_left)

        # Список целей
        self.goals_table = QTableWidget()
        self.goals_table.setColumnCount(4)
        self.goals_table.setHorizontalHeaderLabels(["Цель", "Есть", "План", "Факт"])
        self.goals_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        header = self.goals_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)   # колонка "Цель" тянется
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Собрано
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # План
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Факт
        self.goals_table.setEditTriggers(QTableWidget.NoEditTriggers)  # только просмотр
        self.goals_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.goals_table.setSelectionMode(QTableWidget.SingleSelection)
        self.goals_table.cellClicked.connect(self.load_goal_details)
        goals_left.addWidget(self.goals_table, 2)

        # Кнопки управления целями
        goals_btns = QHBoxLayout()
        btn_goals_add = QPushButton("Добавить цель")
        btn_goals_add.clicked.connect(self.add_goal)
        btn_goals_edit = QPushButton("Редактировать цель")
        btn_goals_edit.clicked.connect(self.edit_goal)
        btn_goals_del = QPushButton("Удалить цель")
        btn_goals_del.clicked.connect(self.delete_goal)
        goals_btns.addWidget(btn_goals_add)
        goals_btns.addWidget(btn_goals_edit)
        goals_btns.addWidget(btn_goals_del)
        goals_left.addLayout(goals_btns)

        # Справа: две формы — План и Факт
        goals_right_widget = QWidget()
        right_goals_layout = QVBoxLayout()
        goals_right_widget.setLayout(right_goals_layout)

        # План
        self.plan_label = QLabel("План: 0.00")
        right_goals_layout.addWidget(self.plan_label)
        self.plan_table = QTableWidget()
        self.plan_table.setColumnCount(2)
        self.plan_table.setHorizontalHeaderLabels(["Детализация", "Стоимость"])
        self.plan_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        plan_header = self.plan_table.horizontalHeader()
        plan_header.setSectionResizeMode(0, QHeaderView.Stretch)  # Детализация
        plan_header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Стоимость
        self.plan_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.plan_table.cellDoubleClicked.connect(self.edit_plan)
        right_goals_layout.addWidget(self.plan_table, 3)

        plan_btns = QHBoxLayout()
        btn_plan_add = QPushButton("Добавить план")
        btn_plan_add.clicked.connect(self.add_plan)
        btn_plan_edit = QPushButton("Редактировать план")
        btn_plan_edit.clicked.connect(self.edit_plan_btn)
        btn_plan_del = QPushButton("Удалить план")
        btn_plan_del.clicked.connect(self.delete_plan)
        plan_btns.addWidget(btn_plan_add)
        plan_btns.addWidget(btn_plan_edit)
        plan_btns.addWidget(btn_plan_del)
        right_goals_layout.addLayout(plan_btns)

        # Факт
        self.fact_label = QLabel("Факт: 0.00")
        right_goals_layout.addWidget(self.fact_label)
        self.fact_table = QTableWidget()
        self.fact_table.setColumnCount(2)
        self.fact_table.setHorizontalHeaderLabels(["Детализация", "Стоимость"])
        self.fact_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        fact_header = self.fact_table.horizontalHeader()
        fact_header.setSectionResizeMode(0, QHeaderView.Stretch)  # Детализация
        fact_header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Стоимость
        self.fact_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.fact_table.cellDoubleClicked.connect(self.edit_fact)
        right_goals_layout.addWidget(self.fact_table, 3)

        fact_btns = QHBoxLayout()
        btn_fact_add = QPushButton("Добавить факт")
        btn_fact_add.clicked.connect(self.add_fact)
        btn_fact_edit = QPushButton("Редактировать факт")
        btn_fact_edit.clicked.connect(self.edit_fact_btn)
        btn_fact_del = QPushButton("Удалить факт")
        btn_fact_del.clicked.connect(self.delete_fact)
        fact_btns.addWidget(btn_fact_add)
        fact_btns.addWidget(btn_fact_edit)
        fact_btns.addWidget(btn_fact_del)
        right_goals_layout.addLayout(fact_btns)

        # Добавляем левую и правую части в общий layout
        splitter = QSplitter()
        splitter.addWidget(goals_left_widget)
        splitter.addWidget(goals_right_widget)

        # начальные пропорции (2:5)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 5)

        goals_layout.addWidget(splitter)
        tabs.addTab(goals_tab, "Цели")

        # Вкладка "Отчеты"
        reports_tab = QWidget()
        reports_layout = QVBoxLayout()
        reports_layout.addWidget(QLabel("Здесь будут отчеты"))
        reports_tab.setLayout(reports_layout)
        tabs.addTab(reports_tab, "Отчеты")

        # загружаем цели
        self.load_goals()

    def load_people(self):
        self.people_list.clear()
        self.cursor.execute("SELECT id, full_name FROM people ORDER BY full_name;")
        for row in self.cursor.fetchall():
            item = QListWidgetItem(row[1])
            item.setData(1, row[0])
            self.people_list.addItem(item)

    def load_person_data(self, current, previous):
        if current is None:
            return
        self.person_id = current.data(1)

        # --- Подписки ---
        self.subscriptions_list.clear()
        self.cursor.execute("SELECT id, title FROM goals ORDER BY title;")
        all_goals = self.cursor.fetchall()

        self.cursor.execute("SELECT goal_id FROM subscriptions WHERE person_id = ?;", (self.person_id,))
        subscribed = {row[0] for row in self.cursor.fetchall()}

        for goal_id, title in all_goals:
            checkbox = QCheckBox(title)
            checkbox.setChecked(goal_id in subscribed)
            checkbox.goal_id = goal_id
            checkbox.person_id = self.person_id
            checkbox.stateChanged.connect(self.update_subscription)

            item = QListWidgetItem()
            self.subscriptions_list.addItem(item)
            self.subscriptions_list.setItemWidget(item, checkbox)

        self.load_money()

    def load_money(self):
        self.cursor.execute("""
            SELECT id, amount, date, goal_id
            FROM money
            WHERE person_id = ?
            ORDER BY date DESC;
        """, (self.person_id,))
        rows = self.cursor.fetchall()

        self.money_table.setRowCount(len(rows))
        self.money_table.setColumnCount(4)
        self.money_table.setHorizontalHeaderLabels(["ID", "Сумма", "Дата", "Цель"])

        for i, (id_, amount, date, goal_id) in enumerate(rows):
            self.money_table.setItem(i, 0, QTableWidgetItem(str(id_)))
            self.money_table.setItem(i, 1, QTableWidgetItem(str(amount)))
            self.money_table.setItem(i, 2, QTableWidgetItem(str(date)))
            self.money_table.setItem(i, 3, QTableWidgetItem(str(goal_id)))

    def update_subscription(self, state):
        checkbox = self.sender()
        person_id = checkbox.person_id
        goal_id = checkbox.goal_id

        if state:
            self.cursor.execute(
                "INSERT INTO subscriptions (person_id, goal_id) VALUES (?, ?) "
                "ON CONFLICT DO NOTHING;",
                (person_id, goal_id)
            )
        else:
            self.cursor.execute(
                "DELETE FROM subscriptions WHERE person_id = ? AND goal_id = ?;",
                (person_id, goal_id)
            )
        self.conn.commit()

    def add_money(self):
        if not hasattr(self, "person_id"):
            return
        amount, ok = QInputDialog.getDouble(self, "Новая запись", "Введите сумму:", 0, -1000000, 1000000, 2)
        if not ok:
            return
        goal_id, ok = QInputDialog.getInt(self, "Новая запись", "Введите ID цели:", 1, 1, 999999)
        if not ok:
            return

        self.cursor.execute(
            "INSERT INTO money (person_id, amount, date, goal_id) VALUES (?, ?, now(), ?) RETURNING id;",
            (self.person_id, amount, goal_id)
        )
        self.conn.commit()
        self.load_money()
        self.load_goals()

    def edit_money(self, row, col):
        """Редактирование по двойному клику"""
        self._edit_money(row)
        self.load_goals()

    def edit_money_btn(self):
        """Редактирование по кнопке"""
        row = self.money_table.currentRow()
        if row >= 0:
            self._edit_money(row)

    def _edit_money(self, row):
        id_ = int(self.money_table.item(row, 0).text())
        old_amount = float(self.money_table.item(row, 1).text())

        amount, ok = QInputDialog.getDouble(self, "Редактировать запись", "Новая сумма:", old_amount, -1000000, 1000000, 2)
        if not ok:
            return

        self.cursor.execute("UPDATE money SET amount = ? WHERE id = ?;", (amount, id_))
        self.conn.commit()
        self.load_money()

    def delete_money(self):
        row = self.money_table.currentRow()
        if row < 0:
            return
        id_ = int(self.money_table.item(row, 0).text())

        reply = QMessageBox.question(self, "Удаление", "Удалить запись?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.cursor.execute("DELETE FROM money WHERE id = ?;", (id_,))
            self.conn.commit()
            self.load_money()
            self.load_goals()

    # ----------------- Goals tab methods -----------------
    def load_goals(self):
        self.cursor.execute("""
            SELECT g.id,
                g.title,
                COALESCE(m.amount, 0) AS Собрано,
                COALESCE(p.cost, 0)   AS План,
                COALESCE(f.cost, 0)   AS Факт
            FROM goals g
            LEFT JOIN (select m.goal_id, sum(m.amount) as amount from money m group by m.goal_id) m ON g.id = m.goal_id
            LEFT JOIN (select p.goal_id, sum(p.cost) as cost from plan p group by p.goal_id) p ON g.id = p.goal_id
            LEFT JOIN (select f.goal_id, sum(f.cost) as cost from fact f group by f.goal_id) f ON g.id = f.goal_id
            ORDER BY g.title;
        """)
        rows = self.cursor.fetchall()

        self.goals_table.setRowCount(len(rows))
        for i, (goal_id, title, sob, plan_sum, fact_sum) in enumerate(rows):
            # сохраняем id в скрытой data
            item_title = QTableWidgetItem(title)
            item_title.setData(1, goal_id)
            self.goals_table.setItem(i, 0, item_title)
            self.goals_table.setItem(i, 1, QTableWidgetItem(f"{sob:.2f}"))
            self.goals_table.setItem(i, 2, QTableWidgetItem(f"{plan_sum:.2f}"))
            self.goals_table.setItem(i, 3, QTableWidgetItem(f"{fact_sum:.2f}"))

    def load_goal_details(self, row, col):
        if row < 0:
            self.current_goal_id = None
            self.plan_table.setRowCount(0)
            self.fact_table.setRowCount(0)
            return
        goal_id = self.goals_table.item(row, 0).data(1)
        self.current_goal_id = goal_id
        self.load_plans()
        self.load_facts()

    # Plans
    def load_plans(self):
        if not hasattr(self, "current_goal_id") or self.current_goal_id is None:
            self.plan_table.setRowCount(0)
            self.plan_label.setText("План: 0.00")
            return
        self.cursor.execute("SELECT id, details, cost FROM plan WHERE goal_id = ? ORDER BY id;", (self.current_goal_id,))
        rows = self.cursor.fetchall()
        total = sum([float(r[2]) if r[2] is not None else 0.0 for r in rows])
        self.plan_table.setRowCount(len(rows))
        self.plan_table.setColumnCount(2)
        self.plan_table.setHorizontalHeaderLabels(["Детализация", "Стоимость"])
        for i, (id_, details, cost) in enumerate(rows):
            item_details = QTableWidgetItem(str(details))
            item_details.setData(1, id_)   # сохраняем id
            self.plan_table.setItem(i, 0, item_details)
            self.plan_table.setItem(i, 1, QTableWidgetItem(str(cost)))
        self.plan_label.setText(f"План: {total:.2f}")

    def add_plan(self):
        if not hasattr(self, "current_goal_id") or self.current_goal_id is None:
            return
        dlg = PlanFactDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            details, cost = dlg.getValues()
            self.cursor.execute(
                "INSERT INTO plan (goal_id, details, cost) VALUES (?, ?, ?);",
                (self.current_goal_id, details, cost)
            )
            self.conn.commit()
            self.load_plans()
            self.load_goals()

    def edit_plan(self, row, col):
        self._edit_plan(row)
        self.load_goals()

    def edit_plan_btn(self):
        row = self.plan_table.currentRow()
        if row >= 0:
            self._edit_plan(row)

    def _edit_plan(self, row):
        item = self.plan_table.item(row, 0)
        id_ = item.data(1)
        old_details = self.plan_table.item(row, 0).text()
        old_cost = float(self.plan_table.item(row, 1).text()) if self.plan_table.item(row, 1).text() else 0.0

        dlg = PlanFactDialog(self, details=old_details, cost=old_cost)
        if dlg.exec_() == QDialog.Accepted:
            details, cost = dlg.getValues()
            self.cursor.execute("UPDATE plan SET details = ?, cost = ? WHERE id = ?;", (details, cost, id_))
            self.conn.commit()
            self.load_plans()

    def delete_plan(self):
        row = self.plan_table.currentRow()
        if row < 0:
            return
        item = self.plan_table.item(row, 0)
        id_ = item.data(1)
        reply = QMessageBox.question(self, "Удаление", "Удалить план?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.cursor.execute("DELETE FROM plan WHERE id = ?;", (id_,))
            self.conn.commit()
            self.load_plans()
            self.load_goals()

    # Facts
    def load_facts(self):
        if not hasattr(self, "current_goal_id") or self.current_goal_id is None:
            self.fact_table.setRowCount(0)
            self.fact_label.setText("Факт: 0.00")
            return
        self.cursor.execute("SELECT id, details, cost FROM fact WHERE goal_id = ? ORDER BY id;", (self.current_goal_id,))
        rows = self.cursor.fetchall()
        total = sum([float(r[2]) if r[2] is not None else 0.0 for r in rows])
        self.fact_table.setRowCount(len(rows))
        self.fact_table.setColumnCount(2)
        self.fact_table.setHorizontalHeaderLabels(["Детализация", "Стоимость"])
        for i, (id_, details, cost) in enumerate(rows):
            item_details = QTableWidgetItem(str(details))
            item_details.setData(1, id_)   # сохраняем id
            self.fact_table.setItem(i, 0, item_details)
            self.fact_table.setItem(i, 1, QTableWidgetItem(str(cost)))
        self.fact_label.setText(f"Факт: {total:.2f}")

    def add_fact(self):
        if not hasattr(self, "current_goal_id") or self.current_goal_id is None:
            return
        dlg = PlanFactDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            details, cost = dlg.getValues()
            self.cursor.execute(
                "INSERT INTO fact (goal_id, details, cost) VALUES (?, ?, ?);",
                (self.current_goal_id, details, cost)
            )
            self.conn.commit()
            self.load_facts()
            self.load_goals()

    def edit_fact(self, row, col):
        self._edit_fact(row)
        self.load_goals()

    def edit_fact_btn(self):
        row = self.fact_table.currentRow()
        if row >= 0:
            self._edit_fact(row)

    def _edit_fact(self, row):
        item = self.fact_table.item(row, 0)
        id_ = item.data(1)
        old_details = self.fact_table.item(row, 0).text()
        old_cost = float(self.fact_table.item(row, 1).text()) if self.fact_table.item(row, 1).text() else 0.0

        dlg = PlanFactDialog(self, details=old_details, cost=old_cost)
        if dlg.exec_() == QDialog.Accepted:
            details, cost = dlg.getValues()
            self.cursor.execute("UPDATE fact SET details = ?, cost = ? WHERE id = ?;", (details, cost, id_))
            self.conn.commit()
            self.load_facts()

    def delete_fact(self):
        row = self.fact_table.currentRow()
        if row < 0:
            return
        item = self.fact_table.item(row, 0)
        id_ = item.data(1)
        reply = QMessageBox.question(self, "Удаление", "Удалить факт?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.cursor.execute("DELETE FROM fact WHERE id = ?;", (id_,))
            self.conn.commit()
            self.load_facts()
            self.load_goals()

    # --- Goals CRUD ---
    def add_goal(self):
        dlg = GoalDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            title, for_all = dlg.getValues()
            if not title:
                return

            self.cursor.execute(
                "INSERT INTO goals (title, priority) VALUES (?, ?);",
                (title, 0)
            )
            self.conn.commit()

            # получаем id новой цели
            self.cursor.execute("SELECT id FROM goals WHERE title = ? ORDER BY id DESC LIMIT 1;", (title,))
            goal_id = self.cursor.fetchone()[0]

            # если стоит галка → подписываем всех людей
            if for_all:
                self.cursor.execute("SELECT id FROM people;")
                all_people = [row[0] for row in self.cursor.fetchall()]
                for pid in all_people:
                    self.cursor.execute(
                        "INSERT INTO subscriptions (person_id, goal_id) VALUES (?, ?) ON CONFLICT DO NOTHING;",
                        (pid, goal_id)
                    )
                self.conn.commit()

            self.load_goals()

    def edit_goal(self):
        row = self.goals_table.currentRow()
        if row < 0:
            return
        item = self.goals_table.item(row, 0)
        goal_id = item.data(1)
        old_title = item.text()
        new_title, ok = QInputDialog.getText(self, "Редактировать цель", "Новое название:", text=old_title)
        if not ok or not new_title.strip():
            return
        self.cursor.execute(
            "UPDATE goals SET title = ? WHERE id = ?;",
            (new_title.strip(), goal_id)
        )
        self.conn.commit()
        self.load_goals()

    def delete_goal(self):
        row = self.goals_table.currentRow()
        if row < 0:
            return
        item = self.goals_table.item(row, 0)
        goal_id = item.data(1)
        reply = QMessageBox.question(self, "Удаление", "Удалить цель?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.cursor.execute("DELETE FROM goals WHERE id = ?;", (goal_id,))
            self.conn.commit()
            self.load_goals()

    def add_person(self):
        name, ok = QInputDialog.getText(self, "Новый человек", "Введите ФИО:")
        if not ok or not name.strip():
            return
        self.cursor.execute(
            "INSERT INTO people (full_name) VALUES (?);",
            (name.strip(),)
        )
        self.conn.commit()
        self.load_people()

    def edit_person(self):
        row = self.people_list.currentRow()
        if row < 0:
            return
        item = self.people_list.currentItem()
        person_id = item.data(1)
        old_name = item.text()

        new_name, ok = QInputDialog.getText(self, "Редактировать", "Новое ФИО:", text=old_name)
        if not ok or not new_name.strip():
            return
        self.cursor.execute(
            "UPDATE people SET full_name = ? WHERE id = ?;",
            (new_name.strip(), person_id)
        )
        self.conn.commit()
        self.load_people()

    def delete_person(self):
        row = self.people_list.currentRow()
        if row < 0:
            return
        item = self.people_list.currentItem()
        person_id = item.data(1)

        reply = QMessageBox.question(self, "Удаление", f"Удалить {item.text()}?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.cursor.execute("DELETE FROM people WHERE id = ?;", (person_id,))
            self.conn.commit()
            self.load_people()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
