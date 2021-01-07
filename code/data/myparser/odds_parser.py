from setting import *

def parse_sanrenpuku(file_srp_odds, file_srp_odds_parsed):
    df_srp = pd.read_csv(file_srp_odds, index_col=0)
    df_srp.reset_index(drop=True, inplace=True)
    df_srp.drop('選択', axis=1, inplace=True)

    df_srp = df_srp.loc[df_srp.オッズ!='---.-']

    tmp = df_srp['組み合わせ'].str.replace('  ', ' ').str.split(' ', expand=True)
    tmp.columns = ['馬1', '馬2', '馬3']

    for col in tmp.columns:
        tmp[col] = tmp[col].astype(int).astype(str).str.zfill(2)

    df_srp = pd.concat([df_srp, tmp], axis=1)

    df_srp['三連複_key'] = df_srp.race_id.astype(str) + df_srp['馬1'] + df_srp['馬2'] + df_srp['馬3']

    df_srp.オッズ = df_srp.オッズ.astype(float)
    df_srp.to_csv(file_srp_odds_parsed, index=False)


def parse_hukusho(file_hukusho_odds):
    df_hukusho = pd.read_csv(file_hukusho_odds)

    df_hukusho = df_hukusho.loc[df_hukusho.オッズ!='---.-']
    df_hukusho = df_hukusho.loc[df_hukusho.オッズ!='-3.0 - -3.0']
    df_hukusho.reset_index(drop=True, inplace=True)

    tmp = df_hukusho['オッズ'].str.split('-', expand=True)
    tmp.columns = ['複勝_odds', '_']

    df_hukusho = pd.concat([df_hukusho, tmp], axis=1)
    df_hukusho.複勝_odds = df_hukusho.複勝_odds.astype(str).str.strip().astype(np.float64)
    return df_hukusho
