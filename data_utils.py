import pandas as pd
from fastf1.ergast import Ergast

def get_current_season():
    ergast = Ergast()
    schedule = ergast.get_race_schedule('current')
    if not schedule.empty and 'season' in schedule.columns:
        return schedule['season'].iloc[0]
    else:
        return "Temporada não encontrada"

def get_current_driver_standings():
    ergast = Ergast()
    standings = ergast.get_driver_standings('current')
    if len(standings.content) > 0:
        df = standings.content[-1]
        df['driverName'] = df['givenName'] + ' ' + df['familyName']
        if 'constructorNames' in df.columns:
            df['constructorNames'] = df['constructorNames'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
        # Garante todas as colunas esperadas
        expected_cols = ['position', 'driverName', 'nationality', 'points', 'wins', 'constructorNames']
        for col in expected_cols:
            if col not in df.columns:
                df[col] = None
        return df[expected_cols]
    else:
        return pd.DataFrame([{'Info': 'Sem dados de classificação de pilotos.'}])

def get_current_constructor_standings():
    ergast = Ergast()
    standings = ergast.get_constructor_standings('current')
    if len(standings.content) > 0:
        df = standings.content[-1]
        expected_cols = ['position', 'name', 'nationality', 'points', 'wins']
        for col in expected_cols:
            if col not in df.columns:
                df[col] = None
        return df[expected_cols]
    else:
        return pd.DataFrame([{'Info': 'Sem dados de classificação de construtores.'}])

def get_driver_points_by_race():
    ergast = Ergast()
    results = ergast.get_race_results('2025')
    desc = results.description
    content = results.content

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
    # Garante que sempre tenha as colunas 'Round' e 'Race'
    for col in ['Round', 'Race']:
        if col not in pivot.columns:
            pivot[col] = None
    return pivot

def get_qualifying_vs_race_delta():
    from fastf1.ergast import Ergast
    import pandas as pd

    ergast = Ergast()
    results = ergast.get_race_results('current')
    desc = results.description
    content = results.content

    if not content or desc.empty:
        return pd.DataFrame([{'Info': 'Sem dados de corrida para análise de delta.'}])

    last_round = desc['round'].max()
    idx_last = desc[desc['round'] == last_round].index[0]
    df_race = content[idx_last]

    qualy = ergast.get_qualifying_results('current', round=last_round)
    # Corrigido: verifica se há DataFrame em qualy.content
    if not qualy.content or df_race.empty:
        return pd.DataFrame([{'Info': 'Sem dados de qualifying ou corrida para a última prova.'}])

    qualy_df = qualy.content[0]  # Pega o primeiro DataFrame da lista
    qualy_df['driverName'] = qualy_df['givenName'] + ' ' + qualy_df['familyName']
    df_race['driverName'] = df_race['givenName'] + ' ' + df_race['familyName']

    merged = pd.merge(df_race, qualy_df, on='driverName', suffixes=('_race', '_qualy'))

    for col in ['positionOrder_qualy', 'positionOrder_race']:
        if col not in merged.columns:
            merged[col] = None

    merged['QualyPos'] = merged['positionOrder_qualy']
    merged['RacePos'] = merged['positionOrder_race']
    merged['Delta'] = merged['QualyPos'] - merged['RacePos']

    expected_cols = ['driverName', 'QualyPos', 'RacePos', 'Delta']
    for col in expected_cols:
        if col not in merged.columns:
            merged[col] = None

    return merged[expected_cols].sort_values('RacePos')

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
    expected_cols = ['driverName', 'fastestLapTime', 'fastestLapSpeed', 'positionOrder', 'points']
    for col in expected_cols:
        if col not in fastest.columns:
            fastest[col] = None
    if fastest.empty:
        return pd.DataFrame([{'Info': 'Sem volta mais rápida registrada.'}])
    return fastest[expected_cols]

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
    expected_cols = ['driverName', 'stop', 'lap', 'time', 'duration']
    for col in expected_cols:
        if col not in pitstops.columns:
            pitstops[col] = None
    return pitstops[expected_cols]
