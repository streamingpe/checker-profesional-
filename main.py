import sys
import os
import threading
import time
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTableWidget, 
                             QTableWidgetItem, QTextEdit, QFileDialog, QFrame,
                             QProgressBar, QSpinBox, QComboBox)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread, QTimer
from PyQt5.QtGui import QFont, QColor, QIcon, QClipboard
from checker_logic import CheckerWorker

class SignalEmitter(QObject):
    update_signal = pyqtSignal(str)
    stats_signal = pyqtSignal(dict)
    result_signal = pyqtSignal(dict)

class VTRCheckerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VTR PRIME VIDEO CHECKER")
        self.setGeometry(50, 50, 1600, 900)
        self.setStyleSheet(self.get_dark_stylesheet())
        
        self.combos = []
        self.proxies = []
        self.checker_worker = CheckerWorker()
        self.is_running = False
        self.current_index = 0
        
        self.stats = {
            'hits': 0,
            'custom': 0,
            'bad': 0,
            'total': 0
        }
        
        self.results_by_status = {
            'HITS': [],
            'CUSTOM': [],
            'BAD': []
        }
        
        self.setup_ui()
        self.connect_signals()
        
    def get_dark_stylesheet(self):
        return """
            QMainWindow { 
                background-color: #0D1B2A; 
            }
            QLabel { 
                color: #E0E0E0; 
            }
            QPushButton {
                background-color: #1E3A5F;
                color: white;
                border: 2px solid #2E5C8F;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #2E5C8F;
                border: 2px solid #4A90E2;
            }
            QPushButton:pressed {
                background-color: #1E3A5F;
            }
            QPushButton:disabled {
                background-color: #0D1B2A;
                border: 2px solid #1A2F4B;
                color: #666666;
            }
            QTableWidget {
                background-color: #1A2F4B;
                color: #E0E0E0;
                gridline-color: #2E5C8F;
                border: 1px solid #2E5C8F;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #2E5C8F;
                color: white;
                padding: 5px;
                border: none;
                font-weight: bold;
            }
            QTextEdit {
                background-color: #1A2F4B;
                color: #E0E0E0;
                border: 1px solid #2E5C8F;
                font-family: Courier;
                font-size: 9px;
            }
            QScrollBar:vertical {
                background-color: #1A2F4B;
                width: 12px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background-color: #2E5C8F;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #4A90E2;
            }
            QFrame {
                background-color: #1A2F4B;
                border: 2px solid #2E5C8F;
                border-radius: 8px;
            }
            QProgressBar {
                background-color: #1A2F4B;
                border: 2px solid #2E5C8F;
                border-radius: 5px;
                text-align: center;
                color: #E0E0E0;
            }
            QProgressBar::chunk {
                background-color: #00FF41;
            }
            QSpinBox, QComboBox {
                background-color: #1A2F4B;
                color: #E0E0E0;
                border: 1px solid #2E5C8F;
                border-radius: 4px;
                padding: 5px;
            }
        """
    
    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # ===== TÍTULO =====
        title_label = QLabel("▶ VTR PRIME VIDEO CHECKER")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setStyleSheet("color: #00FF41;")
        main_layout.addWidget(title_label)
        
        # ===== PANEL DE ESTADÍSTICAS =====
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        self.stat_boxes = {
            'hits': self.create_stat_box("✓ HITS", "0", "#00FF41"),
            'custom': self.create_stat_box("⚠ CUSTOM", "0", "#FFA500"),
            'bad': self.create_stat_box("✗ BAD", "0", "#FF6B6B"),
            'total': self.create_stat_box("🏁 TOTAL", "0", "#00D4FF")
        }
        
        for stat in self.stat_boxes.values():
            stats_layout.addWidget(stat)
        
        main_layout.addLayout(stats_layout)
        
        # ===== BARRA DE PROGRESO =====
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_label = QLabel("0 / 0 procesados")
        self.progress_label.setStyleSheet("color: #E0E0E0; font-size: 10px;")
        
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(QLabel("Progreso:"))
        progress_layout.addWidget(self.progress_bar, 1)
        progress_layout.addWidget(self.progress_label)
        main_layout.addLayout(progress_layout)
        
        # ===== BOTONES DE CONTROL =====
        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)
        
        btn_load_combos = QPushButton("📁 Cargar Combos")
        btn_load_combos.setStyleSheet("background-color: #1E5BA8; border-color: #3FA9F5;")
        btn_load_combos.clicked.connect(self.load_combos)
        control_layout.addWidget(btn_load_combos)
        
        btn_load_proxies = QPushButton("🔗 Cargar Proxies")
        btn_load_proxies.setStyleSheet("background-color: #6F42C1; border-color: #9D6FDB;")
        btn_load_proxies.clicked.connect(self.load_proxies)
        control_layout.addWidget(btn_load_proxies)
        
        # Espacio flexible
        control_layout.addStretch()
        
        # Botones de acción
        self.btn_start = QPushButton("▶ INICIAR")
        self.btn_start.setStyleSheet("background-color: #00AA00; border-color: #00FF41;")
        self.btn_start.setMinimumWidth(120)
        self.btn_start.clicked.connect(self.start_checker)
        control_layout.addWidget(self.btn_start)
        
        self.btn_stop = QPushButton("⏹ DETENER")
        self.btn_stop.setStyleSheet("background-color: #DC3545; border-color: #FF6B6B;")
        self.btn_stop.setMinimumWidth(120)
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_checker)
        control_layout.addWidget(self.btn_stop)
        
        self.btn_restart = QPushButton("🔄 REINICIAR")
        self.btn_restart.setStyleSheet("background-color: #6C757D; border-color: #999999;")
        self.btn_restart.setMinimumWidth(120)
        self.btn_restart.clicked.connect(self.restart_checker)
        control_layout.addWidget(self.btn_restart)
        
        main_layout.addLayout(control_layout)
        
        # ===== CONTENEDOR PRINCIPAL (Resultados + Logs) =====
        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)
        
        # ===== PANEL IZQUIERDO - RESULTADOS =====
        left_panel = QVBoxLayout()
        
        left_title = QLabel("RESULTADOS")
        left_title.setFont(QFont("Arial", 13, QFont.Bold))
        left_title.setStyleSheet("color: #E0E0E0;")
        left_panel.addWidget(left_title)
        
        # Tabs de resultados
        tab_layout = QHBoxLayout()
        
        self.btn_hits_tab = QPushButton("✓ HITS (0)")
        self.btn_hits_tab.setStyleSheet("background-color: #00FF41; color: black; font-weight: bold;")
        self.btn_hits_tab.setMaximumWidth(100)
        self.btn_hits_tab.clicked.connect(lambda: self.filter_results('HITS'))
        tab_layout.addWidget(self.btn_hits_tab)
        
        self.btn_custom_tab = QPushButton("⚠ CUSTOM (0)")
        self.btn_custom_tab.setStyleSheet("background-color: #FFA500; color: black; font-weight: bold;")
        self.btn_custom_tab.setMaximumWidth(100)
        self.btn_custom_tab.clicked.connect(lambda: self.filter_results('CUSTOM'))
        tab_layout.addWidget(self.btn_custom_tab)
        
        self.btn_bad_tab = QPushButton("✗ BAD (0)")
        self.btn_bad_tab.setStyleSheet("background-color: #FF6B6B; color: white; font-weight: bold;")
        self.btn_bad_tab.setMaximumWidth(100)
        self.btn_bad_tab.clicked.connect(lambda: self.filter_results('BAD'))
        tab_layout.addWidget(self.btn_bad_tab)
        
        self.btn_all_tab = QPushButton("📋 TODOS (0)")
        self.btn_all_tab.setStyleSheet("background-color: #00D4FF; color: black; font-weight: bold;")
        self.btn_all_tab.setMaximumWidth(100)
        self.btn_all_tab.clicked.connect(lambda: self.filter_results('ALL'))
        tab_layout.addWidget(self.btn_all_tab)
        
        tab_layout.addStretch()
        left_panel.addLayout(tab_layout)
        
        # Tabla de resultados
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["RUT", "Estado", "Captura", ""])
        self.results_table.horizontalHeader().setStretchLastSection(False)
        self.results_table.setColumnWidth(0, 150)
        self.results_table.setColumnWidth(1, 100)
        self.results_table.setColumnWidth(2, 500)
        self.results_table.setColumnWidth(3, 40)
        self.results_table.setAlternatingRowColors(True)
        left_panel.addWidget(self.results_table)
        
        content_layout.addLayout(left_panel, 2)
        
        # ===== PANEL DERECHO - LOGS =====
        right_panel = QVBoxLayout()
        
        right_title = QLabel("LOGS EN TIEMPO REAL")
        right_title.setFont(QFont("Arial", 13, QFont.Bold))
        right_title.setStyleSheet("color: #E0E0E0;")
        right_panel.addWidget(right_title)
        
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setFont(QFont("Courier", 9))
        right_panel.addWidget(self.logs_text)
        
        # Botones de logs
        logs_btn_layout = QHBoxLayout()
        btn_clear_logs = QPushButton("🗑 Limpiar Logs")
        btn_clear_logs.setMaximumWidth(120)
        btn_clear_logs.clicked.connect(self.clear_logs)
        logs_btn_layout.addWidget(btn_clear_logs)
        logs_btn_layout.addStretch()
        right_panel.addLayout(logs_btn_layout)
        
        content_layout.addLayout(right_panel, 1)
        main_layout.addLayout(content_layout)
        
        main_widget.setLayout(main_layout)
    
    def create_stat_box(self, title, value, color):
        """Crea una caja de estadística"""
        frame = QFrame()
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 11, QFont.Bold))
        title_label.setStyleSheet("color: #999999;")
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 32, QFont.Bold))
        value_label.setStyleSheet(f"color: {color};")
        value_label.setObjectName("stat_value")
        value_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(title_label, alignment=Qt.AlignCenter)
        layout.addWidget(value_label, alignment=Qt.AlignCenter)
        layout.setContentsMargins(20, 15, 20, 15)
        frame.setLayout(layout)
        
        frame.setObjectName("stat_box")
        frame.setStyleSheet(f"QFrame {{ background-color: #1A2F4B; border: 3px solid {color}; border-radius: 10px; }}")
        
        return frame
    
    def connect_signals(self):
        """Conecta señales del checker"""
        self.checker_worker.log_signal.connect(self.add_log)
        self.checker_worker.result_signal.connect(self.add_result)
    
    def load_combos(self):
        """Carga archivo de combos"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Cargar Combos", "", "Text Files (*.txt)")
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.combos = [line.strip() for line in f.readlines() if line.strip()]
                self.add_log(f"✓ Combos cargados: {len(self.combos)} líneas")
                self.btn_start.setEnabled(len(self.combos) > 0)
            except Exception as e:
                self.add_log(f"✗ Error al cargar combos: {str(e)}")
    
    def load_proxies(self):
        """Carga archivo de proxies"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Cargar Proxies", "", "Text Files (*.txt)")
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.proxies = [line.strip() for line in f.readlines() if line.strip()]
                self.add_log(f"✓ Proxies cargados: {len(self.proxies)} líneas")
            except Exception as e:
                self.add_log(f"✗ Error al cargar proxies: {str(e)}")
    
    def start_checker(self):
        """Inicia el checker"""
        if not self.combos:
            self.add_log("✗ Carga un archivo de combos primero")
            return
        
        self.is_running = True
        self.current_index = 0
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        
        self.add_log("▶ ========== INICIANDO CHECKER ==========")
        self.add_log(f"📊 Total de combos: {len(self.combos)}")
        if self.proxies:
            self.add_log(f"🔗 Proxies disponibles: {len(self.proxies)}")
        
        # Iniciar en thread
        self.checker_thread = threading.Thread(target=self.run_checker, daemon=True)
        self.checker_thread.start()
    
    def run_checker(self):
        """Ejecuta el checker en background"""
        total = len(self.combos)
        
        for i, combo in enumerate(self.combos):
            if not self.is_running:
                self.add_log("⏹ Checker detenido por usuario")
                break
            
            self.current_index = i + 1
            
            # Seleccionar proxy
            proxy = self.proxies[i % len(self.proxies)] if self.proxies else None
            
            # Verificar
            result = self.checker_worker.check_vtr(combo, proxy)
            
            # Actualizar UI
            self.add_result(result)
            self.update_progress()
            
            # Pequeño delay
            time.sleep(0.5)
        
        if self.is_running:
            self.add_log("✓ ========== CHECKER COMPLETADO ==========")
            self.stop_checker()
    
    def update_progress(self):
        """Actualiza la barra de progreso"""
        total = len(self.combos)
        if total > 0:
            percentage = int((self.current_index / total) * 100)
            self.progress_bar.setValue(percentage)
            self.progress_label.setText(f"{self.current_index} / {total} procesados")
    
    def stop_checker(self):
        """Detiene el checker"""
        self.is_running = False
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
    
    def restart_checker(self):
        """Reinicia el checker"""
        self.stop_checker()
        self.results_table.setRowCount(0)
        self.reset_stats()
        self.logs_text.clear()
        self.progress_bar.setValue(0)
        self.progress_label.setText("0 / 0 procesados")
        self.results_by_status = {'HITS': [], 'CUSTOM': [], 'BAD': []}
        self.add_log("🔄 Checker reiniciado - Listo para nueva ejecución")
    
    def add_result(self, result):
        """Añade un resultado a la tabla"""
        try:
            status = result.get('status', 'BAD')
            rut = result.get('rut', 'N/A')
            captura = result.get('captura', 'Sin información')
            link = result.get('link', None)
            
            # Guardar en estructura
            self.results_by_status[status].append(result)
            
            # Actualizar tabla
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)
            
            color_map = {
                'HITS': '#00FF41',
                'CUSTOM': '#FFA500',
                'BAD': '#FF6B6B',
                'RETRY': '#FFFF00'
            }
            
            color = QColor(color_map.get(status, '#E0E0E0'))
            
            # Columna 1: RUT
            rut_item = QTableWidgetItem(rut)
            rut_item.setForeground(color)
            rut_item.setFont(QFont("Arial", 10, QFont.Bold))
            self.results_table.setItem(row, 0, rut_item)
            
            # Columna 2: Estado
            estado_item = QTableWidgetItem(status)
            estado_item.setForeground(color)
            estado_item.setFont(QFont("Arial", 10, QFont.Bold))
            self.results_table.setItem(row, 1, estado_item)
            
            # Columna 3: Captura
            captura_item = QTableWidgetItem(captura)
            captura_item.setForeground(QColor('#E0E0E0'))
            self.results_table.setItem(row, 2, captura_item)
            
            # Columna 4: Botón copiar
            copy_btn = QPushButton("📋")
            copy_btn.setMaximumWidth(35)
            copy_btn.setStyleSheet("background-color: #2E5C8F; border: 1px solid #4A90E2;")
            copy_btn.clicked.connect(lambda: self.copy_to_clipboard(rut, captura))
            self.results_table.setCellWidget(row, 3, copy_btn)
            
            # Actualizar estadísticas
            self.update_stats()
            self.update_tab_labels()
            
            # Auto-scroll
            self.results_table.scrollToBottom()
            
        except Exception as e:
            self.add_log(f"✗ Error añadiendo resultado: {str(e)}")
    
    def copy_to_clipboard(self, rut, captura):
        """Copia resultado al portapapeles"""
        text = f"{rut} - {captura}"
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        self.add_log(f"📋 Copiado: {text}")
    
    def update_stats(self):
        """Actualiza las estadísticas"""
        self.stats['hits'] = len(self.results_by_status['HITS'])
        self.stats['custom'] = len(self.results_by_status['CUSTOM'])
        self.stats['bad'] = len(self.results_by_status['BAD'])
        self.stats['total'] = self.stats['hits'] + self.stats['custom'] + self.stats['bad']
        
        # Actualizar UI
        self.stat_boxes['hits'].findChild(QLabel, "stat_value").setText(str(self.stats['hits']))
        self.stat_boxes['custom'].findChild(QLabel, "stat_value").setText(str(self.stats['custom']))
        self.stat_boxes['bad'].findChild(QLabel, "stat_value").setText(str(self.stats['bad']))
        self.stat_boxes['total'].findChild(QLabel, "stat_value").setText(str(self.stats['total']))
    
    def update_tab_labels(self):
        """Actualiza etiquetas de tabs"""
        self.btn_hits_tab.setText(f"✓ HITS ({self.stats['hits']})")
        self.btn_custom_tab.setText(f"⚠ CUSTOM ({self.stats['custom']})")
        self.btn_bad_tab.setText(f"✗ BAD ({self.stats['bad']})")
        self.btn_all_tab.setText(f"📋 TODOS ({self.stats['total']})")
    
    def filter_results(self, status):
        """Filtra resultados por estado"""
        self.results_table.setRowCount(0)
        
        if status == 'ALL':
            results = self.results_by_status['HITS'] + self.results_by_status['CUSTOM'] + self.results_by_status['BAD']
        else:
            results = self.results_by_status.get(status, [])
        
        for result in results:
            self.display_result(result)
    
    def display_result(self, result):
        """Muestra un resultado en la tabla"""
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        
        status = result.get('status', 'BAD')
        rut = result.get('rut', 'N/A')
        captura = result.get('captura', 'Sin información')
        
        color_map = {
            'HITS': '#00FF41',
            'CUSTOM': '#FFA500',
            'BAD': '#FF6B6B'
        }
        
        color = QColor(color_map.get(status, '#E0E0E0'))
        
        rut_item = QTableWidgetItem(rut)
        rut_item.setForeground(color)
        self.results_table.setItem(row, 0, rut_item)
        
        estado_item = QTableWidgetItem(status)
        estado_item.setForeground(color)
        self.results_table.setItem(row, 1, estado_item)
        
        captura_item = QTableWidgetItem(captura)
        captura_item.setForeground(QColor('#E0E0E0'))
        self.results_table.setItem(row, 2, captura_item)
        
        copy_btn = QPushButton("📋")
        copy_btn.setMaximumWidth(35)
        copy_btn.clicked.connect(lambda: self.copy_to_clipboard(rut, captura))
        self.results_table.setCellWidget(row, 3, copy_btn)
    
    def add_log(self, message):
        """Añade un mensaje al log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        self.logs_text.append(log_message)
        self.logs_text.verticalScrollBar().setValue(
            self.logs_text.verticalScrollBar().maximum()
        )
    
    def clear_logs(self):
        """Limpia los logs"""
        self.logs_text.clear()
        self.add_log("🗑 Logs limpios")
    
    def reset_stats(self):
        """Reinicia las estadísticas"""
        self.stats = {'hits': 0, 'custom': 0, 'bad': 0, 'total': 0}
        for key, box in self.stat_boxes.items():
            box.findChild(QLabel, "stat_value").setText("0")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VTRCheckerApp()
    window.show()
    sys.exit(app.exec_())
