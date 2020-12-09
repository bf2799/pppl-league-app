import mysql.connector
import error_reporting
import sys
from enum import Enum, auto


class Table(Enum):
    ROLE = auto(),
    PLAYER = auto(),
    PLAYER_ROLE = auto(),
    SEASON = auto(),
    GAME = auto(),
    FOOTWEAR = auto(),
    PLAYER_GAME = auto()


class PPPLDatabase:
    def __init__(self):
        self.db_connection = None
        self.db_cursor = None
        self.insertion_callbacks_dict = {}  # Used to keep track of callbacks to call after an insert/update statement
        for table in Table:  # Each table successfully inserting may trigger different callbacks
            self.insertion_callbacks_dict[table] = []

    def connect_server(self, host, user, password):
        """
        Connects to MySQL server and keeps connection open until this is called again or the connection is closed
        :param host: Host name/IP to connect to
        :param user: User on host to log in with
        :param password: User password
        """
        # If trying to connect to something else, make sure to close previous database first
        self.disconnect_server()
        try:
            self.db_connection = mysql.connector.connect(host=host, user=user, password=password)
            self.db_cursor = self.db_connection.cursor()
            self.db_cursor.execute('use pppl')
        except Exception:
            error_reporting.report_error(get_error())
            return
        # Notify via callbacks that server is now connected and database is available
        for table in Table:
            for callback in self.insertion_callbacks_dict[table]:
                callback()

    def disconnect_server(self):
        """
        Close connection to MySQL server if the connection is opened
        """
        if self.db_connection is not None:
            self.db_connection.close()

    def reset_database_schema(self):
        try:
            self.db_cursor.execute('create database if not exists pppl')
            self.db_cursor.execute('drop table if exists player_game')
            self.db_cursor.execute('drop table if exists footwear')
            self.db_cursor.execute('drop table if exists game')
            self.db_cursor.execute('drop table if exists season')
            self.db_cursor.execute('drop table if exists player_role')
            self.db_cursor.execute('drop table if exists player')
            self.db_cursor.execute('drop table if exists role')
            self.db_cursor.execute("""
                create table role (
                    role_id int not null unique auto_increment,
                    role_name varchar(50) not null unique,
                    primary key (role_id)
                )
            """)
            self.db_cursor.execute("""
                create table player (
                    player_id int not null unique auto_increment,
                    name varchar(50) not null unique,
                    logo longblob,
                    headshot longblob,
                    primary key (player_id)
                )
            """)
            self.db_cursor.execute("""
                create table player_role (
                    player_id int not null,
                    role_id int not null,
                    foreign key (player_id) references player(player_id),
                    foreign key (role_id) references role(role_id)
                )
            """)
            self.db_cursor.execute("""
                create table season (
                    season_id int not null unique auto_increment,
                    start_date date not null unique,
                    end_date date unique,
                    postseason_start_game int unsigned not null,
                    primary key (season_id)
                )
            """)
            self.db_cursor.execute("""
                create table game (
                    game_id int not null unique auto_increment,
                    season_id int not null,
                    game_number int not null,
                    home_player_id int not null,
                    away_player_id int not null,
                    primary key (game_id),
                    foreign key (season_id) references season(season_id),
                    foreign key (home_player_id) references player(player_id),
                    foreign key (away_player_id) references player(player_id)
                )
            """)
            self.db_cursor.execute("""
                create table footwear (
                    footwear_id int not null unique auto_increment,
                    footwear_name varchar(50) not null unique
                )
            """)
            self.db_cursor.execute("""
                create table player_game (
                    player_id int not null,
                    game_id int not null,
                    footwear_id int not null,
                    differential int not null,
                    knockovers int not null,
                    penalty_shots_made int not null,
                    penalty_shots_attempted int not null,
                    penalties_committed int not null,
                    own_cups int not null,
                    aces int not null,
                    foreign key (player_id) references player(player_id),
                    foreign key (game_id) references game(game_id),
                    foreign key (footwear_id) references footwear(footwear_id)
                )
            """)
        except Exception:
            error_reporting.report_error(get_error())

    # INSERT INTO

    def insert_player(self, name, logo=None, headshot=None):
        field_str = 'name'
        values_str = '%s'
        values = [name]
        if logo is not None:
            field_str += ', logo'
            values_str += ',%s'
            values.append(logo)
        if headshot is not None:
            field_str += ', headshot'
            values_str += ',%s'
            values.append(headshot)
        try:
            self.db_cursor.execute(
                'insert into player (' + field_str + ') values (' + values_str + ')', tuple(values))
            self.db_connection.commit()
        except Exception:
            error_reporting.report_error(get_error())
            return
        # Perform callbacks upon successful insertion of player
        for callback in self.insertion_callbacks_dict[Table.PLAYER]:
            callback()

    def insert_role(self, role_name):
        try:
            self.db_cursor.execute(
                "insert into role (role_name) values ('" + role_name + "')")
            self.db_connection.commit()
        except Exception:
            error_reporting.report_error(get_error())
            return
        # Perform callbacks upon successful insertion of role
        for callback in self.insertion_callbacks_dict[Table.ROLE]:
            callback()

    def insert_player_role(self, player_name, role_name):
        try:
            self.db_cursor.execute("""
                insert into player_role (
                    player_id,
                    role_id
                ) 
                values (
                    (
                        select player_id
                        from player
                        where name = '""" + player_name + """'
                    ),
                    (
                        select role_id
                        from role
                        where role_name = '""" + role_name + """'
                    )
                )
            """)
            self.db_connection.commit()
        except Exception:
            error_reporting.report_error(get_error())
            return
        # Perform callbacks upon successful insertion of role
        for callback in self.insertion_callbacks_dict[Table.PLAYER_ROLE]:
            callback()

    # SELECT RETURNING BOOLEAN

    def is_player_in_db(self, player_name):
        try:
            self.db_cursor.execute("""
                select name
                from player
            """)
            raw_result = self.db_cursor.fetchall()
            if len(raw_result) == 0:
                return False
            result = [row[0].lower() for row in raw_result]
            return player_name.lower() in result
        except Exception:
            error_reporting.report_error(get_error())

    def is_role_in_db(self, role_name):
        try:
            self.db_cursor.execute("""
                select role_name
                from role
            """)
            raw_result = self.db_cursor.fetchall()
            if len(raw_result) == 0:
                return False
            result = [row[0].lower() for row in raw_result]
            return role_name.lower() in result
        except Exception:
            error_reporting.report_error(get_error())

    # SELECT RETURNING ONE FIELD

    def get_player_names(self):
        try:
            self.db_cursor.execute("""
                select name
                from player
            """)
            raw_result = self.db_cursor.fetchall()
            if len(raw_result) == 0:
                return []
            result = [row[0].lower() for row in raw_result]
            return result
        except Exception:
            error_reporting.report_error(get_error())

    def get_role_names(self):
        try:
            self.db_cursor.execute("""
                select role_name
                from role
            """)
            raw_result = self.db_cursor.fetchall()
            if len(raw_result) == 0:
                return []
            result = [row[0].lower() for row in raw_result]
            return result
        except Exception:
            error_reporting.report_error(get_error())

    # REGISTER CALLBACKS FOR UPDATES/INSERT REPORTING
    def register_insert_callback(self, table: Table, callback):
        if table in Table:
            self.insertion_callbacks_dict[table].append(callback)



def get_error():
    return str(sys.exc_info()[0]) + '\n\t' + str(sys.exc_info()[1])
