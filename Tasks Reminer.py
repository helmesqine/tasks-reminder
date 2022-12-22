import random
import os
import time
from pygame import mixer
from datetime import date as get_date_today
from datetime import datetime as get_datetime
from tkinter import *
from threading import Timer
import tkinter.scrolledtext as tkst
from tkinter import messagebox, ttk
from tkcalendar import Calendar
from PIL import Image as bell_image
from PIL import ImageTk as bell_image_tk
import sqlite3
from tktimepicker import AnalogPicker, AnalogThemes, constants

db_connection = sqlite3.connect('stickynotes.db')
db_cursor = db_connection.cursor()

re = True

x_click1 = 0
y_click1 = 0

no_of_windows = 0
HORIZONTAL = 1
VERTICAL = 2

dark_theme = ['#373737', 'black', '#f2f2ef']
grey_theme = ['#373737', '#a3a3a3', '#f2f2ef']
default_theme = ['#F8F796', '#FDFDCA', 'black']

settings_already_open = False
settings_thread = True
settings_thread_stop = False
cancel_settings = False
all_quit = True
active_tasks = {}
hours_dictionary = {'1': '13', '2': '14', '3': '15', '4': '16', '5': '17', '6': '18', '7': '19', '8': '20',
                    '9': '21',
                    '10': '22', '11': '23', '12': '00', }

hours_dictionary1 = {'13': '1',
                     '14': '2',
                     '15': '3',
                     '16': '4',
                     '17': '5',
                     '18': '6',
                     '19': '7',
                     '20': '8',
                     '21': '9',
                     '22': '10',
                     '23': '11',
                     '00': '12', }


class NotificationSettings(Toplevel):
    def __init__(self, master, task_id, task_text, task_date, task_theme, x, y, **kwargs):
        super().__init__(master, **kwargs)
        self.title("Settings")
        self.configure(background='grey')
        self.iconbitmap('img/icon.ico')
        self.attributes('-topmost', 'true')
        self.resizable(False, False)
        self.overrideredirect(True)
        self.geometry("700x450")

        self.titlebar = Frame(self, bg='#373737', relief='flat', bd=2, height=25, width=700)
        self.titlebar.pack_propagate(False)
        self.titlebar.bind('<Button-1>', self.get_pos)
        self.titlebar.bind('<B1-Motion>', self.move_window)
        self.titlebar.place(x=0, y=0)

        self.task_id = task_id
        self.task_text = task_text
        self.task_date = task_date
        self.task_theme = task_theme
        self.x = x
        self.y = y

        self.x_click2 = 0
        self.y_click2 = 0

        # time
        self.time_frame = Frame(self, width=300, height=300)
        self.time_frame.pack_propagate(False)

        # calendar

        try:
            self.str_date = active_tasks[str(self.task_id)][1].split('#')
            str_time1 = str(self.str_date[1]).split('_')
            if str(self.str_date[2]) == 'PM':
                self.time_picker = AnalogPicker(self.time_frame, period=constants.PM)
                self.theme = AnalogThemes(self.time_picker)
                self.time_picker.setHours(int(str_time1[0]))
                self.time_picker.setMinutes(int(str_time1[1]))
                self.theme.setDracula()
                self.time_picker.pack(fill=BOTH)
            elif str(self.str_date[2]) == 'AM':
                self.time_picker = AnalogPicker(self.time_frame, period=constants.AM)
                self.theme = AnalogThemes(self.time_picker)
                self.time_picker.setHours(int(str_time1[0]))
                self.time_picker.setMinutes(int(str_time1[1]))
                self.theme.setDracula()
                self.time_picker.pack(fill=BOTH)
            self.s_date = str(self.str_date[0]).split('-')
            self.calendar = Calendar(self, selectmode="day", year=int(self.s_date[0]), month=int(self.s_date[1]),
                                     date=int(self.s_date[2]))
            # date format day/month/year
            self.calendar.selection_set(f'{self.s_date[1]}/{self.s_date[2]}/{self.s_date[0]}')

        except:
            min_s = round(int(get_datetime.today().time().minute))
            hour_s = round(int(get_datetime.today().time().hour))
            if int(hour_s) > 12:
                hour_s = hours_dictionary1[str(hour_s)]
                self.time_picker = AnalogPicker(self.time_frame, period=constants.PM)
                self.theme = AnalogThemes(self.time_picker)
                self.theme.setDracula()
                self.time_picker.setMinutes(min_s)
                self.time_picker.setHours(hour_s)
                self.time_picker.pack(fill=BOTH)
            else:
                self.time_picker = AnalogPicker(self.time_frame, period=constants.AM)
                self.theme = AnalogThemes(self.time_picker)
                self.theme.setDracula()
                self.time_picker.setMinutes(min_s)
                self.time_picker.setHours(hour_s)
                self.time_picker.pack(fill=BOTH)

            self.str_date = str(get_date_today.today()).split('-')
            self.calendar = Calendar(self, selectmode="day", year=int(self.str_date[0]), month=int(self.str_date[1]),
                                     date=int(self.str_date[2]))
            # date format day/month/year
            self.calendar.selection_set(f'{self.str_date[1]}/{self.str_date[2]}/{self.str_date[0]}')
        self.time_frame.place(relx=0.72, rely=0.46, anchor='center')
        self.calendar.place(relx=0.25, rely=0.35, anchor='center')

        self.s = ttk.Style()
        self.s.configure('MyOwn.TCheckbutton', background='grey', foreground='white')

        self.save_button = Button(self, text='Save', height=2, width=15, background='white', command=self.save_settings)
        self.btn_quit = Button(self, text='Cancel', height=2, width=15, background='white',
                               command=self.not_quit)

        if str(self.task_theme) == 'default_theme':
            self.checkbox_style_default = IntVar(value=1)
            self.checkbox_style_grey = IntVar(value=0)
            self.checkbox_style_dark = IntVar(value=0)
        elif str(self.task_theme) == 'grey_theme':
            self.checkbox_style_default = IntVar(value=0)
            self.checkbox_style_grey = IntVar(value=1)
            self.checkbox_style_dark = IntVar(value=0)
        elif str(self.task_theme) == 'dark_theme':
            self.checkbox_style_default = IntVar(value=0)
            self.checkbox_style_grey = IntVar(value=0)
            self.checkbox_style_dark = IntVar(value=1)
        else:
            self.checkbox_style_default = IntVar(value=1)
            self.checkbox_style_grey = IntVar(value=0)
            self.checkbox_style_dark = IntVar(value=0)
            active_tasks[str(self.task_id)][2] = 'default_theme'
        self.s.configure('MyOwn1.TCheckbutton', background='black', foreground='#f2f2ef')
        self.s.configure('MyOwn2.TCheckbutton', background='#a3a3a3', foreground='#f2f2ef')
        self.s.configure('MyOwn3.TCheckbutton', background='#FDFDCA', foreground='black')
        self.theme_dark_check = ttk.Checkbutton(self, text='Dark Theme', variable=self.checkbox_style_dark,
                                                command=self.set_theme_dark, style='MyOwn1.TCheckbutton')
        self.theme_grey_check = ttk.Checkbutton(self, text='Grey Theme', variable=self.checkbox_style_grey,
                                                command=self.set_theme_grey, style='MyOwn2.TCheckbutton')
        self.theme_default_check = ttk.Checkbutton(self, text='Default Theme',
                                                   variable=self.checkbox_style_default,
                                                   command=self.set_theme_default, style='MyOwn3.TCheckbutton')

        self.theme_default_check.place(relx=0.15, rely=0.65, anchor='center')
        self.theme_grey_check.place(relx=0.35, rely=0.65, anchor='center')
        self.theme_dark_check.place(relx=0.14, rely=0.75, anchor='center')

        self.save_button.place(relx=0.4, rely=0.9, anchor='center')
        self.btn_quit.place(relx=0.6, rely=0.9, anchor='center')

        self.protocol("WM_DELETE_WINDOW", self.not_quit)

    def move_window(self, event):
        self.geometry('+{0}+{1}'.format(event.x_root - self.x_click2, event.y_root - self.y_click2))

    def OnMotion(self, event):
        x11 = self.winfo_pointerx()
        y11 = self.winfo_pointery()
        x00 = self.winfo_rootx()
        y00 = self.winfo_rooty()
        self.geometry("%sx%s" % ((x11 - x00), (y11 - y00)))
        return

    def get_pos(self, event):
        self.x_click2 = event.x
        self.y_click2 = event.y

    def save_settings(self):
        global settings_thread_stop
        global cancel_settings
        if self.calendar.get_date():
            date_obj1 = get_datetime.strptime(str(self.calendar.get_date()), '%m/%d/%y')
            time_obj1 = self.time_picker.time()
            date_time = str(date_obj1.date()) + '#' + str(time_obj1[0]) + '_' + str(time_obj1[1]) + '#' + str(
                time_obj1[2])
            active_tasks[str(self.task_id)][1] = str(date_time)
            settings_thread_stop = True
            cancel_settings = False
        else:
            save_or_no = messagebox.askyesno('Settings', 'No date and time selected you still wanna save?\n'
                                                         'YES = exit and save settings\n'
                                                         'No = exit and ignor saving')
            if save_or_no:
                settings_thread_stop = True
                cancel_settings = False
            else:
                active_tasks[str(self.task_id)][2] = str(self.task_theme)
                settings_thread_stop = True
                cancel_settings = True

        self.destroy()

    def checkbox_style(self):
        pass

    def not_quit(self):
        global settings_thread_stop
        global cancel_settings
        cancel_settings = True
        settings_thread_stop = True
        self.destroy()

    def set_theme_default(self):
        self.checkbox_style_default.set(1)
        self.checkbox_style_grey.set(0)
        self.checkbox_style_dark.set(0)
        active_tasks[str(self.task_id)][2] = 'default_theme'

    def set_theme_grey(self):
        self.checkbox_style_default.set(0)
        self.checkbox_style_grey.set(1)
        self.checkbox_style_dark.set(0)
        active_tasks[str(self.task_id)][2] = 'grey_theme'

    def set_theme_dark(self):
        self.checkbox_style_default.set(0)
        self.checkbox_style_grey.set(0)
        self.checkbox_style_dark.set(1)
        active_tasks[str(self.task_id)][2] = 'dark_theme'


class StickyNotes(Toplevel):
    def __init__(self, master, task_id, task_text, task_date, task_theme, x, y, saved, **kwargs):
        super().__init__(master, **kwargs)
        self.x_click = 0
        self.y_click = 0
        self.get_x = 0
        self.get_y = 0
        self.task_id = task_id
        self.task_text = task_text
        self.task_date = task_date
        self.task_theme = task_theme
        self.saved = saved
        self.bell_running = True
        self.loop_check = True
        self.already_running = False
        self.loop_alarm = True
        self.not_quit1 = True
        self.kill_bell = None
        self.kill_alarm = None
        self.kill_alarm1 = None
        self.bell_stop = None
        self.bell_label = None
        self.kill_bell = None
        self.mixer = mixer
        self.already_in = []
        self.already_out = []
        self.x = x
        self.y = y
        # master (root) window
        self.overrideredirect(True)
        global no_of_windows
        if str(self.x) != 'None' and str(self.y) != 'None':
            self.geometry(f'250x250+{self.x}+{self.y}')
        elif str(self.x) == 'None' and str(self.y) == 'None':
            self.geometry('250x250+' + str(1000 + no_of_windows * (-30)) + '+' + str(100 + no_of_windows * 20))
        self.config(bg='#FDFDCA')
        self.attributes('-topmost', 'true')

        self.resizable(True, True)

        self.wm_maxsize(650, 650)
        self.wm_minsize(250, 50)

        # set theme
        try:
            if self.task_theme:
                self.theme = globals()[str(self.task_theme)]
            else:
                self.theme = default_theme
        except:
            self.theme = default_theme

        self.bar_color = self.theme[0]
        self.background_color = self.theme[1]
        self.text_color = self.theme[2]

        # titlebar
        self.titlebar = Frame(self, bg=self.bar_color, relief='flat', bd=2, height=30)
        self.titlebar.pack_propagate(False)
        self.titlebar.bind('<Button-1>', self.get_pos)
        self.titlebar.bind('<B1-Motion>', self.move_window)
        self.titlebar.pack(fill=X, expand=1, side=TOP)

        self.close_button = Button(self.titlebar, text='x', bg=self.bar_color, relief='flat', font=('Comic Sans MS', 14)
                                   , activebackground=self.bar_color, command=self.quit_window)
        self.close_button.pack(side=RIGHT)

        self.new_button = Button(self.titlebar, text='+', bg=self.bar_color, relief='flat', font=('Comic Sans MS', 14)
                                 , activebackground=self.bar_color, command=new_note)
        self.new_button.pack(side=LEFT)

        self.setting_button = Button(self.titlebar, text='֍', bg=self.bar_color, relief='flat',
                                     font=('Comic Sans MS', 10), activebackground=self.bar_color,
                                     command=self.settings_running)
        self.setting_button.pack(side=LEFT)

        self.date_area = Label(self.titlebar, background=self.bar_color, foreground='black')
        self.date_area.bind('<Button-1>', self.get_pos)
        self.date_area.bind('<B1-Motion>', self.move_window)
        try:
            if self.task_date or len(self.task_date) != 0:
                self.str_date = str(self.task_date).split('#')
                self.s_time = str(self.str_date[1]).replace("_", ":")
                self.date_area.configure(text=f'{self.str_date[0]} {self.s_time} {self.str_date[2]}')
            else:
                self.date_area.configure(text='')
            self.date_area.place(rely=0.5, relx=0.5, anchor='center')
        except:
            self.date_area.configure(text='')
            self.date_area.place(rely=0.5, relx=0.5, anchor='center')
        # main text area
        self.main_area = tkst.ScrolledText(self, bg=self.background_color, font=('Comic Sans MS', 14), relief='flat',
                                           padx=5, pady=10, foreground=self.text_color)
        try:
            if str(self.task_text) != 'None':
                self.main_area.insert(END, self.task_text)
        except:
            pass
        self.main_area.bind('<KeyRelease>', self.update_text)
        self.main_area.pack(fill=BOTH, expand=1, side=TOP)

        self.grip = ttk.Sizegrip(self)
        self.grip.place(relx=1.0, rely=1.0, anchor="se")
        self.grip.bind("<B1-Motion>", self.OnMotion)

        no_of_windows += 1

        self.bell_image1 = bell_image.open("img/bell_center.png")
        self.bell_image2 = bell_image.open("img/bell_right.png")
        self.bell_image3 = bell_image.open("img/bell_left.png")

        self.new_image1 = bell_image_tk.PhotoImage(self.bell_image1)
        self.new_image2 = bell_image_tk.PhotoImage(self.bell_image2)
        self.new_image3 = bell_image_tk.PhotoImage(self.bell_image3)

        self.bell_stop = Button(self, text='Stop', bg=self.background_color, width=10, height=1,
                                activebackground=self.background_color, command=self.bell_stop_1,
                                highlightthickness=2, highlightbackground=self.bar_color)
        self.bell_label = Label(self, bd=2, background=self.background_color, highlightthickness=2,
                                highlightbackground=self.bar_color)
        self.bell_stop.configure(fg=self.text_color)

        self.saved_area = Button(self.titlebar, background=self.bar_color, bd=0, command=self.sav_options)
        self.saved_area.place(rely=0.53, relx=0.25, anchor='center')
        if str(self.saved) == 'saved':
            self.saved_image1 = bell_image.open("img/saved.png")
            self.new_saved = bell_image_tk.PhotoImage(self.saved_image1)
            self.saved_area.configure(image=self.new_saved)
        elif str(self.saved) == 'not saved':
            self.not_saved_image1 = bell_image.open("img/not_saved.png")
            self.not_new_saved = bell_image_tk.PhotoImage(self.not_saved_image1)
            self.saved_area.configure(image=self.not_new_saved)

        Timer(0, self.check_alarm).start()

    def sav_options(self):
        if str(self.saved) == 'not saved':
            self.saved_image1 = bell_image.open("img/saved.png")
            self.new_saved = bell_image_tk.PhotoImage(self.saved_image1)
            self.saved_area.configure(image=self.new_saved)
            self.saved = 'saved'
            db_cursor.execute(f'''INSERT INTO tasks VALUES ('{str(self.task_id)}', '{active_tasks[str(self.task_id)][0]}', 
                                                            '{active_tasks[str(self.task_id)][1]}', '{active_tasks[str(self.task_id)][2]}', 
                                                            '{active_tasks[str(self.task_id)][3]}', 
                                                            '{active_tasks[str(self.task_id)][4]}')''')
            db_connection.commit()
            active_tasks[str(self.task_id)][-1] = 'saved'
        elif str(self.saved) == 'saved':
            self.not_saved_image1 = bell_image.open("img/not_saved.png")
            self.not_new_saved = bell_image_tk.PhotoImage(self.not_saved_image1)
            self.saved_area.configure(image=self.not_new_saved)
            self.saved = 'not saved'
            db_cursor.execute(f'''DELETE FROM tasks WHERE ID={str(self.task_id)}''')
            db_connection.commit()
            active_tasks[str(self.task_id)][-1] = 'not saved'

    def save_to_db(self):
        db_cursor.execute(f'''DELETE FROM tasks WHERE ID={str(self.task_id)}''')
        db_cursor.execute(f'''INSERT INTO tasks VALUES ('{str(self.task_id)}', '{active_tasks[str(self.task_id)][0]}', 
                                                        '{active_tasks[str(self.task_id)][1]}', '{active_tasks[str(self.task_id)][2]}', 
                                                        '{active_tasks[str(self.task_id)][3]}', 
                                                        '{active_tasks[str(self.task_id)][4]}',)''')
        db_connection.commit()

    def update_text(self, event):
        active_tasks[str(self.task_id)][0] = self.main_area.get('1.0', END)
        db_cursor.execute(f'''UPDATE tasks set TEXT='{self.main_area.get('1.0', END)}' WHERE ID='{str(self.task_id)}' ''')
        db_connection.commit()

    def update_action(self):
        try:
            self.theme = globals()[active_tasks[str(self.task_id)][2]]
            self.setting_button.configure(background=self.theme[0])
            self.close_button.configure(background=self.theme[0])
            self.new_button.configure(background=self.theme[0])
            self.date_area.configure(background=self.theme[0])
            self.titlebar.configure(background=self.theme[0])
            self.bell_stop.configure(background=self.theme[0], highlightthickness=2, highlightbackground=self.theme[0])
            self.bell_label.configure(background=self.theme[1], highlightthickness=2, highlightbackground=self.theme[0])
            self.main_area.configure(foreground=self.theme[2], background=self.theme[1])
            self.saved_area.configure(background=self.theme[0])
        except:
            pass
        try:
            self.str_date = str(active_tasks[str(self.task_id)][1]).split('#')
            self.s_time = str(self.str_date[1]).replace("_", ":")
            self.date_area.configure(text=f'{self.str_date[0]} {self.s_time} {self.str_date[2]}')
            self.loop_alarm = True
            Timer(0, self.check_alarm).start()
        except:
            pass

    def settings_running(self):
        global settings_already_open
        if not settings_already_open:
            self.loop_alarm = False
            self.new_button.configure(state=DISABLED)
            self.close_button.configure(state=DISABLED)
            self.setting_button.configure(state=DISABLED)
            self.main_area.configure(state=DISABLED)
            global settings_thread
            settings_thread = True
            # self.withdraw()
            NotificationSettings(self, self.task_id, active_tasks[str(self.task_id)][0],
                                 active_tasks[str(self.task_id)][1],
                                 active_tasks[str(self.task_id)][2], active_tasks[str(self.task_id)][3],
                                 active_tasks[str(self.task_id)][4])
            settings_already_open = True
            Timer(0, self.threading_settings).start()
        else:
            messagebox.showinfo('Settings', 'settings is already open for another\nnote please close it first')

    def threading_settings(self):
        global settings_thread
        global settings_thread_stop
        global settings_already_open
        global cancel_settings
        while settings_thread:
            if settings_thread_stop:
                # self.deiconify()
                settings_already_open = False
                self.new_button.configure(state=NORMAL)
                self.close_button.configure(state=NORMAL)
                self.setting_button.configure(state=NORMAL)
                self.main_area.configure(state=NORMAL)
                if not cancel_settings:
                    Timer(0, self.update_action).start()
                settings_thread_stop = False
                settings_thread = False
            time.sleep(1)

    def get_pos(self, event):
        self.x_click = event.x
        self.y_click = event.y

    def move_window(self, event):
        active_tasks[str(self.task_id)][3] = event.x_root - self.x_click
        active_tasks[str(self.task_id)][4] = event.y_root - self.y_click
        self.geometry('+{0}+{1}'.format(event.x_root - self.x_click, event.y_root - self.y_click))
        pass

    def quit_window(self):
        global no_of_windows
        self.close_button.config(relief='flat', bd=0)
        if active_tasks[str(self.task_id)][5] != 'saved':
            if messagebox.askyesno('Delete Note?', 'This note is not saved!\n'
                                                   'Are you sure you want to delete it?\n'
                                                   'it gonna be deleted permanently!', parent=self):
                self.loop_alarm = False
                self.bell_running = False
                db_cursor.execute(f'''DELETE FROM tasks WHERE ID={str(self.task_id)}''')
                db_connection.commit()
                try:
                    self.mixer.music.stop()
                except:
                    pass
                self.destroy()
                no_of_windows -= 1
                if no_of_windows == 0:
                    self.not_quit1 = False
                    exit()
                active_tasks.pop(str(self.task_id))
        else:
            db_cursor.execute(
                f'''UPDATE tasks set X='{active_tasks[str(self.task_id)][3]}', 
                    Y='{active_tasks[str(self.task_id)][4]}',
                     DATE='{active_tasks[str(self.task_id)][1]}',
                      THEME='{active_tasks[str(self.task_id)][2]}' WHERE ID='{str(self.task_id)}' ''')

            db_connection.commit()
            self.destroy()
            no_of_windows -= 1
            if no_of_windows == 0:
                self.not_quit1 = False
                self.loop_alarm = False
                root.destroy()

    def OnMotion(self, event):
        x1 = self.winfo_pointerx()
        y1 = self.winfo_pointery()
        x0 = self.winfo_rootx()
        y0 = self.winfo_rooty()
        self.geometry("%sx%s" % ((x1 - x0), (y1 - y0)))
        return

    def before_bell_start(self):
        self.kill_bell = Timer(1, self.bell_start)
        self.kill_bell.start()

    def bell_start(self):
        if not self.already_running:
            self.bell_label.place(relx=0.5, rely=0.5, anchor='center')
            self.bell_stop.place(relx=0.5, rely=0.9, anchor='center')
            self.new_button.configure(state=DISABLED)
            self.close_button.configure(state=DISABLED)
            self.setting_button.configure(state=DISABLED)
            self.main_area.configure(state=DISABLED)
            self.already_running = True
            self.bell_running = True
            Timer(0, self.ringtone_start).start()
            while self.bell_running:
                self.bell_label.configure(image=self.new_image1)
                time.sleep(0.01)
                self.bell_label.configure(image=self.new_image2)
                time.sleep(0.01)
                self.bell_label.configure(image=self.new_image1)
                time.sleep(0.01)
                self.bell_label.configure(image=self.new_image3)
                time.sleep(0.01)

    def bell_stop_1(self):
        try:
            self.bell_running = False
            self.already_running = False
            self.loop_alarm = False
            self.bell_label.place_forget()
            self.bell_stop.place_forget()
            self.kill_bell.cancel()
            self.new_button.configure(state=NORMAL)
            self.close_button.configure(state=NORMAL)
            self.setting_button.configure(state=NORMAL)
            self.main_area.configure(state=NORMAL)
            Timer(0, self.ringtone_stop).start()
            self.already_in.remove(str(self.task_id))
        except:
            pass

    def ringtone_start(self):
        global all_quit
        while self.bell_running:
            self.mixer.init()
            self.mixer.music.load('rain_alarm.wav')
            self.mixer.music.play()
            for sleep in range(30):
                if not self.not_quit1:
                    self.bell_running = False
                    self.loop_alarm = False
                    self.ringtone_stop()
                else:
                    time.sleep(sleep)

    def ringtone_stop(self):
        self.mixer.music.stop()

    def check_alarm(self):
        # print(str(active_tasks[str(self.task_id)][1]))
        if '#' in str(active_tasks[str(self.task_id)][1]):
            while self.loop_alarm:
                str_time_date = str(active_tasks[str(self.task_id)][1]).split('#')
                s_date, s_time, am_pm = str_time_date[0], str(str_time_date[1]).split('_'), str(str_time_date[2])
                if am_pm == 'PM':
                    s_time_pm = hours_dictionary[s_time[0]]
                    target_date = f'{s_date} {s_time_pm}:{s_time[1]}:00'
                else:
                    target_date = f'{s_date} {s_time[0]}:{s_time[1]}:00'
                target_date = get_datetime.strptime(str(target_date), '%Y-%m-%d %H:%M:%S')
                today_is = get_datetime.today()
                delta_is = target_date - today_is
                seconds_is = round(delta_is.total_seconds())
                min_is = round(seconds_is / 60)
                hours_is = round(seconds_is / 3600)
                print(seconds_is)
                if 0 >= seconds_is >= -40:
                    if str(self.task_id) not in self.already_in:
                        print('start bell')
                        self.before_bell_start()
                        self.already_in.append(str(self.task_id))
                elif seconds_is >= 1:
                    if seconds_is > 15:
                        sec = round(((seconds_is / 10) - 1) * 10)
                        for secs in range(sec):
                            if self.not_quit1:
                                time.sleep(1)
                            else:
                                break
                            # else:
                                # break
                    # else:
                elif -60 <= seconds_is <= -40:
                    if str(self.task_id) not in self.already_out:
                        self.bell_stop_1()
                        self.already_out.append(str(self.task_id))
                    if not self.not_quit1:
                        self.loop_alarm = False
                else:
                    try:
                        self.already_out.remove(str(self.task_id))
                    except:
                        pass
                    self.loop_alarm = False


def new_note():
    if no_of_windows > 10:
        messagebox.showinfo('New Note', 'Max note is reached')
        return
    id_generated = random.randint(1, 9999)
    db_cursor.execute(f'''SELECT * FROM tasks WHERE ID={id_generated}''')
    records_check = db_cursor.fetchall()
    if records_check and str(id_generated) in active_tasks:
        new_note()
    else:
        active_tasks[str(id_generated)] = [None, None, None, None, None, 'not saved']
        globals()[str(id_generated)] = StickyNotes(root, id_generated, None, None, None, None, None, 'not saved')


def check_db():
    db_cursor.execute(f'''SELECT * FROM tasks''')
    records = db_cursor.fetchall()
    if records:
        for task in records:
            active_tasks[str(task[0])] = [task[1], task[2], task[3], task[4], task[5], 'saved']
            globals()[str(task[0])] = StickyNotes(root, task[0], task[1], task[2], task[3], task[4], task[5], 'saved')
    else:
        new_note()


root = Tk()
root.withdraw()
check_db()
root.mainloop()