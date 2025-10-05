# image_compressor_pro.py
import customtkinter as ctk
from tkinter import filedialog, messagebox, colorchooser
from PIL import Image
import os

# --------- Config / Theme Colors ----------
CTK_APPEARANCE = "dark"   # default appearance
PRIMARY_BG = "#0f1113"    # main window bg
PANEL_BG = "#111214"      # main frame bg
NEON = "#00fff7"          # neon highlight
BTN_NORMAL = "#1e2226"    # normal button bg
BTN_HOVER = "#00cfe6"     # hover color
CORNER = 20               # uniform corner radius

# --------- App ----------
class ImageCompressorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # basic CTk setup
        ctk.set_appearance_mode(CTK_APPEARANCE)
        ctk.set_default_color_theme("dark-blue")

        self.title("⚡ Pro Image Compressor & Converter ⚡")
        self.geometry("980x600")
        self.minsize(700, 480)

        # state
        self.file_path = None
        self.bg_color = PANEL_BG
        self.font_color = NEON
        self.sidebar_width = 300
        self.sidebar_open = False
        self._anim_running = False  # avoid double animations

        # main layout (responsive)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # main frame (center area)
        self.main_frame = ctk.CTkFrame(self, corner_radius=CORNER, fg_color=self.bg_color)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=18, pady=18)

        # topbar (title + menu)
        top_bar = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        top_bar.pack(fill="x", pady=(10, 18), padx=10)

        self.title_label = ctk.CTkLabel(
            top_bar, text="⚡ Pro Image Compressor & Converter ⚡",
            font=("Inter", 20, "bold"), text_color=self.font_color
        )
        self.title_label.pack(side="left", anchor="w")

        # menu button (hamburger)
        self.menu_btn = ctk.CTkButton(
            top_bar, text="≡", width=46, height=42,
            corner_radius=12, fg_color=BTN_NORMAL, text_color="white",
            hover=False, command=self.toggle_sidebar
        )
        self.menu_btn.pack(side="right", anchor="e", padx=(0,6))
        self._apply_hover(self.menu_btn)

        # center content container
        self.content_box = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_box.pack(expand=True)

        # controls card
        card = ctk.CTkFrame(self.content_box, corner_radius=CORNER, fg_color="#121416", width=720)
        card.pack(pady=6, padx=6, ipadx=10, ipady=10)

        # file select row
        self.select_btn = ctk.CTkButton(
            card, text="📂 Select Image", command=self.open_file,
            height=46, corner_radius=18, fg_color=BTN_NORMAL, text_color="white"
        )
        self.select_btn.pack(pady=(12,8))
        self._apply_hover(self.select_btn, neon=BTN_HOVER)

        # format + resize + quality row (horizontal)
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(pady=(6, 12), padx=12, fill="x")

        # format dropdown
        self.format_choice = ctk.CTkComboBox(row, values=["JPG", "PNG", "WEBP"],
                                             corner_radius=12, height=36, fg_color=BTN_NORMAL, text_color="white")
        self.format_choice.set("WEBP")
        self.format_choice.pack(side="left", padx=(0,8), expand=True)

        # resize dropdown
        self.resize_choice = ctk.CTkComboBox(row, values=["Original", "75%", "50%"],
                                             corner_radius=12, height=36, fg_color=BTN_NORMAL, text_color="white")
        self.resize_choice.set("Original")
        self.resize_choice.pack(side="left", padx=8, expand=True)

        # quality dropdown
        self.quality_choice = ctk.CTkComboBox(row, values=["High (95)", "Medium (80)", "Low (60)"],
                                              corner_radius=12, height=36, fg_color=BTN_NORMAL, text_color="white")
        self.quality_choice.set("High (95)")
        self.quality_choice.pack(side="left", padx=(8,0), expand=True)

        # compress button
        self.compress_btn = ctk.CTkButton(
            card, text="🚀 Compress & Convert", command=self.compress_image,
            height=50, corner_radius=22, fg_color=BTN_NORMAL, text_color="white"
        )
        self.compress_btn.pack(pady=(6, 16), ipadx=12)
        self._apply_hover(self.compress_btn, neon=NEON)

        # status label
        self.status_label = ctk.CTkLabel(card, text="No file selected", text_color="#bfc6c8")
        self.status_label.pack(pady=(6, 12))

        # sidebar
        self.sidebar = ctk.CTkFrame(self, width=self.sidebar_width, corner_radius=CORNER, fg_color="#0b0c0d")

        self.bind("<Configure>", lambda e: self._on_window_resize())

    # ---------------- Sidebar + Helpers ----------------
    def _on_window_resize(self):
        if self.sidebar_open and not self._anim_running:
            x = self.winfo_width() - self.sidebar_width - 18
            self.sidebar.place(x=x, y=18)

    def _apply_hover(self, widget, neon=BTN_HOVER):
        normal_color = BTN_NORMAL
        hover_color = neon
        def on_enter(e): widget.configure(fg_color=hover_color)
        def on_leave(e): widget.configure(fg_color=normal_color)
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def toggle_sidebar(self):
        if self._anim_running: return
        if self.sidebar_open: self._animate_sidebar(False)
        else:
            self.build_sidebar()
            self._animate_sidebar(True)

    def build_sidebar(self):
        for w in self.sidebar.winfo_children(): w.destroy()

        header = ctk.CTkLabel(self.sidebar, text="⚙️ Settings", font=("Inter", 16, "bold"), text_color=NEON)
        header.pack(pady=(22,10))

        # Toggle Theme
        theme_btn = ctk.CTkButton(
            self.sidebar, text="🌙 Toggle Dark/Light", command=self._toggle_theme,
            height=44, corner_radius=14, fg_color=BTN_NORMAL, text_color="white"
        )
        theme_btn.pack(fill="x", padx=18, pady=8)
        self._apply_hover(theme_btn)

        # Background color
        bg_btn = ctk.CTkButton(
            self.sidebar, text="🎨 Change Background", command=self._choose_bg_color,
            height=44, corner_radius=14, fg_color=BTN_NORMAL, text_color="white"
        )
        bg_btn.pack(fill="x", padx=18, pady=8)
        self._apply_hover(bg_btn)

        # Font color
        font_btn = ctk.CTkButton(
            self.sidebar, text="🖋 Change Font Color", command=self._choose_font_color,
            height=44, corner_radius=14, fg_color=BTN_NORMAL, text_color="white"
        )
        font_btn.pack(fill="x", padx=18, pady=8)
        self._apply_hover(font_btn)

    def _toggle_theme(self):
        current = ctk.get_appearance_mode()
        ctk.set_appearance_mode("dark" if current == "Light" else "light")

    def _choose_bg_color(self):
        color = colorchooser.askcolor(title="Choose Background Color")[1]
        if color:
            self.bg_color = color
            self.main_frame.configure(fg_color=color)

    def _choose_font_color(self):
        color = colorchooser.askcolor(title="Choose Font Color")[1]
        if color:
            self.font_color = color
            self.title_label.configure(text_color=color)

    def _animate_sidebar(self, opening=True):
        self._anim_running = True
        start_x = self.winfo_width() if opening else (self.winfo_width() - self.sidebar_width - 18)
        end_x = (self.winfo_width() - self.sidebar_width - 18) if opening else (self.winfo_width() + 10)
        step = -24 if opening else 24

        def slide(x):
            if opening and x <= end_x:
                self.sidebar.place(x=end_x, y=18); self.sidebar_open=True; self._anim_running=False; return
            if (not opening) and x >= end_x:
                self.sidebar.place_forget(); self.sidebar_open=False; self._anim_running=False; return
            self.sidebar.place(x=x, y=18)
            self.after(12, lambda: slide(x+step))

        slide(start_x)

    # ---------------- File Handling ----------------
    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.webp")])
        if path:
            self.file_path = path
            size_kb = os.path.getsize(path) / 1024
            self.status_label.configure(text=f"Selected: {os.path.basename(path)}  —  {size_kb:.2f} KB")

    def compress_image(self):
        if not self.file_path:
            messagebox.showerror("Error", "Please select an image first!")
            return

        fmt = self.format_choice.get().lower()
        resize_opt = self.resize_choice.get()
        quality_opt = self.quality_choice.get()

        # map quality selection
        if "95" in quality_opt: quality = 95
        elif "80" in quality_opt: quality = 80
        else: quality = 60

        save_def = os.path.splitext(os.path.basename(self.file_path))[0] + f"_compressed.{fmt}"
        save_path = filedialog.asksaveasfilename(initialfile=save_def, defaultextension=f".{fmt}",
                                                 filetypes=[(f"{fmt.upper()} files", f"*.{fmt}")])
        if not save_path: return

        try:
            img = Image.open(self.file_path)

            # optional resize
            if resize_opt == "75%":
                img = img.resize((int(img.width*0.75), int(img.height*0.75)), Image.LANCZOS)
            elif resize_opt == "50%":
                img = img.resize((int(img.width*0.5), int(img.height*0.5)), Image.LANCZOS)

            if fmt in ("jpg","jpeg"):
                img = img.convert("RGB")
                img.save(save_path, "JPEG", optimize=True, quality=quality)
            elif fmt=="png":
                img = img.convert("P", palette=Image.ADAPTIVE)
                img.save(save_path, "PNG", optimize=True)
            elif fmt=="webp":
                img.save(save_path, "WEBP", lossless=(quality==95), quality=quality, method=6)
            else:
                img.save(save_path)

            orig_size = os.path.getsize(self.file_path)/1024
            new_size = os.path.getsize(save_path)/1024
            self.status_label.configure(text=f"Saved: {os.path.basename(save_path)}  —  {new_size:.2f} KB")
            messagebox.showinfo("Success", f"Saved as {save_path}\n\nOriginal: {orig_size:.2f} KB\nCompressed: {new_size:.2f} KB")

        except Exception as ex:
            messagebox.showerror("Error", f"Failed: {ex}")

# --------- Run ----------
if __name__ == "__main__":
    app = ImageCompressorApp()
    app.mainloop()
