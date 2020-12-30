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

    def connect_server(self, host, user, password, b_reset_schema=False):
        """
        Connects to MySQL server and keeps connection open until this is called again or the connection is closed
        :param host: Host name/IP to connect to
        :param user: User on host to log in with
        :param password: User password
        :param b_reset_schema: Whether schema should be reset upon connection
        """
        # If trying to connect to something else, make sure to close previous database first
        self.disconnect_server()
        try:
            self.db_connection = mysql.connector.connect(host=host, user=user, password=password)
            self.db_cursor = self.db_connection.cursor()
            self.db_cursor.execute('use pppl')
            # Reset schema if told to
            if b_reset_schema:
                self.reset_database_schema()
            # Notify via callbacks that server is now connected and database is available
            for table in Table:
                for callback in self.insertion_callbacks_dict[table]:
                    callback()
        except Exception:
            error_reporting.report_error(get_error())
            return

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
                    start_date date not null unique,
                    end_date date unique,
                    postseason_start_game int unsigned not null,
                    primary key (start_date)
                )
            """)
            self.db_cursor.execute("""
                create table game (
                    game_id int not null unique auto_increment,
                    season date not null,
                    game_number int not null,
                    home_player_id int not null,
                    away_player_id int not null,
                    primary key (game_id),
                    foreign key (season) references season(start_date),
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
                    serve_breaks int not null,
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
        except mysql.connector.IntegrityError:
            pass  # Ignore if role already exists
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

    def insert_player_game(self, player_id, game_id, footwear_id, differential, knockovers, own_cups, aces,
                           serve_breaks, penalty_shots_made, penalty_shots_attempted, penalties_committed):
        try:
            self.db_cursor.execute("""
                insert into player_game (
                    player_id,
                    game_id,
                    footwear_id,
                    differential,
                    knockovers,
                    own_cups,
                    aces,
                    serve_breaks,
                    penalty_shots_made,
                    penalty_shots_attempted,
                    penalties_committed
                )
                values (""" +
                    str(player_id) + ',' +
                    str(game_id) + ',' +
                    str(footwear_id) + ',' +
                    str(differential) + ',' +
                    str(knockovers) + ',' +
                    str(own_cups) + ',' +
                    str(aces) + ',' +
                    str(serve_breaks) + ',' +
                    str(penalty_shots_made) + ',' +
                    str(penalty_shots_attempted) + ',' +
                    str(penalties_committed) + """
                )"""
            )
            self.db_connection.commit()
        except Exception:
            error_reporting.report_error(get_error())
            return
        # Perform callbacks upon successful insertion of player game
        for callback in self.insertion_callbacks_dict[Table.PLAYER_GAME]:
            callback()

    def insert_footwear(self, footwear_name):
        try:
            self.db_cursor.execute("""
                insert into footwear (footwear_name)
                values ('""" + footwear_name + """')
            """)
            self.db_connection.commit()
        except mysql.connector.IntegrityError:
            pass  # Ignore if trying to insert an existing footwear
        except Exception:
            error_reporting.report_error(get_error())
        # Perform callbacks upon successful insertion of footwear
        for callback in self.insertion_callbacks_dict[Table.FOOTWEAR]:
            callback()

    def insert_season(self, start_date, postseason_start_game, end_date=None):
        try:
            self.db_cursor.execute("""
                insert into season (start_date, postseason_start_game""" +
                                   (""", end_date""" if end_date is not None else '') + """)
                values (
                    '""" + start_date.strftime('%Y-%m-%d') + "'," +
                    str(postseason_start_game) +
                    (", '" + end_date.strftime('%Y-%m-%d') + "'" if end_date is not None else '') +
                """)
            """)
            self.db_connection.commit()
        except Exception:
            error_reporting.report_error(get_error())
            return
        # Perform callbacks upon successful insertion of player game
        for callback in self.insertion_callbacks_dict[Table.SEASON]:
            callback()

    def insert_game(self, season, game_number, home_player_id, away_player_id):
        try:
            self.db_cursor.execute("""
                insert into game (season, game_number, home_player_id, away_player_id)
                values (
                    '""" + season.strftime('%Y-%m-%d') + "'," +
                    str(game_number) + ',' +
                    str(home_player_id) + ',' +
                    str(away_player_id) + """
                )
            """)
            self.db_connection.commit()
        except Exception:
            error_reporting.report_error(get_error())
            return
        # Perform callbacks upon successful insertion of player game
        for callback in self.insertion_callbacks_dict[Table.GAME]:
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

    def get_season_start_dates(self):
        try:
            self.db_cursor.execute("""
                select start_date
                from season
            """)
            raw_result = self.db_cursor.fetchall()
            if len(raw_result) == 0:
                return []
            result = [row[0] for row in raw_result]
            return result
        except Exception:
            error_reporting.report_error(get_error())

    def get_footwear_names(self):
        try:
            self.db_cursor.execute("""
                select footwear_name
                from footwear
            """)
            raw_result = self.db_cursor.fetchall()
            if len(raw_result) == 0:
                return []
            result = [row[0] for row in raw_result]
            return result
        except Exception:
            error_reporting.report_error(get_error())

    def get_footwear_id(self, footwear_name):
        try:
            self.db_cursor.execute("""
                select footwear_id
                from footwear
                where footwear_name = '""" + footwear_name + """'
                limit 1
            """)
            raw_result = self.db_cursor.fetchall()
            if len(raw_result) == 0:
                return -1
            return raw_result[0][0]
        except Exception:
            error_reporting.report_error(get_error())

    def get_player_id(self, player_name):
        try:
            self.db_cursor.execute("""
                select player_id
                from player
                where name = '""" + player_name + """'
                limit 1
            """)
            raw_result = self.db_cursor.fetchall()
            if len(raw_result) == 0:
                return -1
            return raw_result[0][0]
        except Exception:
            error_reporting.report_error(get_error())

    # SELECT returning multiple fields

    def get_player_details(self, player_name):
        try:
            self.db_cursor.execute("""
                select
                    name,
                    logo,
                    headshot,
                    player_id
                from player
                where name='""" + player_name + """'
                limit 1
            """)
            raw_result = self.db_cursor.fetchall()
            if len(raw_result) == 0:
                return []
            return raw_result[0]
        except Exception:
            error_reporting.report_error(get_error())

    def get_next_unplayed_game_details(self):
        try:
            self.db_cursor.execute("""
                select 
                    g.game_id,
                    g.season,
                    g.game_number,
                    p_home.name as 'home_player_name',
                    p_away.name as 'away_player_name'
                from game g
                inner join player p_home on (g.home_player_id = p_home.player_id)
                inner join player p_away on (g.away_player_id = p_away.player_id)
                where g.game_id not in (
                    select game_id
                    from player_game
                )
                order by g.season, g.game_number
                limit 1
            """)
            raw_result = self.db_cursor.fetchall()
            if len(raw_result) == 0:
                return []
            return raw_result[0]
        except Exception:
            error_reporting.report_error(get_error())

    # REGISTER CALLBACKS FOR UPDATES/INSERT REPORTING

    def register_insert_callback(self, table: Table, callback):
        if table in Table:
            self.insertion_callbacks_dict[table].append(callback)


def get_error():
    return str(sys.exc_info()[0]) + '\n\t' + str(sys.exc_info()[1])
