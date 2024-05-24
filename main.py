from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import Table, select, and_
import pandas as pd
from io import BytesIO
from database import engine, metadata
import logging

app = FastAPI()

# Configurar el directorio de archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/")
async def read_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/exportar")
async def exportar_datos(fecha_inicio: str = Form(...), fecha_fin: str = Form(...)):
    if not fecha_inicio or not fecha_fin:
        raise HTTPException(status_code=400, detail="Por favor, proporciona las fechas 'fecha_inicio' y 'fecha_fin'")

    try:
        # Las fechas ya están en formato yyyy-mm-dd, no es necesario convertirlas

        # Conectar al motor
        connection = engine.connect()
        table = Table('temperaturas', metadata, autoload_with=engine)

        # Consultar datos entre las fechas especificadas
        query = select(
            table.c.id_temp, table.c.temp_grados, table.c.temp_lugar, table.c.fecha
        ).where(
            and_(table.c.fecha >= fecha_inicio, table.c.fecha <= fecha_fin)
        )
        result = connection.execute(query).fetchall()

    except Exception as e:
        logger.error(f"Error al ejecutar la consulta: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        connection.close()

    if not result:
        raise HTTPException(status_code=404, detail="No se encontraron datos en el rango de fechas especificado")

    # Crear un DataFrame de pandas con los resultados
    df = pd.DataFrame(result, columns=['id_temp', 'temp_grados', 'temp_lugar', 'fecha'])

    # Convertir el formato de la fecha
    if 'fecha' in df.columns:
        df['fecha'] = pd.to_datetime(df['fecha']).dt.strftime('%d-%m-%Y')

    # Exportar a un archivo Excel en memoria
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='Temperaturas')
    writer.close()
    output.seek(0)

    # Enviar el archivo Excel al cliente
    return StreamingResponse(output, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                             headers={"Content-Disposition": "attachment;filename=temperaturas.xlsx"})

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
