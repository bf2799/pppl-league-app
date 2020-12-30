def get_next_game(player_games, total_meetings, combos):
    """
    Helper function for generate_new_schedule to avoid repeat code
    """
    player_games[combos[0][0]] += 1
    player_games[combos[0][1]] += 1
    total_meetings[combos[0]] += 1
    return combos[0]


def generate_new_schedule(games_per_player, player_ids):
    # Generate all possible pairings of home/away
    game_combos = []
    for home in player_ids:
        for away in player_ids:
            if home != away:
                game_combos.append((home, away))
    # Keep track of schedule in a game array and each player's number of games played in a player games array
    games = []
    player_games = {id_: 0 for id_ in player_ids}
    total_meetings = {(home, away): 0 for home in player_ids for away in player_ids}
    # Keep adding games until all players have played at least the given number of games
    while player_games[min(player_games, key=player_games.get)] < games_per_player:

        # Loop through game combos to find next game according to following order
        # Lowest meetings between opponents
        # Lowest meetings between opponents on given sides
        # Lowest games already played
        # Most games since home/away players were home/away - maximum of two
        # Most games since home/away player was home/away - minimum of two
        # Most games since home/away player played - maximum of two
        # Most games since home/away player played - minimum of two
        # Most games since last meeting between opponents

        # Keep combos with lowest total meetings between opponents
        remaining_combos = game_combos.copy()
        combos_total_meetings = [total_meetings[combo] + total_meetings[combo[::-1]]
                                 for combo in remaining_combos]
        min_total_meetings = min(combos_total_meetings)
        remaining_combos = [remaining_combos[combo] for combo in range(len(remaining_combos))
                            if combos_total_meetings[combo] == min_total_meetings]

        # Keep combos with lowest total meetings between opponents on given sides
        combos_total_meetings = [total_meetings[combo] for combo in remaining_combos]
        min_total_meetings = min(combos_total_meetings)
        next_combos = [remaining_combos[combo] for combo in range(len(remaining_combos))
                       if combos_total_meetings[combo] == min_total_meetings]
        if len(next_combos) > 1:
            remaining_combos = next_combos[:]
        elif len(next_combos) == 1:
            games.append(get_next_game(player_games, total_meetings, next_combos))
            continue

        # Keep combos with lowest total games already played
        combos_games_played = [player_games[combo[0]] + player_games[combo[1]] for combo in remaining_combos]
        min_games_played = min(combos_games_played)
        next_combos = [remaining_combos[combo] for combo in range(len(remaining_combos))
                       if combos_games_played[combo] == min_games_played]
        if len(next_combos) > 1:
            remaining_combos = next_combos[:]
        elif len(next_combos) == 1:
            games.append(get_next_game(player_games, total_meetings, next_combos))
            continue

        # Keep combos with most games since home/away players were home/away - maximum of two players
        player_games_since_last_home = [-1] * len(player_ids)
        player_games_since_last_away = [-1] * len(player_ids)
        game_counter = len(games) - 1
        while min(player_games_since_last_home) == -1 and min(player_games_since_last_away) == -1 and game_counter >= 0:
            if player_games_since_last_home[player_ids.index(games[game_counter][0])] == -1:
                player_games_since_last_home[player_ids.index(games[game_counter][0])] = len(games) - game_counter
            if player_games_since_last_away[player_ids.index(games[game_counter][1])] == -1:
                player_games_since_last_away[player_ids.index(games[game_counter][1])] = len(games) - game_counter
            game_counter -= 1
        combos_games_since_last_max = [max(player_games_since_last_home[player_ids.index(combo[0])],
                                           player_games_since_last_away[player_ids.index(combo[1])])
                                       for combo in remaining_combos]
        max_games_since_last = -1 if -1 in combos_games_since_last_max else max(combos_games_since_last_max)
        next_combos = [remaining_combos[combo] for combo in range(len(remaining_combos))
                       if combos_games_since_last_max[combo] == max_games_since_last]
        if len(next_combos) > 1:
            remaining_combos = next_combos[:]
        elif len(next_combos) == 1:
            games.append(get_next_game(player_games, total_meetings, next_combos))
            continue

        # Keep combos with most games since home/away players were home/away - minimum of two players
        combos_games_since_last_min = [min(player_games_since_last_home[player_ids.index(combo[0])],
                                           player_games_since_last_away[player_ids.index(combo[1])])
                                       for combo in remaining_combos]
        max_games_since_last = -1 if -1 in combos_games_since_last_min else max(combos_games_since_last_min)
        next_combos = [remaining_combos[combo] for combo in range(len(remaining_combos))
                       if combos_games_since_last_min[combo] == max_games_since_last]
        if len(next_combos) > 1:
            remaining_combos = next_combos[:]
        elif len(next_combos) == 1:
            games.append(get_next_game(player_games, total_meetings, next_combos))
            continue

        # Keep combos with most games since last played - maximum of two players
        player_games_since_last = [-1] * len(player_ids)
        game_counter = len(games) - 1
        while min(player_games_since_last) == -1 and game_counter >= 0:
            for i in range(2):
                if player_games_since_last[player_ids.index(games[game_counter][i])] == -1:
                    player_games_since_last[player_ids.index(games[game_counter][i])] = len(games) - game_counter
            game_counter -= 1
        combos_games_since_last_max = [max(player_games_since_last[player_ids.index(combo[0])],
                                           player_games_since_last[player_ids.index(combo[1])])
                                       for combo in remaining_combos]
        max_games_since_last = -1 if -1 in combos_games_since_last_max else max(combos_games_since_last_max)
        next_combos = [remaining_combos[combo] for combo in range(len(remaining_combos))
                       if combos_games_since_last_max[combo] == max_games_since_last]
        if len(next_combos) > 1:
            remaining_combos = next_combos[:]
        elif len(next_combos) == 1:
            games.append(get_next_game(player_games, total_meetings, next_combos))
            continue

        # Keep combos with player that has most games since last played - minimum of two players
        combos_games_since_last_min = [min(player_games_since_last[player_ids.index(combo[0])],
                                           player_games_since_last[player_ids.index(combo[1])])
                                       for combo in remaining_combos]
        max_games_since_last = -1 if -1 in combos_games_since_last_min else max(combos_games_since_last_min)
        next_combos = [remaining_combos[combo] for combo in range(len(remaining_combos))
                       if combos_games_since_last_min[combo] == max_games_since_last]
        if len(next_combos) > 1:
            remaining_combos = next_combos[:]
        elif len(next_combos) == 1:
            games.append(get_next_game(player_games, total_meetings, next_combos))
            continue

        # Keep combos with most games since opponents last played each other
        reversed_games = games[::-1]
        combos_games_since_last = [min(reversed_games.index(combo), reversed_games.index(combo[::-1]))
                                   if (combo in reversed_games or combo[::-1] in reversed_games) else -1
                                   for combo in remaining_combos]
        max_games_since_last = -1 if -1 in combos_games_since_last else max(combos_games_since_last)
        remaining_combos = [remaining_combos[combo] for combo in range(len(remaining_combos))
                            if combos_games_since_last[combo] == max_games_since_last]

        # Add random game if still no tiebreakers have been broken
        games.append(get_next_game(player_games, total_meetings, remaining_combos))
    return games
