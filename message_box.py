import traceback


def message_box_error(title, content):
    try:
        import tkinter
        import tkinter.messagebox

        tk_root = tkinter.Tk()
        tk_root.withdraw()
        tkinter.messagebox.showerror(title, content)
        tk_root.destroy()
    except Exception:
        print("Tkinter not found - error message will not be displayed...")
        print(traceback.format_exc())
