import tkinter as tk
from tkinter import messagebox


def report_error(error_message):
    """
    Reports a given error message to the user. There may be different methods of doing this depending on error
    :param error_message: Message to send to user
    """
    # Print pop-up on GUI
    messagebox.showerror('Problem', error_message + "\nProgram will continue after clicking OK")


def report_warning(warning_message):
    """
    Reports a given warning message to the user. There may be different methods of doing this depending on warning
    :param warning_message: Message to send to the user
    """
    # Print pop-up on GUI
    messagebox.showwarning('Warning', warning_message + "\nProgram will continue after clicking OK")