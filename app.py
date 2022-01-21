from ast import arg
from hashlib import new
import tkinter as tk
import datetime
import matplotlib

from co2_ampel import get_all_information

matplotlib.use('TkAgg')

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import data_reader


class CO2AmpelGUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.geometry("1000x600+10+10")
        self.title("CO2Ampel")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=5)

        self.module_selector_frame = tk.Frame(self, bg="green")
        self.module_selector_frame.columnconfigure(0, weight=1)
        self.module_selector_frame.grid(row=0, column=0, sticky='nswe')

        self.module_frame = tk.Frame(self)
        self.module_frame.rowconfigure(0, weight=1)
        self.module_frame.columnconfigure(0, weight=1)
        self.module_frame.grid(row=0, column=1, sticky='nswe')

        self.modules = {}
        self.module_selector_buttons = {}

        self.attrs = {}

    def register_module(self, module):
        if module in self.modules:
            print("Module already registered!")
            return

        self.modules[module] = module(self, self.module_frame)
        self.modules[module].grid(row=0, column=0, sticky='nswe')

        self.module_selector_buttons[module] = tk.Button(self.module_selector_frame, text=module.__name__, 
                                                            command=lambda m=module: self.enable_module(m))
        self.module_selector_frame.rowconfigure(len(self.module_selector_buttons) - 1, weight=1)
        self.module_selector_buttons[module].grid(row=len(self.module_selector_buttons) - 1, column=0, sticky='nswe')

    def enable_module(self, module):
        self.active_module = module
        self.modules[module].tkraise()
        print(f"enabling {module}")

    def mainloop(self, *args, **kwargs):
        if len(self.modules):
            self.enable_module(list(self.modules.keys())[0])
        self.update_modules()
        super().mainloop(*args, **kwargs)

    def update_modules(self):
        self.modules[self.active_module].on_update()

        self.after(1000, self.update_modules)

    def set_attr(self, attr, value):
        self.attrs[attr] = value

    def get_attr(self, attr):
        return self.attrs.get(attr)

class AbstractModule(tk.Frame):
    def __init__(self, app, *args, **kwargs):
        self.app = app
        super().__init__(*args, **kwargs)

    def on_update(self):
        pass


app = CO2AmpelGUI()

@app.register_module
class Home(AbstractModule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=2)
        self.columnconfigure(0, weight=1)

        self.text_frame = tk.Frame(self)
        self.text_frame.grid(row=0, column=0, sticky='nswe')
        tk.Label(self.text_frame, text="Welcome to the CO2Ampel", font=('Georgia', 30)).pack(fill=tk.BOTH, expand=1)
        tk.Label(self.text_frame, text="Lorem ipsum bla bla bla", font=('Georgia', 14)).pack(fill=tk.BOTH, expand=1)

        self.config_frame = tk.Frame(self)
        self.config_frame.grid(row=1, column=0, sticky='nswe')

        self.app.set_attr('running', False)

        self.NOT_RUNNING_BUTTON_CONFIG = {
            'text': 'start CO2Ampel',
            'bg': "red"
        }
        self.RUNNING_BUTTON_CONFIG = {
            'text': 'stop CO2Ampel',
            'bg': "green"
        }

        self.run_button = tk.Button(self.config_frame, command=self.on_run_click, **self.NOT_RUNNING_BUTTON_CONFIG)#
        self.run_button.pack()

        self.process_data()

    def on_run_click(self):
        new_state = not self.app.get_attr('running')
        print(new_state)
        self.app.set_attr('running', new_state)
        self.run_button.configure(self.RUNNING_BUTTON_CONFIG if new_state else self.NOT_RUNNING_BUTTON_CONFIG)

    def process_data(self):
        if self.app.get_attr('running'):
            self.app.set_attr('current_data', get_all_information())
            self.app.set_attr('new_data', True)
        self.after(1000*60, self.process_data)
        


@app.register_module
class Plot(AbstractModule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, bg='blue')

        self.figure = Figure()
        self.figure_canvas = FigureCanvasTkAgg(self.figure, self)
        NavigationToolbar2Tk(self.figure_canvas, self)
        self.ax = self.figure.add_subplot()
        self.figure_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

    def on_update(self):
        # self.plot_data()
        print(self.app.get_attr('new_data'))
        if self.app.get_attr('new_data'):
            self.plot_data()
            self.app.set_attr('new_data', False)

    def plot_data(self):
        data = data_reader.read_latest_n_points(10)
        time, distribution, total, gpkwh = data_reader.convert_to_plot_data(data)

        self.ax.clear()

        self.ax.stackplot(time, distribution, labels=["offshore", "onshore", "solar", "conv"])
        self.ax.plot(time, total, label='total')
        self.ax.set_xlabel('time')
        self.ax.set_ylabel('power in GW')
        self.ax.xaxis.set_major_formatter(lambda x, pos: datetime.datetime.fromtimestamp(x).strftime("%H:%M"))

        ax2 = self.ax.twinx()
        ax2.set_ylim(200, 720)
        ax2.plot(time, gpkwh, 'black', label='emission')
        ax2.set_ylabel('g CO2 per kWh')

        self.ax.legend(loc='upper left')
        ax2.legend(loc='upper right')

        self.figure_canvas.draw()


@app.register_module
class Weather(AbstractModule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


if __name__ == "__main__":
    app.mainloop()