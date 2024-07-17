from sqlalchemy import create_engine, MetaData

# Configura tu conexión a la base de datos MySQL
db_config = {
    'username': 'infra',
    'password': 'pgwrc9q34q',
    'host': '192.168.200.108',
    'database': 'infra'
}

# Crear la URL de conexión
db_url = f"mysql+pymysql://{db_config['username']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"

# Crear un motor SQLAlchemy
engine = create_engine(db_url)

# Crear los metadatos
metadata = MetaData()
metadata.reflect(bind=engine)
