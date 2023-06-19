"""
Provides a Graphical User Interface (GUI) for the simulation of an ecosystem.
"""


# Here ChatGPT (mostly), Stackoverflow, google and relevant documentation was used in order to
# create the GUI. I could not have done this without these tools.


import tkinter as tk
import re

from .simulation import BioSim


class BioSimGUI(tk.Tk):
    """
    Graphical User Interface (GUI) superclass for the simulation of an ecosystem.

    Contains information about the map and the population of animals to be simulated.
    """

    def __init__(self, map_size=20):
        tk.Tk.__init__(self)
        self.title("Feeling creative? Draw and populate your own island!")

        self.grid_map = ["W" * map_size for _ in range(map_size)]
        self.population = []

        self.pages = {"DrawMap": DrawMap(self),
                      "AddAnimals": AddAnimals(self),
                      "ChangeParams": ChangeParams(self)}

        self.pages.get("DrawMap").pack()


class DrawMap(tk.Frame):
    """
    Page in the GUI for drawing the map.
    """

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master

        self.cell_size = 30
        self.grid_width = len(self.master.grid_map[0])
        self.grid_height = len(self.master.grid_map)
        self.canvas_width = self.grid_width * self.cell_size
        self.canvas_height = self.grid_height * self.cell_size

        self.selected_terrain = None
        self.is_drawing = False

        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack(side=tk.LEFT)

        self.terrain_frame = tk.Frame(self)
        self.terrain_frame.pack(side=tk.RIGHT, padx=10)

        self.create_terrain_buttons()

        self.draw_grid()

        self.canvas.bind("<Button-1>", self.handle_canvas_click)
        self.canvas.bind("<Button-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.continue_drawing)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)

    def create_terrain_buttons(self):
        """
        Create buttons for selecting terrain types to draw.
        """

        terrain_types = ["Water", "Highland", "Lowland", "Desert"]
        for terrain in terrain_types:
            button = tk.Button(self.terrain_frame,
                               text=terrain,
                               width=9,
                               command=lambda t=terrain: self._select_terrain(t))
            button.pack(pady=5)
        finished_button = tk.Button(self,
                                    text="Finished Drawing",
                                    width=9,
                                    command=self.finished_drawing)
        finished_button.place(anchor="ne", relx=1, rely=0, x=-10, y=10)

    def _select_terrain(self, terrain):
        """
        Set the selected terrain type.
        """

        self.selected_terrain = terrain[0]

    def draw_grid(self):
        """
        Draw the initial map with the specified colors.
        """

        for x, row in enumerate(self.master.grid_map):
            for y, terrain in enumerate(row):
                color = ""
                if terrain == "W":
                    color = "#95CBCC"
                elif terrain == "H":
                    color = "#E8EC9E"
                elif terrain == "L":
                    color = "#B9D687"
                elif terrain == "D":
                    color = "#FFEEBA"

                self.canvas.create_rectangle(x * self.cell_size,
                                             y * self.cell_size,
                                             (x + 1) * self.cell_size,
                                             (y + 1) * self.cell_size,
                                             fill=color,
                                             tags=f"cell_{x}_{y}")

    def handle_canvas_click(self, event):
        """
        Handle clicks on the map.
        """

        x = event.x // self.cell_size
        y = event.y // self.cell_size

        if x < 0 or x >= self.grid_width or y < 0 or y >= self.grid_height:
            return

        if self.selected_terrain:
            self.update_cell_terrain(x, y, self.selected_terrain)

    def start_drawing(self, event):
        """
        Start drawing when the left mouse button is pressed.
        """

        self.is_drawing = True
        self.update_cell_terrain(event)

    def continue_drawing(self, event):
        """
        Continue drawing when the left mouse button is pressed and is dragged.
        """

        if self.is_drawing:
            self.update_cell_terrain(event)

    def stop_drawing(self, _):
        """
        Stop drawing when the left mouse button is released.
        """

        self.is_drawing = False

    def update_cell_terrain(self, event):
        """
        Update the terrain of the cell based on the drawn terrain type.
        """

        if self.selected_terrain:
            x = event.x // self.cell_size
            y = event.y // self.cell_size

            if 1 <= x < self.grid_width-1 and 1 <= y < self.grid_height-1:
                terrain = self.selected_terrain
                new = self.master.grid_map[x][:y] + terrain + self.master.grid_map[x][y+1:]
                self.master.grid_map[x] = new

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
                    x * self.cell_size,
                    y * self.cell_size,
                    (x + 1) * self.cell_size,
                    (y + 1) * self.cell_size,
                    fill=color)

    def finished_drawing(self):
        """
        Switch to the AddAnimals page.
        """

        self.master.pages["DrawMap"].pack_forget()
        self.master.pages["AddAnimals"].__init__(self.master)
        self.master.pages["AddAnimals"].pack()


class AddAnimals(tk.Frame):
    """
    Class for adding a population of animals to the map.
    """

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master

        self.selected_cell = tk.Variable(value=None)

        self.cell_size = 30
        self.grid_width = len(self.master.grid_map[0])
        self.grid_height = len(self.master.grid_map)
        map_size = self.grid_width + 1

        canvas_width = self.grid_width * self.cell_size
        canvas_height = self.grid_height * self.cell_size

        canvas = tk.Canvas(self, width=canvas_width, height=canvas_height)
        canvas.grid(row=1, column=0, columnspan=map_size, padx=5, pady=5, sticky="w")

        # Visualise the map:
        for x, row in enumerate(self.master.grid_map):
            for y, terrain in enumerate(row):
                color = ""
                if terrain == "W":
                    color = "#95CBCC"
                elif terrain == "H":
                    color = "#E8EC9E"
                elif terrain == "L":
                    color = "#B9D687"
                elif terrain == "D":
                    color = "#FFEEBA"

                canvas.create_rectangle(x * self.cell_size,
                                        y * self.cell_size,
                                        (x + 1) * self.cell_size,
                                        (y + 1) * self.cell_size,
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
                           text="Draw map",
                           width=5,
                           command=lambda: self.navigate_page_draw())
        button_back.grid(row=0, column=9 + map_size, padx=5, pady=5)
        button_next = tk.Button(self,
                           text="Edit parameters",
                           width=9,
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

        geogr = ["".join(terrain) for terrain in zip(*self.master.grid_map)]
        geogr = "\n".join(geogr)
        self.master.sim = BioSim(island_map=geogr, ini_pop=self.master.population)

    def navigate_page_draw(self):
        """
        Navigate back to the drawing page.
        """

        self.master.pages["AddAnimals"].pack_forget()
        self.master.pages["DrawMap"].pack()

    def navigate_page_params(self):
        """
        Navigate back to the drawing page.
        """

        self.master.pages["AddAnimals"].pack_forget()
        self.master.pages["ChangeParams"].pack()

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
            raise ValueError("No cell selected.")

        species = str(self.species_var.get())
        if not species:
            raise ValueError("No species selected.")

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
        x = event.x // self.cell_size
        y = event.y // self.cell_size

        if x < 0 or x >= self.grid_width or y < 0 or y >= self.grid_height:
            return

        if self.master.grid_map[x][y] == "W":
            return

        self.selected_cell.set((y, x))
        canvas.delete("selection")
        canvas.create_rectangle(x * self.cell_size, y * self.cell_size, (x + 1) *
                                self.cell_size,
                                (y + 1) *
                                self.cell_size, outline="black", fill="black", tags="selection")

    def restart(self):
        """
        Clears the population list.
        """

        self.master.population = []
        geogr = ["".join(terrain) for terrain in zip(*self.master.grid_map)]
        geogr = "\n".join(geogr)
        self.master.sim = BioSim(island_map=geogr, ini_pop=self.master.population)

    def simulate(self):
        """
        Simulates the population on the map for the given number of years.
        """

        if not self.year_entry.get().isdigit():
            raise ValueError("Number of years to simulate has not been specified.")
        else:
            years = int(self.year_entry.get())
            self.master.sim.add_population(self.master.population)
            self.master.sim.simulate(years)


class ChangeParams(tk.Frame):

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master

        button_back = tk.Button(self,
                                text="Simulate",
                                width=5,
                                command=lambda: self.navigate_page_draw())
        button_back.grid(row=0, column=8, padx=5, pady=5)

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

        # I couldn't find a elegant solution, so I ended up doing the following:
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
        h_button = tk.Radiobutton(self, text="H", variable=self.landscape_var,
                                          value="H")
        h_button.grid(row=4, column=2, padx=5, pady=5)
        l_button = tk.Radiobutton(self, text="L", variable=self.landscape_var,
                                          value="L")
        l_button.grid(row=5, column=2, padx=5, pady=5)
        d_button = tk.Radiobutton(self, text="D", variable=self.landscape_var,
                                  value="D")
        d_button.grid(row=6, column=2, padx=5, pady=5)
        w_button = tk.Radiobutton(self, text="W", variable=self.landscape_var,
                                  value="W")
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

    def navigate_page_draw(self):
        """
        Navigate back to the drawing page.
        """

        self.master.pages["ChangeParams"].pack_forget()
        self.master.pages["AddAnimals"].pack()