import pandas as pd
from pathlib import Path

SECTORS = {'Cement', 'Fertilisers', 'Aluminium', 'Hydrogen', 'Iron and steel'}
FALLBACK_SHEET = '_Other Countries and Territorie'


def _parse_sheet(path: str, sheet_name: str) -> pd.DataFrame:
    raw = pd.read_excel(path, sheet_name=sheet_name, header=None, engine='openpyxl')
    raw = raw.rename(columns={0:'cn_code',1:'description',2:'direct',3:'indirect',
                              4:'total',5:'dv_2026',6:'dv_2027',7:'dv_2028',8:'route'})
    is_header = raw['cn_code'].isin(SECTORS)
    raw['sector'] = raw['cn_code'].where(is_header).ffill()
    raw = raw[raw['sector'].notna() & ~is_header]
    d = raw['direct'].astype(str).str.strip()
    raw['is_fallback'] = d.eq('–')
    raw = raw[~d.eq('see below')]
    for c in ['direct','indirect','total','dv_2026','dv_2027','dv_2028']:
        raw[c] = pd.to_numeric(raw[c], errors='coerce')
    raw['cn_code'] = raw['cn_code'].astype(str).str.replace(r'\s+','',regex=True).str.replace(r'\.0$','',regex=True)
    raw['route'] = raw['route'].astype(str).str.replace('\xa0',' ',regex=False).str.strip()
    return raw[['cn_code','sector','description','direct','indirect','total',
                'dv_2026','dv_2028','route','is_fallback']].reset_index(drop=True)


def parse_turkiye_defaults(path: str) -> pd.DataFrame:
    df = _parse_sheet(path, 'Türkiye')
    fallback = _parse_sheet(path, FALLBACK_SHEET).drop_duplicates('cn_code').set_index('cn_code')

    # is_fallback rows had '–' for direct in the Türkiye sheet — pull their
    # direct/indirect/total from the _Other Countries default table instead.
    needs_fallback = df['is_fallback']
    for col in ['direct', 'indirect', 'total']:
        df.loc[needs_fallback, col] = df.loc[needs_fallback, 'cn_code'].map(fallback[col])

    return df


def main() -> None:
    base_dir = Path(__file__).resolve().parent.parent
    input_path = base_dir / 'data' / 'item1.xlsx'
    output_path = base_dir / 'data' / 'item1_cleaned.csv'

    df = parse_turkiye_defaults(input_path)
    df.to_csv(output_path, index=False)
    print(f'Cleaned data saved to: {output_path}')


if __name__ == '__main__':
    main()