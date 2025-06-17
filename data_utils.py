import pandas as pd
from fastf1.ergast import Ergast

def get_current_season():
    ergast = Ergast()
    schedule = ergast.get_race_schedule('current')
    content = schedule.data
    if not content.empty and 'season' in content.columns:
        return content['season'].iloc[0]
    else:
        return "Temporada não encontrada"

def get_current_driver_standings():
    """Retorna o DataFrame de classificação atual dos pilotos."""
    ergast = Ergast()
    standings = ergast.get_driver_standings('current')
    df = standings.data
    df['driverName'] = df['givenName'] + ' ' + df['familyName']
    return df[['position', 'driverName', 'nationality', 'points', 'wins', 'constructors']]

def get_current_constructor_standings():
    """Retorna o DataFrame de classificação atual dos construtores."""
    ergast = Ergast()
    standings = ergast.get_constructor_standings('current')
    df = standings.data
    return df[['position', 'name', 'nationality', 'points', 'wins']]

def get_driver_points_by_race():
    """Retorna DataFrame com pontos acumulados dos pilotos por corrida."""
    ergast = Ergast()
    results = ergast.get_race_results('current')
    desc = results.description.data
    content = results.data

    df = content.merge(
        desc[['round', 'raceName']],
        left_on='round', right_on='round'
    )
    df['driverName'] = df['givenName'] + ' ' + df['familyName']
    df['points'] = df['points'].astype(float)
    df = df.sort_values(['driverName', 'round'])
    df['cumulative_points'] = df.groupby('driverName')['points'].cumsum()
    pivot = df.pivot_table(
        index=['round', 'raceName'],
        columns='driverName',
        values='cumulative_points',
        fill_value=0
    ).reset_index().rename(columns={'round': 'Round', 'raceName': 'Race'})
    return pivot

def get_qualifying_vs_race_delta():
    """Retorna DataFrame com a diferença entre posição de largada e chegada na última corrida."""
    ergast = Ergast()
    results = ergast.get_race_results('current')
    desc = results.description.data
    content = results.data
    last_round = desc['round'].max()
    df_race = content[content['round'] == last_round]

    qualy = ergast.get_qualifying('current', round=last_round).data
    if qualy.empty or df_race.empty:
        return pd.DataFrame([{'Info': 'Sem dados de qualifying ou corrida para a última prova.'}])
    qualy['driverName'] = qualy['givenName'] + ' ' + qualy['familyName']
    df_race['driverName'] = df_race['givenName'] + ' ' + df_race['familyName']

    merged = pd.merge(df_race, qualy, on='driverName', suffixes=('_race', '_qualy'))
    merged['QualyPos'] = merged['positionOrder_qualy']
    merged['RacePos'] = merged['positionOrder_race']
    merged['Delta'] = merged['QualyPos'] - merged['RacePos']
    return merged[['driverName', 'QualyPos', 'RacePos', 'Delta']].sort_values('RacePos')

def get_fastest_lap_times():
    """Retorna DataFrame com as voltas mais rápidas da última corrida."""
    ergast = Ergast()
    results = ergast.get_race_results('current')
    desc = results.description.data
    content = results.data
    last_round = desc['round'].max()
    df_race = content[content['round'] == last_round]
    if df_race.empty:
        return pd.DataFrame([{'Info': 'Sem dados de corrida para a última prova.'}])
    df_race['driverName'] = df_race['givenName'] + ' ' + df_race['familyName']
    fastest = df_race[df_race['fastestLapRank'] == 1]
    return fastest[['driverName', 'fastestLapTime', 'fastestLapSpeed', 'positionOrder', 'points']]

def get_pit_stop_data():
    """Retorna DataFrame com dados de pit stop da última corrida."""
    ergast = Ergast()
    results = ergast.get_race_results('current')
    desc = results.description.data
    last_round = desc['round'].max()
    pitstops = ergast.get_pit_stops('current', round=last_round).data
    if pitstops.empty:
        return pd.DataFrame([{'Info': 'Sem dados de pit stop para a última corrida.'}])
    pitstops['driverName'] = pitstops['givenName'] + ' ' + pitstops['familyName']
    return pitstops[['driverName', 'stop', 'lap', 'time', 'duration']]
