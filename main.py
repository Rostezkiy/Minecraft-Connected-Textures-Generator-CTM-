import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox
from PIL import Image, ImageTk, ImageDraw
import os
import sys


CTM_RULES = [
    (1, 1, 1, 1, 1, 1, 1, 1),
    (1, 1, 1, 1, 1, 0, 1, 1),
    (1, 1, 1, 1, 1, 0, 1, 0),
    (1, 1, 1, 1, 1, 1, 1, 0),
    (1, 1, 1, 1, 1, 0, 0, 1),
    (1, 1, 1, 1, 1, 1, 0, 0),
    (1, 1, 1, 1, 0, 0, 0, 1),
    (1, 1, 1, 1, 1, 0, 0, 0),
    (1, 0, 1, 1, 0, 0, 0, 0),
    (1, 1, 1, 0, 0, 0, 0, 0),
    (0, 1, 0, 1, 0, 0, 0, 0),
    (0, 0, 1, 1, 0, 0, 0, 0),
    (1, 1, 1, 1, 1, 1, 0, 1),
    (1, 1, 1, 0, 1, 0, 0, 1),
    (1, 1, 0, 0, 1, 0, 0, 0),
    (1, 1, 0, 1, 1, 1, 0, 0),
    (1, 1, 1, 1, 0, 0, 1, 1),
    (1, 1, 1, 1, 0, 1, 1, 0),
    (1, 1, 1, 1, 0, 0, 1, 0),
    (1, 1, 1, 1, 0, 1, 0, 0),
    (0, 1, 1, 1, 0, 0, 0, 0),
    (1, 1, 0, 1, 0, 0, 0, 0),
    (1, 1, 0, 0, 0, 0, 0, 0),
    (1, 0, 1, 0, 0, 0, 0, 0),
    (1, 1, 1, 1, 0, 1, 0, 1),
    (1, 0, 1, 0, 0, 0, 0, 1),
    (0, 0, 0, 0, 0, 0, 0, 0),
    (0, 1, 0, 1, 0, 1, 0, 0),
    (1, 1, 1, 0, 0, 0, 0, 1),
    (1, 1, 0, 1, 1, 0, 0, 0),
    (1, 0, 1, 1, 0, 0, 0, 1),
    (1, 1, 1, 0, 1, 0, 0, 0),
    (0, 0, 0, 1, 0, 0, 0, 0),
    (0, 0, 1, 0, 0, 0, 0, 0),
    (1, 0, 0, 1, 0, 0, 0, 0),
    (0, 1, 1, 0, 0, 0, 0, 0),
    (1, 1, 1, 1, 0, 1, 1, 1),
    (1, 0, 1, 1, 0, 0, 1, 1),
    (0, 0, 1, 1, 0, 0, 1, 0),
    (0, 1, 1, 1, 0, 1, 1, 0),
    (1, 0, 1, 1, 0, 0, 1, 0),
    (0, 1, 1, 1, 0, 1, 0, 0),
    (0, 1, 1, 1, 0, 0, 1, 0),
    (1, 1, 0, 1, 0, 1, 0, 0),
    (0, 1, 0, 0, 0, 0, 0, 0),
    (1, 0, 0, 0, 0, 0, 0, 0),
    (1, 1, 1, 1, 0, 0, 0, 0),
]


class CTMGeneratorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Minecraft Auto-CTM Tool v2.0")
        self.geometry("1000x650")
        self.minsize(850, 550)

        style = ttk.Style()
        style.theme_use("clam")

        self.base_image = None
        self.base_filename = "texture"
        self.custom_outline_image = None
        self.preview_image_tk = None

        self.var_border_width = tk.IntVar(value=2)
        self.var_alpha = tk.IntVar(value=255)
        self.var_zoom = tk.DoubleVar(value=1.0)
        self.current_color = (0, 0, 0)
        self.use_custom_outline = tk.BooleanVar(value=False)
        self.show_guides = tk.BooleanVar(value=True)

        self._setup_ui()

    def _setup_ui(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=1)

        preview_frame = ttk.LabelFrame(self, text="Preview")
        preview_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.canvas = tk.Canvas(preview_frame, bg="#2b2b2b", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self._draw_checkerboard()

        bottom_bar = ttk.Frame(preview_frame)
        bottom_bar.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(bottom_bar, text="Zoom:").pack(side=tk.LEFT)
        scale_zoom = ttk.Scale(
            bottom_bar,
            from_=0.5,
            to=5.0,
            variable=self.var_zoom,
            command=lambda x: self.update_preview(),
        )
        scale_zoom.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.var_zoom.set(0.5)

        btn_load = ttk.Button(
            bottom_bar, text="📂 Load Base Texture", command=self.load_base_texture
        )
        btn_load.pack(side=tk.RIGHT)

        settings_frame = ttk.Frame(self, padding="15")
        settings_frame.grid(row=0, column=1, sticky="ns")

        lbl_mode = ttk.LabelFrame(settings_frame, text="Mode", padding="10")
        lbl_mode.pack(fill=tk.X, pady=5)

        ttk.Radiobutton(
            lbl_mode,
            text="Simple Color Border",
            variable=self.use_custom_outline,
            value=False,
            command=self.update_ui_state,
        ).pack(anchor="w")
        ttk.Radiobutton(
            lbl_mode,
            text="Custom Outline Image",
            variable=self.use_custom_outline,
            value=True,
            command=self.update_ui_state,
        ).pack(anchor="w")

        self.controls_frame = ttk.LabelFrame(
            settings_frame, text="Settings", padding="10"
        )
        self.controls_frame.pack(fill=tk.X, pady=5)

        self.lbl_width = ttk.Label(self.controls_frame, text="Border Width: 2 px")
        self.lbl_width.pack(anchor="w")

        self.scale_width = ttk.Scale(
            self.controls_frame,
            from_=0,
            to=16,
            variable=self.var_border_width,
            command=self.on_slider_change,
        )
        self.scale_width.pack(fill=tk.X, pady=(0, 10))

        ttk.Checkbutton(
            self.controls_frame,
            text="Show Guide Lines (Red)",
            variable=self.show_guides,
            command=self.update_preview,
        ).pack(anchor="w", pady=(0, 10))

        self.simple_container = ttk.Frame(self.controls_frame)
        self.lbl_alpha = ttk.Label(self.simple_container, text="Alpha: 255")
        self.lbl_alpha.pack(anchor="w")
        ttk.Scale(
            self.simple_container,
            from_=0,
            to=255,
            variable=self.var_alpha,
            command=self.on_slider_change,
        ).pack(fill=tk.X, pady=(0, 10))

        self.btn_color = tk.Button(
            self.simple_container,
            text="Choose Color",
            bg="black",
            fg="white",
            font=("Arial", 10, "bold"),
            height=2,
            command=self.choose_color,
        )
        self.btn_color.pack(fill=tk.X)

        self.custom_container = ttk.Frame(self.controls_frame)
        ttk.Label(
            self.custom_container,
            text="Upload an image that contains\nONLY the border/frame.",
            font=("Arial", 9),
            foreground="gray",
        ).pack(pady=(0, 5))
        ttk.Button(
            self.custom_container,
            text="📂 Load Outline Image",
            command=self.load_custom_outline,
        ).pack(fill=tk.X)

        ttk.Separator(settings_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)
        self.btn_generate = ttk.Button(
            settings_frame,
            text="🚀 GENERATE CTM",
            command=self.generate_files,
            state="disabled",
        )
        self.btn_generate.pack(fill=tk.X, ipady=15)

        self.status_label = ttk.Label(
            settings_frame, text="Ready", wraplength=200, foreground="gray"
        )
        self.status_label.pack(pady=10)

        self.update_ui_state()

    def on_slider_change(self, event=None):
        self.lbl_width.config(text=f"Border Width: {self.var_border_width.get()} px")
        self.lbl_alpha.config(text=f"Alpha: {self.var_alpha.get()}")
        self.update_preview()

    def _draw_checkerboard(self):
        self.canvas.delete("bg")
        w, h = 3000, 3000
        bg_img = Image.new("RGBA", (20, 20), "#333333")
        pixels = bg_img.load()
        for i in range(20):
            for j in range(20):
                if (i + j) % 2:
                    pixels[i, j] = (40, 40, 40)

        bg_pattern = Image.new("RGBA", (w, h))
        for x in range(0, w, 20):
            for y in range(0, h, 20):
                bg_pattern.paste(bg_img, (x, y))

        self.bg_photo = ImageTk.PhotoImage(bg_pattern)
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw", tags="bg")

    def update_ui_state(self):
        if self.use_custom_outline.get():
            self.simple_container.pack_forget()
            self.custom_container.pack(fill=tk.X)
        else:
            self.custom_container.pack_forget()
            self.simple_container.pack(fill=tk.X)
        self.update_preview()

    def choose_color(self):
        color = colorchooser.askcolor(title="Border Color", color=self.current_color)
        if color[0]:
            self.current_color = list(map(int, color[0]))
            self.btn_color.config(bg=color[1])
            self.update_preview()

    def load_base_texture(self):
        path = filedialog.askopenfilename(filetypes=[("PNG Images", "*.png")])
        if not path:
            return

        try:
            img = Image.open(path).convert("RGBA")
            self.base_image = img
            self.base_filename = os.path.basename(path).rsplit(".", 1)[0]

            max_width = img.width // 2
            self.scale_width.configure(to=max_width)
            if self.var_border_width.get() > max_width:
                self.var_border_width.set(max_width)
                self.on_slider_change()

            self.btn_generate.config(state="normal")
            self.update_preview()
            self.status_label.config(text=f"Loaded base: {img.size[0]}x{img.size[1]}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_custom_outline(self):
        if self.base_image is None:
            messagebox.showwarning("Warning", "Please load the Base Texture first.")
            return

        path = filedialog.askopenfilename(filetypes=[("PNG Images", "*.png")])
        if not path:
            return

        try:
            img = Image.open(path).convert("RGBA")
            if img.size != self.base_image.size:
                messagebox.showerror(
                    "Error", f"Size mismatch! Outline must be {self.base_image.size}"
                )
                return

            self.custom_outline_image = img
            self.update_preview()
            self.status_label.config(text="Custom outline loaded.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def get_source_border(self):
        if self.base_image is None:
            return None
        w, h = self.base_image.size

        if self.use_custom_outline.get():
            return (
                self.custom_outline_image
                if self.custom_outline_image
                else Image.new("RGBA", (w, h), (0, 0, 0, 0))
            )
        else:

            img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            c = self.current_color
            color = (c[0], c[1], c[2], self.var_alpha.get())
            bw = self.var_border_width.get()

            draw.rectangle((0, 0, w, bw), fill=color)

            draw.rectangle((0, h - bw, w, h), fill=color)

            draw.rectangle((0, 0, bw, h), fill=color)

            draw.rectangle((w - bw, 0, w, h), fill=color)
            return img

    def create_tile(self, rule):
        if not self.base_image:
            return None
        src_border = self.get_source_border()
        if not src_border:
            return self.base_image.copy()

        w, h = self.base_image.size
        bw = self.var_border_width.get()
        if bw == 0:
            return self.base_image.copy()

        border_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        c_tl, c_tr, c_bl, c_br, e_t, e_r, e_b, e_l = rule

        if c_tl:
            border_layer.paste(src_border.crop((0, 0, bw, bw)), (0, 0))
        if c_tr:
            border_layer.paste(src_border.crop((w - bw, 0, w, bw)), (w - bw, 0))
        if c_bl:
            border_layer.paste(src_border.crop((0, h - bw, bw, h)), (0, h - bw))
        if c_br:
            border_layer.paste(
                src_border.crop((w - bw, h - bw, w, h)), (w - bw, h - bw)
            )

        if e_t:
            border_layer.paste(src_border.crop((bw, 0, w - bw, bw)), (bw, 0))
        if e_r:
            border_layer.paste(src_border.crop((w - bw, bw, w, h - bw)), (w - bw, bw))
        if e_b:
            border_layer.paste(src_border.crop((bw, h - bw, w - bw, h)), (bw, h - bw))
        if e_l:
            border_layer.paste(src_border.crop((0, bw, bw, h - bw)), (0, bw))

        return Image.alpha_composite(self.base_image, border_layer)

    def update_preview(self):
        if self.base_image is None:
            return

        preview_img = self.create_tile(CTM_RULES[0])

        zoom = self.var_zoom.get()
        new_w = int(preview_img.width * zoom * 50)
        new_h = int(preview_img.height * zoom * 50)

        if new_w > 2000:
            new_w = 2000
        if new_h > 2000:
            new_h = 2000

        preview_resized = preview_img.resize((new_w, new_h), Image.Resampling.NEAREST)

        if self.show_guides.get() and self.var_border_width.get() > 0:
            draw = ImageDraw.Draw(preview_resized)
            bw_px = self.var_border_width.get()

            scale = new_w / preview_img.width
            offset = bw_px * scale

            w_px = new_w
            h_px = new_h

            guide_color = "#FF0000"
            line_w = 2

            draw.line([(offset, 0), (offset, h_px)], fill=guide_color, width=line_w)
            draw.line(
                [(w_px - offset, 0), (w_px - offset, h_px)],
                fill=guide_color,
                width=line_w,
            )

            draw.line([(0, offset), (w_px, offset)], fill=guide_color, width=line_w)
            draw.line(
                [(0, h_px - offset), (w_px, h_px - offset)],
                fill=guide_color,
                width=line_w,
            )

        self.preview_image_tk = ImageTk.PhotoImage(preview_resized)

        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        x = max(0, (cw - new_w) // 2)
        y = max(0, (ch - new_h) // 2)

        self.canvas.delete("img")
        self.canvas.create_image(
            x, y, image=self.preview_image_tk, anchor="nw", tags="img"
        )
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def generate_files(self):
        if not self.base_image:
            return
        save_dir = filedialog.askdirectory()
        if not save_dir:
            return

        out_path = os.path.join(save_dir, self.base_filename)
        if not os.path.exists(out_path):
            os.mkdir(out_path)

        self.status_label.config(text="Generating tiles...")
        self.update_idletasks()

        try:
            for i, rule in enumerate(CTM_RULES):
                img = self.create_tile(rule)
                img.save(os.path.join(out_path, f"{i}.png"))

            with open(
                os.path.join(out_path, f"{self.base_filename}.properties"), "w"
            ) as f:
                f.write(f"matchTiles={self.base_filename}\n")
                f.write("method=ctm\n")
                f.write("tiles=0-46\n")

            messagebox.showinfo("Done", f"Success! Saved to:\n{out_path}")
            self.status_label.config(text="Generation Complete")
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    app = CTMGeneratorApp()
    app.mainloop()
