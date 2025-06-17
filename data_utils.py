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
