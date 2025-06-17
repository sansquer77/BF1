import pandas as pd
from fastf1.ergast import Ergast

def get_race_results(season='current'):
    """
    Retorna um DataFrame com todos os resultados de todas as corridas do ano especificado.
    """
    ergast = Ergast()
    results = ergast.get_race_results(season=season)
    desc = results.description
    content = results.content

    # Junta informações da corrida ao resultado de cada piloto
    df = content.merge(
        desc[['round', 'raceName', 'date', 'circuitName']],
        left_on='round', right_on='round'
    )
    # Nome completo do piloto
    df['driverName'] = df['givenName'] + ' ' + df['familyName']
    # Ordena por rodada e posição
    df = df.sort_values(['round', 'positionOrder'])
    return df

def get_driver_cumulative_points(season='current'):
    """
    Retorna um DataFrame com os pontos acumulados de cada piloto por corrida.
    Index: round, raceName
    Colunas: cada piloto
    """
    df = get_race_results(season)
    df['points'] = df['points'].astype(float)
    df['cumulative_points'] = df.groupby('driverName')['points'].cumsum()
    pivot = df.pivot_table(
        index=['round', 'raceName'],
        columns='driverName',
        values='cumulative_points',
        fill_value=0
    ).reset_index()
    return pivot

def get_race_list(season='current'):
    """
    Retorna uma lista de todas as corridas da temporada.
    """
    ergast = Ergast()
    schedule = ergast.get_race_schedule(season=season)
    df = schedule.content
    return df[['round', 'raceName', 'date', 'circuitName']]

def get_driver_list(season='current'):
    """
    Retorna uma lista de todos os pilotos da temporada.
    """
    ergast = Ergast()
    drivers = ergast.get_driver_standings(season=season)
    df = drivers.content
    df['driverName'] = df['givenName'] + ' ' + df['familyName']
    return df[['driverId', 'driverName', 'nationality', 'points', 'position']]
