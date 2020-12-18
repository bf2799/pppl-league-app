import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from database import Table


class MainGUI(tk.Tk):
    def __init__(self, db, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # Title this container
        self.title('Ping Pong Pong League')
        self.db = db

        # Set up primary container
        self.container = tk.Frame(self)
        self.container.pack()

        # Make sure container always uses full screen, even if its child frames don't need it (useless fake label)
        self.state('zoomed')
        fake_label = tk.Label(self.container)
        fake_label.grid(row=0, column=0, sticky='nsew', padx=self.winfo_screenwidth(), pady=self.winfo_screenheight())

        # Load all possible frames
        self.frames = {}
        for frame in (MainWindow, PlayerManagementWindow, EnterLeagueWindow, AddPlayerWindow, EditPlayerWindow,
                      AddRoleWindow, ViewPlayerWindow, StatsWindow, StandingsWindow, ScheduleWindow, NewSeasonWindow,
                      LiveGameWindow):
            temp_frame = frame(self.container, self)
            temp_frame.grid(row=0, column=0, sticky='nsew')
            self.frames[frame] = temp_frame

        # Bring main frame to top
        self.show_frame(MainWindow)

    def show_frame(self, container):
        self.frames[container].tkraise()

    def get_db(self):
        return self.db

    def is_frame_top(self, container):
        return self.frames[container] == self.container.winfo_children()[-1]


class HomeFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        # Home button
        self.button_home = tk.Button(self, text='<< Home',
                                     command=lambda: controller.show_frame(MainWindow))
        self.button_home.grid(row=1, column=1, sticky='w')


class MainWindow(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        # Welcome label
        self.label_welcome = tk.Label(self, justify='center', text='Welcome to Ping Pong Central!\nSelect a Mode')
        self.label_welcome.grid(row=1, column=1)
        # Player management button
        self.button_player_management = tk.Button(self, text='Player Management',
                                                  command=lambda: controller.show_frame(PlayerManagementWindow))
        self.button_player_management.grid(row=2, column=1)
        # Enter league button
        self.button_enter_league = tk.Button(self, text='Enter League',
                                             command=lambda: controller.show_frame(EnterLeagueWindow))
        self.button_enter_league.grid(row=3, column=1)


class PlayerManagementWindow(HomeFrame):
    def __init__(self, parent, controller):
        HomeFrame.__init__(self, parent, controller)
        # Add player button
        self.button_add_player = tk.Button(self, text='Add Player',
                                           command=lambda: controller.show_frame(AddPlayerWindow))
        self.button_add_player.grid(row=2, column=2)
        # Edit player button
        self.edit_player_button = tk.Button(self, text='Edit Player',
                                            command=lambda: controller.show_frame(EditPlayerWindow))
        self.edit_player_button.grid(row=3, column=2)
        # View player button
        self.view_player_button = tk.Button(self, text='View Player',
                                            command=lambda: controller.show_frame(ViewPlayerWindow))
        self.view_player_button.grid(row=4, column=2)
        # Add role button
        self.button_add_role = tk.Button(self, text='Add New Role',
                                         command=lambda: controller.show_frame(AddRoleWindow))
        self.button_add_role.grid(row=5, column=2)


class AddPlayerWindow(HomeFrame):
    def __init__(self, parent, controller):
        HomeFrame.__init__(self, parent, controller)
        self.controller = controller
        # Back button
        self.button_back = tk.Button(self, text='<--Back',
                                     command=lambda: controller.show_frame(PlayerManagementWindow))
        self.button_back.grid(row=2, column=1, sticky='w')
        # Name label
        self.label_name = tk.Label(self, text='* Name:')
        self.label_name.grid(row=3, column=2, sticky='e')
        # Name entry
        self.entry_name = tk.Entry(self, width=50)
        self.entry_name.grid(row=3, column=3, padx=5)
        # Logo label
        self.label_logo = tk.Label(self, text='Logo File:')
        self.label_logo.grid(row=4, column=2, sticky='e')
        # Logo entry
        self.entry_logo = tk.Entry(self, width=50)
        self.entry_logo.grid(row=4, column=3, padx=5)
        # Logo browse button
        self.button_logo_browse = tk.Button(self, text='Browse',
                                            command=lambda: browse_files_for_entry(self.entry_logo))
        self.button_logo_browse.grid(row=4, column=4)
        # Headshot label
        self.label_headshot = tk.Label(self, text='Headshot File:')
        self.label_headshot.grid(row=5, column=2, sticky='e')
        # Headshot entry
        self.entry_headshot = tk.Entry(self, width=50)
        self.entry_headshot.grid(row=5, column=3, padx=5)
        # Headshot browse button
        self.button_headshot_browse = tk.Button(self, text='Browse',
                                                command=lambda: browse_files_for_entry(self.entry_headshot))
        self.button_headshot_browse.grid(row=5, column=4)
        # Add roles label
        self.label_add_roles = tk.Label(self, text='Add Role(s):')
        self.label_add_roles.grid(row=6, column=2, sticky='ne')
        # Add roles listbox
        self.listbox_add_roles = tk.Listbox(self, selectmode='multiple', width=30)
        self.listbox_add_roles.grid(row=6, column=3, sticky='w', padx=5, pady=5)
        self.controller.get_db().register_insert_callback(Table.ROLE, self.update_role_listbox)
        # Save and create player button
        self.button_create_player = tk.Button(self, text='Save and Create Player',
                                              command=self.save_create_player)
        self.button_create_player.grid(row=7, column=3)
        # Bind enter key to fields being entered
        self.entry_name.bind('<Return>', self.save_create_player)
        self.entry_logo.bind('<Return>', self.save_create_player)
        self.entry_headshot.bind('<Return>', self.save_create_player)
        self.listbox_add_roles.bind('<Return>', self.save_create_player)

    def update_role_listbox(self):
        roles = self.controller.get_db().get_role_names()
        self.listbox_add_roles.delete(0, 'end')
        for role in range(len(roles)):
            self.listbox_add_roles.insert(role, roles[role])

    def save_create_player(self, _=None):
        # Check that this frame is on top
        if not self.controller.is_frame_top(AddPlayerWindow):
            return
        # Check if player name already exists or there is no player name, stopping if so
        if self.entry_name.get() == '':
            self.entry_name.delete(0, 'end')
            self.entry_name.insert(0, 'Name field is empty')
            return
        elif self.controller.get_db().is_player_in_db(self.entry_name.get()):
            self.entry_name.delete(0, 'end')
            self.entry_name.insert(0, 'Name already exists')
            return
        # Save new player to database
        try:
            logo_bin = open(self.entry_logo.get(), 'rb').read()
            headshot_bin = open(self.entry_headshot.get(), 'rb').read()
        except Exception:
            logo_bin = None
            headshot_bin = None
        self.controller.get_db().insert_player(self.entry_name.get(), logo_bin, headshot_bin)
        # Save new player's roles to database
        new_roles = [self.listbox_add_roles.get(role) for role in self.listbox_add_roles.curselection()]
        for role in new_roles:
            self.controller.get_db().insert_player_role(self.entry_name.get(), role)
        # At end, clear text from entry fields and go back to previous menu
        self.entry_name.delete(0, 'end')
        self.entry_logo.delete(0, 'end')
        self.entry_headshot.delete(0, 'end')
        self.listbox_add_roles.selection_clear(0, 'end')


class EditPlayerWindow(HomeFrame):
    def __init__(self, parent, controller):
        HomeFrame.__init__(self, parent, controller)
        # Back button
        self.button_back = tk.Button(self, text='<--Back',
                                     command=lambda: controller.show_frame(PlayerManagementWindow))
        self.button_back.grid(row=2, column=1, sticky='w')


class ViewPlayerWindow(HomeFrame):
    def __init__(self, parent, controller):
        HomeFrame.__init__(self, parent, controller)
        # Back button
        self.button_back = tk.Button(self, text='<--Back',
                                     command=lambda: controller.show_frame(PlayerManagementWindow))
        self.button_back.grid(row=2, column=1, sticky='w')


class AddRoleWindow(HomeFrame):
    def __init__(self, parent, controller):
        HomeFrame.__init__(self, parent, controller)
        self.controller = controller
        # Back button
        self.button_back = tk.Button(self, text='<--Back',
                                     command=lambda: controller.show_frame(PlayerManagementWindow))
        self.button_back.grid(row=2, column=1, sticky='w')
        # Current roles label
        self.label_current_roles = tk.Label(self, justify='left', borderwidth=2, relief='groove', padx=5, pady=5)
        self.label_current_roles.grid(row=3, column=2)
        self.controller.get_db().register_insert_callback(Table.ROLE, self.update_role_label)
        # Add frame for adding new role
        self.frame_add_role = tk.Frame(self)
        self.frame_add_role.grid(row=3, column=3, sticky='n', padx=10)
        # Add role label
        self.label_add_role = tk.Label(self.frame_add_role, text='Enter Role:')
        self.label_add_role.grid(row=1, column=1, sticky='w')
        # Add role entry
        self.entry_add_role = tk.Entry(self.frame_add_role, width=50)
        self.entry_add_role.grid(row=2, column=1, pady=5)
        # Add role button
        self.button_add_role = tk.Button(self.frame_add_role, text='Add Role', command=self.add_role)
        self.button_add_role.grid(row=3, column=1)
        # Bind enter key to text field being entered
        self.entry_add_role.bind('<Return>', self.add_role)

    def update_role_label(self):
        # Current roles label
        text = 'Existing Roles:\n\n' + '\n'.join(sorted(self.controller.get_db().get_role_names()))
        self.label_current_roles.config(text=text)

    def add_role(self, _=None):
        # Check that this frame is on top
        if not self.controller.is_frame_top(AddRoleWindow):
            return
        # Check if role name already exists or there is no role name, stopping if so
        if self.entry_add_role.get() == '':
            self.entry_add_role.delete(0, 'end')
            self.entry_add_role.insert(0, 'Role field is empty')
            return
        elif self.controller.get_db().is_role_in_db(self.entry_add_role.get()):
            self.entry_add_role.delete(0, 'end')
            self.entry_add_role.insert(0, 'Role already exists')
            return
        # Save new role to database
        self.controller.get_db().insert_role(self.entry_add_role.get())
        # At end, clear text from entry fields and go back to previous menu
        self.entry_add_role.delete(0, 'end')


class EnterLeagueWindow(HomeFrame):
    def __init__(self, parent, controller):
        HomeFrame.__init__(self, parent, controller)
        self.controller = controller
        # Season view frame
        self.frame_season_view = tk.Frame(self, borderwidth=2, relief='groove')
        self.frame_season_view.grid(row=2, column=2, sticky='nw', padx=10)
        # Choose season label
        self.label_choose_season = tk.Label(self.frame_season_view, text='Choose Season\nStart Date')
        self.label_choose_season.grid(row=1, column=1, padx=5)
        # Season option menu
        self.current_season = tk.StringVar(self)
        self.option_menu_season_options = ['']
        self.option_menu_season = tk.OptionMenu(self.frame_season_view, self.current_season,
                                                *self.option_menu_season_options)
        self.option_menu_season.grid(row=2, column=1, padx=5)
        self.controller.get_db().register_insert_callback(Table.SEASON, self.update_season_options)
        # Season info label
        self.label_season_info = tk.Label(self.frame_season_view, text='Season Info')
        self.label_season_info.grid(row=3, column=1, padx=5)
        # Stats button
        self.button_stats = tk.Button(self.frame_season_view, text='Stats',
                                      command=lambda: controller.show_frame(StatsWindow))
        self.button_stats.grid(row=4, column=1, pady=5, padx=5)
        # Standings button
        self.button_stats = tk.Button(self.frame_season_view, text='Standings',
                                      command=lambda: controller.show_frame(StandingsWindow))
        self.button_stats.grid(row=5, column=1, pady=5, padx=5)
        # Schedule button
        self.button_stats = tk.Button(self.frame_season_view, text='Schedule',
                                      command=lambda: controller.show_frame(ScheduleWindow))
        self.button_stats.grid(row=6, column=1, pady=5, padx=5)
        # New season button
        self.button_stats = tk.Button(self, text='New Season',
                                      command=lambda: controller.show_frame(NewSeasonWindow))
        self.button_stats.grid(row=2, column=3, sticky='n', padx=10)
        # Next game frame
        self.frame_next_game = tk.Frame(self, borderwidth=2, relief='groove')
        self.frame_next_game.grid(row=2, column=4, sticky='n', padx=10)
        # Next game label
        self.label_next_game = tk.Label(self.frame_next_game, text='Next Game')
        self.label_next_game.grid(row=1, column=1, padx=5)
        # Game details message
        self.message_game_details = tk.Message(self.frame_next_game, justify='center')
        self.message_game_details.grid(row=2, column=1, padx=5)
        self.controller.get_db().register_insert_callback(Table.SEASON, self.update_game_details_message)
        self.controller.get_db().register_insert_callback(Table.GAME, self.update_game_details_message)
        self.controller.get_db().register_insert_callback(Table.PLAYER_GAME, self.update_game_details_message)
        # Play game button
        self.button_play_game = tk.Button(self.frame_next_game, text='Play Game',
                                          command=lambda: controller.show_frame(LiveGameWindow))
        self.button_play_game.grid(row=3, column=1, padx=5, pady=5)
        # Initialize helper variables
        self.next_unplayed_game_id = -1

    def update_season_options(self):
        # Update the option menu for the available seasons
        self.option_menu_season_options = self.controller.get_db().get_season_start_dates()
        self.option_menu_season_options = [date.strftime('%m/%d/%Y') for date in self.option_menu_season_options]
        self.option_menu_season_options.sort(reverse=True)
        self.current_season.set('')
        self.option_menu_season['menu'].delete(0, 'end')
        for new_option in self.option_menu_season_options:
            self.option_menu_season['menu'].add_command(label=new_option,
                                                        command=tk._setit(self.current_season, new_option))

    def update_game_details_message(self):
        next_unplayed_game_details = self.controller.get_db().get_next_unplayed_game_details()
        if len(next_unplayed_game_details) == 0:
            game_details_text = "No Upcoming Games"
        else:
            self.next_unplayed_game_id = next_unplayed_game_details[0]
            season = next_unplayed_game_details[1].strftime('%m/%d/%Y')
            game_number = next_unplayed_game_details[2]
            home_player = next_unplayed_game_details[3]
            away_player = next_unplayed_game_details[4]
            game_details_text = "{} @ {}\nGame {}\n Season {} ".format(away_player, home_player, game_number, season)
        self.message_game_details.config(text=game_details_text)


class StatsWindow(HomeFrame):
    def __init__(self, parent, controller):
        HomeFrame.__init__(self, parent, controller)
        self.controller = controller
        # Back button
        self.button_back = tk.Button(self, text='<--Back',
                                     command=lambda: controller.show_frame(EnterLeagueWindow))
        self.button_back.grid(row=2, column=1, sticky='w')


class StandingsWindow(HomeFrame):
    def __init__(self, parent, controller):
        HomeFrame.__init__(self, parent, controller)
        self.controller = controller
        # Back button
        self.button_back = tk.Button(self, text='<--Back',
                                     command=lambda: controller.show_frame(EnterLeagueWindow))
        self.button_back.grid(row=2, column=1, sticky='w')


class ScheduleWindow(HomeFrame):
    def __init__(self, parent, controller):
        HomeFrame.__init__(self, parent, controller)
        self.controller = controller
        # Back button
        self.button_back = tk.Button(self, text='<--Back',
                                     command=lambda: controller.show_frame(EnterLeagueWindow))
        self.button_back.grid(row=2, column=1, sticky='w')


class NewSeasonWindow(HomeFrame):
    def __init__(self, parent, controller):
        HomeFrame.__init__(self, parent, controller)
        self.controller = controller
        # Back button
        self.button_back = tk.Button(self, text='<--Back',
                                     command=lambda: controller.show_frame(EnterLeagueWindow))
        self.button_back.grid(row=2, column=1, sticky='w')


class LiveGameWindow(HomeFrame):
    def __init__(self, parent, controller):
        HomeFrame.__init__(self, parent, controller)
        self.controller = controller
        # Back button
        self.button_back = tk.Button(self, text='<--Back',
                                     command=lambda: controller.show_frame(EnterLeagueWindow))
        self.button_back.grid(row=2, column=1, sticky='w')


def browse_files_for_entry(entry):
    """
    Browse files and enter text into given entry object
    :param entry: tk.Entry object to enter text into
    """
    entry_text = tk.filedialog.askopenfilename()
    if entry_text is not None:
        entry.delete(0, 'end')
        entry.insert(0, entry_text)