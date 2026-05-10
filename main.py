import tkinter as tk
from gui import AlbumApp

def main():
    root = tk.Tk()
    app = AlbumApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()