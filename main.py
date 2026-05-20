import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os

from gui import AlbumApp
from GeminiService import GeminiService
from lastfm_service import LastFmService

from image_service import generate_cover
from export_service import export_album_data

try:
    import config
    GEMINI_KEY = getattr(config, "GEMINI_API_KEY", "")
    LASTFM_KEY = getattr(config, "LASTFM_API_KEY", "")
except ImportError:
    GEMINI_KEY = "YOUR_GEMINI_API_KEY"
    LASTFM_KEY = "YOUR_LASTFM_API_KEY"


class ProjectController:
    def __init__(self, root):
        self.root = root
        
        self.app = AlbumApp(root)
        
        self.gemini_service = GeminiService(api_key=GEMINI_KEY)
        self.lastfm_service = LastFmService(api_key=LASTFM_KEY)
        
        self.current_pil_image = None
        self.current_metadata = None
        self.current_tracklist = None
        
        self.app.bind_generate(self.start_generation_pipeline)
        
        if hasattr(self.app, '_export_btn'):
            self.app._export_btn.configure(command=self.handle_export)

    def start_generation_pipeline(self):
        self.app.set_status("Analyzing input & initializing pipeline...")
        worker_thread = threading.Thread(target=self.async_network_operations)
        worker_thread.start()

    def async_network_operations(self):
        try:
            journal = self.app.get_journal_text()
            genre = self.app.get_genre()
            era = self.app.get_era()
            track_count = self.app.get_track_count()
            
            if not journal.strip():
                messagebox.showwarning("Girdi Hatası", "Lütfen önce günlüğünüze bir şeyler yazın!")
                self.app.set_status("Ready.")
                return

            self.app.set_status("Consulting Gemini AI for metadata...")
            self.current_metadata = self.gemini_service.generate_album_metadata(
                journal_text=journal, genre=genre, era=era, track_count=track_count
            )
            
            if not self.current_metadata:
                raise Exception("Gemini API veri üretemedi.")

            self.app.set_status("Fetching synchronized tracklist from Last.fm...")
            gemini_tags = self.current_metadata.get("lastfm_tags", [])
            tags = gemini_tags + [genre.lower()]
            self.current_tracklist = self.lastfm_service.generate_tracklist(tags, track_count)

            self.app.set_status("Synthesizing AI cover artwork...")
            cover_prompt = self.current_metadata.get("cover_prompt", "Album cover art")
            
            self.current_pil_image = generate_cover(cover_prompt, genre, status_callback=self.app.set_status)

            self.app.display_album(
                metadata=self.current_metadata,
                tracks=self.current_tracklist,
                image=self.current_pil_image
            )
            self.app.set_status("Album generation complete!")

        except Exception as e:
            messagebox.showerror("Üretim Hatası", f"İşlem sırasında bir hata meydana geldi:\n{str(e)}")
            self.app.set_status("Generation failed.")

    def handle_export(self):
        if not self.current_pil_image or not self.current_metadata:
            messagebox.showwarning("Dışa Aktarım Uyarısı", "Lütfen önce albüm verisi ve kapak resmi üretin!")
            return
            
        selected_directory = filedialog.askdirectory(title="Albümün Aktarılacağı Klasörü Seçin")
        
        if selected_directory:
            try:
                album_title = self.current_metadata.get("album_name", "Fictional_Album")
                
                json_file, png_file = export_album_data(
                    folder_path=selected_directory,
                    album_name=album_title,
                    metadata=self.current_metadata,
                    tracklist=self.current_tracklist,
                    cover_image=self.current_pil_image,
                    status_callback=self.app.set_status,
                )
                
                messagebox.showinfo(
                    "Dışa Aktarım Başarılı", 
                    f"Albüm verileri başarıyla kaydedildi!\n\n"
                    f"1. Veri Dosyası: {os.path.basename(json_file)}\n"
                    f"2. Kapak Resmi: {os.path.basename(png_file)}"
                )
            except Exception as e:
                messagebox.showerror("Kayıt Hatası", f"Dosyalar dışa aktarılamadı:\n{str(e)}")


def main():
    root = tk.Tk()
    controller = ProjectController(root)
    root.mainloop()

if __name__ == "__main__":
    main()
