import os
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import instaloader

# Initialize Instaloader
D = instaloader.Instaloader(
    download_videos=False,
    download_video_thumbnails=False,
    download_geotags=False,
    download_comments=False,
    save_metadata=False,
    compress_json=False
)

def load_session(session_username):
    session_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'{session_username}.session')
    try:
        D.load_session_from_file(session_username, session_file)
        print("Session loaded successfully.")
    except FileNotFoundError:
        print("Session file not found. Creating a new one.")
        create_session(session_username)

def create_session(session_username):
    session_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'{session_username}.session')
    password = simpledialog.askstring("Input", f"Enter password for {session_username}:", show='*')
    if password:
        try:
            D.login(session_username, password)
            D.save_session_to_file(session_file)
            messagebox.showinfo("Success", "Session file created and saved successfully.")
        except instaloader.exceptions.ConnectionException as e:
            messagebox.showerror("Login Error", f"Failed to login: {e}")
    else:
        messagebox.showerror("Input Error", "Password is required to create a session file.")

def download_instagram_data(session_username, desired_username, download_dir):
    load_session(session_username)
    
    base_path = os.path.join(download_dir, desired_username)
    posts_path = os.path.join(base_path, 'posts')
    stories_path = os.path.join(base_path, 'stories')
    highlights_path = os.path.join(base_path, 'highlights')
    
    os.makedirs(posts_path, exist_ok=True)
    os.makedirs(stories_path, exist_ok=True)
    os.makedirs(highlights_path, exist_ok=True)

    D.dirname_pattern = posts_path

    try:
        profile = instaloader.Profile.from_username(D.context, desired_username)
        
        # Download posts
        for post in profile.get_posts():
            D.download_post(post, target=posts_path)
        
        # Download stories
        for story in D.get_stories(userids=[profile.userid]):
            for item in story.get_items():
                D.dirname_pattern = stories_path
                D.download_storyitem(item, target=stories_path)
        
        # Download highlights
        for highlight in D.get_highlights(profile):
            highlight_folder = os.path.join(highlights_path, highlight.title)
            os.makedirs(highlight_folder, exist_ok=True)
            for item in highlight.get_items():
                D.dirname_pattern = highlight_folder
                D.download_storyitem(item, target=highlight_folder)
        
        messagebox.showinfo("Success", f"Downloaded all content for user '{desired_username}'")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def browse_directory():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        entry_download_dir.delete(0, tk.END)
        entry_download_dir.insert(0, folder_selected)

def start_download():
    session_username = entry_session_username.get()
    desired_username = entry_desired_username.get()
    download_dir = entry_download_dir.get()

    if not session_username or not desired_username or not download_dir:
        messagebox.showwarning("Input Error", "Please provide session username, desired username, and download directory.")
        return

    download_instagram_data(session_username, desired_username, download_dir)

# Set up the GUI
root = tk.Tk()
root.title("Instagram Downloader")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(padx=10, pady=10)

lbl_session_username = tk.Label(frame, text="Session Username:")
lbl_session_username.grid(row=0, column=0, sticky="e")

entry_session_username = tk.Entry(frame, width=30)
entry_session_username.grid(row=0, column=1, pady=5)

lbl_desired_username = tk.Label(frame, text="Desired Username:")
lbl_desired_username.grid(row=1, column=0, sticky="e")

entry_desired_username = tk.Entry(frame, width=30)
entry_desired_username.grid(row=1, column=1, pady=5)

lbl_download_dir = tk.Label(frame, text="Download Directory:")
lbl_download_dir.grid(row=2, column=0, sticky="e")

current_path = os.path.dirname(os.path.abspath(__file__))
entry_download_dir = tk.Entry(frame, width=30)
entry_download_dir.insert(0, current_path)
entry_download_dir.grid(row=2, column=1, pady=5)

btn_browse = tk.Button(frame, text="Browse", command=browse_directory)
btn_browse.grid(row=2, column=2, padx=5)

btn_download = tk.Button(frame, text="Download", command=start_download)
btn_download.grid(row=3, columnspan=3, pady=10)

root.mainloop()
