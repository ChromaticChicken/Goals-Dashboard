import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import yaml
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import math
import portalocker
import os

# light blue: #eefcff
# light gray: #ebebf5

YAML_LOCATION = "config.yaml"

class GoalsDashboard():
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Goals Dashboard")
        self.root.geometry("1250x800")
        
        self.menuBar = tk.Menu(self.root)
        self.root.config(menu=self.menuBar)
        self.menuBar.add_command(label="Edit Goal", command=self.open_edit_goals_dialogbox)
        self.menuBar.add_command(label="Remove Goal", command=self.open_remove_goals_dialogbox)
        self.menuBar.add_command(label="Set Current Progress", command=self.open_set_current_amount_dialogbox)
        self.menuBar.add_command(label="Set View", command=self.open_set_view_dialogbox)
        
        # make the style that all 'main' frames will use
        main_frame_style = ttk.Style()
        main_frame_style.configure("main.TFrame", borderwidth=5, relief="solid", background = "#002E5D") # Navy (BYU Primary Color)

        # make the style that all frames will use
        self.goals_frame_style = ttk.Style()
        self.goals_frame_style.configure("goals.TFrame", borderwidth=5, relief="solid", background = "#cbcbd5") # Gray 

        # make the full_view_frame, configure it, and pack it to the root
        self.full_view_frame = ttk.Frame(self.root, style="main.TFrame")
        self.full_view_frame.rowconfigure(0, weight=1, uniform=1)
        self.full_view_frame.rowconfigure(1, weight=1, uniform=1)
        self.full_view_frame.rowconfigure(2, weight=1, uniform=1)
        self.full_view_frame.columnconfigure(0, weight=1, uniform=1)
        self.full_view_frame.columnconfigure(1, weight=1, uniform=1)
        self.full_view_frame.columnconfigure(2, weight=1, uniform=1)
        self.full_view_frame.pack(fill=tk.BOTH, expand=True)

        # make the other view frames and configure them, but don't pack them yet
        self.area_focused_frame = ttk.Frame(self.root, style="main.TFrame")
        self.area_focused_frame.rowconfigure(0, weight=1, uniform=1)
        self.area_focused_frame.rowconfigure(1, weight=1, uniform=1)
        self.area_focused_frame.columnconfigure(0, weight=1, uniform=1)
        self.area_focused_frame.columnconfigure(1, weight=1, uniform=1)
        self.area_focused_frame.columnconfigure(2, weight=1, uniform=1)
        self.custom_frame = ttk.Frame(self.root, style="main.TFrame") # Custom will change depending on what the user wants so don't configure it yet
        
        # define what view we are currently useing
        self.current_view = "Full"

        # make the title and goals labels styles for each area that way they can be unique to each area
        self.title_style_dict = {}
        self.label_style_dict = {}
        for area in ["Classroom", "Desktops", "Receiving", "Recycling", "Front Office", "Process", "eBay", "Sale Floor", "Laptops"]:
            self.title_style_dict[area] = ttk.Style()
            self.title_style_dict[area].configure(f"{area} title.TLabel", font=('Arial', 20), background = "#cbcbd5")
            self.label_style_dict[area] = ttk.Style()
            self.label_style_dict[area].configure(f"{area} goals.TLabel", font=('Arial', 12), background = "#cbcbd5")
        
        
        # make the frames for each area and pack them into the full_view_frame along with their title labels
        self.classroomFrame = ttk.Frame(self.full_view_frame, style="goals.TFrame")
        self.classroomFrame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        ttk.Label(self.classroomFrame, text="Classroom", style="Classroom title.TLabel").pack(anchor="center", pady=(2.5,0))

        self.desktopsFrame = ttk.Frame(self.full_view_frame, style="goals.TFrame")
        self.desktopsFrame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        ttk.Label(self.desktopsFrame, text="Desktops", style="Desktops title.TLabel").pack(anchor="center", pady=(2.5,0))

        self.receivingFrame = ttk.Frame(self.full_view_frame, style="goals.TFrame")
        self.receivingFrame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
        ttk.Label(self.receivingFrame, text="Receiving", style="Receiving title.TLabel").pack(anchor="center", pady=(2.5,0))

        self.recyclingFrame = ttk.Frame(self.full_view_frame, style="goals.TFrame")
        self.recyclingFrame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        ttk.Label(self.recyclingFrame, text="Recycling", style="Recycling title.TLabel").pack(anchor="center", pady=(2.5,0))

        self.frontOfficeFrame = ttk.Frame(self.full_view_frame, style="goals.TFrame")
        self.frontOfficeFrame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        ttk.Label(self.frontOfficeFrame, text="Front Office", style="Front Office title.TLabel").pack(anchor="center", pady=(2.5,0))

        self.processFrame = ttk.Frame(self.full_view_frame, style="goals.TFrame")
        self.processFrame.grid(row=1, column=2, sticky="nsew", padx=10, pady=10)
        ttk.Label(self.processFrame, text="Process", style="Process title.TLabel").pack(anchor="center", pady=(2.5,0))

        self.ebayFrame = ttk.Frame(self.full_view_frame, style="goals.TFrame")
        self.ebayFrame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        ttk.Label(self.ebayFrame, text="eBay", style="eBay title.TLabel").pack(anchor="center", pady=(2.5,0))

        self.saleFloorFrame = ttk.Frame(self.full_view_frame, style="goals.TFrame")
        self.saleFloorFrame.grid(row=2, column=1, sticky="nsew", padx=10, pady=10)
        ttk.Label(self.saleFloorFrame, text="Sale Floor", style="Sale Floor title.TLabel").pack(anchor="center", pady=(2.5,0))


        self.laptopsFrame = ttk.Frame(self.full_view_frame, style="goals.TFrame")
        self.laptopsFrame.grid(row=2, column=2, sticky="nsew", padx=10, pady=10)
        ttk.Label(self.laptopsFrame, text="Laptops", style="Laptops title.TLabel").pack(anchor="center", pady=(2.5,0))

        self.full_frames_dict = {
            "Classroom": self.classroomFrame,
            "Desktops": self.desktopsFrame,
            "Receiving": self.receivingFrame,
            "Recycling": self.recyclingFrame,
            "Front Office": self.frontOfficeFrame,
            "Process": self.processFrame,
            "eBay": self.ebayFrame,
            "Sale Floor": self.saleFloorFrame,
            "Laptops": self.laptopsFrame
        } 

        self.periodic_check_yaml()
        self.periodic_backup_and_cleanup()

        self.root.bind("<Configure>", self.on_resize)
        self.root.mainloop()

############################################################################
#                 Restyle/Resize/Repopulate Text Functions                 #
############################################################################
    
    # refresh the text every 20 minutes
    def periodic_refresh(self) -> None:
        if self.current_view == "Full":
            for area in self.full_frames_dict:
                self.repopulate_frame(area)
        elif self.current_view == "Area Focus":
            for area in self.area_focused_frames_dict:
                self.repopulate_frame(area)
        self.root.after(20 * 60 * 1000, self.periodic_refresh)

    def on_resize(self, event: tk.Event) -> None:
        
        if self.current_view == "Full":
            for area in self.full_frames_dict:
               
                starting_text_font_size = 12
                starting_title_font_size = 19
                self.set_style(area, starting_text_font_size, starting_title_font_size)
        
        elif self.current_view == "Area Focus":
            for area in self.area_focused_frames_dict:
                
                if area == self.focused_area:
                    starting_text_font_size = 23
                    starting_title_font_size = 50
                else:
                    starting_text_font_size = 17
                    starting_title_font_size = 30
                self.set_style(area, starting_text_font_size, starting_title_font_size)

                
        
    def set_style(self, area: str, starting_text_font_size: int, starting_title_font_size: int) -> None:
        starting_window_height = 800
        window_height = self.root.winfo_height()
        goals_ratio = len(self.yaml_data[area]) / 2
        if self.current_view == "Area Focus" and area == self.focused_area:
            goals_ratio = 1
        if goals_ratio == 0:
            goals_ratio = 1
        # text is based on log base e and title is based on log base 2 so that the text grows a little slower than the title (e)
        text_ratio = starting_text_font_size * (math.log(window_height / starting_window_height) + 1) / goals_ratio
        title_ratio = (starting_title_font_size * (math.log2(window_height / starting_window_height) + 1)) / goals_ratio

        #set a minimum font size
        if text_ratio < 8:
            text_ratio = 8
        if title_ratio < 10:
            title_ratio = 10

        # round up if the decimal is greater than 0.75
        if int(text_ratio) < text_ratio-0.75:
            text_ratio = int(text_ratio) + 1
        else:
            text_ratio = int(text_ratio)
        
        if int(title_ratio) < title_ratio-0.75:
            title_ratio = int(title_ratio) + 1
        else:
            title_ratio = int(title_ratio)
        
        self.title_style_dict[area].configure(f"{area} title.TLabel", font=('Arial', title_ratio), background = "#cbcbd5")
        self.label_style_dict[area].configure(f"{area} goals.TLabel", font=('Arial', text_ratio), background = "#cbcbd5")

    def repopulate_frame(self, area: str) -> None:
        if self.current_view == "Full":
            frame = self.full_frames_dict[area]    
        elif self.current_view == "Area Focus":
            frame = self.area_focused_frames_dict[area]

        if self.current_view == "Area Focus" and area == self.focused_area:
            # remake the frame so it looses the old column configurations
            frame.destroy()
            frame = ttk.Frame(self.area_focused_frame, style="goals.TFrame")
            self.area_focused_frames_dict[area] = frame
            frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)
            
            i = 0
            for goal in self.yaml_data[area]:
                label = ttk.Label(frame, text=f"{goal['name']}\nTarget: {goal['target_value']}\nCurrent Progress: {goal['current_value']}\nStart Date: {goal['start_date']}\nEnd Date: {goal['end_date']}\n", style=f'{area} goals.TLabel', justify="center")
                label.grid(row=1, column=i, sticky="n", padx=10, pady=10)
                self.recolor_label(label, goal)
                frame.columnconfigure(i, weight=1, uniform=1)
                i += 1

            ttk.Label(frame, text=area, style=f'{area} title.TLabel').grid(row=0, column=0, columnspan=i, pady=(2.5,0))
        else:
            for widget in frame.winfo_children():
                widget.destroy()
            ttk.Label(frame, text=area, style=f'{area} title.TLabel').pack(anchor="center", pady=(2.5,0))
            for goal in self.yaml_data[area]:
                label = ttk.Label(frame, text=f"{goal['name']}\nTarget: {goal['target_value']}\nCurrent Progress: {goal['current_value']}\nStart Date: {goal['start_date']}\nEnd Date: {goal['end_date']}\n", style=f'{area} goals.TLabel', justify="center")
                label.pack(anchor="center")
                self.recolor_label(label, goal)
        self.on_resize(None)
        
    def recolor_label(self, label: ttk.Label, goal: dict) -> None:
        current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if current_date > datetime.strptime(goal['end_date'], "%m/%d/%Y"):
            label.configure(foreground='#e00000') # Red
        elif current_date == datetime.strptime(goal['end_date'], "%m/%d/%Y"):
            label.configure(foreground='#df6500') # Orange
        else:
            label.configure(foreground='#000000') # Black

    
############################################################################
#                            Set View Functions                            #
############################################################################


    def open_set_view_dialogbox(self) -> None:
        self.custum_dialog_views = tk.Toplevel(self.root)
        self.custum_dialog_views.title("Goals")
        self.custum_dialog_views.geometry("400x200")

        label = ttk.Label(self.custum_dialog_views, text="Choose Which View to Set:")
        label.pack()
        
        options = ["Full", "Area Focus", "Custom"]
        selected_value = tk.StringVar(self.custum_dialog_views)
        dropdown = ttk.Combobox(self.custum_dialog_views, textvariable=selected_value, values=options)
        dropdown.pack()
        dropdown.set("Select a view")
        dropdown.bind("<<ComboboxSelected>>", self.on_view_selected)
    
    def on_view_selected(self, event) -> None:
        selected_value = event.widget.get()
        for child in self.custum_dialog_views.winfo_children():
            child.destroy()
        if selected_value == "Full":
            self.current_view = "Full"
            self.show_full_view()
        elif selected_value == "Area Focus":
            label = ttk.Label(self.custum_dialog_views, text="Choose Which Area to Focus on:")
            label.pack()
            options = ["Classroom", "Desktops", "Receiving", "Recycling", "Front Office", "Process", "eBay", "Sale Floor", "Laptops"]
            selected_value = tk.StringVar(self.custum_dialog_views)
            dropdown = ttk.Combobox(self.custum_dialog_views, textvariable=selected_value, values=options)
            dropdown.pack()
            dropdown.set("Select an area")
            dropdown.bind("<<ComboboxSelected>>", self.on_area_selected_area_focus)
        elif selected_value == "Custom":
            self.current_view = "Custom"
            self.show_custom_view()

    def show_full_view(self) -> None:
        self.custum_dialog_views.destroy()
        self.area_focused_frame.forget()
        self.custom_frame.forget()
        self.full_view_frame.pack(fill=tk.BOTH, expand=True)
    
    def on_area_selected_area_focus(self, event: tk.Event) -> None:
        self.focused_area = event.widget.get()
        for child in self.custum_dialog_views.winfo_children():
            child.destroy()

        label = ttk.Label(self.custum_dialog_views, text="Choose the first of three other areas to show:")
        label.pack()
        options = ["Classroom", "Desktops", "Receiving", "Recycling", "Front Office", "Process", "eBay", "Sale Floor", "Laptops"]
        options.remove(self.focused_area)

        option1_selected_value = tk.StringVar(self.custum_dialog_views)
        option1_dropdown = ttk.Combobox(self.custum_dialog_views, textvariable=option1_selected_value, values=options)
        option1_dropdown.pack()
        option1_dropdown.set("Select an area")
        option1_dropdown.bind("<<ComboboxSelected>>", self.on_area_selected_area_focus2)

        
    def on_area_selected_area_focus2(self, event: tk.Event) -> None:
        area_1 = event.widget.get()
        for child in self.custum_dialog_views.winfo_children():
            child.destroy()

        label = ttk.Label(self.custum_dialog_views, text="Choose the second of three other areas to show:")
        label.pack()
        options = ["Classroom", "Desktops", "Receiving", "Recycling", "Front Office", "Process", "eBay", "Sale Floor", "Laptops"]
        options.remove(area_1)
        options.remove(self.focused_area)

        option2_selected_value = tk.StringVar(self.custum_dialog_views)
        option2_dropdown = ttk.Combobox(self.custum_dialog_views, textvariable=option2_selected_value, values=options)
        option2_dropdown.pack()
        option2_dropdown.set("Select an area")
        option2_dropdown.bind("<<ComboboxSelected>>", lambda event: self.on_area_selected_area_focus3(event, area_1))

    def on_area_selected_area_focus3(self, event: tk.Event, area_1: str) -> None:
        area_2 = event.widget.get()
        for child in self.custum_dialog_views.winfo_children():
            child.destroy()

        label = ttk.Label(self.custum_dialog_views, text="Choose the third of three other areas to show:")
        label.pack()
        options = ["Classroom", "Desktops", "Receiving", "Recycling", "Front Office", "Process", "eBay", "Sale Floor", "Laptops"]
        options.remove(area_1)
        options.remove(self.focused_area)
        options.remove(area_2)

        option3_selected_value = tk.StringVar(self.custum_dialog_views)
        option3_dropdown = ttk.Combobox(self.custum_dialog_views, textvariable=option3_selected_value, values=options)
        option3_dropdown.pack()
        option3_dropdown.set("Select an area")
        option3_dropdown.bind("<<ComboboxSelected>>", lambda event: self.on_area_selected_area_focus4(event, area_1, area_2))

    def on_area_selected_area_focus4(self, event: tk.Event, area_1: str, area_2: str) -> None:
        area_3 = event.widget.get()
        for child in self.custum_dialog_views.winfo_children():
            child.destroy()
        self.custum_dialog_views.destroy()

        self.current_view = "Area Focus"
        self.full_view_frame.forget()
        self.custom_frame.forget()

        self.area_focused_frame.pack(fill=tk.BOTH, expand=True)
        self.area_focused_frame.rowconfigure(0, weight=1, uniform=1)
        self.area_focused_frame.rowconfigure(1, weight=1, uniform=1)
        self.area_focused_frame.columnconfigure(0, weight=1, uniform=1)
        self.area_focused_frame.columnconfigure(1, weight=1, uniform=1)
        self.area_focused_frame.columnconfigure(2, weight=1, uniform=1)

        area_1_frame = ttk.Frame(self.area_focused_frame, style="goals.TFrame")
        area_1_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        ttk.Label(area_1_frame, text=area_1, style=f"{area_1} title.TLabel").pack(anchor="center", pady=(2.5,0))

        area_2_frame = ttk.Frame(self.area_focused_frame, style="goals.TFrame")
        area_2_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        ttk.Label(area_2_frame, text=area_2, style=f"{area_2} title.TLabel").pack(anchor="center", pady=(2.5,0))

        area_3_frame = ttk.Frame(self.area_focused_frame, style="goals.TFrame")
        area_3_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
        ttk.Label(area_3_frame, text=area_3, style=f"{area_3} title.TLabel").pack(anchor="center", pady=(2.5,0))

        focus_area_frame = ttk.Frame(self.area_focused_frame, style="goals.TFrame")
        focus_area_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)
        # Grid the focus area frame so that the goals can be side by side rather than only on top of each other

        i = 0
        for goal in self.yaml_data[self.focused_area]:
            focus_area_frame.columnconfigure(i, weight=1, uniform=1)
            i += 1
        ttk.Label(focus_area_frame, text=self.focused_area, style=f"{self.focused_area} title.TLabel").grid(row=0, column=0, columnspan=i, pady=(2.5,0))


        self.area_focused_frames_dict = {
            area_1: area_1_frame,
            area_2: area_2_frame,
            area_3: area_3_frame,
            self.focused_area: focus_area_frame,
            
        }
        for area in self.area_focused_frames_dict:
            self.repopulate_frame(area)

    def show_custom_view(self) -> None:
        self.custum_dialog_views.destroy()
        
        messagebox.showinfo("Info", "Custom view is not yet implemented")

############################################################################
#                        Manage Yaml File Functions                        #
############################################################################

                
    def check_yaml(self) -> None:
        try:
            current_mod_time = os.path.getmtime(YAML_LOCATION)

            if hasattr(self, 'yaml_mod_time') and current_mod_time == self.yaml_mod_time:
                return
            elif hasattr(self, 'yaml_mod_time'):
                messagebox.showinfo("Info", "config.yaml has been updated")
            self.yaml_mod_time = current_mod_time
            with open(YAML_LOCATION, 'r') as file:
                portalocker.lock(file, portalocker.LOCK_SH)
                self.yaml_data = yaml.safe_load(file)
                portalocker.unlock(file)
            for area in self.yaml_data:
                self.repopulate_frame(area)
        except FileNotFoundError:
            messagebox.showerror("Error", "config.yaml not found. Please make sure config.yaml is in the same directory as goalsDashboard.py")
            exit()
        except yaml.YAMLError:
            messagebox.showerror("Error", "config.yaml is not formatted correctly or was corrupted. Please make sure config.yaml is formatted correctly")
            exit()

    def periodic_check_yaml(self) -> None:
        self.check_yaml()
        self.root.after(5000, self.periodic_check_yaml)

    def dump_yaml(self) -> None:
        # write to file but lock the file before writing so that other processes/people can't write to it at the same time
        with open(YAML_LOCATION, 'w') as file:
            portalocker.lock(file, portalocker.LOCK_EX)
            yaml.dump(self.yaml_data, file, default_flow_style=False)
            portalocker.unlock(file)
        self.yaml_mod_time = os.path.getmtime(YAML_LOCATION)

    def periodic_backup_and_cleanup(self) -> None:
        self.backup_yaml()
        self.cleanup_backups()
        self.root.after(86400000, self.periodic_backup_and_cleanup) # 86400000 is the number of milliseconds in a day

    def backup_yaml(self) -> None:
        if not os.path.exists("backups"):
            os.makedirs("backups")

        # make a timestamp for the backup file
        timestamp = datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
        back_up_file_name = f"backups/config_backup_{timestamp}.yaml"

        # write to file but lock the file before writing so that other processes/people can't write to it at the same time
        with open(back_up_file_name, 'w') as file:
            portalocker.lock(file, portalocker.LOCK_EX)
            yaml.dump(self.yaml_data, file, default_flow_style=False)
            portalocker.unlock(file)
        
    def cleanup_backups(self) -> None:
        # get all the files in the backups directory
        files = os.listdir("backups")
        # if there are more than 10 files in the backups directory then delete the oldest one
        if len(files) > 10:
            oldest_file = min(files, key=lambda file: os.path.getctime(os.path.join("backups", file)))
            os.remove(f"backups/{oldest_file}")



############################################################################
#                           Edit Goals Functions                           #
############################################################################


    def open_edit_goals_dialogbox(self) -> None:
        self.custum_dialog_goals = tk.Toplevel(self.root)
        self.custum_dialog_goals.title("Goals")
        self.custum_dialog_goals.geometry("400x250")

        self.area_label = ttk.Label(self.custum_dialog_goals, text="Choose which area to edit:")
        self.area_label.pack()
        area_options = ["Classroom", "Desktops", "Receiving", "Recycling", "Front Office", "Process", "eBay", "Sale Floor", "Laptops"]
        selected_value = tk.StringVar(self.custum_dialog_goals)
        area_dropdown = ttk.Combobox(self.custum_dialog_goals, textvariable=selected_value, values=area_options)
        area_dropdown.pack()
        area_dropdown.set("Select an area")
        area_dropdown.bind("<<ComboboxSelected>>", self.on_area_selected_edit)

        

    def on_area_selected_edit(self, event: tk.Event) -> None:
        area_selected_value = event.widget.get()
        for child in self.custum_dialog_goals.winfo_children():
            child.destroy()
        self.area_label.destroy()

        label = ttk.Label(self.custum_dialog_goals, text="Choose Which Goal to Edit:")
        label.pack()
		
        options = [goal['name'] for goal in self.yaml_data[area_selected_value]]
        options.append("Other")
        goal_selected_value = tk.StringVar(self.custum_dialog_goals)
        goal_dropdown = ttk.Combobox(self.custum_dialog_goals, textvariable=goal_selected_value, values=options)
        goal_dropdown.pack()
        goal_dropdown.set("Select a goal")
        goal_dropdown.bind("<<ComboboxSelected>>", lambda event: self.on_goal_selected_edit(event, area_selected_value))


    def on_goal_selected_edit(self, event: tk.Event, area: str) -> None:
		
        selected_value = event.widget.get()
        for child in self.custum_dialog_goals.winfo_children():
            child.destroy()
        in_goals = False

        reminder_selected_value = tk.StringVar(self.custum_dialog_goals)
        current_weekday = datetime.now().strftime('%A')
        day_of_month = datetime.now().day
        if 10 <= day_of_month % 100 <= 20:
            day_of_month = f"{day_of_month}th"
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day_of_month % 10, 'th')
            day_of_month = f"{day_of_month}{suffix}"
        reminder_dropdown_options = [
            "Weekly on Monday", 
            f"Weekly on {current_weekday}", 
            "Monthly on the 1st", 
            "Monthly on the 3rd Thursday",
            f"Monthly on the {day_of_month}"
        ]
        reminder_selected_value.set(reminder_dropdown_options[0])
        reminder_dropdown = ttk.Combobox(self.custum_dialog_goals, textvariable=reminder_selected_value, values = reminder_dropdown_options, width=24, justify="center")

        for goal in self.yaml_data[area]:
            if goal['name'] == selected_value:
                label = ttk.Label(self.custum_dialog_goals, text=f"Current target: {goal['target_value']}\nSet: {goal['start_date']}")
                label.pack()
                label2 = ttk.Label(self.custum_dialog_goals, text="Target:")
                label2.pack()
                entry = tk.Entry(self.custum_dialog_goals, width=24)
                entry.pack()
                label3 = ttk.Label(self.custum_dialog_goals, text="Start Date:")
                label3.pack()
                start_date_dropdown_options = [datetime.now().strftime("%m/%d/%Y"), goal['start_date']]
                start_date_selected_value = tk.StringVar(self.custum_dialog_goals)
                start_date_dropdown = ttk.Combobox(self.custum_dialog_goals, textvariable=start_date_selected_value, values = start_date_dropdown_options, width=24, justify="center")
                start_date_dropdown.pack()
                start_date_selected_value.set(start_date_dropdown_options[0])
                label3 = ttk.Label(self.custum_dialog_goals, text="End Date:")
                label3.pack()
                reminder_dropdown.pack()
                if goal['reminder_text'] == "Weekly on Monday":
                    reminder_selected_value.set(reminder_dropdown_options[0])
                elif goal['reminder_text'].find('Weekly on') != -1:
                    reminder_selected_value.set(reminder_dropdown_options[1])
                elif goal['reminder_text'] == "Monthly on the 1st":
                    reminder_selected_value.set(reminder_dropdown_options[2])
                elif goal['reminder_text'] == "Monthly on the 3rd Thursday":
                    reminder_selected_value.set(reminder_dropdown_options[3])
                elif goal['reminder_text'].find('Monthly on') != -1:
                    reminder_selected_value.set(reminder_dropdown_options[4])
                else:
                    reminder_selected_value.set(reminder_dropdown_options[0])
                button = tk.Button(self.custum_dialog_goals, text="Submit", command=lambda: self.submit_goal_edit(selected_value, entry.get(), reminder_selected_value.get(), area))
                button.pack()

                in_goals = True
        if not in_goals:
            label = ttk.Label(self.custum_dialog_goals, text="New Goal:")
            label.pack()
            entry = tk.Entry(self.custum_dialog_goals)
            entry.pack()
            label2 = ttk.Label(self.custum_dialog_goals, text="Target:")
            label2.pack()
            entry2 = tk.Entry(self.custum_dialog_goals)
            entry2.pack()	
            label3 = ttk.Label(self.custum_dialog_goals, text="End Date:")
            label3.pack()
            reminder_dropdown.pack()
            button = tk.Button(self.custum_dialog_goals, text="Submit", command=lambda: self.submit_goal_edit(entry.get(), entry2.get(), reminder_selected_value.get(), area))
            button.pack()

    def submit_goal_edit(self, goal_name: str, new_value: str, reminder_text: str, area: str) -> None:
        in_goals = False

        day_of_month = datetime.now().day
        if 10 <= day_of_month % 100 <= 20:
            day_of_month = f"{day_of_month}th"
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day_of_month % 10, 'th')
            day_of_month = f"{day_of_month}{suffix}"

        if reminder_text == "Weekly on Monday":
            reminder_date = (datetime.now() + timedelta(days=7) - timedelta(days=datetime.now().weekday())).strftime("%m/%d/%Y")
        elif reminder_text == f"Weekly on {datetime.now().strftime('%A')}":
            reminder_date = (datetime.now() + timedelta(days=7)).strftime("%m/%d/%Y")
        elif reminder_text == "Monthly on the 1st":
            reminder_date = (datetime.now() + relativedelta(months=1)).replace(day=1).strftime("%m/%d/%Y")
        elif reminder_text == "Monthly on the 3rd Thursday":
            reminder_date = (datetime.now() + relativedelta(months=1)).replace(day=1)
            while reminder_date.weekday() != 3:
                reminder_date += timedelta(days=1)
            reminder_date += timedelta(days=14)
            reminder_date = reminder_date.strftime("%m/%d/%Y")
        elif reminder_text == f"Monthly on the {day_of_month}":
            reminder_date = (datetime.now() + relativedelta(months=1)).strftime("%m/%d/%Y")

        for goal in self.yaml_data[area]:
            if goal['name'] == goal_name:
                goal['target_value'] = new_value
                goal['current_value'] = '0'
                goal['start_date'] = datetime.now().strftime("%m/%d/%Y")
                goal['end_date'] = reminder_date
                goal['reminder_text'] = reminder_text
                in_goals = True
        if not in_goals:
            self.yaml_data[area].append({'name': goal_name, 'target_value': new_value, 'current_value': '0', 'start_date': datetime.now().strftime("%m/%d/%Y"), 'reminder_text': reminder_text, 'end_date': reminder_date})
        self.dump_yaml()
        self.repopulate_frame(area)
        self.custum_dialog_goals.destroy()

############################################################################
#                          Remove Goals Functions                          #
############################################################################


    def open_remove_goals_dialogbox(self) -> None:
        self.custum_dialog_goals = tk.Toplevel(self.root)
        self.custum_dialog_goals.title("Goals")
        self.custum_dialog_goals.geometry("400x200")

        self.area_label = ttk.Label(self.custum_dialog_goals, text="Choose which area to remove from:")
        self.area_label.pack()
        area_options = ["Classroom", "Desktops", "Receiving", "Recycling", "Front Office", "Process", "eBay", "Sale Floor", "Laptops"]
        selected_value = tk.StringVar(self.custum_dialog_goals)
        area_dropdown = ttk.Combobox(self.custum_dialog_goals, textvariable=selected_value, values=area_options)
        area_dropdown.pack()
        area_dropdown.set("Select an area")
        area_dropdown.bind("<<ComboboxSelected>>", self.on_area_selected_remove)

				
    def on_area_selected_remove(self, event: tk.Event) -> None:
        area_selected_value = event.widget.get()
        for child in self.custum_dialog_goals.winfo_children():
            child.destroy()
        self.area_label.destroy()

        label = ttk.Label(self.custum_dialog_goals, text="Choose Which Goal to Remove:")
        label.pack()
        
        options = [goal['name'] for goal in self.yaml_data[area_selected_value]]
        selected_value = tk.StringVar(self.custum_dialog_goals)
        dropdown = ttk.Combobox(self.custum_dialog_goals, textvariable=selected_value, values=options)
        dropdown.pack()
        dropdown.set("Select a goal")
        dropdown.bind("<<ComboboxSelected>>", lambda event: self.on_goal_selected_remove(event, area_selected_value))


    def on_goal_selected_remove(self, event: tk.Event, area: str) -> None:
        selected_goal = event.widget.get()
        for child in self.custum_dialog_goals.winfo_children():
            child.destroy()
        label = ttk.Label(self.custum_dialog_goals, text=f"Are you sure you want to remove {selected_goal}?")
        label.pack()
        button = tk.Button(self.custum_dialog_goals, text="Yes", command=lambda: self.submit_goal_remove(selected_goal, area))
        button.pack()
        button2 = tk.Button(self.custum_dialog_goals, text="No", command=self.custum_dialog_goals.destroy)
        button2.pack()
	
    def submit_goal_remove(self, goal_name: str, area) -> None:
        for goal in self.yaml_data[area]:
            if goal['name'] == goal_name:
                self.yaml_data[area].remove(goal)
                break
        self.dump_yaml()
        self.repopulate_frame(area)
        self.custum_dialog_goals.destroy()

############################################################################
#                       Set Current Amount Functions                       #
############################################################################

    def open_set_current_amount_dialogbox(self) -> None:
        self.custum_dialog_goals = tk.Toplevel(self.root)
        self.custum_dialog_goals.title("Goals")
        self.custum_dialog_goals.geometry("400x200")

        self.area_label = ttk.Label(self.custum_dialog_goals, text="Choose which area to set current progress for:")
        self.area_label.pack()
        area_options = ["Classroom", "Desktops", "Receiving", "Recycling", "Front Office", "Process", "eBay", "Sale Floor", "Laptops"]
        selected_value = tk.StringVar(self.custum_dialog_goals)
        area_dropdown = ttk.Combobox(self.custum_dialog_goals, textvariable=selected_value, values=area_options)
        area_dropdown.pack()
        area_dropdown.set("Select an area")
        area_dropdown.bind("<<ComboboxSelected>>", self.on_area_selected_set_current_amount)

    def on_area_selected_set_current_amount(self, event: tk.Event) -> None:
        area_selected_value = event.widget.get()
        for child in self.custum_dialog_goals.winfo_children():
            child.destroy()
        self.area_label.destroy()

        label = ttk.Label(self.custum_dialog_goals, text="Choose Which Goal to Set Current Progress For:")
        label.pack()
        
        options = [goal['name'] for goal in self.yaml_data[area_selected_value]]
        selected_value = tk.StringVar(self.custum_dialog_goals)
        dropdown = ttk.Combobox(self.custum_dialog_goals, textvariable=selected_value, values=options)
        dropdown.pack()
        dropdown.set("Select a goal")
        dropdown.bind("<<ComboboxSelected>>", lambda event: self.on_goal_selected_set_current_amount(event, area_selected_value))

    def on_goal_selected_set_current_amount(self, event: tk.Event, area: str) -> None:
        selected_goal = event.widget.get()
        for child in self.custum_dialog_goals.winfo_children():
            child.destroy()
        label = ttk.Label(self.custum_dialog_goals, text=f"Set current progress for {selected_goal}:")
        label.pack()
        entry = tk.Entry(self.custum_dialog_goals)
        entry.pack()
        button = tk.Button(self.custum_dialog_goals, text="Submit", command=lambda: self.submit_goal_set_current_amount(selected_goal, entry.get(), area))
        button.pack()

    def submit_goal_set_current_amount(self, goal_name: str, new_value: str, area) -> None:
        for goal in self.yaml_data[area]:
            if goal['name'] == goal_name:
                goal['current_value'] = new_value
                break
        self.dump_yaml()
        self.repopulate_frame(area)
        self.custum_dialog_goals.destroy()

############################################################################
#                               End of Class                               #
############################################################################

	

if __name__ == "__main__":
    GoalsDashboard()
