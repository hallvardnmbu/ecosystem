"""
Provides a Graphical User Interface (GUI) for the simulation of an ecosystem.
"""


# Here ChatGPT (mostly), Stackoverflow, google and relevant documentation was used in order to
# create the GUI. I could not have done this without these tools.


import tkinter as tk
import tkinter.messagebox as messagebox
import re

from simulation import BioSim


class BioSimGUI(tk.Tk):
    """
    Graphical User Interface (GUI) superclass for the simulation of an ecosystem.

    Contains information about the map and the population of animals to be simulated.
    """
    def __init__(self, map_size=15):
        super().__init__()
        self.title("Model herbivores and carnivores on an island")

        self.island = ["W" * map_size for _ in range(map_size)]
        self.population = []
        self.colours = {"W": "#95CBCC",
                        "H": "#E8EC9E",
                        "L": "#B9D687",
                        "D": "#FFEEBA"}

        self.pages = {"Draw": Draw(self),
                      "Populate": Populate(self),
                      "Parameters": Parameters(self)}
        self.pages["Draw"].pack()


class Draw(tk.Frame):
    """
    Page in the GUI for drawing the map.
    """
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master

        self._size = 30

        self.selected = tk.StringVar()
        self.drawing = False

        self.canvas = tk.Canvas(self)

        self.terrain = tk.Frame(self)
        self.terrain.pack(side=tk.RIGHT, padx=10)

        self.buttons()
        self.draw()

        self.canvas.bind("<Button-1>", self.click)
        self.canvas.bind("<Button-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.continue_drawing)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)

    def buttons(self):
        """
        Create buttons for selecting terrain types to draw.
        """
        finished_button = tk.Button(self,
                                    text="Continue",
                                    width=7,
                                    command=self.finished_drawing)
        finished_button.place(anchor="ne", relx=1, rely=0, x=-10, y=10)

        terrain_label = tk.Label(self.terrain,
                                 text="Draw with:")
        terrain_label.pack(pady=5)
        terrain_types = ["Water",
                         "Highland",
                         "Lowland",
                         "Desert"]
        for terrain in terrain_types:
            button = tk.Radiobutton(self.terrain,
                                    text=terrain,
                                    variable=self.selected,
                                    value=terrain[0])
            button.pack(pady=5, anchor="w")

        increase_button = tk.Button(self,
                                    text="Increase",
                                    width=7,
                                    command=self.increase_map_size)
        increase_button.place(anchor="se", relx=1.0, rely=1.0, x=-10, y=-50)

        decrease_button = tk.Button(self,
                                    text="Decrease",
                                    width=7,
                                    command=self.decrease_map_size)
        decrease_button.place(anchor="se", relx=1.0, rely=1.0, x=-10, y=-15)

    def draw(self):
        """
        Draw the initial map to be drawn on.
        """
        self.canvas.delete("all")
        self._canvas()

        for x, row in enumerate(self.master.island):
            for y, terrain in enumerate(row):
                color = self.master.colours[terrain]

                self.canvas.create_rectangle(x * self._size,
                                             y * self._size,
                                             (x + 1) * self._size,
                                             (y + 1) * self._size,
                                             fill=color,
                                             tags=f"cell_{x}_{y}")

    def _canvas(self):
        """
        Configure the canvas.
        """
        self._width = len(self.master.island[0])
        self._height = len(self.master.island)
        self.width = self._width * self._size
        self.height = self._height * self._size

        self.canvas.config(width=self.width, height=self.height)
        self.canvas.pack(side=tk.LEFT, padx=10)

    def click(self, event):
        """
        Handle clicks on the map.
        """
        x = event.x // self._size
        y = event.y // self._size

        if x < 0 or x >= self._width or y < 0 or y >= self._height:
            return

        if self.selected:
            self.update_cell_terrain(x, y, self.selected)

    def start_drawing(self, event):
        """
        Start drawing when the left mouse button is pressed.
        """
        self.drawing = True
        self.update_cell_terrain(event)

    def continue_drawing(self, event):
        """
        Continue drawing when the left mouse button is pressed and is dragged.
        """
        if self.drawing:
            self.update_cell_terrain(event)

    def stop_drawing(self, _):
        """
        Stop drawing when the left mouse button is released.
        """
        self.drawing = False

    def update_cell_terrain(self, event):
        """
        Update the terrain of the cell based on the drawn terrain type.
        """
        if self.selected:
            x = event.x // self._size
            y = event.y // self._size

            if 1 <= x < self._width-1 and 1 <= y < self._height-1:
                terrain = self.selected.get()

                # Inserts the new letter into the string at the position it is drawn:
                new = self.master.island[x][:y] + terrain + self.master.island[x][y+1:]
                self.master.island[x] = new

                color = ""
                if terrain == "W":
                    color = "#95CBCC"
                elif terrain == "H":
                    color = "#E8EC9E"
                elif terrain == "L":
                    color = "#B9D687"
                elif terrain == "D":
                    color = "#FFEEBA"

                self.canvas.create_rectangle(
                    x * self._size,
                    y * self._size,
                    (x + 1) * self._size,
                    (y + 1) * self._size,
                    fill=color)

    def finished_drawing(self):
        """
        Switch to the AddAnimals page.
        """
        self.master.pages["Draw"].pack_forget()
        # When navigating to "Populate" from drawing, a fresh simulation is initiated. This is
        # done in case you for instance draw water where animals currently are residing. This is
        # not strictly necessary, seeing as animals in 'W' can't move and will die due to lack of
        # food, but is done to clean up the visualisation window, without the user having to
        # click the reset button manually.
        self.master.pages["Populate"].__init__(self.master)
        self.master.pages["Populate"].pack()

    def increase_map_size(self):
        """
        Increase the size of the map.
        """
        if len(self.master.island[0]) + 2 < 35:
            new = ["W" * (len(self.master.island[0]) + 2)]
            for row in self.master.island:
                _row = "W" + row + "W"
                new.append(_row)
            new.append("W" * (len(self.master.island[0]) + 2))

            self.master.island = new

            self.draw()
        else:
            messagebox.showinfo("Error", "A bigger map is being prevented.")

    def decrease_map_size(self):
        """
        Decrease the size of the map.
        """
        if len(self.master.island[0]) - 2 > 12:
            new = ["W" * (len(self.master.island[0]) - 2)]
            for row in self.master.island[2:-2]:
                _row = "W" + row[2:-2] + "W"
                new.append(_row)
            new.append("W" * (len(self.master.island[0]) - 2))

            self.master.island = new

            self.draw()
        else:
            messagebox.showinfo("Error", "A smaller map is being prevented.")


class Populate(tk.Frame):
    """
    Page in the GUI for adding a population of animals to the map.
    """
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master

        self.selected_cell = tk.Variable(value=None)

        self._size = 30
        self.grid_width = len(self.master.island[0])
        self.grid_height = len(self.master.island)
        map_size = self.grid_width + 1

        canvas_width = self.grid_width * self._size
        canvas_height = self.grid_height * self._size

        canvas = tk.Canvas(self, width=canvas_width, height=canvas_height)
        canvas.grid(row=1, column=0, columnspan=map_size, padx=5, pady=5, sticky="w")

        # Visualise the map:
        for x, row in enumerate(self.master.island):
            for y, terrain in enumerate(row):
                color = self.master.colours[terrain]

                canvas.create_rectangle(x * self._size,
                                        y * self._size,
                                        (x + 1) * self._size,
                                        (y + 1) * self._size,
                                        fill=color,
                                        tags=f"cell_{x}_{y}")
                canvas.tag_bind(f"cell_{x}_{y}", "<Button-1>", self._handle_click)

        self.validate_integer_cmd = (self.register(self._validate_integer), '%P')
        self.validate_float_cmd = (self.register(self._validate_float), '%P')

        self.species_var = tk.StringVar()
        species_label = tk.Label(self, text="Species:")
        species_label.grid(row=1, column=1 + map_size, padx=5, pady=5)
        herbivore_button = tk.Radiobutton(self, text="Herbivore", variable=self.species_var,
                                          value="Herbivore")
        herbivore_button.grid(row=1, column=2 + map_size, padx=5, pady=5)
        carnivore_button = tk.Radiobutton(self, text="Carnivore", variable=self.species_var,
                                          value="Carnivore")
        carnivore_button.grid(row=1, column=3 + map_size, padx=5, pady=5)

        age_label = tk.Label(self, text="Age:")
        age_label.grid(row=1, column=4 + map_size, padx=5, pady=5)
        self.age_entry = tk.Entry(self, width=5)
        self.age_entry.grid(row=1, column=5 + map_size, padx=5, pady=5)
        self.age_entry.config(validate="key", validatecommand=self.validate_integer_cmd)

        weight_label = tk.Label(self, text="Weight:")
        weight_label.grid(row=1, column=6 + map_size, padx=5, pady=5)
        self.weight_entry = tk.Entry(self, width=5)
        self.weight_entry.grid(row=1, column=7 + map_size, padx=5, pady=5)
        self.weight_entry.config(validate="key", validatecommand=self.validate_float_cmd)

        n_animals_label = tk.Label(self, text="# animals:")
        n_animals_label.grid(row=1, column=8 + map_size, padx=5, pady=5)
        self.n_animals_entry = tk.Entry(self, width=5)
        self.n_animals_entry.grid(row=1, column=9 + map_size, padx=5, pady=5)
        self.n_animals_entry.config(validate="key", validatecommand=self.validate_integer_cmd)

        add_button = tk.Button(self, text="Add", command=self.add_info)
        add_button.grid(row=1, column=10 + map_size, padx=5, pady=5)

        button_back = tk.Button(self,
                                text="Draw",
                                width=7,
                                command=lambda: self.navigate_page_draw())
        button_back.grid(row=0, column=9 + map_size, padx=5, pady=5)
        button_next = tk.Button(self,
                                text="Parameters",
                                width=7,
                                command=lambda: self.navigate_page_params())
        button_next.grid(row=0, column=10 + map_size, padx=5, pady=5)

        text_label = tk.Label(self, text="# years:")
        text_label.place(anchor="se", relx=1.0, rely=1.0, x=-65, y=-45)
        self.year_entry = tk.Entry(self, width=5)
        self.year_entry.place(anchor="se", relx=1.0, rely=1.0, x=-5, y=-40)
        self.year_entry.config(validate="key", validatecommand=self.validate_integer_cmd)

        simulate_button = tk.Button(self,
                                    text="Simulate",
                                    width=9,
                                    command=self.simulate)
        simulate_button.place(anchor="se", relx=1.0, rely=1.0, x=-5, y=-5)

        clear_button = tk.Button(self,
                                 text="Clear animals",
                                 width=9,
                                 command=self.restart)
        clear_button.place(anchor="se", relx=1.0, rely=1.0, x=-120, y=-5)

        geogr = ["".join(terrain) for terrain in zip(*self.master.island)]
        geogr = "\n".join(geogr)
        self.master.sim = BioSim(island_map=geogr, ini_pop=self.master.population)

    def navigate_page_draw(self):
        """
        Navigate back to the drawing page.
        """
        self.master.pages["Populate"].pack_forget()
        self.master.pages["Draw"].pack()

    def navigate_page_params(self):
        """
        Navigate back to the drawing page.
        """
        self.master.pages["Populate"].pack_forget()
        self.master.pages["Parameters"].pack()

    def add_info(self):
        """
        Saves the information about the animals to be added to the map.

        Raises
        ------
        ValueError
            If no cell is selected.
            If no species is selected.
        """
        try:
            x, y = self.selected_cell.get()
        except ValueError:
            messagebox.showinfo("Error", "No cell selected.")

        species = str(self.species_var.get())
        if not species:
            messagebox.showinfo("Error", "No species selected.")

        age = int(self.age_entry.get()) if self.age_entry.get().isdigit() else None
        weight = float(self.weight_entry.get()) if self._is_float(self.weight_entry.get()) else None
        n_animals = int(self.n_animals_entry.get()) if self.n_animals_entry.get().isdigit() else 1

        add_animals = {"loc": (x + 1, y + 1),
                       "pop": [{"species": species,
                                "age": age,
                                "weight": weight} for _ in range(n_animals)]}

        self.master.population.append(add_animals)

    @staticmethod
    def _is_float(value):
        """
        Additional check for float values on input.
        """
        try:
            float(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def _validate_integer(value):
        """
        Checks whether the input value is an integer.
        """
        return re.match(r'^\d*$', value) is not None

    @staticmethod
    def _validate_float(value):
        """
        Checks whether the input value is float.
        """
        return re.match(r'^\d*\.?\d*$', value) is not None

    def _handle_click(self, event):
        """
        Handle clicks on the map, to select the desired cell.
        """
        canvas = event.widget
        x = event.x // self._size
        y = event.y // self._size

        if x < 0 or x >= self.grid_width or y < 0 or y >= self.grid_height:
            return

        if self.master.island[x][y] == "W":
            return

        self.selected_cell.set((y, x))
        canvas.delete("selection")
        canvas.create_rectangle(x * self._size, y * self._size, (x + 1) *
                                self._size,
                                (y + 1) *
                                self._size, outline="black", fill="black", tags="selection")

    def restart(self):
        """
        Clears the population list.
        """
        self.master.population = []
        geogr = ["".join(terrain) for terrain in zip(*self.master.island)]
        geogr = "\n".join(geogr)
        self.master.sim = BioSim(island_map=geogr, ini_pop=self.master.population)

    def simulate(self):
        """
        Simulates the population on the map for the given number of years.

        Raises
        ------
        ValueError
            If number of years to simulate has not been specified.
        """
        if not self.year_entry.get().isdigit():
            messagebox.showinfo("Error", "Number of years to simulate has not been specified.")
        else:
            years = int(self.year_entry.get())
            self.master.sim.add_population(self.master.population)
            self.master.sim.simulate(years)


class Parameters(tk.Frame):
    """
    Page in the GUI to change the parameters of the animals and island.
    """
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master

        button_draw = tk.Button(self,
                                text="Draw",
                                width=7,
                                command=lambda: self.navigate_page_draw())
        button_draw.grid(row=0, column=8, padx=5, pady=5)
        button_simu = tk.Button(self,
                                text="Simulate",
                                width=7,
                                command=lambda: self.navigate_page_simulate())
        button_simu.grid(row=0, column=9, padx=5, pady=5)


        self.validate_text_cmd = (self.register(self._validate_text), '%P')
        self.validate_integer_cmd = (self.register(self._validate_integer), '%P')
        self.validate_float_cmd = (self.register(self._validate_float), '%P')

        self.species_var = tk.StringVar()
        animal_params = tk.Label(self, text="Change animal parameter:")
        animal_params.grid(row=1, column=1, padx=5, pady=5)
        herbivore_button = tk.Radiobutton(self, text="Herbivore", variable=self.species_var,
                                          value="Herbivore")
        herbivore_button.grid(row=1, column=2, padx=5, pady=5)
        carnivore_button = tk.Radiobutton(self, text="Carnivore", variable=self.species_var,
                                          value="Carnivore")
        carnivore_button.grid(row=2, column=2, padx=5, pady=5)

        _animal_param = tk.Label(self, text="Parameter:")
        _animal_param.grid(row=1, column=3, padx=5, pady=5)
        self._animal_param_entry = tk.Entry(self, width=5)
        self._animal_param_entry.grid(row=1, column=4, padx=5, pady=5)
        self._animal_param_entry.config(validate="key", validatecommand=self.validate_text_cmd)

        _animal_value = tk.Label(self, text="Value:")
        _animal_value.grid(row=1, column=5, padx=5, pady=5)
        self._animal_value_entry = tk.Entry(self, width=5)
        self._animal_value_entry.grid(row=1, column=6, padx=5, pady=5)
        self._animal_value_entry.config(validate="key", validatecommand=self.validate_float_cmd)

        add_animal_param_button = tk.Button(self, text="Update", command=self.add_info)
        add_animal_param_button.grid(row=1, column=7, padx=5, pady=5)

        # I couldn't find an elegant solution to separate the animal and landscape parameters,
        # so I ended up doing the following:
        separator1 = tk.Label(self, text=" -=- " * 8)
        separator1.grid(row=3, column=1, padx=0, pady=5)
        separator2 = tk.Label(self, text=" -=- " * 4)
        separator2.grid(row=3, column=2, padx=0, pady=5)
        separator3 = tk.Label(self, text=" -=- " * 4)
        separator3.grid(row=3, column=3, padx=0, pady=5)
        separator4 = tk.Label(self, text=" -=- " * 2)
        separator4.grid(row=3, column=4, padx=0, pady=5)
        separator5 = tk.Label(self, text=" -=- " * 4)
        separator5.grid(row=3, column=5, padx=0, pady=5)
        separator6 = tk.Label(self, text=" -=- " * 3)
        separator6.grid(row=3, column=6, padx=0, pady=5)
        separator7 = tk.Label(self, text=" -=- " * 4)
        separator7.grid(row=3, column=7, padx=0, pady=5)

        self.landscape_var = tk.StringVar()
        landscape_params = tk.Label(self, text="Change landscape parameter:")
        landscape_params.grid(row=4, column=1, padx=5, pady=5)
        h_button = tk.Radiobutton(self, text="H", variable=self.landscape_var, value="H")
        h_button.grid(row=4, column=2, padx=5, pady=5)
        l_button = tk.Radiobutton(self, text="L", variable=self.landscape_var, value="L")
        l_button.grid(row=5, column=2, padx=5, pady=5)
        d_button = tk.Radiobutton(self, text="D", variable=self.landscape_var, value="D")
        d_button.grid(row=6, column=2, padx=5, pady=5)
        w_button = tk.Radiobutton(self, text="W", variable=self.landscape_var, value="W")
        w_button.grid(row=7, column=2, padx=5, pady=5)

        _land_param = tk.Label(self, text="Fodder:")
        _land_param.grid(row=4, column=3, padx=5, pady=5)
        self._land_param_entry = tk.Entry(self, width=5)
        self._land_param_entry.grid(row=4, column=4, padx=5, pady=5)
        self._land_param_entry.config(validate="key", validatecommand=self.validate_integer_cmd)

        add_land_param_button = tk.Button(self, text="Update", command=self.add_info)
        add_land_param_button.grid(row=4, column=5, padx=5, pady=5)

    def add_info(self):
        """
        Saves the information about the parameters to be added to the simulation.
        """
        species = str(self.species_var.get())
        if species:
            param = self._animal_param_entry.get() if self._animal_param_entry.get() else None
            val = float(self._animal_value_entry.get()) if self._is_float(
                self._animal_value_entry.get()) else None
            self.master.sim.set_animal_parameters(species, {param: val})

        landscape = str(self.landscape_var.get())
        if landscape:
            val = float(self._land_param_entry.get()) if self._is_float(
                self._land_param_entry.get()) else None
            self.master.sim.set_landscape_parameters(landscape, {"f_max": val})

    @staticmethod
    def _validate_text(text):
        """
        Checks whether the input text is valid.
        """
        pattern = r'^[a-zA-Z_]+$'
        return re.match(pattern, text) is not None

    @staticmethod
    def _validate_integer(value):
        """
        Checks whether the input value is an integer.
        """
        return re.match(r'^\d*$', value) is not None

    @staticmethod
    def _validate_float(value):
        """
        Checks whether the input value is float.
        """
        return re.match(r'^\d*\.?\d*$', value) is not None

    @staticmethod
    def _is_float(value):
        """
        Additional check for float values on input.
        """
        try:
            float(value)
            return True
        except ValueError:
            return False

    def navigate_page_simulate(self):
        """
        Navigate back to the simulations page.
        """
        self.master.pages["Parameters"].pack_forget()
        self.master.pages["Populate"].pack()

    def navigate_page_draw(self):
        """
        Navigate to the drawing page.
        """
        self.master.pages["Parameters"].pack_forget()
        self.master.pages["Draw"].pack()


if __name__ == "__main__":

    BioSimGUI().mainloop()
