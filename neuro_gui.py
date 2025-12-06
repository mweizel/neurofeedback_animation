import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
import math

# --- 0. AUDIO SYSTEM (Safe Wrapper) ---
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("Note: 'pygame' not installed. Audio disabled.")

class AudioController:
    def __init__(self):
        self.enabled = False
        if PYGAME_AVAILABLE:
            pygame.mixer.init()
            # To use: self.coin_sound = pygame.mixer.Sound("coin.wav")
            pass

    def update_volume(self, world_health):
        if PYGAME_AVAILABLE and self.enabled:
            # Volume gets louder as world gets healthier
            # pygame.mixer.music.set_volume(max(0.1, world_health))
            pass

    def play_coin(self):
        if PYGAME_AVAILABLE and self.enabled:
            # if self.coin_sound: self.coin_sound.play()
            print("Audio: *Chime*") 

# --- 1. UTILITIES ---
def lerp_color(c1, c2, t):
    """Linear interpolation between two RGB tuples."""
    t = max(0.0, min(1.0, t)) # Clamp
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t)
    )

def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % rgb

# --- 2. SCENARIO BASE CLASS ---
class ScenarioBase:
    def __init__(self, name):
        self.name = name
        self.settings = {} 

    def start(self): 
        pass
    
    def update(self, dt, world_health, signal): 
        pass
    
    def draw(self, canvas, w, h, world_health): 
        pass
    
    def get_settings_panel(self, parent):
        return tk.Label(parent, text="No settings.")

# --- 3. NATURE SCENARIO (Restored v2 Features) ---
class NatureScenario(ScenarioBase):
    def __init__(self):
        super().__init__("Nature Restoration")
        self.settings = {
            "tree_probability": 0.005,
            "flower_speed": 0.8
        }
        self.plants = []
        
        # Color Palettes
        self.sky_dead = (100, 100, 110)
        self.sky_alive = (135, 206, 235)
        self.grass_dead = (101, 67, 33)
        self.grass_alive = (34, 139, 34)

    def start(self):
        self.plants = []

    def update(self, dt, world_health, signal):
        # Only spawn if healthy enough
        if world_health > 0.6:
            # Flowers
            if random.random() < 0.05:
                self.plants.append(self._create_plant('flower', world_health))
            
            # Trees (Rare, configurable)
            if random.random() < self.settings["tree_probability"]:
                self.plants.append(self._create_plant('tree', world_health))

        # Grow plants
        for p in self.plants:
            # They only grow if the world is somewhat healthy
            if world_health > 0.3 and p['size'] < p['max_size']:
                p['size'] += self.settings["flower_speed"] * dt

        # Cull old plants to save memory
        if len(self.plants) > 250: self.plants.pop(0)

    def _create_plant(self, p_type, health):
        return {
            'type': p_type,
            'x': random.randint(0, 1200),
            'y': random.randint(400, 800), # Rough horizon line
            'size': 0.1,
            'max_size': random.uniform(0.8, 1.2) if p_type == 'flower' else random.uniform(2.0, 3.5),
            'color': random.choice(["red", "white", "yellow", "purple"]) if p_type == 'flower' else "forestgreen"
        }

    def draw(self, canvas, w, h, world_health):
        # 1. Background Interpolation (The "Dry vs Lush" logic)
        curr_sky = lerp_color(self.sky_dead, self.sky_alive, world_health)
        curr_grass = lerp_color(self.grass_dead, self.grass_alive, world_health)
        
        # Sky
        canvas.create_rectangle(0, 0, w, h*0.6, fill=rgb_to_hex(curr_sky), outline="")
        # Grass
        canvas.create_rectangle(0, h*0.6, w, h, fill=rgb_to_hex(curr_grass), outline="")
        
        # Sun/Moon
        sun_col = lerp_color((200, 200, 200), (255, 215, 0), world_health)
        canvas.create_oval(w-150, 50, w-50, 150, fill=rgb_to_hex(sun_col), outline="")

        # 2. Draw Plants
        # Sort by Y for depth perspective
        self.plants.sort(key=lambda p: p['y'])
        
        for p in self.plants:
            # Clamp X to screen
            px = p['x'] % w
            py = p['y']
            
            # Adjust Y based on canvas height (dynamic resizing)
            if py > h: py = h - 20
            if py < h*0.6: py = int(h*0.6) + 20

            scale = p['size']
            
            if p['type'] == 'flower':
                stem_h = 20 * scale
                canvas.create_line(px, py, px, py-stem_h, fill="darkgreen", width=2)
                # Petals
                r = 6 * scale
                canvas.create_oval(px-r, py-stem_h-r, px+r, py-stem_h+r, fill=p['color'], outline="")
            
            elif p['type'] == 'tree':
                trunk_w = 12 * scale
                trunk_h = 70 * scale
                foliage = 35 * scale
                # Trunk
                canvas.create_rectangle(px-trunk_w/2, py, px+trunk_w/2, py-trunk_h, fill="#5D4037", outline="")
                # Foliage
                canvas.create_oval(px-foliage, py-trunk_h-foliage, px+foliage, py-trunk_h+foliage, fill=p['color'], outline="")

    def get_settings_panel(self, parent):
        f = tk.Frame(parent)
        tk.Label(f, text="Nature Settings", font=("bold", 10)).pack(anchor="w")
        
        tk.Label(f, text="Tree Probability:").pack(anchor="w")
        s1 = tk.Scale(f, from_=0.0, to=0.02, resolution=0.001, orient=tk.HORIZONTAL)
        s1.set(self.settings["tree_probability"])
        s1.pack(fill=tk.X)
        s1.config(command=lambda v: self.settings.update({"tree_probability": float(v)}))

        tk.Label(f, text="Growth Speed:").pack(anchor="w")
        s2 = tk.Scale(f, from_=0.1, to=3.0, resolution=0.1, orient=tk.HORIZONTAL)
        s2.set(self.settings["flower_speed"])
        s2.pack(fill=tk.X)
        s2.config(command=lambda v: self.settings.update({"flower_speed": float(v)}))
        return f

# --- 4. FLIGHT SCENARIO (Placeholder) ---
class FlightScenario(ScenarioBase):
    def __init__(self):
        super().__init__("Flight Mode")
        self.y = 300
    
    def update(self, dt, health, sig):
        target = 600 - (500 * health)
        self.y += (target - self.y) * 2 * dt
    
    def draw(self, canvas, w, h, health):
        canvas.create_rectangle(0,0,w,h, fill="#87CEEB", outline="")
        canvas.create_text(w/2, self.y, text="✈️", font=("Arial", 50))

# --- 5. MAIN APPLICATION ---
class NeurofeedbackApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NeuroFeedback Training v4.0")
        self.root.geometry("1000x700")

        self.audio = AudioController()

        # Global State
        self.scenarios = [NatureScenario(), FlightScenario()]
        self.current_scenario = self.scenarios[0]
        
        self.settings = {
            "threshold": 0.5,
            "smoothing": 0.05,
            "base_points": 10,
            "audio_enabled": False,
            "sim_mode": False
        }

        self.running = False
        self.paused = False
        self.start_time = 0
        self.total_time = 300 # 5 mins default
        
        # Signal & Scoring
        self.raw_signal = 0.0
        self.smooth_signal = 0.0
        self.world_health = 0.0
        self.score = 0.0
        self.score_velocity = 0.0

        self.last_update_time = time.time()
        
        self.setup_ui()
        self.update_loop()

    def setup_ui(self):
        # --- Top Control Bar ---
        ctrl = tk.Frame(self.root, bg="#eee", pady=10, padx=10, relief=tk.RAISED, bd=2)
        ctrl.pack(fill=tk.X)

        # 1. Scenario Selector
        tk.Label(ctrl, text="Scenario:", bg="#eee").pack(side=tk.LEFT)
        self.scn_var = tk.StringVar(value=self.current_scenario.name)
        cb = ttk.Combobox(ctrl, textvariable=self.scn_var, values=[s.name for s in self.scenarios], state="readonly", width=15)
        cb.bind("<<ComboboxSelected>>", self.change_scenario)
        cb.pack(side=tk.LEFT, padx=5)

        # 2. Timer
        tk.Label(ctrl, text="Min:", bg="#eee").pack(side=tk.LEFT)
        self.entry_time = tk.Entry(ctrl, width=4)
        self.entry_time.insert(0, "5")
        self.entry_time.pack(side=tk.LEFT, padx=5)

        # 3. Start Button
        self.btn_start = tk.Button(ctrl, text="START", bg="green", fg="white", font=("bold", 10), width=10, command=self.toggle_start)
        self.btn_start.pack(side=tk.LEFT, padx=15)

        # 4. Settings Button
        tk.Button(ctrl, text="⚙ Settings", command=self.open_settings).pack(side=tk.LEFT)

        # 5. Sim Slider (Hidden by default)
        self.sim_frame = tk.Frame(ctrl, bg="#eee")
        tk.Label(self.sim_frame, text="Signal Sim:", fg="red", bg="#eee").pack(side=tk.LEFT)
        self.scale_sim = tk.Scale(self.sim_frame, from_=0, to=1, resolution=0.01, orient=tk.HORIZONTAL, length=150)
        self.scale_sim.pack(side=tk.LEFT)
        self.scale_sim.config(command=lambda v: setattr(self, 'raw_signal', float(v)))

        # --- Canvas ---
        self.canvas = tk.Canvas(self.root, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def change_scenario(self, event):
        name = self.scn_var.get()
        for s in self.scenarios:
            if s.name == name:
                self.current_scenario = s
                # Restart scenario state if needed
                if self.running: self.current_scenario.start()

    def toggle_start(self):
        if not self.running:
            # START
            try:
                mins = float(self.entry_time.get())
            except ValueError:
                mins = 5
            self.total_time = mins * 60
            self.start_time = time.time()
            self.score = 0
            self.score_velocity = 0
            self.running = True
            self.btn_start.config(text="STOP", bg="red")
            self.current_scenario.start()
        else:
            # STOP
            self.running = False
            self.btn_start.config(text="START", bg="green")

    def open_settings(self):
        win = tk.Toplevel(self.root)
        win.title("Advanced Settings")
        win.geometry("400x600")

        # Global Params
        tk.Label(win, text="-- Global Settings --", font=("bold", 12)).pack(pady=10)
        
        def add_slider(lbl, key, f, t, r):
            tk.Label(win, text=lbl).pack(anchor="w", padx=10)
            s = tk.Scale(win, from_=f, to=t, resolution=r, orient=tk.HORIZONTAL)
            s.set(self.settings[key])
            s.pack(fill=tk.X, padx=10)
            s.config(command=lambda v: self.settings.update({key: float(v)}))

        add_slider("Threshold:", "threshold", 0, 1, 0.05)
        add_slider("Smoothing (Bandwidth):", "smoothing", 0.01, 0.5, 0.01)
        add_slider("Base Score Points:", "base_points", 1, 50, 1)

        # Toggles
        vf = tk.Frame(win); vf.pack(pady=5)
        v_sim = tk.BooleanVar(value=self.settings["sim_mode"])
        
        def toggle_sim():
            self.settings["sim_mode"] = v_sim.get()
            if v_sim.get(): self.sim_frame.pack(side=tk.LEFT, padx=10)
            else: self.sim_frame.pack_forget()

        tk.Checkbutton(vf, text="Enable Sim Slider", variable=v_sim, command=toggle_sim).pack(side=tk.LEFT)

        # Scenario Specific
        tk.Label(win, text=f"-- {self.current_scenario.name} --", font=("bold", 12)).pack(pady=15)
        sc_panel = self.current_scenario.get_settings_panel(win)
        sc_panel.pack(fill=tk.BOTH, expand=True, padx=10)

        tk.Button(win, text="Done", command=win.destroy).pack(pady=10)

    def update_loop(self):
        now = time.time()
        dt = now - self.last_update_time
        self.last_update_time = now

        if self.running:
            # 1. Timer Logic
            elapsed = now - self.start_time
            remaining = max(0, self.total_time - elapsed)
            if remaining == 0: self.toggle_start() # Time's up

            # 2. Signal Processing (Low Pass Filter)
            # This makes the "Transition" smooth
            alpha = self.settings["smoothing"]
            self.smooth_signal += alpha * (self.raw_signal - self.smooth_signal)

            # 3. Calculate World Health (Visual State)
            # 1.0 = Lush, 0.0 = Dead
            # We create a "soft window" around the threshold
            thresh = self.settings["threshold"]
            
            target_health = 0.0
            if self.smooth_signal > thresh:
                target_health = 1.0
            elif self.smooth_signal > (thresh - 0.15):
                # Transition zone (e.g. 0.35 to 0.5 if thresh is 0.5)
                ratio = (self.smooth_signal - (thresh-0.15)) / 0.15
                target_health = ratio * 0.5 # capped at half health in transition
            
            # Smooth the health value too
            self.world_health += (target_health - self.world_health) * 2 * dt

            # 4. Scoring Logic (Momentum)
            if self.smooth_signal > thresh:
                # Accelerate points
                self.score_velocity += 5 * dt 
                if self.score_velocity > self.settings["base_points"]: 
                    self.score_velocity = self.settings["base_points"]
            else:
                # Decelerate points (Coasting)
                self.score_velocity -= 5 * dt
                if self.score_velocity < 0: self.score_velocity = 0
            
            self.score += self.score_velocity * dt

            # 5. Audio
            self.audio.update_volume(self.world_health)

            # 6. Scenario Update
            self.current_scenario.update(dt, self.world_health, self.smooth_signal)

            # 7. Drawing
            self.canvas.delete("all")
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()
            
            # Draw Scenario
            self.current_scenario.draw(self.canvas, w, h, self.world_health)
            
            # Draw HUD
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
        
        # Debug Bar (Visual Feedback of Signal)
        bx, by, bw, bh = 20, 70, 200, 15
        self.canvas.create_rectangle(bx, by, bx+bw, by+bh, fill="#444", outline="white")
        
        # Fill
        fill_w = bw * self.smooth_signal
        col = "green" if self.smooth_signal > self.settings["threshold"] else "orange"
        if self.smooth_signal < (self.settings["threshold"] - 0.1): col = "red"
        
        self.canvas.create_rectangle(bx, by, bx+fill_w, by+bh, fill=col, outline="")
        
        # Threshold Marker
        th_x = bx + (bw * self.settings["threshold"])
        self.canvas.create_line(th_x, by-5, th_x, by+bh+5, fill="white", width=2)
        self.canvas.create_text(th_x, by+25, text="Threshold", fill="white", font=("Arial", 8))

if __name__ == "__main__":
    root = tk.Tk()
    app = NeurofeedbackApp(root)
    root.mainloop()