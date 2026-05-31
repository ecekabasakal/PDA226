import tkinter as tk
from tkinter import filedialog, messagebox
import os

from gui import AlbumApp
from gemini_service import GeminiService
from lastfm_service import LastFmService
from image_service import generate_cover
from export_service import export_album_data
from thread_manager import ThreadManager

GEMINI_KEY = "AIzaSyAp0oDRXWZUTwWIAsLrIjrC1ujb-7Uja_M"
LASTFM_KEY = "d63415de4fe8af0899d5165e484f2132"


class ProjectController:
    def __init__(self, root):
        self.root = root

        self.app = AlbumApp(root)
        self.thread_manager = ThreadManager(root)

        self.gemini_service = GeminiService(api_key=GEMINI_KEY)
        self.lastfm_service = LastFmService(api_key=LASTFM_KEY)

        self.current_pil_image = None
        self.current_metadata = None
        self.current_tracklist = None

        self.app.bind_generate(self.start_generation_pipeline)

        if hasattr(self.app, '_export_btn'):
            self.app._export_btn.configure(command=self.handle_export)

    def start_generation_pipeline(self):
        if self.thread_manager.pipeline_running:
            return
        self.app.set_status("Analyzing input & initializing pipeline...")
        self.thread_manager.run_in_background(self.async_network_operations)

    def async_network_operations(self):
        try:
            journal = self.app.get_journal_text()
            genre = self.app.get_genre()
            era = self.app.get_era()
            track_count = self.app.get_track_count()

            if not journal.strip():
                messagebox.showwarning(
                    "Girdi Hatası", "Lütfen önce günlüğünüze bir şeyler yazın!")
                self.app.set_status("Ready.")
                return

            self.app.set_status("Consulting Gemini AI for metadata...")
            self.current_metadata = self.gemini_service.generate_album_metadata(
                journal_text=journal, genre=genre, era=era, track_count=track_count
            )

            if not self.current_metadata:
                raise Exception("Gemini API veri üretemedi.")

            # Last.fm and Pollinations run at the same time
            gemini_tags = self.current_metadata.get("lastfm_tags", [])
            tags = gemini_tags + [genre.lower()]
            cover_prompt = self.current_metadata.get(
                "cover_prompt", "Album cover art")

            def safe_status(message):
                self.thread_manager.update_gui(
                    lambda: self.app.set_status(message))

            def fetch_tracklist():
                self.thread_manager.update_gui(lambda: self.app.set_status(
                    "Fetching tracklist from Last.fm..."))
                self.current_tracklist = self.lastfm_service.generate_tracklist(
                    tags, track_count)

            def fetch_cover():
                self.thread_manager.update_gui(
                    lambda: self.app.set_status("Synthesizing AI cover artwork..."))
                self.current_pil_image = generate_cover(
                    cover_prompt, genre, status_callback=safe_status)

            lastfm_thread = self.thread_manager.run_parallel(fetch_tracklist)
            pollinations_thread = self.thread_manager.run_parallel(fetch_cover)

            # Wait for both to finish before displaying
            lastfm_thread.join()
            pollinations_thread.join()

            self.thread_manager.update_gui(lambda: self.app.display_album(
                metadata=self.current_metadata,
                tracks=self.current_tracklist,
                image=self.current_pil_image
            ))
            self.thread_manager.update_gui(
                lambda: self.app.set_status("Album generation complete!"))

        except Exception as e:
            self.thread_manager.update_gui(lambda: messagebox.showerror(
                "Üretim Hatası", f"İşlem sırasında bir hata meydana geldi:\n{str(e)}"))
            self.thread_manager.update_gui(
                lambda: self.app.set_status("Generation failed."))

    def handle_export(self):
        if not self.current_pil_image or not self.current_metadata:
            messagebox.showwarning(
                "Dışa Aktarım Uyarısı", "Lütfen önce albüm verisi ve kapak resmi üretin!")
            return

        selected_directory = filedialog.askdirectory(
            title="Albümün Aktarılacağı Klasörü Seçin")

        if selected_directory:
            try:
                album_title = self.current_metadata.get(
                    "album_name", "Fictional_Album")

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
                messagebox.showerror(
                    "Kayıt Hatası", f"Dosyalar dışa aktarılamadı:\n{str(e)}")


def main():
    root = tk.Tk()
    controller = ProjectController(root)
    root.mainloop()


if __name__ == "__main__":
    main()
