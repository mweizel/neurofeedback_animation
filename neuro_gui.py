import tkinter as tk
from tkinter import ttk
import random
import time
import math

# Try importing pygame for audio
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("Warning: 'pygame' not found. Audio will be disabled. Run 'pip install pygame'")

class AudioController:
    def __init__(self):
        self.enabled = False
        if PYGAME_AVAILABLE:
            pygame.mixer.init()
            # PLACEHOLDERS: In a real scenario, load your files here
            # self.bg_channel = pygame.mixer.Channel(0)
            # self.sfx_tree = pygame.mixer.Sound("tree_grow.wav") 
            pass

    def start_bg_music(self):
        if PYGAME_AVAILABLE and self.enabled:
            # pygame.mixer.music.load("relaxing_drone.mp3")
            # pygame.mixer.music.play(-1) # Loop
            pass

    def set_volume(self, level):
        # Level is 0.0 to 1.0. 
        # Map signal strength to volume
        if PYGAME_AVAILABLE and self.enabled:
            pygame.mixer.music.set_volume(max(0.1, level))

    def play_event(self, event_type):
        if PYGAME_AVAILABLE and self.enabled:
            if event_type == "tree":
                # self.sfx_tree.play()
                pass

class NeurofeedbackApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NeuroFeedback Training Module v2.0")
        self.root.geometry("1100x750")

        self.audio = AudioController()

        # --- Configuration ---
        self.settings = {
            "threshold": 0.5,
            "training_time_min": 5,
            "sim_mode": False, 
            "combo_enabled": True,
            "randomness": 0.2,
            
            # NEW SETTINGS
            "base_points_per_sec": 5,    # Slower default points
            "smoothing_factor": 0.05,    # Low Pass Filter (0.01 = very slow, 1.0 = instant)
            "audio_enabled": False,
        }
        
        # State Variables
        self.running = False
        self.start_time = 0
        self.score = 0
        self.score_velocity = 0 # For momentum effect
        
        self.raw_signal = 0.0      # Instant input (mouse or EEG)
        self.smooth_signal = 0.0   # Averaged value for transitions
        self.world_health = 0.0    # 0.0 (Dead) to 1.0 (Lush)
        
        self.consecutive_green_time = 0
        self.last_update_time = time.time()
        
        # Animation Objects
        self.plants = [] # List of dicts: {'type': 'flower'|'tree', 'x', 'y', 'size', 'max_size', 'color'}

        self.setup_ui()
        self.update_loop()

    def setup_ui(self):
        # Control Panel
        control_frame = tk.Frame(self.root, pady=10, padx=10, bg="#dddddd")
        control_frame.pack(fill=tk.X)

        # Standard Controls
        tk.Label(control_frame, text="Time (min):", bg="#dddddd").pack(side=tk.LEFT)
        self.time_entry = tk.Entry(control_frame, width=5)
        self.time_entry.insert(0, "5")
        self.time_entry.pack(side=tk.LEFT, padx=5)

        self.btn_start = tk.Button(control_frame, text="START", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), command=self.toggle_start)
        self.btn_start.pack(side=tk.LEFT, padx=15)
        
        tk.Button(control_frame, text="Advanced Settings", command=self.open_settings).pack(side=tk.LEFT)

        # Signal Simulator (Hidden by default)
        self.sim_frame = tk.Frame(control_frame, bg="#dddddd")
        tk.Label(self.sim_frame, text="Simulate Signal:", bg="#dddddd", fg="red").pack(side=tk.LEFT, padx=10)
        self.sim_slider = tk.Scale(self.sim_frame, from_=0, to=1, resolution=0.01, orient=tk.HORIZONTAL, length=200, command=self.on_slider_move)
        self.sim_slider.set(0.0)
        self.sim_slider.pack(side=tk.LEFT)

        # Main Canvas
        self.canvas = tk.Canvas(self.root, bg="#333")
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def on_slider_move(self, val):
        self.raw_signal = float(val)

    def open_settings(self):
        win = tk.Toplevel(self.root)
        win.title("Advanced Settings")
        win.geometry("400x450")

        def add_scale(label, key, from_, to_, res):
            frame = tk.Frame(win, pady=5)
            frame.pack(fill=tk.X, padx=10)
            tk.Label(frame, text=label, width=25, anchor='w').pack(side=tk.LEFT)
            val = tk.DoubleVar(value=self.settings[key])
            s = tk.Scale(frame, from_=from_, to=to_, resolution=res, orient=tk.HORIZONTAL, variable=val)
            s.pack(side=tk.RIGHT, fill=tk.X, expand=True)
            return key, val

        controls = []
        controls.append(add_scale("Threshold (0-1):", "threshold", 0, 1, 0.05))
        controls.append(add_scale("Smoothing (Bandwidth):", "smoothing_factor", 0.01, 0.3, 0.01))
        controls.append(add_scale("Base Points / sec:", "base_points_per_sec", 1, 50, 1))
        
        # Checkboxes
        c_frame = tk.Frame(win, pady=10)
        c_frame.pack()
        v_sim = tk.BooleanVar(value=self.settings["sim_mode"])
        tk.Checkbutton(c_frame, text="Enable Sim Slider", variable=v_sim).pack(anchor='w')
        
        v_audio = tk.BooleanVar(value=self.settings["audio_enabled"])
        tk.Checkbutton(c_frame, text="Enable Audio", variable=v_audio).pack(anchor='w')

        def save():
            for key, val in controls:
                self.settings[key] = val.get()
            
            self.settings["sim_mode"] = v_sim.get()
            self.settings["audio_enabled"] = v_audio.get()
            self.audio.enabled = v_audio.get()

            if self.settings["sim_mode"]:
                self.sim_frame.pack(side=tk.LEFT)
            else:
                self.sim_frame.pack_forget()
            win.destroy()

        tk.Button(win, text="Save & Close", command=save, bg="#ccc").pack(pady=20)

    def toggle_start(self):
        if not self.running:
            try:
                mins = float(self.time_entry.get())
            except: mins = 5
            self.start_time = time.time()
            self.total_time_sec = mins * 60
            self.score = 0
            self.plants = [] 
            self.smooth_signal = 0.0 # Reset smoothing
            self.consecutive_green_time = 0
            self.running = True
            self.btn_start.config(text="STOP", bg="#f44336")
            self.audio.start_bg_music()
        else:
            self.running = False
            self.btn_start.config(text="START", bg="#4CAF50")
            if PYGAME_AVAILABLE: pygame.mixer.music.stop()

    def lerp_color(self, c1, c2, t):
        """Linear interpolation between two RGB tuples."""
        return (
            int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t)
        )

    def rgb_to_hex(self, rgb):
        return "#%02x%02x%02x" % rgb

    def update_loop(self):
        now = time.time()
        dt = now - self.last_update_time
        self.last_update_time = now

        if self.running:
            elapsed = now - self.start_time
            remaining = max(0, self.total_time_sec - elapsed)
            if remaining == 0: self.toggle_start()

            # --- 1. Signal Smoothing (Low Pass Filter) ---
            # This creates the "Transition Phase" you requested.
            alpha = self.settings["smoothing_factor"]
            # Logic: New = Old + alpha * (Target - Old)
            self.smooth_signal = self.smooth_signal + alpha * (self.raw_signal - self.smooth_signal)

            # Determine "Health" of the world (0.0 to 1.0) relative to threshold
            # If we are way below threshold, health is 0. If above, it scales to 1.
            threshold = self.settings["threshold"]
            
            # Create a soft transition range around the threshold
            if self.smooth_signal < (threshold - 0.1):
                target_health = 0.0
            elif self.smooth_signal > threshold:
                target_health = 1.0
            else:
                # In the transition zone
                target_health = 0.5

            # Smooth the health metric too for visual changes
            self.world_health = self.world_health + (2.0 * dt) * (target_health - self.world_health)
            self.world_health = max(0.0, min(1.0, self.world_health))

            is_above_threshold = self.smooth_signal > threshold

            # --- 2. Scoring Momentum ---
            # If green, accelerate point gain. If red, decelerate.
            target_velocity = 0
            if is_above_threshold:
                target_velocity = self.settings["base_points_per_sec"]
                self.consecutive_green_time += dt
            else:
                target_velocity = 0
                self.consecutive_green_time = 0
            
            # Smooth velocity change (Momentum)
            self.score_velocity += (target_velocity - self.score_velocity) * (1.0 * dt)
            self.score += self.score_velocity * dt

            # --- 3. Audio Update ---
            self.audio.set_volume(self.world_health)

            # --- 4. Render Scene ---
            self.draw_scene(dt)
            self.draw_hud(remaining)
        
        else:
            self.canvas.delete("all")
            self.canvas.create_text(550, 350, text="Ready", fill="white", font=("Arial", 30))

        self.root.after(33, self.update_loop)

    def draw_scene(self, dt):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        # --- A. Background Transition ---
        # Color Palettes (RGB)
        sky_dead = (100, 100, 110)
        sky_alive = (135, 206, 235)
        grass_dead = (101, 67, 33)
        grass_alive = (34, 139, 34)

        current_sky = self.lerp_color(sky_dead, sky_alive, self.world_health)
        current_grass = self.lerp_color(grass_dead, grass_alive, self.world_health)

        # Draw Background
        self.canvas.create_rectangle(0, 0, w, h*0.7, fill=self.rgb_to_hex(current_sky), outline="")
        self.canvas.create_rectangle(0, h*0.7, w, h, fill=self.rgb_to_hex(current_grass), outline="")

        # --- B. Spawning Logic ---
        # Only spawn if the world is "healthy" (above thresholdish)
        if self.world_health > 0.8:
            
            # Flower Spawn (Common)
            if random.random() < 0.05: 
                self.plants.append({
                    'type': 'flower',
                    'x': random.randint(20, w-20),
                    'y': random.randint(int(h*0.7) + 20, h-10),
                    'size': 0.1,
                    'max_size': random.uniform(0.8, 1.2),
                    'color': random.choice(["red", "white", "yellow", "orange"]),
                    'growth_speed': 0.5
                })
            
            # Tree Spawn (Rare OR Sustained Effort)
            # High chance if held for 10s, Low chance randomly
            spawn_tree = False
            if self.consecutive_green_time > 10 and random.random() < 0.05:
                spawn_tree = True
                self.consecutive_green_time = 0 # Consume the "charge" or keep it? Let's consume slightly to space trees
            elif random.random() < 0.001: # 0.1% chance random spawn
                spawn_tree = True
            
            if spawn_tree:
                self.plants.append({
                    'type': 'tree',
                    'x': random.randint(50, w-50),
                    'y': int(h*0.7) + 20, # Trees rooted at horizon
                    'size': 0.1,
                    'max_size': random.uniform(2.0, 3.5), # Trees are big
                    'color': "forestgreen",
                    'growth_speed': 0.2 # Trees grow slow
                })
                self.audio.play_event("tree")

        # --- C. Draw Plants ---
        # Sort by Y so lower plants are drawn on top (perspective)
        self.plants.sort(key=lambda p: p['y'])

        for p in self.plants:
            # Grow logic: Only grow if world is healthy
            if self.world_health > 0.5 and p['size'] < p['max_size']:
                p['size'] += p['growth_speed'] * dt

            # Draw Logic
            scale = p['size']
            
            if p['type'] == 'flower':
                stem_h = 20 * scale
                # Stem
                self.canvas.create_line(p['x'], p['y'], p['x'], p['y']-stem_h, fill="darkgreen", width=2)
                # Petals
                r = 6 * scale
                self.canvas.create_oval(p['x']-r, p['y']-stem_h-r, p['x']+r, p['y']-stem_h+r, fill=p['color'], outline="")
            
            elif p['type'] == 'tree':
                trunk_w = 10 * scale
                trunk_h = 60 * scale
                foliage_r = 30 * scale
                
                # Trunk
                self.canvas.create_rectangle(p['x']-trunk_w/2, p['y'], p['x']+trunk_w/2, p['y']-trunk_h, fill="#5D4037", outline="")
                # Foliage (Circle)
                self.canvas.create_oval(p['x']-foliage_r, p['y']-trunk_h-foliage_r, p['x']+foliage_r, p['y']-trunk_h+foliage_r, fill=p['color'], outline="")

    def draw_hud(self, remaining):
        # Time
        mins, secs = divmod(int(remaining), 60)
        self.canvas.create_text(1050, 30, text=f"{mins:02}:{secs:02}", font=("Courier", 18, "bold"), fill="white", anchor="e")
        
        # Score
        self.canvas.create_text(50, 30, text=f"Points: {int(self.score)}", font=("Courier", 18, "bold"), fill="white", anchor="w")
        
        # Signal Bar (Visual Debug + Patient Feedback)
        # Draw a bar that shows smoothed signal
        bar_w = 200
        bar_h = 10
        x_start = 50
        y_start = 60
        
        # Background bar
        self.canvas.create_rectangle(x_start, y_start, x_start+bar_w, y_start+bar_h, fill="#555", outline="")
        
        # Fill bar
        fill_w = bar_w * self.smooth_signal
        # Color changes based on threshold
        fill_col = "green" if self.smooth_signal > self.settings["threshold"] else "orange"
        self.canvas.create_rectangle(x_start, y_start, x_start+fill_w, y_start+bar_h, fill=fill_col, outline="")
        
        # Threshold Marker
        thresh_x = x_start + (bar_w * self.settings["threshold"])
        self.canvas.create_line(thresh_x, y_start-5, thresh_x, y_start+bar_h+5, fill="white", width=2)


if __name__ == "__main__":
    root = tk.Tk()
    app = NeurofeedbackApp(root)
    root.mainloop()