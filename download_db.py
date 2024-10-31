from typing import Optional

import pandas as pd
import sqlite3
import logging
import time

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("app.log"),
                        logging.StreamHandler()
                    ])

def create_tables():
    with sqlite3.connect('imdb.db') as conn:
        with open('create_tables.sql', 'r') as f:
            conn.executescript(f.read())
        logging.info("Tabelas criadas com sucesso.")

def insert_data_to_db(df, table_name, conn):
    start_time = time.time()
    try:
        logging.info(f"Inserindo dados na tabela {table_name} com {len(df)} registros.")
        df.to_sql(table_name, conn, if_exists='append', index=False)
        elapsed_time = time.time() - start_time
        logging.info(f"Dados inseridos na tabela {table_name} em {elapsed_time:.2f} segundos.")
    except Exception as e:
        logging.error(f"Erro ao inserir dados na tabela {table_name}: {e}", exc_info=True)

def process_genres(df, conn):
    logging.info("Processando a coluna genres.")
    if 'genres' not in df.columns:
        logging.warning("A coluna 'genres' não está presente no DataFrame.")
        return
    df['genres'] = df['genres'].str.split(',')
    df_exploded = df.explode('genres')[['tconst', 'genres']]
    df_exploded = df_exploded.rename(columns={'genres': 'genre'})
    df_exploded = df_exploded.drop_duplicates()
    insert_data_to_db(df_exploded, 'genres', conn)

def process_primary_professions(df, conn):
    logging.info("Processando a coluna primaryProfession.")
    df['primaryProfession'] = df['primaryProfession'].str.split(',')
    df_exploded = df.explode('primaryProfession')[['nconst', 'primaryProfession']]
    df_exploded = df_exploded.drop_duplicates().rename(columns={'primaryProfession': 'profession'})
    insert_data_to_db(df_exploded, 'primaryProfession', conn)

def process_known_for_titles(df, conn):
    logging.info("Processando a coluna knownForTitles.")
    df['knownForTitles'] = df['knownForTitles'].str.split(',')
    df_exploded = df.explode('knownForTitles')[['nconst', 'knownForTitles']]
    df_exploded = df_exploded.drop_duplicates().rename(columns={'knownForTitles': 'tconst'})
    insert_data_to_db(df_exploded, 'knownForTitles', conn)

def main():
    #create_tables()
    conn = sqlite3.connect('imdb.db')
    
    tables = {
        'title_basics': 'title_basics.tsv',
        'name_basics': 'name_basics.tsv',
        'title_akas': 'title_akas.tsv',
        'title_episode': 'title_episode.tsv',
        'title_principals': 'title_principals.tsv',
        'title_ratings': 'title_ratings.tsv',
    }
    
    title_basics_dtype = {
        'tconst': 'string',
        'titleType': 'string',
        'primaryTitle': 'string',
        'originalTitle': 'string',
        'isAdult': 'string',
        'startYear': 'Int64',
        'endYear': 'Int64',
        'runtimeMinutes': 'Int64'
    }
    name_basics_dtype = {
        'nconst': 'string',
        'primaryName': 'string',
        'birthYear': 'Int64',
        'deathYear': 'Int64',
        'primaryProfession': 'string',
        'knownForTitles': 'string'
    }
    
    try:
        title_basics_df = pd.read_csv(tables['title_basics'], sep='\t', na_values='\\N')
        title_basics_df['isAdult'] = title_basics_df['isAdult'].map({'0': False, '1': True})
        genres_df = title_basics_df[['tconst', 'genres']].dropna()
        title_basics_df = title_basics_df.drop(columns=['genres'])
        insert_data_to_db(title_basics_df, 'title_basics', conn)
        process_genres(genres_df, conn)
        
        name_basics_df = pd.read_csv(tables['name_basics'], sep='\t', dtype=name_basics_dtype, na_values='\\N')
        insert_data_to_db(name_basics_df, 'name_basics', conn)
        
        for table_name in ['title_akas', 'title_episode', 'title_principals', 'title_ratings']:
            df = pd.read_csv(tables[table_name], sep='\t', na_values='\\N')
            insert_data_to_db(df, table_name, conn)
        
        process_genres(title_basics_df, conn)
        process_primary_professions(name_basics_df, conn)
        process_known_for_titles(name_basics_df, conn)
    
    except Exception as e:
        logging.error("Erro ao processar os arquivos TSV: ", exc_info=True)
    
    finally:
        conn.close()
        logging.info("Conexão com o banco de dados encerrada.")

if __name__ == '__main__':
    main()
