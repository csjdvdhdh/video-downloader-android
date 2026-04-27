from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivy.core.window import Window
from kivy.clock import Clock
import yt_dlp
import threading
import os

# حجم النافذة للتجربة على الكمبيوتر
Window.size = (400, 700)

class Content(MDBoxLayout):
    pass

class VideoDownloaderApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"
        self.save_folder = "/storage/emulated/0/Download"
        self.quality = "bestvideo+bestaudio/best"
        self.quality_label = "أفضل جودة"
        self.is_downloading = False
        self.video_info = None
        
        # إنشاء الواجهة
        self.root = MDBoxLayout(orientation='vertical', padding=20, spacing=15,
                                md_bg_color=[0.06, 0.05, 0.07, 1])
        
        self.build_ui()
        return self.root
    
    def build_ui(self):
        # العنوان
        self.root.add_widget(MDLabel(
            text="⬇ Video Downloader",
            font_style="H5",
            halign="center",
            theme_text_color="Custom",
            text_color=[0.64, 0.55, 0.98, 1],
            size_hint_y=None,
            height=50
        ))
        
        # حقل الرابط
        self.url_field = MDTextField(
            hint_text="أدخل رابط الفيديو...",
            mode="rectangle",
            fill_color_normal=[0.09, 0.08, 0.13, 1],
            text_color_normal=[1, 1, 1, 1],
            icon_right="link"
        )
        self.root.add_widget(self.url_field)
        
        # زر جلب المعلومات
        self.fetch_btn = MDRaisedButton(
            text="▶ جلب المعلومات",
            md_bg_color=[0.49, 0.23, 0.93, 1],
            on_release=self.fetch_info,
            size_hint_y=None,
            height=48
        )
        self.root.add_widget(self.fetch_btn)
        
        # معلومات الفيديو
        self.info_label = MDLabel(
            text="العنوان: —\nالقناة: —\nالمدة: —",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=70,
            font_style="Body2"
        )
        self.root.add_widget(self.info_label)
        
        # اختيار الجودة
        self.quality_btn = MDRaisedButton(
            text="أفضل جودة ▾",
            md_bg_color=[0.3, 0.2, 0.5, 1],
            on_release=self.show_quality_menu,
            size_hint_y=None,
            height=48
        )
        self.root.add_widget(self.quality_btn)
        
        # شريط التقدم
        self.progress_bar = MDProgressBar(
            value=0,
            color=[0.49, 0.23, 0.93, 1],
            size_hint_y=None,
            height=8
        )
        self.root.add_widget(self.progress_bar)
        
        # نسبة التحميل
        self.percent_label = MDLabel(
            text="",
            halign="center",
            theme_text_color="Custom",
            text_color=[0.64, 0.55, 0.98, 1],
            size_hint_y=None,
            height=25,
            font_style="Caption"
        )
        self.root.add_widget(self.percent_label)
        
        # حالة التحميل
        self.status_label = MDLabel(
            text="جاهز",
            halign="center",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=25,
            font_style="Caption"
        )
        self.root.add_widget(self.status_label)
        
        # زر التحميل
        self.download_btn = MDRaisedButton(
            text="⬇ ابدأ التحميل",
            md_bg_color=[0.49, 0.23, 0.93, 1],
            on_release=self.start_download,
            size_hint_y=None,
            height=56,
            font_style="Button"
        )
        self.root.add_widget(self.download_btn)
    
    def show_quality_menu(self, instance):
        menu_items = [
            {
                "text": "أفضل جودة",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="bestvideo+bestaudio/best": self.set_quality(x, "أفضل جودة"),
            },
            {
                "text": "1080p",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="bestvideo[height<=1080]+bestaudio/best[height<=1080]": 
                    self.set_quality(x, "1080p"),
            },
            {
                "text": "720p",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="bestvideo[height<=720]+bestaudio/best[height<=720]": 
                    self.set_quality(x, "720p"),
            },
            {
                "text": "480p",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="bestvideo[height<=480]+bestaudio/best[height<=480]": 
                    self.set_quality(x, "480p"),
            },
            {
                "text": "صوت فقط MP3",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="bestaudio/best": self.set_quality(x, "صوت MP3"),
            },
        ]
        self.menu = MDDropdownMenu(
            caller=instance,
            items=menu_items,
            width_mult=4,
        )
        self.menu.open()
    
    def set_quality(self, q, label):
        self.quality = q
        self.quality_label = label
        self.quality_btn.text = f"{label} ▾"
        self.menu.dismiss()
    
    def fetch_info(self, instance):
        url = self.url_field.text.strip()
        if not url:
            self.show_error("أدخل رابطاً صحيحاً")
            return
        
        self.fetch_btn.disabled = True
        self.fetch_btn.text = "⏳ جاري الجلب..."
        self.status_label.text = "جاري جلب المعلومات..."
        
        threading.Thread(target=self._fetch_info_thread, args=(url,), daemon=True).start()
    
    def _fetch_info_thread(self, url):
        try:
            opts = {"quiet": True, "no_warnings": True, "skip_download": True}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
            self.video_info = info
            Clock.schedule_once(lambda dt: self._update_info_ui(info))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.show_error(f"خطأ: {str(e)[:80]}"))
            Clock.schedule_once(lambda dt: self._reset_fetch_btn())
    
    def _update_info_ui(self, info):
        title = info.get("title", "غير معروف")[:60]
        channel = info.get("uploader", info.get("channel", "—"))[:30]
        dur = info.get("duration", 0)
        if dur:
            m, s = divmod(int(dur), 60)
            h, m = divmod(m, 60)
            duration = f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"
        else:
            duration = "—"
        
        self.info_label.text = f"العنوان: {title}\nالقناة: {channel}\nالمدة: {duration}"
        self.status_label.text = "✅ تم جلب المعلومات"
        self._reset_fetch_btn()
    
    def _reset_fetch_btn(self):
        self.fetch_btn.disabled = False
        self.fetch_btn.text = "▶ جلب المعلومات"
    
    def start_download(self, instance):
        if self.is_downloading:
            return
        
        url = self.url_field.text.strip()
        if not url:
            self.show_error("أدخل رابطاً صحيحاً")
            return
        
        self.is_downloading = True
        self.download_btn.disabled = True
        self.download_btn.text = "⏳ جاري التحميل..."
        self.progress_bar.value = 0
        self.percent_label.text = "0%"
        self.status_label.text = "بدء التحميل..."
        
        threading.Thread(target=self._download_thread, args=(url,), daemon=True).start()
    
    def _download_thread(self, url):
        if self.quality_label == "صوت MP3":
            opts = {
                "outtmpl": os.path.join(self.save_folder, "%(title)s.%(ext)s"),
                "format": self.quality,
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
                "progress_hooks": [self.progress_hook],
                "quiet": True,
                "no_warnings": True,
            }
        else:
            opts = {
                "outtmpl": os.path.join(self.save_folder, "%(title)s.%(ext)s"),
                "format": self.quality,
                "merge_output_format": "mp4",
                "progress_hooks": [self.progress_hook],
                "quiet": True,
                "no_warnings": True,
            }
        
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            Clock.schedule_once(lambda dt: self._on_success())
        except Exception as e:
            Clock.schedule_once(lambda dt: self._on_error(str(e)))
    
    def progress_hook(self, d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            downloaded = d.get("downloaded_bytes", 0)
            speed = d.get("speed", 0)
            
            if total > 0:
                percent = (downloaded / total) * 100
                speed_str = self.format_bytes(speed) + "/s" if speed else ""
                
                def update():
                    self.progress_bar.value = percent
                    self.percent_label.text = f"{percent:.1f}%"
                    self.status_label.text = f"⬇ {self.format_bytes(downloaded)} / {self.format_bytes(total)}  {speed_str}"
                
                Clock.schedule_once(lambda dt: update())
        
        elif d["status"] == "finished":
            def update():
                self.status_label.text = "🔄 جاري المعالجة..."
                self.progress_bar.value = 100
                self.percent_label.text = "100%"
            Clock.schedule_once(lambda dt: update())
    
    def _on_success(self):
        self.status_label.text = "✅ اكتمل التحميل!"
        self.download_btn.disabled = False
        self.download_btn.text = "⬇ ابدأ التحميل"
        self.is_downloading = False
        self.show_success("اكتمل التحميل بنجاح! 📁 الملف محفوظ في مجلد التحميلات")
    
    def _on_error(self, error):
        self.status_label.text = f"❌ فشل"
        self.download_btn.disabled = False
        self.download_btn.text = "⬇ ابدأ التحميل"
        self.is_downloading = False
        self.show_error(f"فشل التحميل:\n{error[:100]}")
    
    def show_error(self, msg):
        dialog = MDDialog(
            title="❌ خطأ",
            text=msg,
            buttons=[MDFlatButton(text="حسناً", on_release=lambda x: dialog.dismiss())],
        )
        dialog.open()
    
    def show_success(self, msg):
        dialog = MDDialog(
            title="✅ تم بنجاح",
            text=msg,
            buttons=[MDFlatButton(text="حسناً", on_release=lambda x: dialog.dismiss())],
        )
        dialog.open()
    
    def format_bytes(self, b):
        if not b:
            return "0 B"
        for unit in ("B", "KB", "MB", "GB"):
            if b < 1024:
                return f"{b:.1f} {unit}"
            b /= 1024
        return f"{b:.1f} TB"


if __name__ == "__main__":
    VideoDownloaderApp().run()
