import ast
import csv
import time

from CTkMenuBar import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import CTkMessagebox
import customtkinter as ctk
import numpy as np
import port_search
import pygame
import serial_data
from PIL import Image


class SharedData:
    date = np.array([], dtype=str)
    time_data = np.array([], dtype=float)
    x_data = np.array([], dtype=float)
    y_data = np.array([], dtype=float)
    z_data = np.array([], dtype=float)


class App(ctk.CTk):
    def __init__(self, title, size):
        # main setup
        super().__init__()
        self.title(title)
        self.window_placement(size)
        self.minsize(size[0], size[1])
        self.maxsize(size[0], size[1])
        self.animation = None
        self.iconbitmap('img/wave.ico')
        self.create_parameters()

        # widgets
        self.create_widgets()
        self.button_status = True

        # settings
        self.menu_bar()

        # run
        self.bind("<Destroy>", self.on_destroy)

        self.mainloop()

    def menu_bar(self):
        self.menu = CTkTitleMenu(self)

        self.home_menu = self.menu.add_cascade('Home')
        self.clear_menu = self.menu.add_cascade('Clear', postcommand=lambda: self.scrolled_text.delete('1.0', 'end'))

        self.home_dropdown = CustomDropdownMenu(widget=self.home_menu)
        self.home_dropdown.add_option(option='Analysis Mode', command=lambda: print('Analysis Mode'))
        self.home_dropdown.add_option(option='Experimental Mode', command=lambda: print('Experimental Mode'))
        self.home_dropdown.add_option(option='Load Mode', command=lambda: print('Load Mode'))
        self.home_dropdown.add_separator()
        self.home_dropdown.add_option(option='Settings', command=self.open_settings)

    def open_settings(self):
        self.settings = Settings('Settings', (600, 400), self.refresh_app)

    def create_parameters(self):
        values = ast.literal_eval(load_value(filename))
        # colors
        self.primary_color = values['primary']
        self.secondary_color = values['secondary']
        self.tertiary_color = values['tertiary_color']
        self.x_color = values['x_color']
        self.y_color = values['y_color']
        self.z_color = values['z_color']
        self.border_color = values['border_color']

        # graph
        self.animation = None
        self.running_graph = 'False'
        self.data_points = int(values['data_points'])
        self.enable_notif = values['enable_notif']
        self.enable_graph = 'False'

    def window_placement(self, size):
        window_width = size[0]
        window_height = size[1]
        display_width = self.winfo_screenwidth()
        display_length = self.winfo_screenheight()

        left = 0.5 * (display_width - window_width)
        top = 0.5 * (display_length - window_height)

        self.geometry(f'{window_width}x{window_height}+{int(left)}+{int(top - 50)}')

    def create_widgets(self):
        # create
        self.dropdown_widget()
        self.refresh_button()
        self.command_button()
        self.data_frame = ctk.CTkFrame(self, width=474, height=193, border_width=2, border_color=self.border_color,
                                       fg_color=self.primary_color)
        self.scrolled_text = ScrolledText(self)
        # self.experimental_data()
        self.create_figure()  # Move this line before placing the widgets
        # place
        self.dropdown.place(x=17, y=16)
        self.refresh.place(x=265, y=16)
        self.command_but.place(x=683, y=481)
        self.scrolled_text.place(x=17, y=83)
        self.graph_frame.place(x=534, y=16)
        self.data_frame.place(x=534, y=593)

    def dropdown_widget(self):
        self.combo_var = ctk.StringVar(value='COM PORT')
        self.dropdown = ctk.CTkComboBox(self, variable=self.combo_var, state='readonly', width=229, height=44,
                                        values=port_search.port_search(), command=self.combobox_event,
                                        fg_color=self.primary_color, button_hover_color='#144870',
                                        dropdown_hover_color='#144870')

    def refresh_button(self):
        self.refresh_ico = Image.open('img\\refresh.png').resize((44, 44))
        self.refresh_ico_ctk = ctk.CTkImage(dark_image=self.refresh_ico)

        self.refresh = ctk.CTkButton(self, width=44, height=44, fg_color=self.secondary_color,
                                     border_color=self.border_color,
                                     border_width=2, text=None, image=self.refresh_ico_ctk, command=self.refresh_event)

    def refresh_event(self):
        print(port_search.port_search())
        self.dropdown.configure(values=port_search.port_search())
        self.dropdown.set('COM PORT')
        self.scrolled_text.delete('1.0', 'end')

    def command_button(self):
        self.command_text = ctk.StringVar(value='START')
        self.command_but = ctk.CTkButton(self, width=176, height=44, fg_color=self.secondary_color,
                                         border_color=self.border_color,
                                         border_width=2, textvariable=self.command_text, command=self.command_event)

    def command_event(self):

        self.port_val = self.dropdown.get()
        if self.port_val not in ['COM PORT', 'COM1']:
            print('sigma identified')
            if self.command_text.get() == 'START':
                with open('txt/settings.txt', 'w') as f:
                    values['button_event'] = 'True'
                    f.write(str(values))
                self.command_text.set('STOP')
                self.start_time = time.time()
                self.scrolled_text.enable_text()
                # self.mr.configure(text='N/A')
                self.start_animation()
            else:
                with open('txt/settings.txt', 'w') as f:
                    values['button_event'] = 'False'
                    f.write(str(values))
                time_object = time.localtime()
                local_time = time.strftime("%m-%d-%Y %H-%M-%S", time_object)
                with open(f'data/{local_time}.csv', 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Date', 'Time', 'X', 'Y', 'Z'])
                    for d, t, x,y,z in zip(SharedData.date, SharedData.time_data, SharedData.x_data,SharedData.y_data,SharedData.z_data):
                        writer.writerow([d, t, x,y,z])
                    # max_resultant = self.mr.cget('text')
                    # intensity_level = self.intensity.cget('text')
                    # writer.writerow([max_resultant,intensity_level])
                    self.end_time = time.time()
                    print(f'\n{(self.end_time - self.start_time) - 3.58}')
                    if values['enable_notif'] == 'True':
                        CTkMessagebox.show_info('Gyatt..', 'CSV File saved in OHIO /data folder.')

                self.command_text.set('START')
                self.scrolled_text.enable_text()
                self.reset_graph()
        else:
            CTkMessagebox.show_warning('Erm.. What the sigma', 'Rizz not Identified', 'Bye Bye')
            self.after(50, self.play_error)

    def play_error(self):
        pygame.mixer.music.load('aud\\special_error.mp3')
        pygame.mixer.music.play(0)

    def combobox_event(self, choice):
        self.port_val = self.dropdown.get()
        with open('txt/com_port.txt', 'w') as f:
            f.write(self.port_val)
            print(f'com_port saved: {self.port_val}')

    def create_figure(self):
        self.graph_frame = ctk.CTkFrame(self, width=474, height=394, border_width=2, border_color=self.border_color,
                                        fg_color=self.primary_color)

        self.fig = Figure(figsize=(4.7, 3.9), dpi=100, facecolor='#1d1e1e')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(self.primary_color)
        self.ax.tick_params(colors=self.tertiary_color)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(expand=True, padx=5, pady=5)

        self.date = np.array([], dtype=str)
        self.time_data = np.array([], dtype=float)
        self.x_data = np.array([], dtype=float)
        self.y_data = np.array([], dtype=float)
        self.z_data = np.array([], dtype=float)


    def start_animation(self):
        self.ax.clear()
        self.line, = self.ax.plot([], [])
        self.canvas.draw()
        print(self.running_graph)

    def update_graph(self, frame):
        self.ax.clear()
        # self.mr.configure(text=np.max(self.y_data))
        # self.configure_intensity(np.max(self.y_data))

    def reset_graph(self):
        self.ax.clear()
        self.canvas.draw()

    def on_destroy(self, event):
        if event.widget == self:
            print("Window destroyed")
            with open('txt/com_port.txt', 'w') as f:
                f.write('COM1')

    def experimental_data(self):

        self.mr_label = ctk.CTkLabel(self, text='Max Resultant:', text_color=self.tertiary_color, width=188, height=47,
                                     font=('Montserrat', 16, 'bold'), fg_color=self.primary_color)
        self.int_label = ctk.CTkLabel(self, text='Intensity:', text_color=self.tertiary_color, width=188, height=47,
                                      font=('Montserrat', 16, 'bold'), fg_color=self.primary_color)
        self.mr = ctk.CTkLabel(self, text='N/A', text_color=self.tertiary_color,
                               font=('Montserrat', 16, 'bold'), fg_color=self.primary_color)
        self.intensity = ctk.CTkLabel(self, text='N/A', text_color=self.tertiary_color,
                                      font=('Montserrat', 16, 'bold'), fg_color=self.primary_color)

        self.mr.place(x=832, y=637)
        self.mr_label.place(x=576, y=629)
        self.int_label.place(x=576, y=703)
        self.intensity.place(x=832, y=711)

    def configure_intensity(self, value):
        match value:
            case _ if 0.0276 < value < 0.115:
                self.intensity.configure(text='V')

            case _ if 0.115 < value < 0.215:
                self.intensity.configure(text='VI')

            case _ if 0.215 < value < 0.401:
                self.intensity.configure(text='VII')

            case _ if 0.401 < value < 0.747:
                self.intensity.configure(text='VIII')

            case _ if 0.747 < value < 1.39:
                self.intensity.configure(text='IX')

            case _ if value > 1.39:
                self.intensity.configure(text='X+')

            case _:
                self.intensity.configure(text='N/A')

    def refresh_app(self):
        self.create_parameters()
        self.create_widgets()


class ScrolledText(ctk.CTkTextbox):
    def __init__(self, parent):
        super().__init__(master=parent, width=467, height=703, border_color=values['border_color'], border_width=2,
                         fg_color=values['primary'])

    def enable_text(self):
        command_status = values['button_event']

        if command_status == 'True':
            hyphen_count = (104 - len('Flushing Data')) // 2
            hyphens = '-' * hyphen_count
            self.insert('end', f'{hyphens}Flushing Data{hyphens}\n\n')
            serial_data.flush_data()
            serial_data.flush_data()
            hyphen_count = (105 - len('Status: Ready!')) // 2
            hyphens = '-' * hyphen_count
            self.insert('end', f'{hyphens}Status: Ready!{hyphens}\n\n')
            self.update_textbox(1)
        else:
            hyphen_count = (98 - 20) // 2
            hyphens = '-' * hyphen_count
            self.insert('end', f'\n{hyphens}Data Stream Stopped!{hyphens}\n\n')
            self.update_textbox(1)

    def update_textbox(self, value):
        command_status = values['button_event']
        if command_status == 'True':
            date, time_val, x_val, y_val, z_val = serial_data.read_and_process_data()
            data_text = f"Date: {date}, Time: {time_val}, X: {x_val}, Y: {y_val}, Z: {z_val}\n"

            SharedData.date = np.append(SharedData.date, date)
            SharedData.time_data = np.append(SharedData.time_data, time_val)
            SharedData.x_data = np.append(SharedData.x_data, x_val)
            SharedData.y_data = np.append(SharedData.y_data, y_val)
            SharedData.z_data = np.append(SharedData.z_data, z_val)

            self.insert('end', f'{data_text}\n')
            self.after(1, self.update_textbox, self)
            self.see('end')


class Settings(ctk.CTkToplevel):

    apply = None

    def __init__(self, title, size, refresh):
        super().__init__()
        self.title(title)
        self.window_placement(size)
        self.minsize(size[0], size[1])
        self.maxsize(size[0], size[1])
        self.after(250, lambda: self.iconbitmap('img/wave.ico'))

        self.create_parameters()
        self.create_widgets()

        self.refresh = refresh

    def window_placement(self, size):
        window_width = size[0]
        window_height = size[1]
        display_width = self.winfo_screenwidth()
        display_length = self.winfo_screenheight()

        left = 0.5 * (display_width - window_width)
        top = 0.5 * (display_length - window_height)

        self.geometry(f'{window_width}x{window_height}+{int(left)}+{int(top - 50)}')

    def create_parameters(self):
        values = ast.literal_eval(load_value(filename))
        print(values)
        # colors
        self.primary_color = values['primary']
        self.secondary_color = values['secondary']
        self.tertiary_color = values['tertiary_color']
        self.x_color = values['x_color']
        self.y_color = values['y_color']
        self.z_color = values['z_color']
        self.border_color = values['border_color']

    def create_widgets(self):
        #Labels
        self.general_label = ctk.CTkLabel(self, anchor='center', text='General', text_color=self.tertiary_color,
                                          font=('Montserrat', 14, 'bold'))
        self.general_label.place(x=268, y=20)

        self.colors_label = ctk.CTkLabel(self, anchor='center', text='Colors', text_color=self.tertiary_color,
                                         font=('Montserrat', 14, 'bold'))
        self.colors_label.place(x=272, y=191)

        #Frames
        self.general_section = ctk.CTkFrame(self, fg_color=self.primary_color, border_color=self.border_color,
                                            border_width=1, width=505, height=143)
        self.general_section.place(x=47, y=47)

        self.color_section = ctk.CTkFrame(self, fg_color=self.primary_color, border_color=self.border_color,
                                          border_width=1, width=505, height=130)
        self.color_section.place(x=47, y=218)

        #Apply and Cancel Buttons
        self.apply_button()
        self.cancel_button()

        #Frame Widgets
        self.general_widgets()
        self.colors_widgets()

    def apply_button(self):
        self.apply = ctk.CTkButton(self, width=91, height=29, fg_color=self.secondary_color,
                                   border_color=self.border_color,
                                   border_width=2, text='Apply', font=('Montserrat', 12, 'bold'),
                                   state='disabled', command=self.apply_event)
        Settings.apply = self.apply

        self.apply.place(x=385, y=357)

    def cancel_button(self):
        self.cancel = ctk.CTkButton(self, width=91, height=29, fg_color=self.secondary_color,
                                    border_color=self.border_color,
                                    border_width=2, text='Cancel', font=('Montserrat', 12, 'bold'),
                                    command=self.cancel_event)

        self.cancel.place(x=497, y=357)

    def general_widgets(self):
        values = ast.literal_eval(load_value(filename))
        # <editor-fold desc="Graph Check">
        self.graph_var = ctk.StringVar(value=values['enable_graph'])
        self.graph_check = ctk.CTkCheckBox(self.general_section, width=142, height=20, checkbox_width=20,
                                           checkbox_height=20, border_width=2, border_color=self.border_color,
                                           text='Enable Graph', font=('Montserrat', 12, 'bold'),
                                           variable=self.graph_var, onvalue='True', offvalue='False',
                                           state='disabled')
        self.graph_check.place(x=22, y=23)
        # </editor-fold>

        # <editor-fold desc="Rolling Check">

        self.running_var = ctk.StringVar(value=values['enable_running'])
        self.running_graph_check = ctk.CTkCheckBox(self.general_section, width=142, height=20, checkbox_width=20,
                                                   checkbox_height=20, border_width=2, border_color=self.border_color,
                                                   text='Enable Rolling Graph', font=('Montserrat', 12, 'bold'),
                                                   variable=self.running_var, onvalue='True', offvalue='False',
                                                   state='disabled')
        if self.graph_check.get() != 'True':
            self.running_graph_check.configure(state='disabled')
            self.running_var.set('False')
        self.running_graph_check.place(x=22, y=62)
        # </editor-fold>

        # <editor-fold desc="Notif Check">
        self.csv_var = ctk.StringVar(value=values['enable_notif'])
        self.enable_csv_check = ctk.CTkCheckBox(self.general_section, width=142, height=20, checkbox_width=20,
                                                checkbox_height=20, border_width=2, border_color=self.border_color,
                                                text='Enable CSV Notification', font=('Montserrat', 12, 'bold'),
                                                variable=self.csv_var, onvalue='True', offvalue='False',
                                                command=self.csv_check_event)
        self.enable_csv_check.place(x=22, y=101)
        # </editor-fold>

        # <editor-fold desc="Brain Rot Check">
        self.brainrot_var = ctk.StringVar(value=values['enable_brain_rot'])
        self.enable_brainrot_check = ctk.CTkCheckBox(self.general_section, width=142, height=20, checkbox_width=20,
                                                     checkbox_height=20, border_width=2, border_color=self.border_color,
                                                     text='Enable BrainRot', font=('Montserrat', 12, 'bold'),
                                                     variable=self.brainrot_var, onvalue='True', offvalue='False',
                                                     command=self.brain_rot_check_event)
        self.enable_brainrot_check.place(x=296, y=23)
        # </editor-fold>

        # <editor-fold desc="Data Points">
        self.data_points_input = EntryWidget(parent=self.general_section, text='Data Points',
                                             entry_color=values['tertiary_color'], key='data_points',
                                             name='Data Points')

        self.data_points_input.place(x=296, y=62)
        # </editor-fold>

    def colors_widgets(self):
        self.primary_entry = EntryWidget(self.color_section, text='Primary', entry_color=self.primary_color,
                                         key='primary', name='Primary Color')
        self.primary_entry.place(x=22, y=11)

        self.secondary_entry = EntryWidget(self.color_section, text='Secondary', entry_color=self.secondary_color,
                                           key='secondary', name='Secondary Color')
        self.secondary_entry.place(x=22, y=40)

        self.tertiary_entry = EntryWidget(self.color_section, text='Tertiary', entry_color=self.tertiary_color,
                                          key='tertiary_color', name='Tertiary Color')
        self.tertiary_entry.place(x=22, y=69)

        self.border_entry = EntryWidget(self.color_section, text='Border', entry_color=self.border_color,
                                        key='border_color', name='Border Color')
        self.border_entry.place(x=22, y=98)

        self.x_entry = EntryWidget(self.color_section, text='X', entry_color=self.x_color, key='x_color',
                                   name='X Color')
        self.x_entry.place(x=296, y=11)

        self.y_entry = EntryWidget(self.color_section, text='Y', entry_color=self.y_color, key='y_color',
                                   name='Y Color')
        self.y_entry.place(x=296, y=40)

        self.z_entry = EntryWidget(self.color_section, text='Z', entry_color=self.z_color, key='z_color',
                                   name='Z Color')
        self.z_entry.place(x=296, y=69)

    def csv_check_event(self):
        values['enable_notif'] = self.enable_csv_check.get()
        print(f'Enable Rolling Graph set to {values['enable_notif']}!')
        self.apply.configure(state='normal')

    def brain_rot_check_event(self):
        values['enable_brain_rot'] = self.enable_brainrot_check.get()
        print(f'Enable Brain Rot set to {values['enable_brain_rot']}!')
        self.apply.configure(state='normal')

    def cancel_event(self):
        values = ast.literal_eval(load_value(filename))
        print(values)
        self.destroy()

    def apply_event(self):
        save_value(str(values), filename)
        print(f'Current Values: {values}')
        self.destroy()
        self.refresh()


class EntryWidget(ctk.CTkFrame):
    def __init__(self, parent, text, entry_color, key, name):
        super().__init__(master=parent, fg_color='transparent', height=22)
        self.text = text
        self.entry_color = entry_color
        self.key = key
        self.name = name

        self.label()
        self.entry()
        self.input.bind('<KeyPress-Return>',
                        lambda event, key=self.key, name=self.name: self.save_entry(key=key, name=name))

    def label(self):
        self.text_label = ctk.CTkLabel(self, text=self.text, anchor='nw', text_color=values['tertiary_color'],
                                       font=('Montserrat', 12, 'bold'))
        self.text_label.place(x=0, y=0)

    def entry(self):
        if self.key == 'data_points':
            self.input = ctk.CTkEntry(self, fg_color='transparent', width=105, height=18, text_color=self.entry_color,
                                      placeholder_text=values['data_points'], state='disabled')
            self.input.place(x=83, y=0)
        else:
            self.input = ctk.CTkEntry(self, fg_color='transparent', width=105, height=18, text_color=self.entry_color, placeholder_text_color=self.entry_color, placeholder_text='#HEXCODE',  font=('Montserrat', 12, 'bold'))
            self.input.place(x=83, y=0)

    def save_entry(self, dum=None, key=None, name=None):
        Settings.apply.configure(state='normal')
        values[key] = self.input.get()
        if key != 'data_points':
            self.entry_color = values[key]
        else:
            val = values[key]
            if not val.isdigit():
                CTkMessagebox.show_warning('Erm.. What the sigma', 'SKIBIDI DATA POINTS WRONG', 'Bye Bye')
                self.after(50, App.play_error(App))
        try:
            self.input.configure(text_color=self.entry_color)
        except:
            Settings.apply.configure(state='disabled')
            CTkMessagebox.show_warning('Erm.. What the sigma', 'SKIBIDI COLOR WRONG', 'Bye Bye')
            self.after(50, App.play_error(App))
        else:
            print(self.entry_color)
            print(f'Enable {name} set to {values[key]}!')
            Settings.apply.configure(state='normal')


def load_value(filename):
    with open(filename, 'r') as f:
        item = f.read()
    return item


def save_value(input_value, filename):
    with open(filename, 'w') as f:
        f.write(input_value)




if __name__ == '__main__':
    filename = 'txt/settings.txt'
    pygame.mixer.init()

    values = ast.literal_eval(load_value(filename))
    print(f'Loaded Settings: {values}')

    App('EMS v0.2b: Experimental ', (1025, 802))
    print(port_search.port_search())
