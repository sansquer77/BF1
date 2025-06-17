import requests
import pandas as pd

BASE_URL = "https://api.jolpi.ca/ergast/f1"

def get_current_season():
    url = f"{BASE_URL}/seasons"
    resp = requests.get(url)
    data = resp.json()
    # Pega a última temporada (mais recente)
    seasons = data.get('MRData', {}).get('SeasonTable', {}).get('Seasons', [])
    if seasons:
        return seasons[-1]['season']
    return "Temporada não encontrada"

def get_current_driver_standings(season=None):
    if season is None:
        season = get_current_season()
    url = f"{BASE_URL}/{season}/driverstandings"
    resp = requests.get(url)
    data = resp.json()
    standings = (
        data.get('MRData', {})
            .get('StandingsTable', {})
            .get('StandingsLists', [{}])[0]
            .get('DriverStandings', [])
    )
    if not standings:
        return pd.DataFrame([{'Info': 'Sem dados de classificação de pilotos.'}])
    df = pd.json_normalize(standings)
    df['driverName'] = df['Driver.givenName'] + ' ' + df['Driver.familyName']
    # Garante colunas esperadas
    expected = ['position', 'driverName', 'Driver.nationality', 'points', 'wins', 'Constructors']
    for col in expected:
        if col not in df.columns:
            df[col] = None
    # Construtores como string
    df['constructorNames'] = df['Constructors'].apply(lambda x: ', '.join([c['name'] for c in x]) if isinstance(x, list) else '')
    return df[['position', 'driverName', 'Driver.nationality', 'points', 'wins', 'constructorNames']]

def get_current_constructor_standings(season=None):
    if season is None:
        season = get_current_season()
    url = f"{BASE_URL}/{season}/constructorstandings"
    resp = requests.get(url)
    data = resp.json()
    standings = (
        data.get('MRData', {})
            .get('StandingsTable', {})
            .get('StandingsLists', [{}])[0]
            .get('ConstructorStandings', [])
    )
    if not standings:
        return pd.DataFrame([{'Info': 'Sem dados de classificação de construtores.'}])
    df = pd.json_normalize(standings)
    expected = ['position', 'Constructor.name', 'Constructor.nationality', 'points', 'wins']
    for col in expected:
        if col not in df.columns:
            df[col] = None
    df = df.rename(columns={
        'Constructor.name': 'name',
        'Constructor.nationality': 'nationality'
    })
    return df[['position', 'name', 'nationality', 'points', 'wins']]

def get_driver_points_by_race(season=None):
    if season is None:
        season = get_current_season()
    url = f"{BASE_URL}/{season}/results"
    resp = requests.get(url)
    data = resp.json()
    races = data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
    if not races:
        return pd.DataFrame([{'Info': 'Sem dados de resultados de corridas.'}])
    all_races = []
    for race in races:
        round_num = int(race['round'])
        race_name = race['raceName']
        for result in race.get('Results', []):
            driver_name = f"{result['Driver']['givenName']} {result['Driver']['familyName']}"
            points = float(result['points'])
            all_races.append({
                'Round': round_num,
                'Race': race_name,
                'driverName': driver_name,
                'points': points
            })
    if not all_races:
        return pd.DataFrame([{'Info': 'Sem dados de resultados de corridas.'}])
    df = pd.DataFrame(all_races)
    df = df.sort_values(['driverName', 'Round'])
    df['cumulative_points'] = df.groupby('driverName')['points'].cumsum()
    pivot = df.pivot_table(
        index=['Round', 'Race'],
        columns='driverName',
        values='cumulative_points',
        fill_value=0
    ).reset_index()
    return pivot

def get_qualifying_vs_race_delta(season=None):
    if season is None:
        season = get_current_season()
    # Última corrida
    url_races = f"{BASE_URL}/{season}/races"
    races_resp = requests.get(url_races)
    races = races_resp.json().get('MRData', {}).get('RaceTable', {}).get('Races', [])
    if not races:
        return pd.DataFrame([{'Info': 'Sem dados de corridas.'}])
    last_race = races[-1]
    round_num = int(last_race['round'])
    # Resultados da corrida
    url_results = f"{BASE_URL}/{season}/{round_num}/results"
    url_qualy = f"{BASE_URL}/{season}/{round_num}/qualifying"
    resp_results = requests.get(url_results)
    resp_qualy = requests.get(url_qualy)
    race_data = resp_results.json().get('MRData', {}).get('RaceTable', {}).get('Races', [{}])[0].get('Results', [])
    qualy_data = resp_qualy.json().get('MRData', {}).get('RaceTable', {}).get('Races', [{}])[0].get('QualifyingResults', [])
    if not race_data or not qualy_data:
        return pd.DataFrame([{'Info': 'Sem dados de qualifying ou corrida para a última prova.'}])
    df_race = pd.json_normalize(race_data)
    df_qualy = pd.json_normalize(qualy_data)
    df_race['driverName'] = df_race['Driver.givenName'] + ' ' + df_race['Driver.familyName']
    df_qualy['driverName'] = df_qualy['Driver.givenName'] + ' ' + df_qualy['Driver.familyName']
    merged = pd.merge(df_race, df_qualy, on='driverName', suffixes=('_race', '_qualy'))
    merged['QualyPos'] = merged['position_qualy'].astype(float)
    merged['RacePos'] = merged['position_race'].astype(float)
    merged['Delta'] = merged['QualyPos'] - merged['RacePos']
    expected_cols = ['driverName', 'QualyPos', 'RacePos', 'Delta']
    for col in expected_cols:
        if col not in merged.columns:
            merged[col] = None
    return merged[expected_cols].sort_values('RacePos')

def get_fastest_lap_times(season=None):
    if season is None:
        season = get_current_season()
    url = f"{BASE_URL}/{season}/results"
    resp = requests.get(url)
    data = resp.json()
    races = data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
    if not races:
        return pd.DataFrame([{'Info': 'Sem dados de corridas.'}])
    last_race = races[-1]
    results = last_race.get('Results', [])
    if not results:
        return pd.DataFrame([{'Info': 'Sem dados de resultados para a última corrida.'}])
    fastest = []
    for result in results:
        if result.get('FastestLap', {}).get('rank') == '1':
            driver_name = f"{result['Driver']['givenName']} {result['Driver']['familyName']}"
            fastest.append({
                'driverName': driver_name,
                'fastestLapTime': result['FastestLap'].get('Time', {}).get('time'),
                'fastestLapSpeed': result['FastestLap'].get('AverageSpeed', {}).get('speed'),
                'positionOrder': result.get('position'),
                'points': result.get('points')
            })
    if not fastest:
        return pd.DataFrame([{'Info': 'Sem volta mais rápida registrada.'}])
    return pd.DataFrame(fastest)

def get_pit_stop_data(season=None):
    if season is None:
        season = get_current_season()
    url_races = f"{BASE_URL}/{season}/races"
    races_resp = requests.get(url_races)
    races = races_resp.json().get('MRData', {}).get('RaceTable', {}).get('Races', [])
    if not races:
        return pd.DataFrame([{'Info': 'Sem dados de corridas.'}])
    last_race = races[-1]
    round_num = int(last_race['round'])
    url = f"{BASE_URL}/{season}/{round_num}/pitstops"
    resp = requests.get(url)
    pitstops = resp.json().get('MRData', {}).get('RaceTable', {}).get('Races', [{}])[0].get('PitStops', [])
    if not pitstops:
        return pd.DataFrame([{'Info': 'Sem dados de pit stop para a última corrida.'}])
    df = pd.json_normalize(pitstops)
    df['driverName'] = df['DriverId']
    expected_cols = ['driverName', 'stop', 'lap', 'time', 'duration']
    for col in expected_cols:
        if col not in df.columns:
            df[col] = None
    return df[expected_cols]
