import sys,os,threading
from PyQt5 import QtWidgets
from untitled import *
from PyQt5.QtWidgets import QApplication, QMainWindow,QFileDialog,QMessageBox
from PyQt5  import *
import PyQt5
from subprocess import Popen, PIPE, STDOUT
from pathlib import Path

class Ui_MainWindows(QMainWindow):
    def __init__(self):
        super(Ui_MainWindows, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.anim = None
        self.path = os.path.abspath(".")
        self.effect_shadow_style(self.ui.frame)
        self.bind_event()
        self.setWindowTitle('Python代码加密工具')
        self.setWindowIcon(QIcon('encrypt_logo.ico'))

    def bind_event(self):
        self.ui.pushButton.clicked.connect(self.file_choices)
        self.ui.pushButton_2.clicked.connect(self.encrypt_file)
        self.ui.pushButton_3.clicked.connect(self.open_files)


    def encrypt_file(self):
        enc_path = self.ui.lineEdit.text()
        if not enc_path:
            QMessageBox.warning(self, '警告', '请先选择要加密的Python文件！')
            return
            
        # 检查文件是否存在
        if not os.path.exists(enc_path):
            QMessageBox.critical(self, '错误', f"文件不存在: {enc_path}")
            return
            
        # 检查路径中是否有中文字符
        has_chinese = False
        for ch in enc_path:
            if '\u4e00' <= ch <= '\u9fff':
                has_chinese = True
                break
        
        if has_chinese:
            QMessageBox.warning(self, '警告', '文件路径中包含中文字符，可能导致加密失败。\n建议移动文件到不含中文的路径后再试。')
            
        try:
            # 切换到当前工作目录
            current_dir = os.path.abspath(".")
            os.chdir(current_dir)
            
            app_name = "pyarmor.exe"

            # 使用本地pyarmor.exe
            pyarmor_exe = os.path.join(current_dir, app_name)
            if not os.path.exists(pyarmor_exe):
                QMessageBox.critical(self, '错误', f"未找到pyarmor.exe文件，请确保该文件在程序目录下")
                return
            
            # 获取文件所在目录和文件名
            file_dir = os.path.dirname(enc_path)
            file_name = os.path.basename(enc_path)

            file_path = Path(file_dir) / file_name
            
            # 使用直接方式执行pyarmor命令
            cmd = f'{app_name} gen {file_path}'
            print(f"执行命令: {cmd}")
            
            process = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT, cwd=file_dir if file_dir else None)
            outs, errs = process.communicate()
            
            try:
                content = [z.strip() for z in outs.decode('gb18030', errors='ignore').split("\n") if z]
            except:
                try:
                    content = [z.strip() for z in outs.decode('utf-8', errors='ignore').split("\n") if z]
                except:
                    content = ["无法解析输出"]
            # 打印完整输出以帮助调试
            print("执行命令输出:")
            for line in content:
                print(line)
            
            # 检查是否成功
            if process.returncode == 0 and ("Obfuscated script" in str(outs) or "Target scripts" in str(outs)):
                # 找到正确的dist目录
                if file_dir:
                    # 如果是在文件目录下执行的，dist应该在文件目录下
                    dist_dir = os.path.join(file_dir, "dist")
                else:
                    # 否则在当前目录下
                    dist_dir = os.path.join(current_dir, "dist")
                
                print(f"检查dist目录: {dist_dir}")
                
                if os.path.exists(dist_dir):
                    success_message = f"加密成功！\n加密后的文件在: {dist_dir}"
                    QMessageBox.information(self, '提示', success_message)
                    # 打开dist目录
                    os.startfile(dist_dir)
                else:
                    # 尝试在上级目录查找dist
                    parent_dist = os.path.join(os.path.dirname(current_dir), "dist")
                    if os.path.exists(parent_dist):
                        success_message = f"加密成功！\n加密后的文件在: {parent_dist}"
                        QMessageBox.information(self, '提示', success_message)
                        # 打开dist目录
                        os.startfile(parent_dist)
                    else:
                        success_message = "加密成功！但无法找到dist目录，请手动查找加密后的文件。"
                        QMessageBox.information(self, '提示', success_message)
            else:
                # 显示错误信息
                if content:
                    error_message = "加密失败！\n" + "\n".join(content[-3:])
                else:
                    error_message = "加密失败！无法执行pyarmor命令。"
                QMessageBox.critical(self, '错误', error_message)
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"发生异常: {str(e)}\n{error_details}")
            QMessageBox.critical(self, '错误', f"发生异常: {str(e)}")

    def file_choices(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '请选择要加密的Python文件', '', 'Python文件 (*.py)')
        if file_path:
            print(f"选择的文件路径: {file_path}")
            self.ui.lineEdit.setText(file_path)

    def open_files(self):
        def action():
            # 优先打开dist目录（如果存在）
            dist_dir = os.path.join(self.path, "dist")
            if os.path.exists(dist_dir):
                os.startfile(dist_dir)
            else:
                os.startfile(self.path)
        t = threading.Thread(target=action)
        t.setDaemon(True)
        t.start()

    # 鼠标点击
    def mousePressEvent(self, event: PyQt5.QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.LeftButton and self.isMaximized() == False:
            self.m_flag = True
            self.m_Position = event.globalPosition().toPoint() - self.pos()
            event.accept()
            self.setCursor(PyQt5.QtGui.QCursor(QtCore.Qt.OpenHandCursor))

    # 鼠标点拖之后移动
    def mouseMoveEvent(self, event: PyQt5.QtGui.QMouseEvent) -> None:
        if QtCore.Qt.LeftButton and self.m_flag:
            self.move(event.globalPosition().toPoint() - self.m_Position)
            event.accept()

    # 鼠标释放
    def mouseReleaseEvent(self, event: PyQt5.QtGui.QMouseEvent) -> None:
        self.m_flag = False
        self.setCursor(PyQt5.QtGui.QCursor(QtCore.Qt.ArrowCursor))

    def effect_shadow_style(self, widget):
        effect_shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        effect_shadow.setOffset(0, 8)  # 偏移
        effect_shadow.setBlurRadius(48)  # 阴影半径
        effect_shadow.setColor(QColor(162, 129, 247))  # 阴影颜色
        widget.setGraphicsEffect(effect_shadow)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Ui_MainWindows()
    window.show()
    sys.exit(app.exec())