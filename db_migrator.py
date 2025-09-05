import sys
import re
from pathlib import Path
from PyQt5.QtWidgets import QMessageBox, QTextEdit, QDialog, QVBoxLayout, QPushButton

def show_error_dialog(parent, title, text):
    """Показать окно с текстом ошибки и возможностью копировать"""
    dlg = QDialog(parent)
    dlg.setWindowTitle(title)
    layout = QVBoxLayout(dlg)

    edit = QTextEdit()
    edit.setPlainText(text)
    edit.setReadOnly(True)
    layout.addWidget(edit)

    btn = QPushButton("OK")
    btn.clicked.connect(dlg.accept)
    layout.addWidget(btn)

    dlg.exec_()

def ensure_db_structure(parent, cursor, conn, project_dir):
    """
    Проверяет структуру БД и выполняет миграции.
    :param parent: QWidget (для QMessageBox)
    :param cursor: pyodbc.Cursor
    :param conn: pyodbc.Connection
    :param project_dir: str
    """
    # проверяем наличие params
    cursor.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name = 'params';
    """)
    has_params = cursor.fetchone()[0]

    if not has_params:
        # Структуры нет → спросим пользователя
        reply = QMessageBox.question(
            parent,
            "Инициализация БД",
            "Структура БД не найдена.\nСоздать структуру?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.No:
            sys.exit(1)

        try:
            current_sql = Path(project_dir, "db", "Current.sql").read_text(encoding="utf-8")
            for stmt in current_sql.split(";"):
                if stmt.strip():
                    cursor.execute(stmt)
            conn.commit()
            print("Структура создана из Current.sql")
            return
        except Exception as e:
            show_error_dialog(parent, "Ошибка создания структуры", str(e))
            sys.exit(1)

    # --- читаем версию ---
    try:
        cursor.execute("SELECT param_value FROM params WHERE param_name = 'db_version';")
        row = cursor.fetchone()
        if not row:
            raise ValueError("db_version отсутствует")
        db_version = row[0]
        m = re.match(r"^(\d+)\.(\d+)$", db_version)
        if not m:
            raise ValueError(f"Неверный формат db_version: {db_version}")
        major, minor = map(int, m.groups())
    except Exception as e:
        reply = QMessageBox.question(
            parent,
            "Версия БД",
            f"Ошибка при чтении db_version: {e}\n\n"
            f"Продолжить без обновления?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.No:
            sys.exit(1)
        return

    # --- ищем миграции ---
    updates_dir = Path(project_dir, "update", "db")
    if not updates_dir.exists():
        return

    migrations = sorted(updates_dir.glob("*.sql"))

    for mig in migrations:
        m = re.match(r"^(\d+)\.(\d+)__.*\.sql$", mig.name)
        if not m:
            continue
        maj, minr = map(int, m.groups())

        if (maj > major) or (maj == major and minr > minor):
            print(f"Применяем миграцию {mig.name}")
            try:
                sql = mig.read_text(encoding="utf-8")
                for stmt in sql.split(";"):
                    if stmt.strip():
                        cursor.execute(stmt)
                conn.commit()
                major, minor = maj, minr
                cursor.execute(
                    "UPDATE params SET param_value = ? WHERE param_name = 'db_version';",
                    (f"{major:02d}.{minor:02d}",)
                )
                conn.commit()
            except Exception as e:
                show_error_dialog(parent, f"Ошибка миграции {mig.name}", str(e))
                sys.exit(1)
