import pandas as pd

DATA_FILE = "data/schedule_database.csv"

def import_excel(file):
    df = pd.read_excel(file)
    
    try:
        existing = pd.read_csv(DATA_FILE)
        df = pd.concat([existing, df])    
    except:
        pass
    
    df.to_csv(DATA_FILE, index = False)
    return {"message" : "Data imported", "rows" : len(df)}

    