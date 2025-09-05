import os
import sys
import subprocess
import shutil
import glob
from PyQt5.QtWidgets import QMessageBox

def self_update(repo_url, branch="main"):
    update_dir = os.path.join(PROJECT_DIR, "update")

    def try_update():
        # если update/ нет → клонируем
        if not os.path.exists(update_dir):
            subprocess.check_call(["git", "clone", "-b", branch, repo_url, update_dir])

        # проверяем локальный и удалённый коммиты
        local = subprocess.check_output(
            ["git", "-C", update_dir, "rev-parse", "HEAD"],
            text=True
        ).strip()

        subprocess.check_call(["git", "-C", update_dir, "fetch", "origin", branch])

        remote = subprocess.check_output(
            ["git", "-C", update_dir, "rev-parse", f"origin/{branch}"],
            text=True
        ).strip()

        if local == remote:
            print("Обновлений нет.")
            return False  # обновлений не было

        print(f"Найдены обновления в ветке {branch}. Обновляем update/")
        subprocess.check_call(["git", "-C", update_dir, "pull", "origin", branch])

        # копируем только .py файлы
        for pyfile in glob.glob(os.path.join(update_dir, "*.py")):
            shutil.copy(pyfile, PROJECT_DIR)

        print("Файлы обновлены. Перезапуск...")
        os.execv(sys.executable, [sys.executable] + sys.argv)

    # --- первая попытка ---
    try:
        return try_update()
    except Exception as e1:
        print(f"Ошибка автообновления (первая попытка): {e1}")
        if os.path.exists(update_dir):
            shutil.rmtree(update_dir)

        # --- вторая попытка ---
        try:
            return try_update()
        except Exception as e2:
            print(f"Ошибка автообновления (вторая попытка): {e2}")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Обновление")
            msg.setText("Не удалось обновить.\n\n" + str(e2) + "\n\nПродолжить?")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            if msg.exec_() == QMessageBox.No:
                sys.exit(1)  # выходим
            return False