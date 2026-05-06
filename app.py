from PIL import Image  
import cv2  
import customtkinter as ctk
from tkinter import filedialog
import os
import time
from threading import Thread
from processor import classify_video 

# Library Settings
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class DeepFakeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Main Window Settings
        self.title("DeepFake Detection System")
        self.geometry("1100x700")
        
        # Enable Resizing
        self.resizable(True, True)
        self.minsize(1000, 600)

        # Professional Colors
        self.colors = {
            "bg": "#121212",             
            "panel": "#1E1E1E",          
            "accent": "#00E676",         
            "danger": "#FF1744",         
            "text": "#E0E0E0",           
            "text_dim": "#757575",       
            "button_default": "#2962FF",
            "button_play": "#FF9100"      
        }

        self.video_path = None
        self.configure(fg_color=self.colors["bg"])

        # Screen Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()
        self.create_main_area()

    def create_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color=self.colors["panel"])
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        title_label = ctk.CTkLabel(
            sidebar,
            text="🛡️ DF DETECTOR",
            font=("Segoe UI", 26, "bold"),
            text_color=self.colors["button_default"]
        )
        title_label.pack(pady=(40, 10))
        
        subtitle = ctk.CTkLabel(
            sidebar,
            text="AI Powered Security",
            font=("Segoe UI", 12),
            text_color=self.colors["text_dim"]
        )
        subtitle.pack(pady=(0, 40))

        # Select Video Button
        self.btn_select = ctk.CTkButton(
            sidebar, 
            text="📂  UPLOAD VIDEO",
            font=("Segoe UI", 14, "bold"),
            height=45,
            corner_radius=8,
            fg_color="#333333",
            hover_color="#444444",
            command=self.select_video
        )
        self.btn_select.pack(padx=20, pady=10, fill="x")

        # Play Video Button
        self.btn_play = ctk.CTkButton(
            sidebar, 
            text="▶️  PLAY VIDEO",
            font=("Segoe UI", 14, "bold"),
            height=45,
            corner_radius=8,
            fg_color=self.colors["button_play"],
            hover_color="#E65100",
            state="disabled",
            command=self.play_video_external
        )
        self.btn_play.pack(padx=20, pady=10, fill="x")

        # Analyze Button
        self.btn_analyze = ctk.CTkButton(
            sidebar, 
            text="⚡  START ANALYSIS",
            font=("Segoe UI", 14, "bold"),
            height=45,
            corner_radius=8,
            fg_color=self.colors["button_default"],
            hover_color="#1E88E5",
            state="disabled",
            command=self.start_analysis
        )
        self.btn_analyze.pack(padx=20, pady=10, fill="x")

        spacer = ctk.CTkLabel(sidebar, text="", height=50)
        spacer.pack()
        
        info_frame = ctk.CTkFrame(sidebar, fg_color="#181818", corner_radius=10)
        info_frame.pack(padx=20, fill="x", side="bottom", pady=20)
        
        ctk.CTkLabel(
            info_frame,
            text="Model: ResNet50 + GRU",
            font=("Consolas", 11),
            text_color=self.colors["text_dim"]
        ).pack(pady=5)

        ctk.CTkLabel(
            info_frame,
            text="Status: Ready",
            font=("Consolas", 11),
            text_color=self.colors["accent"]
        ).pack(pady=(0,5))

    def create_main_area(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)

        self.file_label = ctk.CTkLabel(
            main_frame,
            text="Please select a video file...",
            font=("Segoe UI", 16),
            text_color=self.colors["text_dim"],
            anchor="w"
        )
        self.file_label.pack(fill="x", pady=(0, 15))

        self.preview_frame = ctk.CTkFrame(
            main_frame,
            fg_color="black",
            corner_radius=15,
            border_width=2,
            border_color="#333333"
        )
        self.preview_frame.pack(fill="both", expand=True) 
        
        self.preview_icon = ctk.CTkLabel(
            self.preview_frame,
            text="🎬",
            font=("Segoe UI", 60)
        )
        self.preview_icon.place(relx=0.5, rely=0.4, anchor="center")
        
        self.preview_text = ctk.CTkLabel(
            self.preview_frame,
            text="SYSTEM STANDBY",
            font=("Segoe UI", 14, "bold"),
            text_color="#555555"
        )
        self.preview_text.place(relx=0.5, rely=0.55, anchor="center")

        self.progress_bar = ctk.CTkProgressBar(
            main_frame,
            height=12,
            corner_radius=6,
            progress_color=self.colors["button_default"]
        )
        self.progress_bar.pack(fill="x", pady=(30, 10))
        self.progress_bar.set(0)

        self.result_frame = ctk.CTkFrame(
            main_frame,
            height=120,
            fg_color="#1E1E1E",
            corner_radius=15
        )
        self.result_frame.pack(fill="x", pady=10)
        self.result_frame.pack_propagate(False)

        self.result_label = ctk.CTkLabel(
            self.result_frame,
            text="---",
            font=("Segoe UI", 36, "bold"),
            text_color=self.colors["text_dim"]
        )
        self.result_label.place(relx=0.5, rely=0.5, anchor="center")

    def select_video(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Video Files", "*.mp4 *.avi *.mov")]
        )

        if file_path:
            self.video_path = file_path
            filename = os.path.basename(file_path)
            
            self.file_label.configure(
                text=f"📄 Selected File: {filename}",
                text_color="white"
            )

            self.btn_analyze.configure(state="normal")
            self.btn_play.configure(state="normal")
            
            try:
                cap = cv2.VideoCapture(file_path)
                ret, frame = cap.read()
                cap.release()
                
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame)
                    
                    w = self.preview_frame.winfo_width()
                    h = self.preview_frame.winfo_height()
                    
                    if w < 10:
                        w = 850
                    if h < 10:
                        h = 480
                    
                    my_image = ctk.CTkImage(
                        light_image=img,
                        dark_image=img,
                        size=(w-4, h-4)
                    )
                    
                    self.preview_icon.place(relx=0.5, rely=0.5, anchor="center")
                    self.preview_icon.configure(image=my_image, text="") 
                else:
                    self.preview_icon.configure(image=None, text="▶️")
                    self.preview_icon.place(relx=0.5, rely=0.4, anchor="center")

            except Exception as e:
                print(f"Image could not be loaded: {e}")
                self.preview_icon.configure(image=None, text="▶️")

            self.preview_frame.configure(border_color="white")

            self.preview_text.configure(
                text="VIDEO LOADED - READY FOR ANALYSIS",
                text_color="white"
            )
            
            self.result_frame.configure(fg_color="#1E1E1E", border_width=0)
            self.result_label.configure(text="---", text_color=self.colors["text_dim"])
            self.progress_bar.set(0)

    def play_video_external(self):
        if self.video_path:
            try:
                os.startfile(self.video_path)
            except Exception as e:
                print(f"Video could not be opened: {e}")

    def start_analysis(self):
        if not self.video_path:
            return
        
        self.btn_analyze.configure(state="disabled", text="⏳ PROCESSING...")
        self.btn_select.configure(state="disabled")
        self.btn_play.configure(state="disabled")
        
        self.preview_text.configure(
            text="AI IS ANALYZING...",
            text_color=self.colors["button_default"]
        )
        
        Thread(target=self.run_logic, daemon=True).start()

    def run_logic(self):
        try:
            for i in range(1, 4):
                time.sleep(0.3)
                self.progress_bar.set(i / 10)

            label, confidence = classify_video(self.video_path)

            for i in range(4, 11):
                time.sleep(0.1)
                self.progress_bar.set(i / 10)

            self.after(0, lambda: self.show_result(label, confidence))

        except Exception as e:
            print(e)

            self.after(
                0,
                lambda: self.file_label.configure(
                    text="An error occurred!",
                    text_color="red"
                )
            )

            self.after(0, self.reset_buttons)

    def show_result(self, label, confidence):
        percentage = f"{confidence*100:.1f}%"
        
        if label == "real":
            text = f"✅ REAL - CONFIDENCE: {percentage}"
            color = self.colors["accent"]
            bg_color = "#0f2e1a"
        else:
            text = f"⛔ FAKE - CONFIDENCE: {percentage}"
            color = self.colors["danger"]
            bg_color = "#3b0c13"

        self.result_label.configure(text=text, text_color=color)
        self.result_frame.configure(
            fg_color=bg_color,
            border_width=2,
            border_color=color
        )

        self.preview_frame.configure(border_color=color)

        self.preview_text.configure(
            text="ANALYSIS COMPLETED",
            text_color=color
        )

        self.reset_buttons()

    def reset_buttons(self):
        self.btn_analyze.configure(
            state="normal",
            text="⚡  START ANALYSIS"
        )

        self.btn_select.configure(state="normal")
        self.btn_play.configure(state="normal")

if __name__ == "__main__":
    app = DeepFakeApp()
    app.mainloop()