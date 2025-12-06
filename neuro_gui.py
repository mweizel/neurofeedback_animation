import tkinter as tk
from tkinter import ttk, colorchooser, filedialog
import random
import time
import math

class NeurofeedbackApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NeuroFeedback Training Module")
        self.root.geometry("1000x700")

        # --- Configuration / State Variables ---
        self.settings = {
            "threshold": 0.5,
            "training_time_min": 5,
            "sound_enabled": True,
            "coin_sound": "Chime",
            "mystery_img_path": "",
            "show_hud": True, # Heads up display (time/score)
            "sim_mode": False, # Testing slider
            "combo_time_trigger": 5, # Seconds needed for double points
            "combo_enabled": True,
            "randomness": 0.2 # 20% fluctuation in points
        }
        
        self.running = False
        self.paused = False
        self.start_time = 0
        self.elapsed_time = 0
        self.score = 0
        self.current_signal = 0.0 # From 0.0 to 1.0
        
        # Gamification State
        self.consecutive_green_time = 0
        self.last_update_time = time.time()
        
        # Animation State (Nature)
        self.flowers = [] # List of active flower objects
        self.sky_color = "#87CEEB"
        self.grass_color = "#228B22"

        self.setup_ui()
        self.update_loop()

    def setup_ui(self):
        # --- Top Control Panel ---
        control_frame = tk.Frame(self.root, pady=10, padx=10, bg="#f0f0f0")
        control_frame.pack(fill=tk.X)

        # Scenario Selection
        tk.Label(control_frame, text="Scenario:", bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
        self.scenario_var = tk.StringVar(value="1. Nature Restoration")
        scenario_menu = ttk.Combobox(control_frame, textvariable=self.scenario_var, state="readonly")
        scenario_menu['values'] = ("1. Nature Restoration", "2. Clarity (Picture)", "3. Flight", "4. Abstract Flow")
        scenario_menu.pack(side=tk.LEFT, padx=5)

        # Time Setting
        tk.Label(control_frame, text="Time (min):", bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
        self.time_entry = tk.Entry(control_frame, width=5)
        self.time_entry.insert(0, "5")
        self.time_entry.pack(side=tk.LEFT, padx=5)

        # Buttons
        self.btn_start = tk.Button(control_frame, text="START", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), command=self.toggle_start)
        self.btn_start.pack(side=tk.LEFT, padx=10)
        
        btn_settings = tk.Button(control_frame, text="Advanced Settings", command=self.open_settings)
        btn_settings.pack(side=tk.LEFT, padx=5)

        # Simulation Slider (Hidden by default)
        self.sim_frame = tk.Frame(control_frame, bg="#f0f0f0")
        tk.Label(self.sim_frame, text="Signal Sim:", bg="#f0f0f0", fg="red").pack(side=tk.LEFT)
        self.sim_slider = tk.Scale(self.sim_frame, from_=0, to=1, resolution=0.01, orient=tk.HORIZONTAL, length=200, command=self.on_slider_move)
        self.sim_slider.set(0.2) # Start low
        self.sim_slider.pack(side=tk.LEFT)
        # Pack sim_frame later if enabled

        # --- Main Canvas ---
        self.canvas = tk.Canvas(self.root, bg="gray")
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def on_slider_move(self, val):
        self.current_signal = float(val)

    def open_settings(self):
        # Create a popup window
        win = tk.Toplevel(self.root)
        win.title("Advanced Settings")
        win.geometry("400x500")

        def add_row(label_text, var_key, type="entry", opts=None):
            row = tk.Frame(win, pady=5)
            row.pack(fill=tk.X, padx=10)
            tk.Label(row, text=label_text, width=20, anchor='w').pack(side=tk.LEFT)
            
            if type == "entry":
                val = tk.StringVar(value=str(self.settings[var_key]))
                e = tk.Entry(row, textvariable=val)
                e.pack(side=tk.RIGHT, expand=True, fill=tk.X)
                return val
            elif type == "check":
                val = tk.BooleanVar(value=self.settings[var_key])
                c = tk.Checkbutton(row, variable=val)
                c.pack(side=tk.RIGHT)
                return val
            elif type == "scale":
                val = tk.DoubleVar(value=self.settings[var_key])
                s = tk.Scale(row, from_=opts[0], to=opts[1], resolution=opts[2], orient=tk.HORIZONTAL, variable=val)
                s.pack(side=tk.RIGHT, fill=tk.X, expand=True)
                return val

        # Settings Fields
        v_thresh = add_row("Threshold (0.0 - 1.0):", "threshold", "scale", (0, 1, 0.05))
        v_hud = add_row("Show HUD (Score/Time):", "show_hud", "check")
        v_sim = add_row("Enable Sim Slider:", "sim_mode", "check")
        
        tk.Label(win, text="--- Gamification ---", font=("Arial", 10, "bold")).pack(pady=10)
        v_combo = add_row("Enable Combo Bonus:", "combo_enabled", "check")
        v_combo_t = add_row("Combo Seconds:", "combo_time_trigger", "entry")
        v_rand = add_row("Point Randomness (0-1):", "randomness", "entry")

        def save():
            self.settings["threshold"] = v_thresh.get()
            self.settings["show_hud"] = v_hud.get()
            self.settings["sim_mode"] = v_sim.get()
            self.settings["combo_enabled"] = v_combo.get()
            self.settings["combo_time_trigger"] = float(v_combo_t.get())
            self.settings["randomness"] = float(v_rand.get())
            
            # Toggle Slider visibility
            if self.settings["sim_mode"]:
                self.sim_frame.pack(side=tk.LEFT, padx=20)
            else:
                self.sim_frame.pack_forget()
                
            win.destroy()

        tk.Button(win, text="Save & Close", command=save, bg="#ddd").pack(pady=20)

    def toggle_start(self):
        if not self.running:
            # Start
            try:
                mins = float(self.time_entry.get())
            except ValueError:
                mins = 5
            self.start_time = time.time()
            self.total_time_sec = mins * 60
            self.score = 0
            self.flowers = [] # Reset animation
            self.running = True
            self.btn_start.config(text="STOP", bg="#f44336")
        else:
            # Stop
            self.running = False
            self.btn_start.config(text="START", bg="#4CAF50")
            self.canvas.delete("all")

    def update_loop(self):
        # 1. Calculate Delta Time
        now = time.time()
        dt = now - self.last_update_time
        self.last_update_time = now

        if self.running:
            # 2. Update Timer
            elapsed = now - self.start_time
            remaining = max(0, self.total_time_sec - elapsed)
            
            if remaining == 0:
                self.running = False # Session done
                self.btn_start.config(text="START", bg="#4CAF50")

            # 3. Process Signal Logic
            # In a real app, you would fetch self.current_signal from your EEG stream here
            is_green = self.current_signal >= self.settings["threshold"]

            # 4. Gamification Logic
            if is_green:
                self.consecutive_green_time += dt
                
                # Calculate Points
                base_points = 10 * dt
                
                # Combo Multiplier
                multiplier = 1.0
                if self.settings["combo_enabled"] and self.consecutive_green_time > self.settings["combo_time_trigger"]:
                    multiplier = 2.0
                
                # Randomness
                rand_factor = random.uniform(1.0 - self.settings["randomness"], 1.0 + self.settings["randomness"])
                
                self.score += (base_points * multiplier * rand_factor)
                
            else:
                self.consecutive_green_time = 0 # Reset combo

            # 5. Draw Scene
            self.draw_nature_scenario(is_green, dt)

            # 6. Draw HUD
            if self.settings["show_hud"]:
                self.draw_hud(remaining, multiplier if is_green else 1.0)

        else:
            # Idle Screen
            self.canvas.delete("all")
            self.canvas.create_text(500, 350, text="Ready to Start", font=("Arial", 24), fill="white")

        # Schedule next frame (approx 30 FPS)
        self.root.after(33, self.update_loop)

    def draw_nature_scenario(self, is_green, dt):
        self.canvas.delete("all")
        
        # --- Background Color Interpolation ---
        # If green: fade to lush colors. If red: fade to grey/dry colors.
        target_sky = (135, 206, 235) if is_green else (100, 100, 100) # Blue vs Grey
        target_grass = (34, 139, 34) if is_green else (139, 69, 19)   # Green vs Brown
        
        # Simple helper to interpolate hex
        current_bg = self.canvas["bg"] # We won't do full smooth color lerp for background in this simple loop to save CPU, 
        # but we will switch the drawing colors
        
        # Draw Sky
        sky_hex = "#%02x%02x%02x" % target_sky
        grass_hex = "#%02x%02x%02x" % target_grass
        
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        # Sky
        self.canvas.create_rectangle(0, 0, w, h*0.7, fill=sky_hex, outline="")
        # Grass
        self.canvas.create_rectangle(0, h*0.7, w, h, fill=grass_hex, outline="")

        # --- Sun / Moon ---
        if is_green:
            # Bright Sun
            self.canvas.create_oval(w-150, 50, w-50, 150, fill="yellow", outline="orange", width=2)
        else:
            # Dim Moon/Sun
            self.canvas.create_oval(w-150, 50, w-50, 150, fill="#ccc", outline="gray")

        # --- Growing Flowers ---
        # If green, chance to spawn new flower
        if is_green and random.random() < 0.05: # 5% chance per frame
            new_flower = {
                'x': random.randint(50, w-50),
                'y': random.randint(int(h*0.7) + 20, h-20),
                'size': 0.1,
                'color': random.choice(["red", "purple", "white", "yellow", "orange"])
            }
            self.flowers.append(new_flower)

        # Draw flowers
        for f in self.flowers:
            # Grow if green
            if is_green and f['size'] < 1.0:
                f['size'] += 0.5 * dt
            
            # Draw stem
            stem_h = 30 * f['size']
            self.canvas.create_line(f['x'], f['y'], f['x'], f['y']-stem_h, fill="darkgreen", width=2)
            
            # Draw petals
            r = 10 * f['size']
            cx, cy = f['x'], f['y']-stem_h
            self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=f['color'], outline="")

    def draw_hud(self, remaining_time, multiplier):
        # Time
        mins = int(remaining_time // 60)
        secs = int(remaining_time % 60)
        time_str = f"{mins:02}:{secs:02}"
        self.canvas.create_text(950, 30, text=time_str, font=("Courier", 20, "bold"), fill="white", anchor="e")
        
        # Score
        score_str = f"Points: {int(self.score)}"
        self.canvas.create_text(50, 30, text=score_str, font=("Courier", 20, "bold"), fill="white", anchor="w")
        
        # Combo Indicator
        if multiplier > 1.0:
            self.canvas.create_text(50, 60, text=f"COMBO x{int(multiplier)}!", font=("Arial", 14, "bold"), fill="gold", anchor="w")

if __name__ == "__main__":
    root = tk.Tk()
    app = NeurofeedbackApp(root)
    root.mainloop()