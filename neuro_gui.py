import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
import math

# ==========================================
# 1. AUDIO SYSTEM (Robust & Safe)
# ==========================================
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("WARNING: 'pygame' not found. Install it via 'pip install pygame' for sound.")

class AudioController:
    def __init__(self):
        self.enabled = False
        self.mixer_initialized = False
        
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init()
                self.mixer_initialized = True
                # PLACEHOLDER: Uncomment these lines if you have actual files
                # self.snd_coin = pygame.mixer.Sound("coin.wav")
                # self.snd_tree = pygame.mixer.Sound("tree.wav")
            except Exception as e:
                print(f"Audio Error: {e}")

    def update_ambient(self, world_health):
        """Adjusts background volume based on how 'lush' the world is."""
        if self.mixer_initialized and self.enabled:
            # Example: Volume rises as you get deeper into the 'green' state
            # pygame.mixer.music.set_volume(max(0.1, world_health))
            pass

    def play_event(self, event_type):
        """Plays specific sound effects."""
        if self.mixer_initialized and self.enabled:
            if event_type == "coin":
                # if self.snd_coin: self.snd_coin.play()
                pass
            elif event_type == "tree":
                # if self.snd_tree: self.snd_tree.play()
                print("Audio: *Tree Grow Sound*")

# ==========================================
# 2. DATA ABSTRACTION LAYER
# ==========================================
class DataStream:
    """
    Handles where the signal comes from.
    Encapsulates the logic so the GUI doesn't get messy.
    """
    MODE_MANUAL = "Manual (Mouse)"
    MODE_SYNTHETIC = "Synthetic (Demo Wave)"
    MODE_HARDWARE = "Real EEG (BrainFlow)"

    def __init__(self):
        self.mode = self.MODE_MANUAL
        self.manual_value = 0.0
        self.start_time = time.time()
        self.board = None # Placeholder for BrainFlow board object

    def set_manual_input(self, val):
        self.manual_value = float(val)

    def get_current_signal(self):
        """Returns float 0.0 to 1.0"""
        if self.mode == self.MODE_MANUAL:
            return self.manual_value
            
        elif self.mode == self.MODE_SYNTHETIC:
            # Create a gentle sine wave to simulate a breathing brain
            # Period: 4 seconds
            elapsed = time.time() - self.start_time
            val = 0.5 + 0.35 * math.sin(elapsed * 1.5)
            return max(0.0, min(1.0, val))
            
        elif self.mode == self.MODE_HARDWARE:
            # FUTURE BRAINFLOW CODE GOES HERE
            return 0.0
            
        return 0.0

# ==========================================
# 3. VISUAL HELPERS
# ==========================================
def lerp_color(c1, c2, t):
    """Linearly interpolates between color c1 and c2 by factor t (0.0-1.0)"""
    t = max(0.0, min(1.0, t))
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t)
    )

def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % rgb

# ==========================================
# 4. SCENARIOS (Modular Design)
# ==========================================
class ScenarioBase:
    def __init__(self, name):
        self.name = name
        self.settings = {} # Exposed to the Advanced Settings panel
    
    def start(self): 
        """Called when Start is pressed"""
        pass
    
    def update(self, dt, world_health, signal, audio_ctrl): 
        """Called every frame to update logic"""
        pass
    
    def draw(self, canvas, w, h, world_health): 
        """Called every frame to draw pixels"""
        pass
    
    def get_settings_panel(self, parent):
        """Returns a TK Frame with specific sliders"""
        return tk.Label(parent, text="No settings available.")

class NatureScenario(ScenarioBase):
    def __init__(self):
        super().__init__("Nature Restoration")
        # These are the knobs you can turn in the settings menu
        self.settings = {
            "tree_probability": 0.005,
            "flower_speed": 0.8
        }
        self.plants = []
        
        # Defining the Color Transitions
        self.sky_dead = (100, 100, 110)   # Grey/Stormy
        self.sky_alive = (135, 206, 235)  # Sky Blue
        self.grass_dead = (101, 67, 33)   # Mud/Dead
        self.grass_alive = (34, 139, 34)  # Lush Green

    def start(self):
        self.plants = []

    def update(self, dt, world_health, signal, audio_ctrl):
        # 1. Spawning Logic
        if world_health > 0.6:
            # Flowers (Frequent)
            if random.random() < 0.05:
                self.plants.append(self._create_plant('flower', world_health))
            
            # Trees (Rare - controlled by settings)
            if random.random() < self.settings["tree_probability"]:
                self.plants.append(self._create_plant('tree', world_health))
                audio_ctrl.play_event("tree") # Trigger sound

        # 2. Growth Logic
        for p in self.plants:
            # Plants only grow if the world is healthy
            if world_health > 0.4 and p['size'] < p['max_size']:
                p['size'] += self.settings["flower_speed"] * dt

        # 3. Cleanup (Performance)
        if len(self.plants) > 300:
            self.plants.pop(0)

    def _create_plant(self, p_type, health):
        """Helper to generate plant data structures"""
        return {
            'type': p_type,
            'x': random.randint(0, 1200),
            'y': random.randint(400, 800), # Horizon area
            'size': 0.1,
            'max_size': random.uniform(0.8, 1.2) if p_type == 'flower' else random.uniform(2.5, 4.0),
            'color': random.choice(["red", "white", "yellow", "purple", "orange"]) if p_type == 'flower' else "forestgreen"
        }

    def draw(self, canvas, w, h, world_health):
        # A. Draw Background (Lerp Colors)
        curr_sky = lerp_color(self.sky_dead, self.sky_alive, world_health)
        curr_grass = lerp_color(self.grass_dead, self.grass_alive, world_health)
        
        # Sky
        canvas.create_rectangle(0, 0, w, h*0.6, fill=rgb_to_hex(curr_sky), outline="")
        # Grass
        canvas.create_rectangle(0, h*0.6, w, h, fill=rgb_to_hex(curr_grass), outline="")
        
        # Sun (gets brighter and more yellow)
        sun_col = lerp_color((150, 150, 150), (255, 215, 0), world_health)
        canvas.create_oval(w-150, 50, w-50, 150, fill=rgb_to_hex(sun_col), outline="")

        # B. Draw Plants (Sorted by Y for depth)
        self.plants.sort(key=lambda p: p['y'])
        
        for p in self.plants:
            # Clamp X to screen width (handles window resizing)
            px = p['x'] % w 
            py = p['y']
            
            # Ensure plants stay on the ground area
            if py > h: py = h - 10
            if py < h*0.6: py = int(h*0.6) + 10

            scale = p['size']
            
            if p['type'] == 'flower':
                stem_h = 25 * scale
                # Draw Stem
                canvas.create_line(px, py, px, py-stem_h, fill="darkgreen", width=2)
                # Draw Petals
                r = 8 * scale
                canvas.create_oval(px-r, py-stem_h-r, px+r, py-stem_h+r, fill=p['color'], outline="")
            
            elif p['type'] == 'tree':
                trunk_w = 15 * scale
                trunk_h = 80 * scale
                foliage = 40 * scale
                # Draw Trunk
                canvas.create_rectangle(px-trunk_w/2, py, px+trunk_w/2, py-trunk_h, fill="#5D4037", outline="")
                # Draw Foliage
                canvas.create_oval(px-foliage, py-trunk_h-foliage, px+foliage, py-trunk_h+foliage, fill=p['color'], outline="")

    def get_settings_panel(self, parent):
        f = tk.Frame(parent)
        tk.Label(f, text="Nature Scenario Options", font=("bold", 10)).pack(anchor="w", pady=5)
        
        tk.Label(f, text="Tree Spawn Probability:").pack(anchor="w")
        s1 = tk.Scale(f, from_=0.0, to=0.03, resolution=0.001, orient=tk.HORIZONTAL)
        s1.set(self.settings["tree_probability"])
        s1.pack(fill=tk.X)
        s1.config(command=lambda v: self.settings.update({"tree_probability": float(v)}))

        tk.Label(f, text="Flower Growth Speed:").pack(anchor="w")
        s2 = tk.Scale(f, from_=0.1, to=3.0, resolution=0.1, orient=tk.HORIZONTAL)
        s2.set(self.settings["flower_speed"])
        s2.pack(fill=tk.X)
        s2.config(command=lambda v: self.settings.update({"flower_speed": float(v)}))
        return f

class FlightScenario(ScenarioBase):
    def __init__(self):
        super().__init__("Flight Mode")
        self.y = 300
    
    def update(self, dt, health, sig, audio_ctrl):
        # Plane seeks altitude based on health
        target = 600 - (500 * health)
        # Smooth movement
        self.y += (target - self.y) * 2 * dt
    
    def draw(self, canvas, w, h, health):
        canvas.create_rectangle(0,0,w,h, fill="#87CEEB", outline="")
        # Simple plane representation
        canvas.create_text(w/2, self.y, text="✈️", font=("Arial", 60))
        # Clouds
        canvas.create_text(w*0.2, 100, text="☁️", font=("Arial", 40), fill="white")
        canvas.create_text(w*0.8, 150, text="☁️", font=("Arial", 40), fill="white")

# ==========================================
# 5. MAIN ENGINE
# ==========================================
class NeurofeedbackApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NeuroFeedback Training v6.0 (Stable)")
        self.root.geometry("1000x700")

        # Subsystems
        self.audio = AudioController()
        self.stream = DataStream()

        # Configuration
        self.scenarios = [NatureScenario(), FlightScenario()]
        self.current_scenario = self.scenarios[0]
        
        self.settings = {
            "threshold": 0.5,
            "smoothing": 0.05,  # The "Bandwidth" setting
            "base_points": 10,
            "audio_enabled": False,
        }

        # Session State
        self.running = False
        self.start_time = 0
        self.total_time = 300 
        
        # Real-time Data
        self.raw_signal = 0.0
        self.smooth_signal = 0.0
        self.world_health = 0.0
        
        # Scoring
        self.score = 0.0
        self.score_velocity = 0.0

        self.last_update_time = time.time()
        self.setup_ui()
        self.update_loop()

    def setup_ui(self):
        # -- Control Bar --
        ctrl = tk.Frame(self.root, bg="#eee", pady=10, padx=10, relief=tk.RAISED, bd=2)
        ctrl.pack(fill=tk.X)

        # 1. Scenario Dropdown
        tk.Label(ctrl, text="Scenario:", bg="#eee").pack(side=tk.LEFT)
        self.scn_var = tk.StringVar(value=self.current_scenario.name)
        cb = ttk.Combobox(ctrl, textvariable=self.scn_var, values=[s.name for s in self.scenarios], state="readonly", width=18)
        cb.bind("<<ComboboxSelected>>", self.change_scenario)
        cb.pack(side=tk.LEFT, padx=5)

        # 2. Time Input
        tk.Label(ctrl, text="Time (min):", bg="#eee").pack(side=tk.LEFT, padx=5)
        self.entry_time = tk.Entry(ctrl, width=5)
        self.entry_time.insert(0, "5")
        self.entry_time.pack(side=tk.LEFT)

        # 3. Start Button
        self.btn_start = tk.Button(ctrl, text="START", bg="green", fg="white", font=("Arial", 11, "bold"), width=12, command=self.toggle_start)
        self.btn_start.pack(side=tk.LEFT, padx=20)

        # 4. Settings Button
        tk.Button(ctrl, text="⚙ Advanced Settings", command=self.open_settings).pack(side=tk.LEFT)

        # 5. Simulation Slider (Visible if mode is Manual)
        self.sim_frame = tk.Frame(ctrl, bg="#eee")
        self.sim_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(self.sim_frame, text="Signal Sim:", fg="red", bg="#eee").pack(side=tk.LEFT)
        self.scale_sim = tk.Scale(self.sim_frame, from_=0, to=1, resolution=0.01, orient=tk.HORIZONTAL, length=150)
        self.scale_sim.pack(side=tk.LEFT)
        # Connect slider to DataStream
        self.scale_sim.config(command=lambda v: self.stream.set_manual_input(v))

        # -- Main Canvas --
        self.canvas = tk.Canvas(self.root, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def change_scenario(self, event):
        name = self.scn_var.get()
        for s in self.scenarios:
            if s.name == name:
                self.current_scenario = s
                if self.running: self.current_scenario.start()

    def toggle_start(self):
        if not self.running:
            # START SESSION
            try: mins = float(self.entry_time.get())
            except: mins = 5
            self.total_time = mins * 60
            self.start_time = time.time()
            self.score = 0
            self.score_velocity = 0
            self.running = True
            self.btn_start.config(text="STOP", bg="red")
            self.current_scenario.start()
        else:
            # STOP SESSION
            self.running = False
            self.btn_start.config(text="START", bg="green")

    def open_settings(self):
        """Creates the Advanced Settings Popup"""
        win = tk.Toplevel(self.root)
        win.title("Advanced Settings")
        win.geometry("400x650")

        # -- Section 1: Signal Source --
        tk.Label(win, text="-- Signal Input Source --", font=("Arial", 12, "bold")).pack(pady=10)
        
        modes = [DataStream.MODE_MANUAL, DataStream.MODE_SYNTHETIC, DataStream.MODE_HARDWARE]
        src_var = tk.StringVar(value=self.stream.mode)
        
        def on_mode_change(event):
            self.stream.mode = src_var.get()
            # Toggle Slider Visibility based on mode
            if self.stream.mode == DataStream.MODE_MANUAL:
                self.sim_frame.pack(side=tk.LEFT, padx=20)
                self.scale_sim.config(state="normal")
            else:
                self.sim_frame.pack_forget()

        cb_src = ttk.Combobox(win, textvariable=src_var, values=modes, state="readonly")
        cb_src.bind("<<ComboboxSelected>>", on_mode_change)
        cb_src.pack()

        # -- Section 2: Global Params --
        tk.Label(win, text="-- Global Parameters --", font=("Arial", 12, "bold")).pack(pady=10)
        
        def add_slider(lbl, key, f, t, r):
            tk.Label(win, text=lbl).pack(anchor="w", padx=10)
            s = tk.Scale(win, from_=f, to=t, resolution=r, orient=tk.HORIZONTAL)
            s.set(self.settings[key])
            s.pack(fill=tk.X, padx=10)
            s.config(command=lambda v: self.settings.update({key: float(v)}))

        add_slider("Threshold:", "threshold", 0, 1, 0.05)
        add_slider("Smoothing Bandwidth:", "smoothing", 0.01, 0.5, 0.01)
        add_slider("Base Points per Sec:", "base_points", 1, 50, 1)

        # Audio Toggle
        v_audio = tk.BooleanVar(value=self.settings["audio_enabled"])
        def toggle_audio():
            self.settings["audio_enabled"] = v_audio.get()
            self.audio.enabled = v_audio.get()
        tk.Checkbutton(win, text="Enable Audio", variable=v_audio, command=toggle_audio).pack(pady=5)

        # -- Section 3: Scenario Specific --
        tk.Label(win, text=f"-- {self.current_scenario.name} Settings --", font=("Arial", 12, "bold")).pack(pady=15)
        
        # Embed the scenario's own settings frame here
        sc_frame = self.current_scenario.get_settings_panel(win)
        sc_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        tk.Button(win, text="Close", command=win.destroy).pack(pady=20)

    def calculate_health(self, signal, thresh):
        """
        The Core 'Transition' Logic.
        Calculates a 'Health' factor (0.0 to 1.0) based on signal vs threshold.
        Includes a 'Transition Zone' so it doesn't snap abruptly.
        """
        if signal > thresh:
            return 1.0
        elif signal < (thresh - 0.15):
            return 0.0
        else:
            # We are in the transition zone (e.g., 0.35 to 0.5)
            # Interpolate 0.0 to 1.0 within this small window
            window = 0.15
            dist = signal - (thresh - window)
            ratio = dist / window
            return ratio * 0.8 # Cap at 80% health while in transition

    def update_loop(self):
        now = time.time()
        dt = now - self.last_update_time
        self.last_update_time = now

        if self.running:
            # 1. Check Timer
            elapsed = now - self.start_time
            remaining = max(0, self.total_time - elapsed)
            if remaining == 0: self.toggle_start()

            # 2. Get Signal (Manual, Synthetic, or Hardware)
            self.raw_signal = self.stream.get_current_signal()

            # 3. Apply Low Pass Filter (Smoothing)
            alpha = self.settings["smoothing"]
            self.smooth_signal += alpha * (self.raw_signal - self.smooth_signal)

            # 4. Calculate World Health (Visual State)
            target_health = self.calculate_health(self.smooth_signal, self.settings["threshold"])
            
            # Smooth the Health Value too (for visual elegance)
            self.world_health += (target_health - self.world_health) * 2.0 * dt

            # 5. Scoring Logic (Momentum)
            if self.smooth_signal > self.settings["threshold"]:
                self.score_velocity += 5 * dt 
                if self.score_velocity > self.settings["base_points"]: 
                    self.score_velocity = self.settings["base_points"]
            else:
                self.score_velocity -= 5 * dt
                if self.score_velocity < 0: self.score_velocity = 0
            
            self.score += self.score_velocity * dt

            # 6. Audio Update
            self.audio.update_ambient(self.world_health)

            # 7. Scenario Update
            self.current_scenario.update(dt, self.world_health, self.smooth_signal, self.audio)

            # 8. Drawing
            self.canvas.delete("all")
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()
            
            self.current_scenario.draw(self.canvas, w, h, self.world_health)
            self.draw_hud(remaining, w, h)

        else:
            # Idle Screen
            self.canvas.delete("all")
            self.canvas.create_text(500, 350, text="Press START", fill="white", font=("Arial", 30))

        self.root.after(33, self.update_loop)

    def draw_hud(self, remaining, w, h):
        # Time
        mins, secs = divmod(int(remaining), 60)
        self.canvas.create_text(w-20, 30, text=f"{mins:02}:{secs:02}", font=("Courier", 24, "bold"), fill="white", anchor="e")
        
        # Score
        self.canvas.create_text(20, 30, text=f"Score: {int(self.score)}", font=("Courier", 24, "bold"), fill="gold", anchor="w")
        
        # Debug / Signal Bar
        bx, by, bw, bh = 20, 70, 200, 15
        self.canvas.create_rectangle(bx, by, bx+bw, by+bh, fill="#444", outline="white")
        
        fill_w = bw * self.smooth_signal
        col = "green" if self.smooth_signal > self.settings["threshold"] else "orange"
        if self.smooth_signal < (self.settings["threshold"] - 0.15): col = "red"
        
        self.canvas.create_rectangle(bx, by, bx+fill_w, by+bh, fill=col, outline="")
        
        # Threshold Marker
        th_x = bx + (bw * self.settings["threshold"])
        self.canvas.create_line(th_x, by-5, th_x, by+bh+5, fill="white", width=2)
        
        # Info Text
        self.canvas.create_text(bx, by+25, text=f"Source: {self.stream.mode}", fill="#aaa", font=("Arial", 8), anchor="w")

if __name__ == "__main__":
    root = tk.Tk()
    app = NeurofeedbackApp(root)
    root.mainloop()