#!/usr/bin/env python3
"""
StudyFlow TDAH v2.1 - CORREGIDO
Sistema de estudio neurodivergente de alto rendimiento
Arquitectura: Modular, async-aware, dopamina-optimizada, THREAD-SAFE
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
import time
import threading
import random
from datetime import datetime, timedelta
from collections import deque
import webbrowser
from typing import Dict, List, Optional, Callable
import queue


class DopamineRewardSystem:
    """
    Sistema de recompensas variable que mantiene el engagement
    Basado en mecánicas de juegos que funcionan con TDAH
    """
    
    REWARDS = [
        "🧠 ¡Neurona activada! Conexión sináptica fortalecida",
        "⚡ ¡Racha eléctrica! Tu cerebro está en modo flow",
        "🎯 ¡Bullseye! Precisión de enfoque al máximo",
        "🔥 ¡Combustión! Energía cognitiva desbloqueada",
        "🚀 ¡Lanzamiento! Productividad en órbita",
        "💎 ¡Gema rara! Enfoque profundo conseguido",
        "⚔️ ¡Victoria! Derrotaste a la procrastinación",
        "🌟 ¡Supernova! Brillo intelectual detectado",
    ]
    
    MILESTONES = {
        1: "🌱 Primera semilla plantada",
        3: "🔥 Racha de 3 ¡Esto es fuego!",
        5: "⚡ Maestría del enfoque incoming",
        10: "🧠 Modo cerebro galáctico activado",
        15: "👑 Leyenda del estudio",
        20: "🚀 Productividad fuera de serie",
        25: "💎 Diamante en bruto pulido",
        50: "🌟 Arquitecto de tu propio destino"
    }
    
    def __init__(self):
        self.session_count = 0
        self.total_focus_minutes = 0
        self.current_streak = 0
        self.best_streak = 0
        self.achievements_unlocked = set()
        
    def register_session(self, minutes: int, quality: float = 1.0) -> Dict:
        """Registra una sesión y calcula recompensas"""
        self.session_count += 1
        self.total_focus_minutes += minutes
        self.current_streak += 1
        
        if self.current_streak > self.best_streak:
            self.best_streak = self.current_streak
            
        # Sistema de recompensa variable (más adictivo que fijo)
        reward = {
            'message': random.choice(self.REWARDS),
            'session_number': self.session_count,
            'streak': self.current_streak,
            'milestone': None,
            'bonus': False
        }
        
        # Milestones
        if self.session_count in self.MILESTONES:
            reward['milestone'] = self.MILESTONES[self.session_count]
            self.achievements_unlocked.add(self.session_count)
            
        # Bonus por calidad (si completaste sin pausas)
        if quality > 0.9:
            reward['bonus'] = True
            reward['message'] += " ⭐ BONUS: Enfoque puro!"
            
        return reward
    
    def break_streak(self):
        """Rompe la racha (cuando fallas un día)"""
        self.current_streak = 0
        
    def get_stats(self) -> Dict:
        return {
            'sessions': self.session_count,
            'total_hours': round(self.total_focus_minutes / 60, 1),
            'current_streak': self.current_streak,
            'best_streak': self.best_streak,
            'achievements': len(self.achievements_unlocked)
        }


class TaskEnergyMatcher:
    """
    Empareja tareas con tu nivel de energía actual
    Crítico para TDAH: no todas las horas son iguales
    """
    
    ENERGY_LEVELS = {
        'high': {'color': '#00d26a', 'icon': '🔥', 'duration': 25},
        'medium': {'color': '#4a9eff', 'icon': '⚡', 'duration': 15},
        'low': {'color': '#f0ad4e', 'icon': '💡', 'duration': 10},
        'minimal': {'color': '#ff6b6b', 'icon': '🌱', 'duration': 5}
    }
    
    def __init__(self):
        self.current_energy = 'medium'
        
    def set_energy(self, level: str):
        if level in self.ENERGY_LEVELS:
            self.current_energy = level
            
    def get_recommended_duration(self) -> int:
        return self.ENERGY_LEVELS[self.current_energy]['duration']
    
    def get_task_suggestion(self, task_difficulty: str) -> str:
        """Sugiere si hacer la tarea ahora o posponer"""
        energy_map = {
            'high': ['high', 'medium'],
            'medium': ['medium', 'low', 'high'],
            'low': ['low', 'minimal'],
            'minimal': ['minimal']
        }
        
        if self.current_energy in energy_map.get(task_difficulty, ['medium']):
            return "match"
        elif task_difficulty == 'high' and self.current_energy in ['low', 'minimal']:
            return "postpone"
        else:
            return "adapt"


class FocusGuardian:
    """
    Sistema anti-distracción proactivo - VERSION THREAD-SAFE
    Usa una cola para comunicarse con el hilo principal de Tkinter
    """
    
    def __init__(self, message_queue: queue.Queue):
        self.message_queue = message_queue
        self.check_interval = 30  # segundos
        self.last_interaction = time.time()
        self.is_monitoring = False
        self.distraction_count = 0
        self._timer = None
        
    def start_monitoring(self):
        self.is_monitoring = True
        self.last_interaction = time.time()
        self._monitor_loop()
        
    def register_interaction(self):
        """Llama esto cuando el usuario interactúa"""
        self.last_interaction = time.time()
        self.distraction_count = 0
        
    def _monitor_loop(self):
        if not self.is_monitoring:
            return
            
        idle_time = time.time() - self.last_interaction
        
        # Niveles de intervención
        if idle_time > 120:  # 2 minutos sin actividad
            self.distraction_count += 1
            # Enviar mensaje a la cola en lugar de llamar directamente
            self.message_queue.put(('severe', f"¡Distraído por {int(idle_time/60)} min! ¿Volvemos?"))
            self.last_interaction = time.time()  # Reset para no spamear
            
        elif idle_time > 60:  # 1 minuto
            if self.distraction_count == 0:
                self.message_queue.put(('mild', "¿Sigues ahí? Un click y volvemos al flow"))
                
        # Programar siguiente revisión
        if self.is_monitoring:
            self._timer = threading.Timer(self.check_interval, self._monitor_loop)
            self._timer.daemon = True
            self._timer.start()
            
    def stop_monitoring(self):
        self.is_monitoring = False
        if self._timer:
            self._timer.cancel()


class BodyDoublingRoom:
    """
    Simulación de "body doubling" (estudiar con alguien más)
    Técnica probada para TDAH: la presencia externa reduce distracción
    """
    
    COMPANIONS = [
        {"name": "Alex", "type": "Bibliotecario silencioso", "msg": "Alex está leyendo junto a ti..."},
        {"name": "Sam", "type": "Compañero de café", "msg": "Sam está en su laptop, tecleando suavemente..."},
        {"name": "Jordan", "type": "Artista concentrado", "msg": "Jordan está dibujando en su cuaderno..."},
        {"name": "Taylor", "type": "Estudiante de medicina", "msg": "Taylor está memorizando anatomía..."},
        {"name": "Morgan", "type": "Programador nocturno", "msg": "Morgan está debuggeando código..."}
    ]
    
    ENCOURAGEMENTS = [
        "Tu compañero mira su reloj y sigue enfocado. Tú también puedes.",
        "Un suspiro de concentración desde la mesa de al lado.",
        "El ritmo constante de tu compañero te ancla.",
        "Silencio productivo. Estás en buena compañía.",
        "Tu compañero gira una página. Tú sigues avanzando."
    ]
    
    def __init__(self):
        self.active_companion = None
        self.session_messages = deque(maxlen=5)
        
    def start_session(self) -> Dict:
        self.active_companion = random.choice(self.COMPANIONS)
        return self.active_companion
    
    def get_ambient_message(self) -> str:
        """Mensaje ambiental periódico"""
        if random.random() < 0.3:  # 30% de probabilidad
            return random.choice(self.ENCOURAGEMENTS)
        return None


class StudyFlowV2:
    """
    Aplicación principal v2.1 - THREAD SAFE
    Rediseñada desde cero con principios de UX para neurodivergencia
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("StudyFlow TDAH v2.1 - Modo Cerebro Galáctico")
        self.root.geometry("1100x800")
        self.root.minsize(1000, 700)
        
        # Paleta de colores científicamente seleccionada para TDAH
        self.colors = {
            'bg_primary': '#0f172a',      # Azul oscuro profundo (calma)
            'bg_secondary': '#1e293b',     # Slate 800
            'bg_card': '#334155',          # Slate 700
            'accent_primary': '#38bdf8',   # Cyan 400 (enfoque)
            'accent_success': '#4ade80',   # Green 400 (logro)
            'accent_energy': '#fb923c',    # Orange 400 (energía)
            'accent_urgent': '#f87171',    # Red 400 (alerta)
            'text_primary': '#f8fafc',     # Slate 50
            'text_secondary': '#cbd5e1',   # Slate 300
            'text_muted': '#64748b'        # Slate 500
        }
        
        # Sistemas
        self.reward_system = DopamineRewardSystem()
        self.energy_matcher = TaskEnergyMatcher()
        self.body_doubling = BodyDoublingRoom()
        
        # Cola para mensajes thread-safe
        self.msg_queue = queue.Queue()
        self.focus_guardian: Optional[FocusGuardian] = None
        
        # Estado
        self.timer_state = 'idle'  # idle, running, paused, break
        self.timer_thread: Optional[threading.Thread] = None
        self.current_task: Optional[Dict] = None
        self.session_start_time: Optional[datetime] = None
        self.pause_count = 0
        
        # Datos
        self.tasks: List[Dict] = []
        self.sessions_history: List[Dict] = []
        
        self.setup_ui()
        self.apply_theme()
        self.load_data()
        
        # Iniciar check de cola de mensajes
        self.check_message_queue()
        
        # Bindings globales para focus guardian
        self.root.bind_all('<Button-1>', lambda e: self.on_user_activity())
        self.root.bind_all('<Key>', lambda e: self.on_user_activity())
        
    def check_message_queue(self):
        """Revisa la cola de mensajes del Focus Guardian (thread-safe)"""
        try:
            while True:
                level, message = self.msg_queue.get_nowait()
                self.on_distraction_detected(level, message)
        except queue.Empty:
            pass
        finally:
            # Revisar cada 100ms
            self.root.after(100, self.check_message_queue)
        
    def setup_ui(self):
        """Configuración de interfaz con layout optimizado"""
        
        # Frame principal con padding generoso (reduce sensación de abrumo)
        self.main_container = tk.Frame(self.root, bg=self.colors['bg_primary'])
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # HEADER: Estado actual y energía
        self.setup_header()
        
        # CONTENIDO: Notebook con pestañas rediseñadas
        self.setup_notebook()
        
        # FOOTER: Barra de estado persistente
        self.setup_footer()
        
    def setup_header(self):
        """Header con selector de energía y estado del sistema"""
        header = tk.Frame(self.main_container, bg=self.colors['bg_primary'])
        header.pack(fill=tk.X, pady=(0, 20))
        
        # Logo y título
        left = tk.Frame(header, bg=self.colors['bg_primary'])
        left.pack(side=tk.LEFT)
        
        tk.Label(left, text="🧠", font=('Segoe UI Emoji', 32), 
                bg=self.colors['bg_primary']).pack(side=tk.LEFT)
        
        title_frame = tk.Frame(left, bg=self.colors['bg_primary'])
        title_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(title_frame, text="StudyFlow", 
                font=('Helvetica Neue', 24, 'bold'),
                fg=self.colors['text_primary'], 
                bg=self.colors['bg_primary']).pack(anchor=tk.W)
        
        self.subtitle_label = tk.Label(title_frame, 
                                      text="Modo: Esperando inicio", 
                                      font=('Helvetica Neue', 12),
                                      fg=self.colors['text_secondary'],
                                      bg=self.colors['bg_primary'])
        self.subtitle_label.pack(anchor=tk.W)
        
        # Selector de energía (CRÍTICO para TDAH)
        right = tk.Frame(header, bg=self.colors['bg_primary'])
        right.pack(side=tk.RIGHT)
        
        tk.Label(right, text="Mi energía ahora:", 
                font=('Helvetica Neue', 11),
                fg=self.colors['text_secondary'],
                bg=self.colors['bg_primary']).pack(side=tk.LEFT, padx=10)
        
        self.energy_var = tk.StringVar(value='medium')
        energy_frame = tk.Frame(right, bg=self.colors['bg_secondary'], 
                               highlightbackground=self.colors['accent_primary'],
                               highlightthickness=2, bd=0)
        energy_frame.pack(side=tk.LEFT)
        
        for level, info in self.energy_matcher.ENERGY_LEVELS.items():
            btn = tk.Radiobutton(energy_frame, text=f"{info['icon']} {level.upper()}", 
                               variable=self.energy_var, value=level,
                               command=self.on_energy_change,
                               font=('Helvetica Neue', 10, 'bold'),
                               fg=info['color'], bg=self.colors['bg_secondary'],
                               selectcolor=self.colors['bg_primary'],
                               activebackground=self.colors['bg_card'],
                               cursor='hand2')
            btn.pack(side=tk.LEFT, padx=5, pady=5)
            
    def setup_notebook(self):
        """Notebook con pestañas modernas"""
        # Estilo personalizado para tabs
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Custom.TNotebook', 
                       background=self.colors['bg_primary'],
                       tabmargins=[2, 5, 2, 0])
        
        style.configure('Custom.TNotebook.Tab', 
                       font=('Helvetica Neue', 11, 'bold'),
                       padding=[15, 8],
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_secondary'])
        
        style.map('Custom.TNotebook.Tab',
                 background=[('selected', self.colors['accent_primary'])],
                 foreground=[('selected', self.colors['bg_primary'])],
                 expand=[('selected', [1, 1, 1, 0])])
        
        self.notebook = ttk.Notebook(self.main_container, style='Custom.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestañas
        self.tab_focus = self.create_focus_tab()
        self.tab_tasks = self.create_tasks_tab()
        self.tab_analytics = self.create_analytics_tab()
        self.tab_tools = self.create_tools_tab()
        
        self.notebook.add(self.tab_focus, text="  ⏱️  FOCUS  ")
        self.notebook.add(self.tab_tasks, text="  📝  TAREAS  ")
        self.notebook.add(self.tab_analytics, text="  📊  PROGRESO  ")
        self.notebook.add(self.tab_tools, text="  🛠️  HERRAMIENTAS  ")
        
    def create_focus_tab(self):
        """Pestaña de focus con body doubling y timer inmersivo"""
        frame = tk.Frame(self.notebook, bg=self.colors['bg_primary'])
        
        # Layout de dos columnas
        left_col = tk.Frame(frame, bg=self.colors['bg_primary'])
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        
        right_col = tk.Frame(frame, bg=self.colors['bg_primary'], width=300)
        right_col.pack(side=tk.RIGHT, fill=tk.Y)
        right_col.pack_propagate(False)
        
        # === COLUMNA IZQUIERDA: Timer principal ===
        
        # Card del timer
        timer_card = tk.Frame(left_col, bg=self.colors['bg_secondary'],
                             highlightbackground=self.colors['accent_primary'],
                             highlightthickness=2)
        timer_card.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Info de sesión actual
        self.session_info_frame = tk.Frame(timer_card, bg=self.colors['bg_secondary'])
        self.session_info_frame.pack(fill=tk.X, padx=20, pady=15)
        
        self.current_task_label = tk.Label(self.session_info_frame,
                                          text="Ninguna tarea seleccionada",
                                          font=('Helvetica Neue', 14),
                                          fg=self.colors['text_secondary'],
                                          bg=self.colors['bg_secondary'])
        self.current_task_label.pack(side=tk.LEFT)
        
        self.session_badge = tk.Label(self.session_info_frame,
                                     text="SESION #0",
                                     font=('Helvetica Neue', 10, 'bold'),
                                     fg=self.colors['bg_primary'],
                                     bg=self.colors['accent_primary'],
                                     padx=10, pady=3)
        self.session_badge.pack(side=tk.RIGHT)
        
        # Timer circular grande
        self.timer_canvas = tk.Canvas(timer_card, height=350, 
                                     bg=self.colors['bg_secondary'],
                                     highlightthickness=0)
        self.timer_canvas.pack(pady=20)
        
        self.timer_text_id = self.timer_canvas.create_text(
            200, 175, text="15:00", 
            font=('Helvetica Neue', 64, 'bold'),
            fill=self.colors['accent_primary']
        )
        
        # Barra de progreso lineal (más intuitiva que solo círculo)
        self.progress_bar = tk.Canvas(timer_card, height=8, 
                                     bg=self.colors['bg_card'],
                                     highlightthickness=0)
        self.progress_bar.pack(fill=tk.X, padx=50, pady=10)
        
        # Controles principales
        controls = tk.Frame(timer_card, bg=self.colors['bg_secondary'])
        controls.pack(pady=20)
        
        self.btn_main = tk.Button(controls, text="▶ INICIAR FOCUS",
                                 font=('Helvetica Neue', 14, 'bold'),
                                 bg=self.colors['accent_success'],
                                 fg=self.colors['bg_primary'],
                                 activebackground=self.colors['accent_primary'],
                                 cursor='hand2',
                                 width=20, height=2,
                                 command=self.toggle_timer)
        self.btn_main.pack(side=tk.LEFT, padx=5)
        
        self.btn_reset = tk.Button(controls, text="↺",
                                  font=('Helvetica Neue', 14),
                                  bg=self.colors['bg_card'],
                                  fg=self.colors['text_primary'],
                                  cursor='hand2',
                                  width=4, height=2,
                                  command=self.reset_timer)
        self.btn_reset.pack(side=tk.LEFT, padx=5)
        
        # Estado y mensajes
        self.status_frame = tk.Frame(timer_card, bg=self.colors['bg_secondary'])
        self.status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.status_icon = tk.Label(self.status_frame, text="⏳",
                                   font=('Segoe UI Emoji', 24),
                                   bg=self.colors['bg_secondary'])
        self.status_icon.pack(side=tk.LEFT, padx=(0, 10))
        
        self.status_message = tk.Label(self.status_frame,
                                      text="Listo para tu mejor sesión",
                                      font=('Helvetica Neue', 12),
                                      fg=self.colors['text_secondary'],
                                      bg=self.colors['bg_secondary'],
                                      wraplength=400, justify=tk.LEFT)
        self.status_message.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # === COLUMNA DERECHA: Body Doubling & Tools ===
        
        # Body Doubling Card
        bd_card = tk.LabelFrame(right_col, text=" Body Doubling ",
                               font=('Helvetica Neue', 12, 'bold'),
                               fg=self.colors['accent_primary'],
                               bg=self.colors['bg_secondary'])
        bd_card.pack(fill=tk.X, pady=(0, 15), ipady=10)
        
        self.bd_avatar = tk.Label(bd_card, text="👤", 
                                 font=('Segoe UI Emoji', 48),
                                 bg=self.colors['bg_secondary'])
        self.bd_avatar.pack(pady=5)
        
        self.bd_name = tk.Label(bd_card, text="Esperando compañero...",
                               font=('Helvetica Neue', 11, 'bold'),
                               fg=self.colors['text_primary'],
                               bg=self.colors['bg_secondary'])
        self.bd_name.pack()
        
        self.bd_type = tk.Label(bd_card, text="",
                               font=('Helvetica Neue', 9),
                               fg=self.colors['text_secondary'],
                               bg=self.colors['bg_secondary'])
        self.bd_type.pack()
        
        self.bd_message = tk.Label(bd_card, text="",
                                  font=('Helvetica Neue', 10, 'italic'),
                                  fg=self.colors['text_muted'],
                                  bg=self.colors['bg_secondary'],
                                  wraplength=250, justify=tk.CENTER)
        self.bd_message.pack(pady=10)
        
        # Quick Tools
        tools_card = tk.LabelFrame(right_col, text=" Accesos Rápidos ",
                                  font=('Helvetica Neue', 12, 'bold'),
                                  fg=self.colors['accent_energy'],
                                  bg=self.colors['bg_secondary'])
        tools_card.pack(fill=tk.X, pady=(0, 15))
        
        tools = [
            ("🎵 Sonido Focus", self.open_focus_sound),
            ("🧘 Respiración 4-7-8", self.breathing_exercise),
            ("🚰 Descanso Activo", self.active_break),
            ("🆘 Modo Emergencia", self.emergency_mode),
        ]
        
        for text, cmd in tools:
            tk.Button(tools_card, text=text,
                     font=('Helvetica Neue', 10),
                     bg=self.colors['bg_card'],
                     fg=self.colors['text_primary'],
                     activebackground=self.colors['accent_primary'],
                     cursor='hand2',
                     command=cmd).pack(fill=tk.X, padx=10, pady=3)
        
        # Mini-stats
        stats_card = tk.LabelFrame(right_col, text=" Hoy ",
                                  font=('Helvetica Neue', 12, 'bold'),
                                  fg=self.colors['accent_success'],
                                  bg=self.colors['bg_secondary'])
        stats_card.pack(fill=tk.X)
        
        self.mini_stats = tk.Label(stats_card,
                                  text="0 sesiones • 0 min focus",
                                  font=('Helvetica Neue', 11),
                                  fg=self.colors['text_secondary'],
                                  bg=self.colors['bg_secondary'])
        self.mini_stats.pack(pady=10)
        
        return frame
    
    def create_tasks_tab(self):
        """Gestor de tareas con sistema de chunks inteligente"""
        frame = tk.Frame(self.notebook, bg=self.colors['bg_primary'])
        
        # Input inteligente
        input_card = tk.Frame(frame, bg=self.colors['bg_secondary'])
        input_card.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(input_card, text="📝 Nueva Tarea / Chunk",
                font=('Helvetica Neue', 14, 'bold'),
                fg=self.colors['text_primary'],
                bg=self.colors['bg_secondary']).pack(anchor=tk.W, padx=15, pady=(15, 5))
        
        input_row = tk.Frame(input_card, bg=self.colors['bg_secondary'])
        input_row.pack(fill=tk.X, padx=15, pady=10)
        
        self.task_entry = tk.Entry(input_row,
                                  font=('Helvetica Neue', 12),
                                  bg=self.colors['bg_card'],
                                  fg=self.colors['text_primary'],
                                  insertbackground=self.colors['accent_primary'],
                                  relief=tk.FLAT)
        self.task_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        self.task_entry.bind('<Return>', lambda e: self.add_task())
        
        # Dificultad/Energía requerida
        self.task_difficulty = ttk.Combobox(input_row, 
                                           values=['high', 'medium', 'low', 'minimal'],
                                           width=12, state='readonly')
        self.task_difficulty.set('medium')
        self.task_difficulty.pack(side=tk.LEFT, padx=10)
        
        tk.Button(input_row, text="+ AGREGAR",
                 font=('Helvetica Neue', 11, 'bold'),
                 bg=self.colors['accent_success'],
                 fg=self.colors['bg_primary'],
                 cursor='hand2',
                 command=self.add_task).pack(side=tk.LEFT)
        
        # Sugerencia inteligente
        self.suggestion_label = tk.Label(input_card,
                                        text="💡 Sugerencia: Con tu energía MEDIUM, prioriza tareas MEDIUM",
                                        font=('Helvetica Neue', 10),
                                        fg=self.colors['accent_primary'],
                                        bg=self.colors['bg_secondary'])
        self.suggestion_label.pack(anchor=tk.W, padx=15, pady=(0, 10))
        
        # Lista de tareas
        list_container = tk.Frame(frame, bg=self.colors['bg_primary'])
        list_container.pack(fill=tk.BOTH, expand=True)
        
        # Columnas
        headers = tk.Frame(list_container, bg=self.colors['bg_card'])
        headers.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(headers, text="ESTADO", width=10,
                font=('Helvetica Neue', 10, 'bold'),
                fg=self.colors['text_muted'], bg=self.colors['bg_card']).pack(side=tk.LEFT)
        tk.Label(headers, text="TAREA",
                font=('Helvetica Neue', 10, 'bold'),
                fg=self.colors['text_muted'], bg=self.colors['bg_card']).pack(side=tk.LEFT, expand=True)
        tk.Label(headers, text="ENERGÍA", width=12,
                font=('Helvetica Neue', 10, 'bold'),
                fg=self.colors['text_muted'], bg=self.colors['bg_card']).pack(side=tk.LEFT)
        tk.Label(headers, text="ACCIÓN", width=15,
                font=('Helvetica Neue', 10, 'bold'),
                fg=self.colors['text_muted'], bg=self.colors['bg_card']).pack(side=tk.LEFT)
        
        # Scrollable list
        canvas_frame = tk.Frame(list_container, bg=self.colors['bg_primary'])
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tasks_canvas = tk.Canvas(canvas_frame, bg=self.colors['bg_primary'],
                                     highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", 
                                 command=self.tasks_canvas.yview)
        
        self.tasks_list_frame = tk.Frame(self.tasks_canvas, bg=self.colors['bg_primary'])
        
        self.tasks_canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tasks_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.tasks_canvas.create_window((0, 0), window=self.tasks_list_frame, 
                                       anchor="nw", width=1000)
        self.tasks_list_frame.bind("<Configure>", 
                                  lambda e: self.tasks_canvas.configure(
                                      scrollregion=self.tasks_canvas.bbox("all")))
        
        # Botón de ritual de inicio
        ritual_card = tk.Frame(frame, bg=self.colors['bg_secondary'])
        ritual_card.pack(fill=tk.X, pady=15)
        
        tk.Label(ritual_card, text="✨ Ritual de Inicio (2 min)",
                font=('Helvetica Neue', 12, 'bold'),
                fg=self.colors['accent_energy'],
                bg=self.colors['bg_secondary']).pack(anchor=tk.W, padx=15, pady=10)
        
        self.ritual_checks = {}
        rituals = [
            "☕ Preparé mi bebida y ambiente",
            "📱 Activé modo focus / bloqueé distracciones",
            "🎵 Puse música/sonido de fondo",
            "🧘 Hice 3 respiraciones conscientes",
            "✅ Seleccioné la tarea específica a trabajar"
        ]
        
        for ritual in rituals:
            var = tk.BooleanVar()
            self.ritual_checks[ritual] = var
            tk.Checkbutton(ritual_card, text=ritual, variable=var,
                          font=('Helvetica Neue', 10),
                          fg=self.colors['text_secondary'],
                          bg=self.colors['bg_secondary'],
                          selectcolor=self.colors['bg_card'],
                          activebackground=self.colors['bg_secondary']).pack(anchor=tk.W, padx=30)
        
        return frame
    
    def create_analytics_tab(self):
        """Dashboard de progreso con gamificación"""
        frame = tk.Frame(self.notebook, bg=self.colors['bg_primary'])
        
        # Stats grid
        stats_grid = tk.Frame(frame, bg=self.colors['bg_primary'])
        stats_grid.pack(fill=tk.X, pady=10)
        
        self.stat_cards = {}
        stats_config = [
            ('sessions', 'Sesiones Hoy', '🔥', self.colors['accent_energy']),
            ('streak', 'Racha Actual', '⚡', self.colors['accent_primary']),
            ('total', 'Minutos Focus', '🧠', self.colors['accent_success']),
            ('best', 'Mejor Racha', '👑', self.colors['accent_urgent'])
        ]
        
        for i, (key, label, icon, color) in enumerate(stats_config):
            card = tk.Frame(stats_grid, bg=self.colors['bg_secondary'], padx=20, pady=15)
            card.grid(row=0, column=i, padx=10, sticky='nsew')
            stats_grid.columnconfigure(i, weight=1)
            
            tk.Label(card, text=icon, font=('Segoe UI Emoji', 32),
                    bg=self.colors['bg_secondary']).pack()
            tk.Label(card, text="0", font=('Helvetica Neue', 28, 'bold'),
                    fg=color, bg=self.colors['bg_secondary']).pack()
            tk.Label(card, text=label, font=('Helvetica Neue', 10),
                    fg=self.colors['text_secondary'], 
                    bg=self.colors['bg_secondary']).pack()
            
            self.stat_cards[key] = card.winfo_children()[1]  # El número
        
        # Gráfico de racha visual
        streak_frame = tk.LabelFrame(frame, text=" Visualización de Racha ",
                                    font=('Helvetica Neue', 12, 'bold'),
                                    fg=self.colors['text_primary'],
                                    bg=self.colors['bg_secondary'])
        streak_frame.pack(fill=tk.X, pady=15, ipady=10)
        
        self.streak_canvas = tk.Canvas(streak_frame, height=60,
                                      bg=self.colors['bg_secondary'],
                                      highlightthickness=0)
        self.streak_canvas.pack(fill=tk.X, padx=20)
        
        # Log de sesiones
        log_frame = tk.LabelFrame(frame, text=" Historial de Sesiones ",
                                 font=('Helvetica Neue', 12, 'bold'),
                                 fg=self.colors['text_primary'],
                                 bg=self.colors['bg_secondary'])
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            font=('JetBrains Mono', 10),
            bg=self.colors['bg_card'],
            fg=self.colors['text_secondary'],
            insertbackground=self.colors['accent_primary'],
            relief=tk.FLAT,
            padx=10, pady=10
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Exportar
        tk.Button(frame, text="💾 Exportar Reporte Semanal",
                 font=('Helvetica Neue', 11, 'bold'),
                 bg=self.colors['accent_primary'],
                 fg=self.colors['bg_primary'],
                 cursor='hand2',
                 command=self.export_report).pack(pady=10)
        
        return frame
    
    def create_tools_tab(self):
        """Herramientas adicionales"""
        frame = tk.Frame(self.notebook, bg=self.colors['bg_primary'])
        
        # Grid de herramientas
        tools_grid = tk.Frame(frame, bg=self.colors['bg_primary'])
        tools_grid.pack(fill=tk.BOTH, expand=True)
        
        tools = [
            ("🎵 Generador de Ruido", self.open_noise_generator),
            ("🧘 Guía de Respiración", self.breathing_guide),
            ("📝 Plantilla Cornell", self.open_cornell_template),
            ("⏰ Calculador de Sueño", self.sleep_calculator),
            ("📊 Análisis de Energía", self.energy_analyzer),
            ("🎯 Desbloqueo de Logros", self.show_achievements),
        ]
        
        for i, (name, cmd) in enumerate(tools):
            row, col = divmod(i, 2)
            btn = tk.Button(tools_grid, text=name,
                          font=('Helvetica Neue', 14),
                          bg=self.colors['bg_secondary'],
                          fg=self.colors['text_primary'],
                          activebackground=self.colors['accent_primary'],
                          cursor='hand2',
                          height=4,
                          command=cmd)
            btn.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            tools_grid.columnconfigure(col, weight=1)
            tools_grid.rowconfigure(row, weight=1)
        
        return frame
    
    def setup_footer(self):
        """Barra de estado inferior"""
        footer = tk.Frame(self.main_container, bg=self.colors['bg_secondary'])
        footer.pack(fill=tk.X, pady=(15, 0))
        
        self.footer_status = tk.Label(footer,
                                     text="🟢 Sistema listo • Selecciona tu nivel de energía",
                                     font=('Helvetica Neue', 10),
                                     fg=self.colors['text_secondary'],
                                     bg=self.colors['bg_secondary'])
        self.footer_status.pack(side=tk.LEFT, padx=15, pady=10)
        
        self.version_label = tk.Label(footer,
                                     text="v2.1 • Modo Cerebro Galáctico (Thread-Safe)",
                                     font=('Helvetica Neue', 9),
                                     fg=self.colors['text_muted'],
                                     bg=self.colors['bg_secondary'])
        self.version_label.pack(side=tk.RIGHT, padx=15, pady=10)
        
    # === FUNCIONALIDADES PRINCIPALES ===
    
    def on_energy_change(self):
        """Cuando cambia el nivel de energía seleccionado"""
        level = self.energy_var.get()
        self.energy_matcher.set_energy(level)
        
        # Actualizar UI
        duration = self.energy_matcher.get_recommended_duration()
        self.update_timer_display(duration * 60)
        
        # Actualizar sugerencia en pestaña de tareas
        suggestion = f"💡 Con energía {level.upper()}, recomiendo: "
        if level == 'high':
            suggestion += "tareas difíciles, sesiones de 25 min"
        elif level == 'medium':
            suggestion += "tareas moderadas, sesiones de 15 min"
        elif level == 'low':
            suggestion += "tareas simples, sesiones de 10 min"
        else:
            suggestion += "modo mínimo viable, solo 5 min"
        
        self.suggestion_label.config(text=suggestion)
        self.footer_status.config(text=f"⚡ Energía: {level.upper()} • Duración: {duration} min")
        
    def toggle_timer(self):
        """Inicia o pausa el timer"""
        if self.timer_state == 'idle':
            self.start_session()
        elif self.timer_state == 'running':
            self.pause_session()
        elif self.timer_state == 'paused':
            self.resume_session()
            
    def start_session(self):
        """Inicia una nueva sesión de focus"""
        # Verificar ritual
        ritual_completed = sum(1 for v in self.ritual_checks.values() if v.get())
        if ritual_completed < 2 and self.reward_system.session_count == 0:
            if not messagebox.askyesno("Ritual de Inicio",
                                      f"Solo completaste {ritual_completed}/5 pasos del ritual.\n\n"
                                      "¿Seguro que quieres empezar sin prepararte?"):
                return
        
        # Seleccionar tarea si hay disponibles
        available_tasks = [t for t in self.tasks if not t.get('done')]
        if available_tasks and not self.current_task:
            # Sugerir tarea que match con energía actual
            energy = self.energy_var.get()
            matching = [t for t in available_tasks 
                       if self.energy_matcher.get_task_suggestion(t['difficulty']) == 'match']
            
            if matching:
                self.current_task = matching[0]
            else:
                self.current_task = available_tasks[0]
                
            self.current_task_label.config(
                text=f"📚 {self.current_task['text'][:40]}...",
                fg=self.colors['accent_primary']
            )
        
        # Iniciar body doubling
        companion = self.body_doubling.start_session()
        self.bd_avatar.config(text="👤")
        self.bd_name.config(text=companion['name'])
        self.bd_type.config(text=companion['type'])
        self.bd_message.config(text=companion['msg'])
        
        # Configurar timer
        duration = self.energy_matcher.get_recommended_duration()
        self.total_time = duration * 60
        self.current_time = self.total_time
        self.session_start_time = datetime.now()
        self.pause_count = 0
        
        # Iniciar focus guardian (ahora con cola thread-safe)
        self.focus_guardian = FocusGuardian(self.msg_queue)
        self.focus_guardian.start_monitoring()
        
        # Estado
        self.timer_state = 'running'
        self.btn_main.config(text="⏸ PAUSAR", bg=self.colors['accent_energy'])
        self.status_icon.config(text="🔥")
        self.status_message.config(
            text=f"Modo FLOW activado • {companion['name']} te acompaña",
            fg=self.colors['accent_success']
        )
        self.subtitle_label.config(text="🔥 ENFOQUE ACTIVO")
        
        # Actualizar badge
        self.session_badge.config(text=f"SESION #{self.reward_system.session_count + 1}")
        
        # Iniciar countdown
        self.timer_thread = threading.Thread(target=self.countdown, daemon=True)
        self.timer_thread.start()
        
        # Programar mensajes ambientales de body doubling
        self.schedule_body_doubling_messages()
        
    def countdown(self):
        """Loop del countdown"""
        while self.timer_state == 'running' and self.current_time > 0:
            time.sleep(1)
            if self.timer_state == 'running':
                self.current_time -= 1
                self.root.after(0, self.update_timer_visuals)
        
        if self.current_time <= 0 and self.timer_state == 'running':
            self.root.after(0, self.session_complete)
            
    def update_timer_visuals(self):
        """Actualiza todos los elementos visuales del timer"""
        mins, secs = divmod(self.current_time, 60)
        time_str = f"{mins:02d}:{secs:02d}"
        
        # Texto
        self.timer_canvas.itemconfig(self.timer_text_id, text=time_str)
        
        # Color según tiempo restante
        progress = self.current_time / self.total_time
        if progress > 0.5:
            color = self.colors['accent_success']
        elif progress > 0.25:
            color = self.colors['accent_energy']
        else:
            color = self.colors['accent_urgent']
            
        self.timer_canvas.itemconfig(self.timer_text_id, fill=color)
        
        # Barra de progreso
        self.progress_bar.delete('all')
        bar_width = self.progress_bar.winfo_width()
        fill_width = bar_width * (1 - progress)
        self.progress_bar.create_rectangle(0, 0, fill_width, 8, 
                                          fill=color, outline='')
        
        # Círculo de progreso (sutil)
        self.timer_canvas.delete('progress_ring')
        if progress < 1:
            extent = 360 * progress
            self.timer_canvas.create_arc(50, 50, 350, 350, start=90, 
                                        extent=-extent, style='arc',
                                        outline=color, width=4, tags='progress_ring')
        
    def update_timer_display(self, seconds: int):
        """Actualiza display sin iniciar"""
        mins, secs = divmod(seconds, 60)
        self.timer_canvas.itemconfig(self.timer_text_id, text=f"{mins:02d}:{secs:02d}")
        
    def pause_session(self):
        """Pausa la sesión actual"""
        self.timer_state = 'paused'
        self.pause_count += 1
        self.btn_main.config(text="▶ REANUDAR", bg=self.colors['accent_success'])
        self.status_icon.config(text="⏸")
        self.status_message.config(
            text=f"Pausado • Pausa #{self.pause_count} • Haz click para volver",
            fg=self.colors['accent_energy']
        )
        self.subtitle_label.config(text="⏸ PAUSADO")
        
        if self.focus_guardian:
            self.focus_guardian.stop_monitoring()
            
    def resume_session(self):
        """Reanuda sesión pausada"""
        self.timer_state = 'running'
        self.btn_main.config(text="⏸ PAUSAR", bg=self.colors['accent_energy'])
        self.status_icon.config(text="🔥")
        self.status_message.config(text="¡De vuelta al flow!", fg=self.colors['accent_success'])
        self.subtitle_label.config(text="🔥 ENFOQUE ACTIVO")
        
        if self.focus_guardian:
            self.focus_guardian.start_monitoring()
            
        self.timer_thread = threading.Thread(target=self.countdown, daemon=True)
        self.timer_thread.start()
        
    def reset_timer(self):
        """Reinicia todo"""
        self.timer_state = 'idle'
        self.current_time = 0
        
        if self.focus_guardian:
            self.focus_guardian.stop_monitoring()
            
        self.btn_main.config(text="▶ INICIAR FOCUS", bg=self.colors['accent_success'])
        self.status_icon.config(text="⏳")
        self.status_message.config(text="Listo para tu mejor sesión", 
                                  fg=self.colors['text_secondary'])
        self.subtitle_label.config(text="Modo: Esperando inicio")
        self.current_task_label.config(text="Ninguna tarea seleccionada",
                                      fg=self.colors['text_secondary'])
        self.session_badge.config(text="SESION #0")
        
        # Reset body doubling
        self.bd_avatar.config(text="👤")
        self.bd_name.config(text="Esperando compañero...")
        self.bd_type.config(text="")
        self.bd_message.config(text="")
        
        duration = self.energy_matcher.get_recommended_duration()
        self.update_timer_display(duration * 60)
        self.progress_bar.delete('all')
        self.timer_canvas.delete('progress_ring')
        
    def session_complete(self):
        """Cuando termina una sesión exitosamente"""
        self.timer_state = 'idle'
        
        # Calcular calidad (basada en pausas)
        quality = 1.0 - (self.pause_count * 0.1)
        quality = max(0.5, quality)
        
        # Registrar en sistema de recompensas
        duration_mins = self.total_time // 60
        reward = self.reward_system.register_session(duration_mins, quality)
        
        # Guardar en historial
        session_data = {
            'timestamp': datetime.now().isoformat(),
            'duration': duration_mins,
            'task': self.current_task['text'] if self.current_task else "General",
            'pauses': self.pause_count,
            'quality': quality,
            'energy_level': self.energy_var.get()
        }
        self.sessions_history.append(session_data)
        
        # Actualizar UI
        self.update_stats()
        self.reset_timer()
        
        # Mostrar recompensa
        self.show_reward_popup(reward)
        
        # Marcar tarea como hecha si existe
        if self.current_task:
            self.current_task['done'] = True
            self.render_tasks()
            self.current_task = None
            
        self.save_data()
        
    def show_reward_popup(self, reward: Dict):
        """Muestra popup de recompensa con dopamina"""
        popup = tk.Toplevel(self.root)
        popup.title("¡LOGRO DESBLOQUEADO!")
        popup.geometry("400x300")
        popup.configure(bg=self.colors['bg_secondary'])
        popup.transient(self.root)
        popup.grab_set()
        
        # Animación de entrada
        popup.alpha = 0.0
        def fade_in():
            if popup.alpha < 1.0:
                popup.alpha += 0.1
                popup.attributes('-alpha', popup.alpha)
                popup.after(50, fade_in)
        fade_in()
        
        tk.Label(popup, text=reward['message'], 
                font=('Helvetica Neue', 16, 'bold'),
                fg=self.colors['accent_success'],
                bg=self.colors['bg_secondary'],
                wraplength=350).pack(pady=30)
        
        tk.Label(popup, text=f"Sesión #{reward['session_number']} completada",
                font=('Helvetica Neue', 12),
                fg=self.colors['text_secondary'],
                bg=self.colors['bg_secondary']).pack()
        
        tk.Label(popup, text=f"🔥 Racha actual: {reward['streak']}",
                font=('Helvetica Neue', 14, 'bold'),
                fg=self.colors['accent_energy'],
                bg=self.colors['bg_secondary']).pack(pady=10)
        
        if reward['milestone']:
            tk.Label(popup, text=f"🏆 {reward['milestone']}",
                    font=('Helvetica Neue', 12, 'bold'),
                    fg=self.colors['accent_primary'],
                    bg=self.colors['bg_secondary']).pack(pady=10)
        
        if reward['bonus']:
            tk.Label(popup, text="⭐ SIN PAUSAS: Bonus de concentración!",
                    font=('Helvetica Neue', 11),
                    fg=self.colors['accent_success'],
                    bg=self.colors['bg_secondary']).pack()
        
        tk.Button(popup, text="¡AWESOME! SIGAMOS →",
                 font=('Helvetica Neue', 12, 'bold'),
                 bg=self.colors['accent_success'],
                 fg=self.colors['bg_primary'],
                 command=popup.destroy).pack(pady=20)
        
    def on_distraction_detected(self, level: str, message: str):
        """Callback del Focus Guardian - AHORA SIEMPRE EN HILO PRINCIPAL"""
        self.status_icon.config(text="⚠️")
        self.status_message.config(text=message, fg=self.colors['accent_urgent'])
        
        if level == 'severe':
            # Vibración visual
            self.flash_screen()
            
    def flash_screen(self):
        """Flash de alerta sutil"""
        original_bg = self.root.cget('bg')
        self.root.config(bg=self.colors['accent_urgent'])
        self.root.after(200, lambda: self.root.config(bg=original_bg))
        
    def on_user_activity(self):
        """Registra actividad del usuario para Focus Guardian"""
        if self.focus_guardian:
            self.focus_guardian.register_interaction()
            
    def schedule_body_doubling_messages(self):
        """Programa mensajes ambientales periódicos"""
        if self.timer_state != 'running':
            return
            
        msg = self.body_doubling.get_ambient_message()
        if msg:
            self.bd_message.config(text=msg)
            
        # Siguiente mensaje en 2-4 minutos aleatorio
        next_time = random.randint(120, 240) * 1000
        self.root.after(next_time, self.schedule_body_doubling_messages)
        
    # === GESTIÓN DE TAREAS ===
    
    def add_task(self):
        """Agrega nueva tarea"""
        text = self.task_entry.get().strip()
        if not text:
            messagebox.showwarning("Atención", "Describe la tarea primero")
            return
            
        task = {
            'id': len(self.tasks),
            'text': text,
            'difficulty': self.task_difficulty.get(),
            'done': False,
            'created': datetime.now().isoformat()
        }
        
        self.tasks.append(task)
        self.task_entry.delete(0, tk.END)
        self.render_tasks()
        self.save_data()
        
    def render_tasks(self):
        """Renderiza la lista de tareas"""
        # Limpiar
        for widget in self.tasks_list_frame.winfo_children():
            widget.destroy()
            
        # Ordenar: pendientes primero, luego por dificultad
        sorted_tasks = sorted(self.tasks, 
                            key=lambda x: (x['done'], 
                                         ['high', 'medium', 'low', 'minimal'].index(x['difficulty'])))
        
        for task in sorted_tasks:
            row = tk.Frame(self.tasks_list_frame, bg=self.colors['bg_secondary'])
            row.pack(fill=tk.X, pady=2)
            
            # Estado
            status = "✅" if task['done'] else "⬜"
            tk.Label(row, text=status, width=10,
                    font=('Segoe UI Emoji', 14),
                    bg=self.colors['bg_secondary']).pack(side=tk.LEFT)
            
            # Texto
            fg = self.colors['text_muted'] if task['done'] else self.colors['text_primary']
            tk.Label(row, text=task['text'],
                    font=('Helvetica Neue', 11, 'overstrike' if task['done'] else 'normal'),
                    fg=fg, bg=self.colors['bg_secondary']).pack(side=tk.LEFT, expand=True)
            
            # Dificultad
            color = self.energy_matcher.ENERGY_LEVELS[task['difficulty']]['color']
            tk.Label(row, text=task['difficulty'].upper(),
                    font=('Helvetica Neue', 9, 'bold'),
                    fg=color, bg=self.colors['bg_secondary'],
                    width=12).pack(side=tk.LEFT)
            
            # Acciones
            if not task['done']:
                tk.Button(row, text="ESTUDIAR",
                         font=('Helvetica Neue', 9, 'bold'),
                         bg=self.colors['accent_primary'],
                         fg=self.colors['bg_primary'],
                         cursor='hand2',
                         command=lambda t=task: self.select_task_for_study(t)).pack(side=tk.LEFT, padx=5)
            
            tk.Button(row, text="✓" if not task['done'] else "↺",
                     font=('Helvetica Neue', 10),
                     bg=self.colors['bg_card'],
                     fg=self.colors['accent_success'] if not task['done'] else self.colors['accent_energy'],
                     cursor='hand2',
                     command=lambda t=task: self.toggle_task_done(t)).pack(side=tk.LEFT)
            
    def select_task_for_study(self, task: Dict):
        """Selecciona tarea para estudiar ahora"""
        self.current_task = task
        self.notebook.select(0)  # Ir a focus tab
        self.current_task_label.config(
            text=f"📚 {task['text'][:40]}...",
            fg=self.colors['accent_primary']
        )
        
        # Sugerir energía adecuada
        suggestion = self.energy_matcher.get_task_suggestion(task['difficulty'])
        if suggestion == 'postpone':
            messagebox.showwarning("Energía baja", 
                                  "Esta tarea requiere alta energía y tú estás en modo bajo.\n\n"
                                  "Sugerencia: Haz una tarea más simple primero o toma un descanso.")
        
    def toggle_task_done(self, task: Dict):
        """Marca/desmarca tarea"""
        task['done'] = not task['done']
        self.render_tasks()
        self.save_data()
        
        if task['done']:
            self.celebrate_task_completion()
            
    def celebrate_task_completion(self):
        """Efecto visual de celebración"""
        original = self.tasks_canvas.cget('bg')
        self.tasks_canvas.config(bg=self.colors['accent_success'])
        self.root.after(300, lambda: self.tasks_canvas.config(bg=original))
        
    # === ANALYTICS ===
    
    def update_stats(self):
        """Actualiza todas las estadísticas"""
        stats = self.reward_system.get_stats()
        
        self.stat_cards['sessions'].config(text=str(stats['sessions']))
        self.stat_cards['streak'].config(text=str(stats['current_streak']))
        self.stat_cards['total'].config(text=str(int(stats['total_hours'] * 60)))
        self.stat_cards['best'].config(text=str(stats['best_streak']))
        
        self.mini_stats.config(
            text=f"{stats['sessions']} sesiones • {int(stats['total_hours'] * 60)} min focus"
        )
        
        # Dibujar racha
        self.streak_canvas.delete('all')
        streak = stats['current_streak']
        for i in range(min(streak, 20)):
            x = 30 + i * 45
            y = 30
            self.streak_canvas.create_oval(x-15, y-15, x+15, y+15,
                                          fill=self.colors['accent_success'],
                                          outline=self.colors['accent_primary'],
                                          width=2)
            
        # Actualizar log
        self.log_text.delete(1.0, tk.END)
        for session in reversed(self.sessions_history[-20:]):
            time_str = datetime.fromisoformat(session['timestamp']).strftime("%H:%M")
            quality_str = "⭐" if session['quality'] > 0.9 else ""
            self.log_text.insert(tk.END, 
                               f"[{time_str}] {session['duration']}min {quality_str} - {session['task'][:30]}...\n")
        
    # === HERRAMIENTAS ===
    
    def open_focus_sound(self):
        """Abre sonido de focus"""
        webbrowser.open("https://www.youtube.com/results?search_query=brown+noise+focus+adhd")
        
    def breathing_exercise(self):
        """Ejercicio de respiración rápido"""
        popup = tk.Toplevel(self.root)
        popup.title("Respiración 4-7-8")
        popup.geometry("300x200")
        popup.configure(bg=self.colors['bg_secondary'])
        
        label = tk.Label(popup, text="Inhala... 4", 
                        font=('Helvetica Neue', 24, 'bold'),
                        fg=self.colors['accent_primary'],
                        bg=self.colors['bg_secondary'])
        label.pack(expand=True)
        
        sequence = [('Inhala', 4), ('Mantén', 7), ('Exhala', 8)]
        step = 0
        count = 0
        
        def breathe():
            nonlocal step, count
            action, max_count = sequence[step]
            count += 1
            
            if count > max_count:
                step = (step + 1) % 3
                count = 1
                action, _ = sequence[step]
            
            label.config(text=f"{action}... {count}")
            popup.after(1000, breathe)
            
        breathe()
        
    def active_break(self):
        """Sugiere actividad para descanso"""
        activities = [
            "🚰 Ve por agua y bebe un vaso completo",
            "🧘 Estira brazos arriba 30 segundos",
            "👁️ Mira por la ventana a lo lejos (descanso visual)",
            "🚶 Camina hasta la puerta y regresa",
            "🤲 Masajea tus muñecas 20 segundos"
        ]
        messagebox.showinfo("Descanso Activo", random.choice(activities))
        
    def emergency_mode(self):
        """Modo mínimo viable"""
        if messagebox.askyesno("Modo Emergencia", 
                              "¿Activar modo supervivencia?\n\n"
                              "• Timer: 5 minutos\n"
                              "• Sin presión de completar\n"
                              "• Solo sentarte y empezar"):
            self.energy_var.set('minimal')
            self.on_energy_change()
            self.notebook.select(0)
            messagebox.showinfo("Modo Activado", 
                              "Regla de oro: Solo 5 minutos.\n"
                              "Si quieres parar después, está bien.\n"
                              "Pero probablemente querrás seguir.")
        
    def open_noise_generator(self):
        webbrowser.open("https://mynoise.net/NoiseMachines/cafeRestaurantNoiseGenerator.php")
        
    def breathing_guide(self):
        self.breathing_exercise()
        
    def open_cornell_template(self):
        messagebox.showinfo("Plantilla Cornell", 
                           "Método Cornell para notas:\n\n"
                           "1. Divide página: columna izq (30%), derecha (70%)\n"
                           "2. Durante clase: notas en derecha\n"
                           "3. Después: preguntas/claves en izquierda\n"
                           "4. Abajo: resumen de 2-3 líneas\n\n"
                           "Perfecto para TDAH: estructura clara y revisión eficiente.")
        
    def sleep_calculator(self):
        """Calcula hora de dormir/despertar óptima"""
        now = datetime.now()
        # Ciclos de 90 min, tiempo de quedarse dormido: 15 min
        cycles = [4, 5, 6]  # 6h, 7.5h, 9h
        msg = "Si te duermes AHORA, despierta a las:\n\n"
        for c in cycles:
            wake_time = now + timedelta(minutes=15 + c*90)
            msg += f"• {c*1.5:.1f} horas ({c} ciclos): {wake_time.strftime('%H:%M')}\n"
        messagebox.showinfo("Calculador de Sueño", msg)
        
    def energy_analyzer(self):
        """Analiza patrones de energía"""
        if len(self.sessions_history) < 3:
            messagebox.showinfo("Análisis", "Necesitas al menos 3 sesiones para analizar patrones.")
            return
            
        energy_counts = {}
        for s in self.sessions_history:
            e = s['energy_level']
            energy_counts[e] = energy_counts.get(e, 0) + 1
            
        most_common = max(energy_counts, key=energy_counts.get)
        msg = f"Tu nivel de energía más frecuente: {most_common.upper()}\n\n"
        msg += "Distribución:\n"
        for level, count in sorted(energy_counts.items()):
            bar = "█" * count
            msg += f"{level:8} {bar} ({count})\n"
            
        messagebox.showinfo("Análisis de Energía", msg)
        
    def show_achievements(self):
        """Muestra logros desbloqueados"""
        stats = self.reward_system.get_stats()
        msg = f"🏆 Logros desbloqueados: {stats['achievements']}\n\n"
        for num, name in self.reward_system.MILESTONES.items():
            status = "✅" if num in self.reward_system.achievements_unlocked else "⬜"
            msg += f"{status} {num} sesiones: {name}\n"
        messagebox.showinfo("Tus Logros", msg)
        
    def export_report(self):
        """Exporta reporte semanal"""
        filename = f"studyflow_report_{datetime.now().strftime('%Y%m%d')}.txt"
        with open(filename, 'w') as f:
            f.write("STUDYFLOW TDAH v2.1 - REPORTE SEMANAL\n")
            f.write("=" * 50 + "\n\n")
            
            stats = self.reward_system.get_stats()
            f.write(f"Total sesiones: {stats['sessions']}\n")
            f.write(f"Horas de focus: {stats['total_hours']}\n")
            f.write(f"Mejor racha: {stats['best_streak']}\n")
            f.write(f"Racha actual: {stats['current_streak']}\n\n")
            
            f.write("DETALLE DE SESIONES:\n")
            for s in self.sessions_history:
                date = datetime.fromisoformat(s['timestamp']).strftime("%Y-%m-%d %H:%M")
                f.write(f"{date} | {s['duration']}min | {s['task'][:40]} | {s['energy_level']}\n")
                
        messagebox.showinfo("Exportado", f"Reporte guardado: {filename}")
        
    # === UTILIDADES ===
    
    def apply_theme(self):
        """Aplica tema oscuro completo"""
        self.root.configure(bg=self.colors['bg_primary'])
        
    def save_data(self):
        """Persistencia de datos"""
        data = {
            'tasks': self.tasks,
            'sessions': self.sessions_history,
            'reward_stats': {
                'sessions': self.reward_system.session_count,
                'minutes': self.reward_system.total_focus_minutes,
                'best_streak': self.reward_system.best_streak,
                'achievements': list(self.reward_system.achievements_unlocked)
            },
            'settings': {
                'energy': self.energy_var.get()
            },
            'last_save': datetime.now().isoformat()
        }
        try:
            with open('studyflow_v2_data.json', 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error guardando: {e}")
            
    def load_data(self):
        """Carga datos previos"""
        if os.path.exists('studyflow_v2_data.json'):
            try:
                with open('studyflow_v2_data.json', 'r') as f:
                    data = json.load(f)
                    
                self.tasks = data.get('tasks', [])
                self.sessions_history = data.get('sessions', [])
                
                # Restaurar stats
                rs = data.get('reward_stats', {})
                self.reward_system.session_count = rs.get('sessions', 0)
                self.reward_system.total_focus_minutes = rs.get('minutes', 0)
                self.reward_system.best_streak = rs.get('best_streak', 0)
                self.reward_system.achievements_unlocked = set(rs.get('achievements', []))
                
                # Restaurar settings
                settings = data.get('settings', {})
                if 'energy' in settings:
                    self.energy_var.set(settings['energy'])
                    self.on_energy_change()
                    
                self.render_tasks()
                self.update_stats()
                
            except Exception as e:
                print(f"Error cargando: {e}")
        
    def run(self):
        """Inicia la aplicación"""
        self.root.mainloop()


def main():
    root = tk.Tk()
    app = StudyFlowV2(root)
    app.run()


if __name__ == "__main__":
    main()