import customtkinter as ctk
import vlc
from PIL import Image, ImageTk
import cv2
import os

# os.environ['PYTHON_VLC_LIB_PATH'] = r"C:\Program Files\VideoLAN\VLC\npvlc.dll"


class AdvancedVideoPlayer:
    def __init__(self, master, video_path=None):
        self.master = master
        self.video_path = video_path

        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()

        self.create_player_widgets()

        if video_path:
            self.load_video(video_path)

    def create_player_widgets(self):
        self.player_frame = ctk.CTkFrame(self.master, corner_radius=10)
        self.player_frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.canvas = ctk.CTkCanvas(
            self.player_frame,
            width=640,
            height=360,
            bg="black",
            highlightthickness=0
        )
        self.canvas.pack(expand=True, fill="both", padx=10, pady=10)

        controls_frame = ctk.CTkFrame(self.player_frame, corner_radius=10)
        controls_frame.pack(fill="x", padx=10, pady=10)

        self.play_pause_btn = ctk.CTkButton(
            controls_frame,
            text="▶",
            command=self.toggle_play_pause
        )
        self.play_pause_btn.pack(side="left", padx=5)

        self.stop_btn = ctk.CTkButton(
            controls_frame,
            text="■",
            command=self.stop_video
        )
        self.stop_btn.pack(side="left", padx=5)

    def extract_first_frame(self, video_path):
        cap = cv2.VideoCapture(video_path)
        first_frame = None

        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                first_frame = frame

        cap.release()
        return first_frame

    def load_video(self, video_path):
        self.video_path = video_path

        first_frame = self.extract_first_frame(video_path)
        if first_frame is not None:
            self._display_frame(first_frame)

        media = self.vlc_instance.media_new(video_path)
        self.player.set_media(media)

        handle = self.canvas.winfo_id()
        self.player.set_hwnd(handle)

    def _display_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame)
        photo = ImageTk.PhotoImage(image=pil_image)

        self.canvas.create_image(0, 0, anchor="nw", image=photo)
        self.canvas.image = photo

    def toggle_play_pause(self):
        if self.player.is_playing():
            self.player.pause()
            self.play_pause_btn.configure(text="▶")  # Play symbol
        else:
            self.player.play()
            self.play_pause_btn.configure(text="❚❚")  # Pause symbol

    def stop_video(self):
        self.player.stop()
        self.play_pause_btn.configure(text="▶")  # Reset to play symbol
