import pandas as pd
from fastf1.ergast import Ergast

def get_current_season():
    ergast = Ergast()
    schedule = ergast.get_race_schedule('current')
    # schedule já é um DataFrame
    if not schedule.empty and 'season' in schedule.columns:
        return schedule['season'].iloc[0]
    else:
        return "Temporada não encontrada"

def get_current_driver_standings():
    from fastf1.ergast import Ergast
    ergast = Ergast()
    standings = ergast.get_driver_standings('current')
    if len(standings.content) > 0:
        df = standings.content[-1]
        df['driverName'] = df['givenName'] + ' ' + df['familyName']
        # 'constructorNames' pode ser uma lista, junte em string
        if 'constructorNames' in df.columns:
            df['constructorNames'] = df['constructorNames'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
        # Monta lista de colunas conforme disponíveis
        cols = ['position', 'driverName', 'points', 'wins', 'constructorNames']
        if 'nationality' in df.columns:
            cols.insert(2, 'nationality')
        return df[cols]
    else:
        return pd.DataFrame([{'Info': 'Sem dados de classificação de pilotos.'}])

def get_current_constructor_standings():
    ergast = Ergast()
    standings = ergast.get_constructor_standings('current')
    if len(standings.content) > 0:
        df = standings.content[-1]
        return df[['position', 'name', 'nationality', 'points', 'wins']]
    else:
        return pd.DataFrame([{'Info': 'Sem dados de classificação de construtores.'}])

def get_driver_points_by_race():
    ergast = Ergast()
    results = ergast.get_race_results('current')
    desc = results.description  # DataFrame de rounds/corridas
    content = results.content   # lista de DFs, um por corrida

    if not content or desc.empty:
        return pd.DataFrame([{'Info': 'Sem dados de resultados de corridas.'}])

    all_races = []
    for i, race_df in enumerate(content):
        if race_df.empty:
            continue
        race_name = desc.iloc[i]['raceName']
        round_num = desc.iloc[i]['round']
        race_df['driverName'] = race_df['givenName'] + ' ' + race_df['familyName']
        race_df['Race'] = race_name
        race_df['Round'] = round_num
        all_races.append(race_df[['Round', 'Race', 'driverName', 'points']])
    if not all_races:
        return pd.DataFrame([{'Info': 'Sem dados de resultados de corridas.'}])
    df = pd.concat(all_races)
    df['points'] = df['points'].astype(float)
    df = df.sort_values(['driverName', 'Round'])
    df['cumulative_points'] = df.groupby('driverName')['points'].cumsum()
    pivot = df.pivot_table(
        index=['Round', 'Race'],
        columns='driverName',
        values='cumulative_points',
        fill_value=0
    ).reset_index()
    return pivot

def get_qualifying_vs_race_delta():
    ergast = Ergast()
    results = ergast.get_race_results('current')
    desc = results.description
    content = results.content
    if not content or desc.empty:
        return pd.DataFrame([{'Info': 'Sem dados de corrida para análise de delta.'}])
    last_round = desc['round'].max()
    idx_last = desc[desc['round'] == last_round].index[0]
    df_race = content[idx_last]

    qualy = ergast.get_qualifying('current', round=last_round)
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
    ergast = Ergast()
    results = ergast.get_race_results('current')
    desc = results.description
    content = results.content
    if not content or desc.empty:
        return pd.DataFrame([{'Info': 'Sem dados de corrida para a última prova.'}])
    last_round = desc['round'].max()
    idx_last = desc[desc['round'] == last_round].index[0]
    df_race = content[idx_last]
    if df_race.empty:
        return pd.DataFrame([{'Info': 'Sem dados de corrida para a última prova.'}])
    df_race['driverName'] = df_race['givenName'] + ' ' + df_race['familyName']
    fastest = df_race[df_race['fastestLapRank'] == 1]
    if fastest.empty:
        return pd.DataFrame([{'Info': 'Sem volta mais rápida registrada.'}])
    return fastest[['driverName', 'fastestLapTime', 'fastestLapSpeed', 'positionOrder', 'points']]

def get_pit_stop_data():
    ergast = Ergast()
    results = ergast.get_race_results('current')
    desc = results.description
    if desc.empty:
        return pd.DataFrame([{'Info': 'Sem dados de corridas para pit stops.'}])
    last_round = desc['round'].max()
    pitstops = ergast.get_pit_stops('current', round=last_round)
    if pitstops.empty:
        return pd.DataFrame([{'Info': 'Sem dados de pit stop para a última corrida.'}])
    pitstops['driverName'] = pitstops['givenName'] + ' ' + pitstops['familyName']
    return pitstops[['driverName', 'stop', 'lap', 'time', 'duration']]
