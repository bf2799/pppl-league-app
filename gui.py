import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from database import Table
from PIL import Image, ImageTk
import io
import error_reporting
import tkcalendar
import datetime
import analysis

MAX_CUPS = 10  # Number of cups to get in game, useful for verification in GUI


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

    def get_frame(self, container):
        return self.frames[container]


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
            error_reporting.report_warning('Name field is empty')
            return
        elif self.controller.get_db().is_player_in_db(self.entry_name.get()):
            self.entry_name.delete(0, 'end')
            error_reporting.report_warning('Name already exists')
            return
        # Save new player to database
        try:
            logo_bin = open(self.entry_logo.get(), 'rb').read()
        except Exception:
            logo_bin = None
        try:
            headshot_bin = open(self.entry_headshot.get(), 'rb').read()
        except Exception:
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
            error_reporting.report_warning('Role field is empty')
            return
        elif self.controller.get_db().is_role_in_db(self.entry_add_role.get()):
            self.entry_add_role.delete(0, 'end')
            error_reporting.report_warning('Role already exists')
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
        self.selected_season = tk.StringVar(self)
        self.option_menu_season_options = ['']
        self.option_menu_season = tk.OptionMenu(self.frame_season_view, self.selected_season,
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
        # Next game details message
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
        self.selected_season.set('')
        self.option_menu_season['menu'].delete(0, 'end')
        for new_option in self.option_menu_season_options:
            self.option_menu_season['menu'].add_command(label=new_option,
                                                        command=tk._setit(self.selected_season, new_option))

    def update_game_details_message(self):
        next_unplayed_game_details = self.controller.get_db().get_next_unplayed_game_details()
        if len(next_unplayed_game_details) == 0:
            game_details_text = "No Upcoming Games"
            self.button_play_game.config(state='disabled')
        else:
            self.next_unplayed_game_id = next_unplayed_game_details[0]
            season = next_unplayed_game_details[1].strftime('%m/%d/%Y')
            game_number = next_unplayed_game_details[2]
            home_player = next_unplayed_game_details[3]
            away_player = next_unplayed_game_details[4]
            game_details_text = "{} @ {}\nGame {}\n Season {} ".format(away_player, home_player, game_number, season)
            self.button_play_game.config(state='normal')
        self.message_game_details.config(text=game_details_text)

    def get_selected_season(self):
        return self.selected_season


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
        self.button_home.config(command=self.go_home)
        self.controller = controller
        # Back button
        self.button_back = tk.Button(self, text='<--Back', command=self.go_back)
        self.button_back.grid(row=2, column=1, sticky='w')
        # Number of games label
        self.label_num_games = tk.Label(self, text='Games / Player')
        self.label_num_games.grid(row=3, column=2, sticky='e')
        # Number of games spinbox
        self.spinbox_num_games = tk.Spinbox(self, from_=0, to_=1000, width=5)
        self.spinbox_num_games.grid(row=3, column=3, sticky='w', pady=5, padx=5)
        # Season start date label
        self.label_start_date = tk.Label(self, text='Start Date')
        self.label_start_date.grid(row=4, column=2, sticky='e')
        # Season start date entry
        self.date_entry_start_date = tkcalendar.DateEntry(self, firstweekday='sunday', showweeknumbers=False,
                                                          date_pattern='y-mm-dd')
        self.date_entry_start_date.grid(row=4, column=3, sticky='w', pady=5, padx=5)
        # Players label
        self.label_players = tk.Label(self, text='Players')
        self.label_players.grid(row=5, column=2, sticky='e')
        # Players listbox
        self.listbox_players = tk.Listbox(self, selectmode='multiple', width=30)
        self.listbox_players.grid(row=5, column=3, sticky='w', pady=5, padx=5)
        self.controller.get_db().register_insert_callback(Table.PLAYER, self.update_player_listbox)
        # Submit button
        self.button_submit = tk.Button(self, text='Submit', command=self.submit_new_season)
        self.button_submit.grid(row=6, column=3, sticky='w', padx=5, pady=5)

    def go_home(self):
        self.reset_entries()
        self.controller.show_frame(MainWindow)

    def go_back(self):
        self.reset_entries()
        self.controller.show_frame(EnterLeagueWindow)

    def reset_entries(self):
        self.spinbox_num_games.delete(0, 'end')
        self.spinbox_num_games.insert(0, '0')
        self.date_entry_start_date.set_date(datetime.datetime.now())
        self.listbox_players.selection_clear(0, 'end')

    def update_player_listbox(self):
        players = self.controller.get_db().get_player_names()
        players.sort()
        self.listbox_players.delete(0, 'end')
        for player in range(len(players)):
            self.listbox_players.insert(player, players[player])

    def submit_new_season(self):
        # Check all user-entered values and players are valid
        if eval(self.spinbox_num_games.get()) <= 0:
            error_reporting.report_warning('Invalid number of games per player')
            return
        if len(self.listbox_players.curselection()) <= 0:
            error_reporting.report_warning('No players selected for the new season')
            return
        if self.date_entry_start_date.get_date() in self.controller.get_db().get_season_start_dates():
            error_reporting.report_warning('Existing season already started on date entered')
            return
        players = [self.listbox_players.get(player) for player in self.listbox_players.curselection()]
        player_ids = [self.controller.get_db().get_player_id(name) for name in players]
        if -1 in player_ids:
            error_reporting.report_error('Database error. A player name did not match any known entries.')
            return
        # Enter new season into database
        schedule = analysis.generate_new_schedule(eval(self.spinbox_num_games.get()), player_ids)
        self.controller.get_db().insert_season(self.date_entry_start_date.get_date(), len(schedule) + 1)
        for game in range(len(schedule)):
            self.controller.get_db().insert_game(self.date_entry_start_date.get_date(), game + 1, schedule[game][0],
                                                 schedule[game][1])
        self.reset_entries()


class LiveGameWindow(tk.Frame):
    def __init__(self, parent, controller):
        self.IMAGE_SIZE_PX = (100, 100)
        tk.Frame.__init__(self, parent)
        self.controller = controller
        # Game info label
        self.label_game_info = tk.Label(self, justify='center')
        self.label_game_info.grid(row=1, column=1, pady=10)
        # Live players frame
        self.frame_players = tk.Frame(self)
        self.frame_players.grid(row=2, column=1, pady=10)
        # Home player frame
        self.frame_home_player = tk.Frame(self.frame_players)
        self.frame_home_player.grid(row=1, column=2, padx=20, sticky='s')
        # Home player name frame
        self.frame_home_player_name = tk.Frame(self.frame_home_player)
        self.frame_home_player_name.grid(row=1, column=1, pady=5)
        # Home label
        self.label_home = tk.Label(self.frame_home_player_name, text='Home')
        self.label_home.grid(row=1, column=1, columnspan=2)
        # Home player name label
        self.label_home_player_name = tk.Label(self.frame_home_player_name)
        self.label_home_player_name.grid(row=2, column=1, columnspan=2)
        # Home player logo label
        self.label_home_player_logo = tk.Label(self.frame_home_player_name)
        self.label_home_player_logo.grid(row=3, column=1)
        # Home player headshot label
        self.label_home_player_headshot = tk.Label(self.frame_home_player_name)
        self.label_home_player_headshot.grid(row=3, column=2)
        # Home player note stats frame
        self.frame_home_player_note_stats = tk.Frame(self.frame_home_player)
        self.frame_home_player_note_stats.grid(row=2, column=1, pady=5)
        # Home player footwear label
        self.label_home_player_footwear = tk.Label(self.frame_home_player_note_stats, text='Footwear')
        self.label_home_player_footwear.grid(row=1, column=1)
        # Home player footwear combobox
        self.combobox_home_player_footwear = ttk.Combobox(self.frame_home_player_note_stats, width=30)
        self.combobox_home_player_footwear.grid(row=2, column=1)
        # Home player number stats frame
        self.frame_home_player_num_stats = tk.Frame(self.frame_home_player)
        self.frame_home_player_num_stats.grid(row=3, column=1, pady=5)
        # Home player knockovers label
        self.label_home_player_knockovers = tk.Label(self.frame_home_player_num_stats, text='Knockovers')
        self.label_home_player_knockovers.grid(row=1, column=1, padx=5)
        # Home player knockovers spinbox
        self.spinbox_home_player_knockovers = tk.Spinbox(self.frame_home_player_num_stats, from_=0, to_=10, width=4,
                                                         wrap=True)
        self.spinbox_home_player_knockovers.grid(row=2, column=1, padx=5)
        # Home player own cups label
        self.label_home_player_own_cups = tk.Label(self.frame_home_player_num_stats, text='Own Cups')
        self.label_home_player_own_cups.grid(row=1, column=2, padx=5)
        # Home player own cups spinbox
        self.spinbox_home_player_own_cups = tk.Spinbox(self.frame_home_player_num_stats, from_=0, to_=10, width=4,
                                                       wrap=True)
        self.spinbox_home_player_own_cups.grid(row=2, column=2, padx=5)
        # Home player aces label
        self.label_home_player_aces = tk.Label(self.frame_home_player_num_stats, text='Aces')
        self.label_home_player_aces.grid(row=1, column=3, padx=5, sticky='w')
        # Home player aces spinbox
        self.spinbox_home_player_aces = tk.Spinbox(self.frame_home_player_num_stats, from_=0, to_=10, width=4,
                                                   wrap=True)
        self.spinbox_home_player_aces.grid(row=2, column=3, padx=5)
        # Home player serve breaks label
        self.label_home_player_serve_breaks = tk.Label(self.frame_home_player_num_stats, text='Serve Breaks')
        self.label_home_player_serve_breaks.grid(row=1, column=4, padx=5)
        # Home player serve breaks spinbox
        self.spinbox_home_player_serve_breaks = tk.Spinbox(self.frame_home_player_num_stats, from_=0, to_=10, width=4,
                                                           wrap=True)
        self.spinbox_home_player_serve_breaks.grid(row=2, column=4, padx=5)
        # Home player rate stats frame
        self.frame_home_player_rate_stats = tk.Frame(self.frame_home_player)
        self.frame_home_player_rate_stats.grid(row=4, column=1, pady=5)
        # Home player penalty shots label
        self.label_home_player_penalty_shots = tk.Label(self.frame_home_player_rate_stats, text='Penalty Shots')
        self.label_home_player_penalty_shots.grid(row=1, column=1, columnspan=3)
        # Home player penalty shots made spinbox
        self.spinbox_home_player_psm = tk.Spinbox(self.frame_home_player_rate_stats, from_=0, to_=10, width=3,
                                                  wrap=True)
        self.spinbox_home_player_psm.grid(row=2, column=1)
        # Home player penalty shots division label
        self.label_home_player_ps_div = tk.Label(self.frame_home_player_rate_stats, text='/')
        self.label_home_player_ps_div.grid(row=2, column=2)
        # Home player penalty shots attempted spinbox
        self.spinbox_home_player_psa = tk.Spinbox(self.frame_home_player_rate_stats, from_=0, to_=10, width=3,
                                                  wrap=True)
        self.spinbox_home_player_psa.grid(row=2, column=3)
        # Away player frame
        self.frame_away_player = tk.Frame(self.frame_players)
        self.frame_away_player.grid(row=1, column=1, padx=20, sticky='s')
        # Away player name frame
        self.frame_away_player_name = tk.Frame(self.frame_away_player)
        self.frame_away_player_name.grid(row=1, column=1, pady=5)
        # Away label
        self.label_away = tk.Label(self.frame_away_player_name, text='Away')
        self.label_away.grid(row=1, column=1, columnspan=2)
        # Away player name label
        self.label_away_player_name = tk.Label(self.frame_away_player_name)
        self.label_away_player_name.grid(row=2, column=1, columnspan=2)
        # Away player logo label
        self.label_away_player_logo = tk.Label(self.frame_away_player_name)
        self.label_away_player_logo.grid(row=3, column=1)
        # Away player headshot label
        self.label_away_player_headshot = tk.Label(self.frame_away_player_name)
        self.label_away_player_headshot.grid(row=3, column=2)
        # Away player note stats frame
        self.frame_away_player_note_stats = tk.Frame(self.frame_away_player)
        self.frame_away_player_note_stats.grid(row=2, column=1, pady=5)
        # Away player footwear label
        self.label_away_player_footwear = tk.Label(self.frame_away_player_note_stats, text='Footwear')
        self.label_away_player_footwear.grid(row=1, column=1)
        # Away player footwear combobox
        self.combobox_away_player_footwear = ttk.Combobox(self.frame_away_player_note_stats, width=30)
        self.combobox_away_player_footwear.grid(row=2, column=1)
        # Away player number stats frame
        self.frame_away_player_num_stats = tk.Frame(self.frame_away_player)
        self.frame_away_player_num_stats.grid(row=3, column=1, pady=5)
        # Away player knockovers label
        self.label_away_player_knockovers = tk.Label(self.frame_away_player_num_stats, text='Knockovers')
        self.label_away_player_knockovers.grid(row=1, column=1, padx=5)
        # Away player knockovers spinbox
        self.spinbox_away_player_knockovers = tk.Spinbox(self.frame_away_player_num_stats, from_=0, to_=10, width=4,
                                                         wrap=True)
        self.spinbox_away_player_knockovers.grid(row=2, column=1, padx=5)
        # Away player own cups label
        self.label_away_player_own_cups = tk.Label(self.frame_away_player_num_stats, text='Own Cups')
        self.label_away_player_own_cups.grid(row=1, column=2, padx=5)
        # Away player own cups spinbox
        self.spinbox_away_player_own_cups = tk.Spinbox(self.frame_away_player_num_stats, from_=0, to_=10, width=4,
                                                       wrap=True)
        self.spinbox_away_player_own_cups.grid(row=2, column=2, padx=5)
        # Away player aces label
        self.label_away_player_aces = tk.Label(self.frame_away_player_num_stats, text='Aces')
        self.label_away_player_aces.grid(row=1, column=3, padx=5, sticky='w')
        # Away player aces spinbox
        self.spinbox_away_player_aces = tk.Spinbox(self.frame_away_player_num_stats, from_=0, to_=10, width=4,
                                                   wrap=True)
        self.spinbox_away_player_aces.grid(row=2, column=3, padx=5)
        # Away player serve breaks label
        self.label_away_player_serve_breaks = tk.Label(self.frame_away_player_num_stats, text='Serve Breaks')
        self.label_away_player_serve_breaks.grid(row=1, column=4, padx=5)
        # Away player serve breaks spinbox
        self.spinbox_away_player_serve_breaks = tk.Spinbox(self.frame_away_player_num_stats, from_=0, to_=10, width=4,
                                                           wrap=True)
        self.spinbox_away_player_serve_breaks.grid(row=2, column=4, padx=5)
        # Away player rate stats frame
        self.frame_away_player_rate_stats = tk.Frame(self.frame_away_player)
        self.frame_away_player_rate_stats.grid(row=4, column=1, pady=5)
        # Away player penalty shots label
        self.label_away_player_penalty_shots = tk.Label(self.frame_away_player_rate_stats, text='Penalty Shots')
        self.label_away_player_penalty_shots.grid(row=1, column=1, columnspan=3)
        # Away player penalty shots made spinbox
        self.spinbox_away_player_psm = tk.Spinbox(self.frame_away_player_rate_stats, from_=0, to_=10, width=3,
                                                  wrap=True)
        self.spinbox_away_player_psm.grid(row=2, column=1)
        # Away player penalty shots division label
        self.label_away_player_ps_div = tk.Label(self.frame_away_player_rate_stats, text='/')
        self.label_away_player_ps_div.grid(row=2, column=2)
        # Away player penalty shots attempted spinbox
        self.spinbox_away_player_psa = tk.Spinbox(self.frame_away_player_rate_stats, from_=0, to_=10, width=3,
                                                  wrap=True)
        self.spinbox_away_player_psa.grid(row=2, column=3)
        # Game outcome frame
        self.frame_game_outcome = tk.Frame(self)
        self.frame_game_outcome.grid(row=3, column=1, pady=5)
        # Winner label
        self.label_winner = tk.Label(self.frame_game_outcome, text='Winner')
        self.label_winner.grid(row=1, column=1)
        # Winner radiobutton
        self.winner = tk.StringVar()
        self.radiobutton_winner_home = tk.Radiobutton(self.frame_game_outcome, value='home', variable=self.winner)
        self.radiobutton_winner_home.grid(row=2, column=1, sticky='w')
        self.radiobutton_winner_away = tk.Radiobutton(self.frame_game_outcome, value='away', variable=self.winner)
        self.radiobutton_winner_away.grid(row=3, column=1, sticky='w')
        # Differential label
        self.label_differential = tk.Label(self.frame_game_outcome, text='Differential')
        self.label_differential.grid(row=4, column=1)
        # Differential spinbox
        self.spinbox_differential = tk.Spinbox(self.frame_game_outcome, from_=0, to_=10, width=4, wrap=True)
        self.spinbox_differential.grid(row=5, column=1)
        # Completed game action frame
        self.frame_completed_game_action = tk.Frame(self)
        self.frame_completed_game_action.grid(row=4, column=1, pady=5)
        # Cancel game button
        self.button_cancel = tk.Button(self.frame_completed_game_action, text='Cancel Game',
                                       command=self.cancel_game)
        self.button_cancel.grid(row=1, column=1, padx=10)
        # Submit game button
        self.button_submit = tk.Button(self.frame_completed_game_action, text='Submit Game',
                                       command=self.submit_game)
        self.button_submit.grid(row=1, column=2, padx=10)
        # Set up callbacks for updating text for next unplayed game details
        self.controller.get_db().register_insert_callback(Table.SEASON, self.update_game_details)
        self.controller.get_db().register_insert_callback(Table.GAME, self.update_game_details)
        self.controller.get_db().register_insert_callback(Table.PLAYER_GAME, self.update_game_details)
        self.controller.get_db().register_insert_callback(Table.FOOTWEAR, self.update_footwear_options)

    def update_game_details(self):
        next_unplayed_game_details = self.controller.get_db().get_next_unplayed_game_details()
        # This window should never be opened if there isn't another unplayed game
        # If there is, make sure the game can't be submitted but don't bother updating any information
        if len(next_unplayed_game_details) == 0:
            self.button_submit.config(state='disabled')
            return
        # Update game info label
        game_info_text = "Game " + str(next_unplayed_game_details[2]) + \
                         "\nSeason " + str(next_unplayed_game_details[1].strftime('%m/%d/%Y'))
        self.label_game_info.config(text=game_info_text)
        # Update home player details
        home_player_details = self.controller.get_db().get_player_details(next_unplayed_game_details[3])
        if len(home_player_details) == 0:
            self.button_submit.config(state='disabled')
            return
        if home_player_details[1] is not None:
            logo = ImageTk.PhotoImage(Image.open(io.BytesIO(home_player_details[1])).resize(self.IMAGE_SIZE_PX))
            self.label_home_player_logo.config(image=logo)
            self.label_home_player_logo.image = logo
        else:
            self.label_home_player_logo.config(image=None)
            self.label_home_player_logo.image = None
        if home_player_details[2] is not None:
            headshot = ImageTk.PhotoImage(Image.open(io.BytesIO(home_player_details[2])).resize(self.IMAGE_SIZE_PX))
            self.label_home_player_headshot.config(image=headshot)
            self.label_home_player_headshot.image = headshot
        else:
            self.label_home_player_headshot.config(image=None)
            self.label_home_player_headshot.image = None
        self.label_home_player_name.config(text=home_player_details[0].upper())
        # Update away player details
        away_player_details = self.controller.get_db().get_player_details(next_unplayed_game_details[4])
        if len(away_player_details) == 0:
            self.button_submit.config(state='disabled')
            return
        if away_player_details[1] is not None:
            logo = ImageTk.PhotoImage(Image.open(io.BytesIO(away_player_details[1])).resize(self.IMAGE_SIZE_PX))
            self.label_away_player_logo.config(image=logo)
            self.label_away_player_logo.image = logo
        else:
            self.label_away_player_logo.config(image=None)
            self.label_away_player_logo.image = None
        if away_player_details[2] is not None:
            headshot = ImageTk.PhotoImage(Image.open(io.BytesIO(away_player_details[2])).resize(self.IMAGE_SIZE_PX))
            self.label_away_player_headshot.config(image=headshot)
            self.label_away_player_headshot.image = headshot
        else:
            self.label_away_player_headshot.config(image=None)
            self.label_away_player_headshot.image = None
        self.label_away_player_name.config(text=away_player_details[0].upper())
        self.button_submit.config(state='normal')
        # Update winner choices
        self.radiobutton_winner_home.config(text=home_player_details[0].upper())
        self.radiobutton_winner_away.config(text=away_player_details[0].upper())

    def update_footwear_options(self):
        current_footwear = self.controller.get_db().get_footwear_names()
        current_footwear.sort()
        self.combobox_home_player_footwear.config(values=current_footwear)
        self.combobox_away_player_footwear.config(values=current_footwear)

    def reset_entries(self):
        self.combobox_home_player_footwear.delete(0, 'end')
        self.spinbox_home_player_knockovers.delete(0, 'end')
        self.spinbox_home_player_knockovers.insert(0, 0)
        self.spinbox_home_player_own_cups.delete(0, 'end')
        self.spinbox_home_player_own_cups.insert(0, 0)
        self.spinbox_home_player_aces.delete(0, 'end')
        self.spinbox_home_player_aces.insert(0, 0)
        self.spinbox_home_player_serve_breaks.delete(0, 'end')
        self.spinbox_home_player_serve_breaks.insert(0, 0)
        self.spinbox_home_player_psm.delete(0, 'end')
        self.spinbox_home_player_psm.insert(0, 0)
        self.spinbox_home_player_psa.delete(0, 'end')
        self.spinbox_home_player_psa.insert(0, 0)
        self.combobox_away_player_footwear.delete(0, 'end')
        self.spinbox_away_player_knockovers.delete(0, 'end')
        self.spinbox_away_player_knockovers.insert(0, 0)
        self.spinbox_away_player_own_cups.delete(0, 'end')
        self.spinbox_away_player_own_cups.insert(0, 0)
        self.spinbox_away_player_aces.delete(0, 'end')
        self.spinbox_away_player_aces.insert(0, 0)
        self.spinbox_away_player_serve_breaks.delete(0, 'end')
        self.spinbox_away_player_serve_breaks.insert(0, 0)
        self.spinbox_away_player_psm.delete(0, 'end')
        self.spinbox_away_player_psm.insert(0, 0)
        self.spinbox_away_player_psa.delete(0, 'end')
        self.spinbox_away_player_psa.insert(0, 0)
        self.spinbox_differential.delete(0, 'end')
        self.spinbox_differential.insert(0, 0)
        self.radiobutton_winner_home.deselect()
        self.radiobutton_winner_away.deselect()

    def cancel_game(self):
        self.reset_entries()
        self.controller.show_frame(EnterLeagueWindow)

    def submit_game(self):
        # If no winner declared, differential must be 0 for a tie. Stop submitting if this isn't the case
        if len(self.winner.get()) == 0 and self.spinbox_differential.get() != 0:
            error_reporting.report_warning('No winner chosen')
            return
        if len(self.combobox_home_player_footwear.get()) == 0 or len(self.combobox_away_player_footwear.get()) == 0:
            error_reporting.report_warning('No footwear entered')
            return
        next_unplayed_game_details = self.controller.get_db().get_next_unplayed_game_details()
        home_player_details = self.controller.get_db().get_player_details(next_unplayed_game_details[3])
        away_player_details = self.controller.get_db().get_player_details(next_unplayed_game_details[4])
        # Insert home player to database
        current_footwear = self.combobox_home_player_footwear.get()
        self.controller.get_db().insert_footwear(current_footwear)
        footwear_id = self.controller.get_db().get_footwear_id(current_footwear)
        differential = ('-' if self.winner.get() == 'away' else '') + self.spinbox_differential.get()
        self.controller.get_db().insert_player_game(
            player_id=home_player_details[3], game_id=next_unplayed_game_details[0], footwear_id=footwear_id,
            differential=differential, knockovers=self.spinbox_home_player_knockovers.get(),
            own_cups=self.spinbox_home_player_own_cups.get(), aces=self.spinbox_home_player_aces.get(),
            serve_breaks=self.spinbox_home_player_serve_breaks.get(),
            penalty_shots_made=self.spinbox_home_player_psm.get(),
            penalty_shots_attempted=self.spinbox_home_player_psa.get(),
            penalties_committed=self.spinbox_away_player_psa.get())
        # Insert away player to database
        current_footwear = self.combobox_away_player_footwear.get()
        self.controller.get_db().insert_footwear(current_footwear)
        footwear_id = self.controller.get_db().get_footwear_id(current_footwear)
        differential = ('-' if self.winner.get() == 'home' else '') + self.spinbox_differential.get()
        self.controller.get_db().insert_player_game(
            player_id=away_player_details[3], game_id=next_unplayed_game_details[0], footwear_id=footwear_id,
            differential=differential, knockovers=self.spinbox_away_player_knockovers.get(),
            own_cups=self.spinbox_away_player_own_cups.get(), aces=self.spinbox_away_player_aces.get(),
            serve_breaks=self.spinbox_away_player_serve_breaks.get(),
            penalty_shots_made=self.spinbox_away_player_psm.get(),
            penalty_shots_attempted=self.spinbox_away_player_psa.get(),
            penalties_committed=self.spinbox_home_player_psa.get())
        self.reset_entries()
        self.controller.show_frame(EnterLeagueWindow)


def browse_files_for_entry(entry):
    """
    Browse files and enter text into given entry object
    :param entry: tk.Entry object to enter text into
    """
    entry_text = tk.filedialog.askopenfilename()
    if entry_text is not None:
        entry.delete(0, 'end')
        entry.insert(0, entry_text)
