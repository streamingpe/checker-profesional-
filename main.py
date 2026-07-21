import sys
import json
import threading
import time
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel, QFileDialog,
    QTextEdit, QProgressBar, QTabWidget, QMessageBox, QSpinBox, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QColor, QFont, QIcon
from checker_logic import CheckerWorker

class VTRCheckerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VTR PRIME VIDEO CHECKER v1.0.0")
        self.setGeometry(100, 100, 1400, 800)
        
        self.combos = []
        self.proxies = []
        self.current_proxy_index = 0
        self.results = {'HITS': 0, 'CUSTOM': 0, 'BAD': 0}
        self.running = False
        
        self.setup_ui()
        self.apply_styles()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        
        # Panel izquierdo (Tabla de resultados)
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("📊 RESULTADOS"))
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["RUT", "ESTADO", "DETALLES"])
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 300)
        left_layout.addWidget(self.table)
        
        # Panel derecho (Controles)
        right_layout = QVBoxLayout()
        
        # Estadísticas
        stats_layout = QHBoxLayout()
        self.label_hits = QLabel("✓ HITS: 0")
        self.label_custom = QLabel("⚠ CUSTOM: 0")
        self.label_bad = QLabel("✗ BAD: 0")
        self.label_total = QLabel("🏁 TOTAL: 0")
        
        for label in [self.label_hits, self.label_custom, self.label_bad, self.label_total]:
            label_widget = QLabel(label.text())
            label_widget.setFont(QFont("Arial", 10, QFont.Bold))
            stats_layout.addWidget(label_widget)
        
        right_layout.addLayout(stats_layout)
        
        # Botones de carga
        btn_layout = QHBoxLayout()
        self.btn_combos = QPushButton("📁 Cargar Combos")
        self.btn_combos.clicked.connect(self.load_combos)
        self.btn_proxies = QPushButton("🔗 Cargar Proxies")
        self.btn_proxies.clicked.connect(self.load_proxies)
        btn_layout.addWidget(self.btn_combos)
        btn_layout.addWidget(self.btn_proxies)
        right_layout.addLayout(btn_layout)
        
        # Barra de progreso
        self.progress = QProgressBar()
        self.progress.setValue(0)
        right_layout.addWidget(self.progress)
        
        # Botón de inicio
        self.btn_start = QPushButton("▶ INICIAR")
        self.btn_start.setStyleSheet("background-color: #00FF41; color: black; font-weight: bold;")
        self.btn_start.clicked.connect(self.start_checker)
        self.btn_start.setMinimumHeight(40)
        right_layout.addWidget(self.btn_start)
        
        # Logs
        right_layout.addWidget(QLabel("📋 LOGS EN VIVO"))
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setMaximumHeight(400)
        right_layout.addWidget(self.logs_text)
        
        # Agregar layouts principales
        left_container = QWidget()
        left_container.setLayout(left_layout)
        right_container = QWidget()
        right_container.setLayout(right_layout)
        
        main_layout.addWidget(left_container, 2)
        main_layout.addWidget(right_container, 1)
        
        central_widget.setLayout(main_layout)
    
    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0D1B2A;
            }
            QLabel {
                color: #00D4FF;
                font-weight: bold;
            }
            QPushButton {
                background-color: #1A2F4B;
                color: #00D4FF;
                border: 2px solid #2E5C8F;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4A90E2;
                border: 2px solid #00D4FF;
            }
            QTableWidget {
                background-color: #1A2F4B;
                color: #00D4FF;
                border: 1px solid #2E5C8F;
                gridline-color: #2E5C8F;
            }
            QTextEdit {
                background-color: #1A2F4B;
                color: #00FF41;
                font-family: Courier;
                border: 1px solid #2E5C8F;
            }
            QProgressBar {
                background-color: #1A2F4B;
                border: 2px solid #2E5C8F;
                border-radius: 5px;
                color: #00FF41;
            }
            QProgressBar::chunk {
                background-color: #00FF41;
            }
        """)
    
    def load_combos(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo de combos", "", "Text Files (*.txt)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.combos = [line.strip() for line in f.readlines() if line.strip()]
                
                QMessageBox.information(self, "Éxito", f"✓ Combos cargados: {len(self.combos)} líneas")
                self.add_log(f"✓ Cargados {len(self.combos)} combos")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error cargando combos: {str(e)}")
    
    def load_proxies(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo de proxies", "", "Text Files (*.txt)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.proxies = [line.strip() for line in f.readlines() if line.strip()]
                
                QMessageBox.information(self, "Éxito", f"✓ Proxies cargados: {len(self.proxies)} líneas")
                self.add_log(f"✓ Cargados {len(self.proxies)} proxies")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error cargando proxies: {str(e)}")
    
    def start_checker(self):
        if not self.combos:
            QMessageBox.warning(self, "Advertencia", "Carga combos primero")
            return
        
        self.running = True
        self.btn_start.setEnabled(False)
        self.btn_combos.setEnabled(False)
        self.btn_proxies.setEnabled(False)
        self.table.setRowCount(0)
        self.results = {'HITS': 0, 'CUSTOM': 0, 'BAD': 0}
        self.current_proxy_index = 0
        
        self.add_log("▶ Iniciando verificación...")
        
        thread = threading.Thread(target=self.run_checker)
        thread.daemon = True
        thread.start()
    
    def run_checker(self):
        worker = CheckerWorker()
        worker.log_signal.connect(self.add_log)
        
        total = len(self.combos)
        
        for i, combo in enumerate(self.combos):
            if not self.running:
                break
            
            proxy = None
            if self.proxies:
                proxy = self.proxies[self.current_proxy_index]
                self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
            
            result = worker.check_vtr(combo, proxy)
            
            status = result.get('status', 'BAD')
            self.results[status] = self.results.get(status, 0) + 1
            
            self.add_result(result)
            self.update_stats()
            
            progress = int((i + 1) / total * 100)
            self.progress.setValue(progress)
            
            time.sleep(0.5)
        
        self.running = False
        self.btn_start.setEnabled(True)
        self.btn_combos.setEnabled(True)
        self.btn_proxies.setEnabled(True)
        self.add_log("✓ Verificación completada")
    
    def add_result(self, result):
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        rut = result.get('rut', 'N/A')
        status = result.get('status', 'BAD')
        captura = result.get('captura', '')
        
        # Color según estado
        if status == 'HITS':
            color = QColor(0, 255, 65)
        elif status == 'CUSTOM':
            color = QColor(255, 165, 0)
        else:
            color = QColor(255, 107, 107)
        
        for j, text in enumerate([rut, status, captura]):
            item = QTableWidgetItem(text)
            item.setForeground(color)
            self.table.setItem(row, j, item)
    
    def add_log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs_text.append(f"[{timestamp}] {message}")
    
    def update_stats(self):
        total = sum(self.results.values())
        self.label_hits.setText(f"✓ HITS: {self.results.get('HITS', 0)}")
        self.label_custom.setText(f"⚠ CUSTOM: {self.results.get('CUSTOM', 0)}")
        self.label_bad.setText(f"✗ BAD: {self.results.get('BAD', 0)}")
        self.label_total.setText(f"🏁 TOTAL: {total}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VTRCheckerApp()
    window.show()
    sys.exit(app.exec_())
