"""
Set parameters for API calls and SQL queries used for table transformations
"""

season_start = 1999
season_end = 2022

current_season = 2022
latest_week = 15

weekly_config = {
    'name':'weekly',
    'date_range':range(season_start, season_end+1)
}

seasonal_config = {
    'name':'seasonal',
    'date_range':range(season_start, season_end+1)
}

team_desc_config = {
    'name':'team_descriptions'
}

rosters_config = {
    'name':'rosters',
    'date_range':range(season_start, season_end+1)
}

win_totals_config = {
    'name':'win_totals',
    'date_range':range(season_start, season_end+1)
}

score_lines_config = {
    'name':'score_lines',
    'date_range':range(season_start, season_end+1)
}

officials_config = {
    'name':'officials',
    'date_range':range(season_start, season_end+1)
}

draft_picks_config = {
    'name':'draft_picks',
    'date_range':range(season_start, season_end+1)
}

draft_values_config = {
    'name':'draft_values'
}

combine_config = {
    'name':'combine',
    'date_range':range(season_start, season_end+1)
}

schedules_config = {
    'name':'schedules',
    'date_range':range(season_start, season_end+1)
}

ids_config = {
    'name':'ids'
}

ngs_passing_config = {
    'name':'ngs_pass',
    'type':'passing',
    'date_range':range(season_start, season_end+1)
}

ngs_receiving_config = {
    'name':'ngs_rec',
    'type':'receiving',
    'date_range':range(season_start, season_end+1)
}

ngs_rushing_config = {
    'name':'ngs_rush',
    'type':'rushing',
    'date_range':range(season_start, season_end+1)
}

injuries_config = {
    'name':'injuries',
    'date_range':range(2009, season_end+1)
}

qbr_config = {
    'name':'qbr',
    'date_range':range(2006, season_end+1)
}

pfr_passing_config = {
    'name':'pfr_pass',
    'type':'pass',
    'date_range':range(2019, season_end+1)
}

pfr_receiving_config = {
    'name':'pfr_rec',
    'type':'rec',
    'date_range':range(2019, season_end+1)
}

pfr_rushing_config = {
    'name':'pfr_rush',
    'type':'rush',
    'date_range':range(2019, season_end+1)
}

snap_counts_config = {
    'name':'snap_counts',
    'date_range':range(2012, season_end+1)
}

play_by_play_config = {
    'name':'pbp',
    'date_range':range(season_start, season_end+1),
    'cols': ['game_id', 'season', 'week', 'season_type', 'home_team', 'away_team', 
             'posteam', 'defteam', 'time', 'game_half', 'quarter_end', 'touchdown', 
             'pass_touchdown', 'rush_touchdown', 'return_touchdown', 'extra_point_attempt', 
             'extra_point_result', 'field_goal_attempt', 'field_goal_result', 
             'two_point_attempt', 'two_point_conv_result', 'safety', 'success', 'td_team', 
             'posteam_score', 'defteam_score', 'posteam_score_post', 'defteam_score_post', 
             'total_home_score', 'total_away_score', 'away_score', 'home_score', 'desc', 
             'yardline_100', 'goal_to_go', 'yrdln', 'ydstogo', 'play_type', 'penalty', 
             'receiver_player_id', 'receiver_player_name', 'receiving_yards', 'rusher_player_id', 
             'rusher_player_name', 'rushing_yards']
}