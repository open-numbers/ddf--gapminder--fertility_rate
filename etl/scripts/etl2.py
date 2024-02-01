# coding: utf-8

import os.path as osp
import pandas as pd

from ddf_utils.io import open_google_spreadsheet, serve_datapoint


DOCID = '1aLtIpAWvDGGa9k2XXEz6hZugWn0wCd5nmzaRPPjbYNA'
SHEET = 'data-for-countries-etc-by-year'
SHEETS = {'country':'data-for-countries-etc-by-year','global':'data-for-world-by-year','world_4region':'data-for-regions-by-year'}


DIMENSIONS = ['geo', 'time']
OUT_DIR = '../../'

COLUMN_TO_CONCEPT = {'Babies per woman':'children_per_woman_total_fertility'}


def gen_datapoints(df_: pd.DataFrame):
    df = df_.copy()
    df = df.set_index(DIMENSIONS).drop('name', axis=1)  # set index and drop column 'name'
    for c in df:
        yield (c, df[[c]])


def create_geo_domain(df: pd.DataFrame) -> pd.DataFrame:
    return df[['geo', 'name']].drop_duplicates()


def main():
    print('running etl...')
    for sheet in SHEETS:
        data = pd.read_excel(open_google_spreadsheet(DOCID), sheet_name=SHEETS[sheet])

        measures = list()

        for c, df in gen_datapoints(data):
            c_id = COLUMN_TO_CONCEPT[c]
            df.columns = [c_id]
            #serve_datapoint(df, OUT_DIR, c_id)
            df.index.rename([sheet,'time'],inplace=True)
            #print(df.index)
            df.to_csv(osp.join(OUT_DIR, 'ddf--datapoints--'+c_id+'--by--'+sheet+'.csv'))

   # Writing Geos/Regions/Global
        geo_df = create_geo_domain(data)
        
        geo_df = geo_df.rename(columns={'geo':sheet})
        geo_df.to_csv(osp.join(OUT_DIR, 'ddf--entities--'+sheet+'.csv'), index=False)

    measures.append((COLUMN_TO_CONCEPT[list(COLUMN_TO_CONCEPT.keys())[0]],list(COLUMN_TO_CONCEPT.keys())[0],'measure',''))

    measures_df = pd.DataFrame(measures, columns=['concept', 'name','concept_type','domain'])
    measures_df['concept_type'] = 'measure'

    discrete_df = pd.DataFrame.from_dict(
        dict(concept=['geo', 'name', 'time','country','world_4region','global','domain'],
             name=['Geo', 'Name', 'Time','Country','four regions','global','Domain'],
             concept_type=['entity_domain', 'string', 'time','entity_set','entity_set','entity_set','string'],
             domain=['','','','geo','geo','geo',''])
    )
    pd.concat([measures_df, discrete_df], ignore_index=True).to_csv(osp.join(OUT_DIR, 'ddf--concepts.csv'), index=False)




if __name__ == '__main__':
    main()
    print('Done.')
