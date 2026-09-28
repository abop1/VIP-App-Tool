import flet as ft
import os
import hashlib
import yt_dlp
import subprocess
import math
import uuid

# --- LICENSE KEY SYSTEM ---
SECRET_KEY = "VipShorts2026" # Yeh aapka khufiya password hai

def get_device_id():
    # Mobile ke liye ek pakka Device ID generate karega
    id_file = "device_id.txt"
    if os.path.exists(id_file):
        with open(id_file, "r") as f:
            return f.read().strip()
    new_id = "VIP-" + str(uuid.uuid4().hex[:8]).upper()
    with open(id_file, "w") as f:
        f.write(new_id)
    return new_id

def generate_correct_key(device_id):
    return hashlib.sha256((device_id + SECRET_KEY).encode()).hexdigest()[:10].upper()

# --- MAIN APP UI ---
def main(page: ft.Page):
    page.title = "VIP Shorts Tool"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 400
    page.window_height = 700
    page.padding = 20

    device_id = get_device_id()
    
    # ---------------- UI ELEMENTS ----------------
    # Auth Screen
    auth_title = ft.Text("🔒 VIP License Required", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_400)
    id_text = ft.Text(f"Your Device ID: {device_id}", size=16, selectable=True, color=ft.colors.RED_ACCENT)
    key_input = ft.TextField(label="Enter License Key", password=True, width=300)
    auth_status = ft.Text("", color=ft.colors.RED)
    
    # Downloader Screen
    dl_url = ft.TextField(label="Creator URL (e.g., .../@channel/shorts)", width=350)
    dl_count = ft.TextField(label="Number of Videos", value="5", width=150)
    dl_status = ft.Text("Ready to download.", color=ft.colors.GREY)
    
    # Splitter Screen
    sp_name = ft.TextField(label="Video File Name (e.g., video.mp4)", width=350)
    sp_mode = ft.Dropdown(
        label="Split Mode",
        options=[ft.dropdown.Option("Time (Seconds)"), ft.dropdown.Option("Parts")],
        value="Time (Seconds)",
        width=200
    )
    sp_val = ft.TextField(label="Value (e.g., 15)", value="15", width=100)
    sp_status = ft.Text("Ready to split.", color=ft.colors.GREY)

    # ---------------- LOGIC FUNCTIONS ----------------
    def check_license(e):
        user_key = key_input.value.strip()
        correct_key = generate_correct_key(device_id)
        
        if user_key == correct_key:
            page.views.clear()
            page.views.append(main_view)
            page.update()
        else:
            auth_status.value = "❌ Invalid License Key! Developer se contact karein."
            page.update()

    def run_download(e):
        dl_status.value = "⏳ Downloading... Please wait."
        dl_status.color = ft.colors.YELLOW
        page.update()
        
        try:
            download_dir = "/storage/emulated/0/Download/YT_Shorts"
            os.makedirs(download_dir, exist_ok=True)
            
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
                'download_archive': os.path.join(download_dir, 'history.txt'),
                'outtmpl': os.path.join(download_dir, '%(uploader)s_%(id)s.%(ext)s'),
                'match_filter': yt_dlp.utils.match_filter_func("duration < 65"),
                'playlist_random': True,
                'max_downloads': int(dl_count.value),
                'quiet': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([dl_url.value])
                
            dl_status.value = f"✅ Download Complete! Saved in Downloads/YT_Shorts"
            dl_status.color = ft.colors.GREEN
        except Exception as ex:
            dl_status.value = f"❌ Error: {str(ex)}"
            dl_status.color = ft.colors.RED
        page.update()

    def run_split(e):
        sp_status.value = "⏳ Splitting... Please wait."
        sp_status.color = ft.colors.YELLOW
        page.update()
        
        try:
            download_dir = "/storage/emulated/0/Download/YT_Shorts"
            filepath = os.path.join(download_dir, sp_name.value)
            
            if not os.path.exists(filepath):
                sp_status.value = "❌ File nahi mili. Naam check karein."
                sp_status.color = ft.colors.RED
                page.update()
                return

            val = int(sp_val.value)
            name, ext = os.path.splitext(sp_name.value)
            out_pattern = os.path.join(download_dir, f"{name}_part%03d{ext}")

            if sp_mode.value == "Time (Seconds)":
                segment_time = val
            else:
                cmd_dur = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{filepath}"'
                result = subprocess.run(cmd_dur, shell=True, stdout=subprocess.PIPE, text=True)
                duration = float(result.stdout.strip())
                segment_time = math.ceil(duration / val)

            cmd_split = f'ffmpeg -i "{filepath}" -c copy -map 0 -segment_time {segment_time} -f segment -reset_timestamps 1 "{out_pattern}"'
            subprocess.run(cmd_split, shell=True)
            
            sp_status.value = "✅ Split Complete! Check folder."
            sp_status.color = ft.colors.GREEN
        except Exception as ex:
            sp_status.value = f"❌ Error: {str(ex)}"
            sp_status.color = ft.colors.RED
        page.update()

    # ---------------- VIEWS SETUP ----------------
    # 1. Auth View (Lock Screen)
    auth_view = ft.View(
        "/",
        [
            ft.Column(
                [
                    auth_title,
                    ft.Text("Is software ko chalane ke liye license key darj karein.", color=ft.colors.GREY),
                    ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                    id_text,
                    ft.Text("(Ye ID copy karke Admin ko bhejain)", size=12, color=ft.colors.GREY),
                    ft.Divider(height=10, color=ft.colors.TRANSPARENT),
                    key_input,
                    ft.ElevatedButton("🔓 Unlock App", on_click=check_license, bgcolor=ft.colors.GREEN_700, color=ft.colors.WHITE),
                    auth_status
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        ]
    )

    # 2. Main App View (Tabs)
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="📥 Downloader",
                content=ft.Column([
                    ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                    dl_url,
                    dl_count,
                    ft.ElevatedButton("Start Download", on_click=run_download, bgcolor=ft.colors.BLUE_700, color=ft.colors.WHITE),
                    dl_status
                ], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            ),
            ft.Tab(
                text="✂️ Splitter",
                content=ft.Column([
                    ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                    sp_name,
                    ft.Row([sp_mode, sp_val], alignment=ft.MainAxisAlignment.CENTER),
                    ft.ElevatedButton("Start Split", on_click=run_split, bgcolor=ft.colors.RED_700, color=ft.colors.WHITE),
                    sp_status
                ], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            ),
        ],
        expand=1,
    )

    main_view = ft.View(
        "/main",
        [
            ft.Text("👑 VIP Shorts Manager", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_400),
            tabs
        ]
    )

    # Start with Auth View
    page.views.append(auth_view)
    page.update()

ft.app(target=main)

