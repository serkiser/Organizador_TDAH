#!/usr/bin/env python3
"""
StudyFlow TDAH - Sistema de estudio diseñado para cerebros neurodivergentes
Autor: Asistente Claude
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
import time
import threading
from datetime import datetime, timedelta
import random


class StudyFlowApp:
    def __init__(self, root):
        self.root = root
        self.root.title("StudyFlow TDAH")
        self.root.geometry("900x700")
        self.root.configure(bg='#2b2b2b')
        
        # Variables de estado
        self.timer_running = False
        self.timer_paused = False
        self.current_time = 0
        self.current_session = 0
        self.total_sessions = 0
        self.study_subject = ""
        self.tasks = []
        self.sessions_data = []
        
        # Configuración
        self.config = {
            'work_time': 15,  # minutos
            'short_break': 5,
            'long_break': 30,
            'sessions_before_long_break': 3
        }
        
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """Configura la interfaz con colores amigables para TDAH"""
        # Estilos
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores
        self.colors = {
            'bg': '#2b2b2b',
            'fg': '#ffffff',
            'accent': '#4a9eff',  # Azul calmante
            'success': '#5cb85c',
            'warning': '#f0ad4e',
            'danger': '#d9534f',
            'card': '#3b3b3b'
        }
        
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TButton', font=('Helvetica', 10, 'bold'))
        
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # === HEADER ===
        header = ttk.Frame(main_frame)
        header.pack(fill=tk.X, pady=(0, 20))
        
        title = tk.Label(header, text="🧠 StudyFlow TDAH", 
                        font=('Helvetica', 24, 'bold'),
                        bg=self.colors['bg'], fg=self.colors['accent'])
        title.pack(side=tk.LEFT)
        
        # Modo de emergencia
        emergency_btn = tk.Button(header, text="⚡ Modo Mínimo", 
                                 bg=self.colors['warning'], fg='black',
                                 font=('Helvetica', 10, 'bold'),
                                 command=self.emergency_mode)
        emergency_btn.pack(side=tk.RIGHT)
        
        # === NOTEBOOK (pestañas) ===
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña 1: Timer
        self.timer_tab = self.create_timer_tab()
        self.notebook.add(self.timer_tab, text="⏱️ Timer de Enfoque")
        
        # Pestaña 2: Planificador
        self.planner_tab = self.create_planner_tab()
        self.notebook.add(self.planner_tab, text="📝 Planificador")
        
        # Pestaña 3: Progreso
        self.progress_tab = self.create_progress_tab()
        self.notebook.add(self.progress_tab, text="📊 Mi Progreso")
        
        # Pestaña 4: Config
        self.config_tab = self.create_config_tab()
        self.notebook.add(self.config_tab, text="⚙️ Configuración")
        
    def create_timer_tab(self):
        """Crea la pestaña del timer Pomodoro modificado"""
        frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        
        # Info de sesión
        self.session_info = tk.Label(frame, text="Sesión 0 de 0", 
                                    font=('Helvetica', 12),
                                    bg=self.colors['bg'], fg=self.colors['fg'])
        self.session_info.pack(pady=10)
        
        # Timer circular visual
        timer_frame = tk.Frame(frame, bg=self.colors['bg'])
        timer_frame.pack(pady=20)
        
        self.timer_canvas = tk.Canvas(timer_frame, width=300, height=300, 
                                     bg=self.colors['bg'], highlightthickness=0)
        self.timer_canvas.pack()
        
        self.draw_timer_circle(0)
        
        self.timer_label = tk.Label(timer_frame, text="15:00", 
                                   font=('Helvetica', 48, 'bold'),
                                   bg=self.colors['bg'], fg=self.colors['accent'])
        self.timer_label.place(relx=0.5, rely=0.5, anchor='center')
        
        # Estado
        self.status_label = tk.Label(frame, text="Listo para comenzar", 
                                    font=('Helvetica', 14),
                                    bg=self.colors['bg'], fg=self.colors['success'])
        self.status_label.pack(pady=10)
        
        # Controles
        controls = tk.Frame(frame, bg=self.colors['bg'])
        controls.pack(pady=20)
        
        self.start_btn = tk.Button(controls, text="▶ Iniciar", 
                                  bg=self.colors['success'], fg='white',
                                  font=('Helvetica', 12, 'bold'),
                                  width=12, command=self.start_timer)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.pause_btn = tk.Button(controls, text="⏸ Pausar", 
                                  bg=self.colors['warning'], fg='black',
                                  font=('Helvetica', 12, 'bold'),
                                  width=12, command=self.pause_timer,
                                  state='disabled')
        self.pause_btn.pack(side=tk.LEFT, padx=5)
        
        self.reset_btn = tk.Button(controls, text="↺ Reiniciar", 
                                  bg=self.colors['danger'], fg='white',
                                  font=('Helvetica', 12, 'bold'),
                                  width=12, command=self.reset_timer)
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        
        # Quick actions
        quick_frame = tk.LabelFrame(frame, text="Acciones Rápidas", 
                                   bg=self.colors['card'], fg=self.colors['fg'],
                                   font=('Helvetica', 11))
        quick_frame.pack(fill=tk.X, padx=50, pady=20)
        
        tk.Button(quick_frame, text="🎵 Música Focus (Abrir Spotify/YouTube)", 
                 bg=self.colors['accent'], fg='white',
                 command=lambda: self.open_url("https://www.youtube.com/results?search_query=brown+noise+focus")).pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(quick_frame, text="🚰 Descanso Activo (Ejercicios 2 min)", 
                 bg=self.colors['accent'], fg='white',
                 command=self.show_break_exercises).pack(fill=tk.X, padx=10, pady=5)
        
        return frame
    
    def create_planner_tab(self):
        """Crea el planificador de tareas con chunks"""
        frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        
        # Input de materia
        input_frame = tk.Frame(frame, bg=self.colors['bg'])
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(input_frame, text="📚 Materia/Proyecto:", 
                bg=self.colors['bg'], fg=self.colors['fg'],
                font=('Helvetica', 11)).pack(side=tk.LEFT)
        
        self.subject_entry = tk.Entry(input_frame, font=('Helvetica', 11), width=30)
        self.subject_entry.pack(side=tk.LEFT, padx=10)
        self.subject_entry.bind('<Return>', lambda e: self.add_task())
        
        # Chunk size
        tk.Label(input_frame, text="Tamaño:", 
                bg=self.colors['bg'], fg=self.colors['fg']).pack(side=tk.LEFT)
        self.chunk_size = ttk.Combobox(input_frame, values=["Pequeño (15 min)", 
                                                           "Mediano (30 min)", 
                                                           "Grande (45 min)"], 
                                      width=15, state='readonly')
        self.chunk_size.set("Pequeño (15 min)")
        self.chunk_size.pack(side=tk.LEFT, padx=5)
        
        add_btn = tk.Button(input_frame, text="+ Agregar Chunk", 
                           bg=self.colors['success'], fg='white',
                           command=self.add_task)
        add_btn.pack(side=tk.LEFT, padx=10)
        
        # Lista de tareas
        list_frame = tk.LabelFrame(frame, text="Chunks de Hoy (Máximo 5 recomendado)", 
                                  bg=self.colors['card'], fg=self.colors['fg'],
                                  font=('Helvetica', 12))
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.tasks_listbox = tk.Listbox(list_frame, font=('Helvetica', 11),
                                       bg=self.colors['card'], fg=self.colors['fg'],
                                       selectmode=tk.SINGLE, height=10)
        self.tasks_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.tasks_listbox, orient="vertical", 
                                 command=self.tasks_listbox.yview)
        self.tasks_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Botones de acción
        btn_frame = tk.Frame(frame, bg=self.colors['bg'])
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(btn_frame, text="✓ Marcar como Hecho", 
                 bg=self.colors['success'], fg='white',
                 command=self.complete_task).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="🎯 Estudiar Seleccionado", 
                 bg=self.colors['accent'], fg='white',
                 command=self.study_selected).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="🗑 Eliminar", 
                 bg=self.colors['danger'], fg='white',
                 command=self.delete_task).pack(side=tk.LEFT, padx=5)
        
        # Ritual de inicio
        ritual_frame = tk.LabelFrame(frame, text="Ritual de Inicio (2 minutos)", 
                                    bg=self.colors['card'], fg=self.colors['fg'])
        ritual_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.ritual_check = tk.BooleanVar()
        tk.Checkbutton(ritual_frame, text="☕ Preparé mi bebida/ambiente", 
                      variable=self.ritual_check, 
                      bg=self.colors['card'], fg=self.colors['fg'],
                      selectcolor=self.colors['bg']).pack(anchor=tk.W, padx=10)
        
        tk.Checkbutton(ritual_frame, text="🎵 Puse música/sonido de fondo", 
                      variable=tk.BooleanVar(),
                      bg=self.colors['card'], fg=self.colors['fg'],
                      selectcolor=self.colors['bg']).pack(anchor=tk.W, padx=10)
        
        tk.Checkbutton(ritual_frame, text="📱 Alejé distracciones (modo avión/apps)", 
                      variable=tk.BooleanVar(),
                      bg=self.colors['card'], fg=self.colors['fg'],
                      selectcolor=self.colors['bg']).pack(anchor=tk.W, padx=10)
        
        return frame
    
    def create_progress_tab(self):
        """Crea la visualización de progreso"""
        frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        
        # Estadísticas
        stats_frame = tk.LabelFrame(frame, text="Estadísticas de Hoy", 
                                   bg=self.colors['card'], fg=self.colors['fg'],
                                   font=('Helvetica', 12))
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.stats_text = tk.Label(stats_frame, 
                                  text="Sesiones completadas: 0\nTiempo total: 0 min\nChunks terminados: 0",
                                  bg=self.colors['card'], fg=self.colors['fg'],
                                  font=('Helvetica', 11), justify=tk.LEFT)
        self.stats_text.pack(padx=20, pady=10)
        
        # Visualización de racha
        streak_frame = tk.LabelFrame(frame, text="Racha de Enfoque", 
                                    bg=self.colors['card'], fg=self.colors['fg'])
        streak_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.streak_canvas = tk.Canvas(streak_frame, height=50, 
                                      bg=self.colors['card'], highlightthickness=0)
        self.streak_canvas.pack(fill=tk.X, padx=10, pady=10)
        
        # Log de sesiones
        log_frame = tk.LabelFrame(frame, text="Historial de Sesiones", 
                                 bg=self.colors['card'], fg=self.colors['fg'])
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, 
                                                 bg=self.colors['card'], 
                                                 fg=self.colors['fg'],
                                                 font=('Helvetica', 10),
                                                 height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Botón de exportar
        tk.Button(frame, text="💾 Guardar Reporte", 
                 bg=self.colors['accent'], fg='white',
                 command=self.save_report).pack(pady=10)
        
        return frame
    
    def create_config_tab(self):
        """Configuración del timer"""
        frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        
        config_frame = tk.LabelFrame(frame, text="Configuración de Timer", 
                                    bg=self.colors['card'], fg=self.colors['fg'],
                                    font=('Helvetica', 12))
        config_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Work time
        tk.Label(config_frame, text="Tiempo de enfoque (min):", 
                bg=self.colors['card'], fg=self.colors['fg']).pack(anchor=tk.W, padx=10, pady=5)
        self.work_spin = tk.Spinbox(config_frame, from_=5, to=45, width=10)
        self.work_spin.delete(0, tk.END)
        self.work_spin.insert(0, "15")
        self.work_spin.pack(anchor=tk.W, padx=10)
        
        # Short break
        tk.Label(config_frame, text="Descanso corto (min):", 
                bg=self.colors['card'], fg=self.colors['fg']).pack(anchor=tk.W, padx=10, pady=5)
        self.short_spin = tk.Spinbox(config_frame, from_=1, to=15, width=10)
        self.short_spin.delete(0, tk.END)
        self.short_spin.insert(0, "5")
        self.short_spin.pack(anchor=tk.W, padx=10)
        
        # Long break
        tk.Label(config_frame, text="Descanso largo (min):", 
                bg=self.colors['card'], fg=self.colors['fg']).pack(anchor=tk.W, padx=10, pady=5)
        self.long_spin = tk.Spinbox(config_frame, from_=10, to=60, width=10)
        self.long_spin.delete(0, tk.END)
        self.long_spin.insert(0, "30")
        self.long_spin.pack(anchor=tk.W, padx=10)
        
        # Sessions before long break
        tk.Label(config_frame, text="Sesiones antes de descanso largo:", 
                bg=self.colors['card'], fg=self.colors['fg']).pack(anchor=tk.W, padx=10, pady=5)
        self.sessions_spin = tk.Spinbox(config_frame, from_=2, to=6, width=10)
        self.sessions_spin.delete(0, tk.END)
        self.sessions_spin.insert(0, "3")
        self.sessions_spin.pack(anchor=tk.W, padx=10)
        
        # Save button
        tk.Button(config_frame, text="Guardar Configuración", 
                 bg=self.colors['success'], fg='white',
                 command=self.save_config).pack(pady=20)
        
        # Tips
        tips_frame = tk.LabelFrame(frame, text="💡 Tips para TDAH", 
                                  bg=self.colors['card'], fg=self.colors['fg'])
        tips_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tips_text = """• Si no puedes iniciar, reduce el tiempo a 5 minutos
• Usa el modo mínimo viable en días difíciles
• Celebra cada sesión completada (dopamina!)
• Si te distraes, no te culpes, solo reinicia
• La consistencia vence a la intensidad"""
        
        tk.Label(tips_frame, text=tips_text, 
                bg=self.colors['card'], fg=self.colors['fg'],
                justify=tk.LEFT, font=('Helvetica', 10)).pack(padx=10, pady=10)
        
        return frame
    
    # === FUNCIONALIDADES ===
    
    def draw_timer_circle(self, percentage):
        """Dibuja el círculo de progreso del timer"""
        self.timer_canvas.delete("all")
        x, y = 150, 150
        radius = 120
        
        # Círculo base
        self.timer_canvas.create_oval(x-radius, y-radius, x+radius, y+radius, 
                                     outline='#555555', width=8)
        
        # Arco de progreso
        if percentage > 0:
            extent = 360 * (1 - percentage)
            self.timer_canvas.create_arc(x-radius, y-radius, x+radius, y+radius,
                                        start=90, extent=-extent,
                                        outline=self.colors['accent'], 
                                        width=8, style='arc')
    
    def start_timer(self):
        """Inicia el timer"""
        if not self.timer_running:
            self.timer_running = True
            self.timer_paused = False
            self.start_btn.config(state='disabled')
            self.pause_btn.config(state='normal', text="⏸ Pausar")
            
            if self.current_time == 0:
                self.current_time = int(self.work_spin.get()) * 60
            
            self.status_label.config(text="🔥 Enfoque activo", fg=self.colors['success'])
            self.update_timer()
    
    def update_timer(self):
        """Actualiza el timer cada segundo"""
        if self.timer_running and not self.timer_paused:
            if self.current_time > 0:
                self.current_time -= 1
                mins, secs = divmod(self.current_time, 60)
                self.timer_label.config(text=f"{mins:02d}:{secs:02d}")
                
                total_time = int(self.work_spin.get()) * 60
                percentage = self.current_time / total_time
                self.draw_timer_circle(percentage)
                
                self.root.after(1000, self.update_timer)
            else:
                self.timer_complete()
    
    def pause_timer(self):
        """Pausa o reanuda el timer"""
        if self.timer_paused:
            self.timer_paused = False
            self.pause_btn.config(text="⏸ Pausar")
            self.status_label.config(text="🔥 Enfoque activo", fg=self.colors['success'])
            self.update_timer()
        else:
            self.timer_paused = True
            self.pause_btn.config(text="▶ Reanudar")
            self.status_label.config(text="⏸ Pausado", fg=self.colors['warning'])
    
    def reset_timer(self):
        """Reinicia el timer"""
        self.timer_running = False
        self.timer_paused = False
        self.current_time = int(self.work_spin.get()) * 60
        mins, secs = divmod(self.current_time, 60)
        self.timer_label.config(text=f"{mins:02d}:{secs:02d}")
        self.draw_timer_circle(0)
        self.start_btn.config(state='normal')
        self.pause_btn.config(state='disabled', text="⏸ Pausar")
        self.status_label.config(text="Listo para comenzar", fg=self.colors['success'])
    
    def timer_complete(self):
        """Cuando el timer termina"""
        self.timer_running = False
        self.current_session += 1
        
        # Sonido (beep del sistema)
        self.root.bell()
        
        # Registrar sesión
        now = datetime.now().strftime("%H:%M")
        self.sessions_data.append({
            'time': now,
            'duration': self.work_spin.get(),
            'subject': self.study_subject or "General"
        })
        
        # Determinar tipo de descanso
        if self.current_session % int(self.sessions_spin.get()) == 0:
            break_time = self.long_spin.get()
            msg = f"¡{self.current_session} sesiones! Descanso largo de {break_time} min 🎉"
            self.status_label.config(text=msg, fg=self.colors['accent'])
        else:
            break_time = self.short_spin.get()
            msg = f"¡Sesión {self.current_session} completa! Descanso de {break_time} min ✓"
            self.status_label.config(text=msg, fg=self.colors['success'])
        
        self.update_stats()
        self.reset_timer()
        messagebox.showinfo("¡Tiempo completado!", 
                           f"Tomate un descanso de {break_time} minutos.\n\nRecuerda: Levántate, estira, hidrátate. ¡No abras el celular!")
    
    def add_task(self):
        """Agrega un chunk a la lista"""
        subject = self.subject_entry.get().strip()
        if not subject:
            messagebox.showwarning("Atención", "Escribe qué vas a estudiar")
            return
        
        chunk = self.chunk_size.get()
        task_text = f"[ ] {subject} - {chunk}"
        self.tasks_listbox.insert(tk.END, task_text)
        self.tasks.append({'subject': subject, 'chunk': chunk, 'done': False})
        self.subject_entry.delete(0, tk.END)
        self.save_data()
    
    def complete_task(self):
        """Marca tarea como completada"""
        selection = self.tasks_listbox.curselection()
        if selection:
            idx = selection[0]
            text = self.tasks_listbox.get(idx)
            if text.startswith("[ ]"):
                new_text = text.replace("[ ]", "[✓]", 1)
                self.tasks_listbox.delete(idx)
                self.tasks_listbox.insert(idx, new_text)
                if idx < len(self.tasks):
                    self.tasks[idx]['done'] = True
                self.save_data()
                # Pequeña celebración visual
                self.celebrate_completion()
    
    def celebrate_completion(self):
        """Efecto visual de celebración"""
        original_bg = self.tasks_listbox.cget('bg')
        self.tasks_listbox.config(bg=self.colors['success'])
        self.root.after(300, lambda: self.tasks_listbox.config(bg=original_bg))
    
    def delete_task(self):
        """Elimina tarea seleccionada"""
        selection = self.tasks_listbox.curselection()
        if selection:
            idx = selection[0]
            self.tasks_listbox.delete(idx)
            if idx < len(self.tasks):
                self.tasks.pop(idx)
            self.save_data()
    
    def study_selected(self):
        """Carga la tarea seleccionada en el timer"""
        selection = self.tasks_listbox.curselection()
        if selection:
            idx = selection[0]
            if idx < len(self.tasks):
                self.study_subject = self.tasks[idx]['subject']
                self.notebook.select(0)  # Ir a timer
                self.status_label.config(text=f"Estudiando: {self.study_subject}", 
                                       fg=self.colors['accent'])
    
    def emergency_mode(self):
        """Modo mínimo viable para días difíciles"""
        response = messagebox.askyesno("Modo Mínimo Viable", 
                                      "¿Activar modo de emergencia?\n\n"
                                      "• Timer reducido a 10 minutos\n"
                                      "• Solo 1 chunk objetivo\n"
                                      "• Sin presión de completar todo")
        if response:
            self.work_spin.delete(0, tk.END)
            self.work_spin.insert(0, "10")
            self.reset_timer()
            messagebox.showinfo("Modo Activado", 
                              "Objetivo: Solo hacer el 10%.\n\n"
                              "Recuerda: Es mejor 10 minutos reales que 0 minutos perfectos.")
    
    def show_break_exercises(self):
        """Muestra ejercicios para descanso activo"""
        exercises = [
            "🧘 Respiración 4-7-8: Inhala 4s, mantén 7s, exhala 8s",
            "🚶 Camina hasta la cocina y bebe un vaso de agua",
            "🙆‍♂️ Estiramientos de cuello y hombros (30s cada lado)",
            "👁️ Mira por la ventana a 6 metros de distancia (descanso visual)",
            "🦶 Levanta los talones 10 veces (activación sanguínea)"
        ]
        msg = "Descanso Activo (2 min):\n\n" + random.choice(exercises)
        messagebox.showinfo("Descanso Estructurado", msg)
    
    def update_stats(self):
        """Actualiza las estadísticas"""
        total_sessions = len(self.sessions_data)
        total_time = sum(int(s['duration']) for s in self.sessions_data)
        completed_tasks = sum(1 for t in self.tasks if t.get('done'))
        
        stats = f"Sesiones completadas: {total_sessions}\n"
        stats += f"Tiempo total: {total_time} minutos\n"
        stats += f"Chunks terminados: {completed_tasks}/{len(self.tasks)}"
        self.stats_text.config(text=stats)
        
        # Actualizar log
        self.log_text.delete(1.0, tk.END)
        for session in self.sessions_data[-10:]:  # Últimas 10
            self.log_text.insert(tk.END, 
                               f"{session['time']} - {session['duration']}min - {session['subject']}\n")
        
        # Dibujar racha
        self.draw_streak()
        self.save_data()
    
    def draw_streak(self):
        """Dibuja visualización de racha"""
        self.streak_canvas.delete("all")
        width = self.streak_canvas.winfo_width()
        circles = min(len(self.sessions_data), 10)
        spacing = width / (circles + 1) if circles > 0 else width / 2
        
        for i in range(circles):
            x = spacing * (i + 1)
            y = 25
            self.streak_canvas.create_oval(x-10, y-10, x+10, y+10, 
                                          fill=self.colors['success'], 
                                          outline=self.colors['accent'], width=2)
    
    def save_config(self):
        """Guarda configuración"""
        self.config = {
            'work_time': self.work_spin.get(),
            'short_break': self.short_spin.get(),
            'long_break': self.long_spin.get(),
            'sessions_before_long_break': self.sessions_spin.get()
        }
        self.save_data()
        messagebox.showinfo("Guardado", "Configuración actualizada")
    
    def save_data(self):
        """Guarda datos en archivo JSON"""
        data = {
            'config': self.config,
            'tasks': self.tasks,
            'sessions': self.sessions_data,
            'last_date': datetime.now().strftime("%Y-%m-%d")
        }
        try:
            with open('studyflow_data.json', 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error guardando: {e}")
    
    def load_data(self):
        """Carga datos previos"""
        if os.path.exists('studyflow_data.json'):
            try:
                with open('studyflow_data.json', 'r') as f:
                    data = json.load(f)
                
                # Verificar si es un nuevo día
                last_date = data.get('last_date', '')
                today = datetime.now().strftime("%Y-%m-%d")
                
                if last_date == today:
                    self.config = data.get('config', self.config)
                    self.tasks = data.get('tasks', [])
                    self.sessions_data = data.get('sessions', [])
                    
                    # Cargar tasks en listbox
                    for task in self.tasks:
                        status = "[✓]" if task.get('done') else "[ ]"
                        self.tasks_listbox.insert(tk.END, 
                                                f"{status} {task['subject']} - {task['chunk']}")
                    
                    self.update_stats()
                else:
                    # Nuevo día, resetear sesiones pero mantener config
                    self.config = data.get('config', self.config)
                    
            except Exception as e:
                print(f"Error cargando: {e}")
    
    def save_report(self):
        """Guarda reporte diario en texto"""
        filename = f"reporte_{datetime.now().strftime('%Y-%m-%d')}.txt"
        with open(filename, 'w') as f:
            f.write(f"StudyFlow Reporte - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write("="*50 + "\n\n")
            f.write(f"Sesiones completadas: {len(self.sessions_data)}\n")
            f.write(f"Tiempo total: {sum(int(s['duration']) for s in self.sessions_data)} min\n\n")
            f.write("Sesiones:\n")
            for s in self.sessions_data:
                f.write(f"  {s['time']} - {s['duration']}min - {s['subject']}\n")
            f.write("\nChunks completados:\n")
            for t in self.tasks:
                if t.get('done'):
                    f.write(f"  ✓ {t['subject']}\n")
        
        messagebox.showinfo("Reporte Guardado", f"Guardado como: {filename}")
    
    def open_url(self, url):
        """Abre URL en navegador"""
        import webbrowser
        webbrowser.open(url)


def main():
    root = tk.Tk()
    app = StudyFlowApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()