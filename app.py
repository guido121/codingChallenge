from flask import Flask, request
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, text
import pandas as pd
from pathlib import Path
import os, json
import urllib
import pyodbc

from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)

ALLOWED_EXTENTIONS = {'csv'}

BASE_DIR = os.getcwd()
if not os.path.exists(os.path.join(BASE_DIR,  "tmp")):
    os.makedirs(os.path.join(BASE_DIR,  "tmp"))

@app.route('/')
def root():
  return "Welcome to the Globant Challenge"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENTIONS

def create_engine_connection_string():
  print(os.getenv('DB_DRIVER'))
  #Create a SQLAlchemy Engine
  #params = urllib.parse.quote_plus('Driver={ODBC Driver 18 for SQL Server};Server=tcp:srv70903775.database.windows.net,1433;Database=db70903775;Uid=adminchallenge;Pwd=passLu15;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
  connectionstring = "Driver={driver};Server=tcp:{server},{port};Database={database};Uid={username};Pwd={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"\
  .format(
          driver = "{"+ os.getenv('DB_DRIVER') +"}",
          server = os.getenv('DB_SERVER'),
          port = os.getenv('DB_PORT'),
          database = os.getenv('DB_DATABASE'),
          username = os.getenv('DB_USERNAME'),
          password = os.getenv('DB_PASSWORD')
         )
  params = urllib.parse.quote_plus(connectionstring)

  conn_str = 'mssql+pyodbc:///?odbc_connect={}'.format(params)
  return create_engine(conn_str,echo=True)

def run_sql_query(engine,query,param):
  with engine.connect() as connection:
    result = connection.execute(text(query),param)
    query_result = result.fetchall()
  
  # Convert query result to JSON
  return json.dumps([dict(row) for row in query_result])

@app.route('/api/upload_csvs', methods=['POST'])
def upload_departments():

  #Validating the file is attached
  department_key = 'department_file'
  hired_employees_key = 'hired_employees_file'
  jobs_key = 'jobs_file'

  if department_key not in request.files or \
    hired_employees_key not in request.files or \
    jobs_key not in request.files:
    return 'Please, make sure the department, hired_employees_file and jobs files are attached'
  
  department_file = request.files[department_key]
  hired_employees_file = request.files[hired_employees_key]
  jobs_file = request.files[jobs_key]

  if department_file.filename == '' or \
  hired_employees_file.filename == '' or \
  jobs_file.filename == '':
    return 'Please select the department, hired_employees_file and jobs files'
  
  #Saving the file in a temporary directory
  department_path = os.path.join(BASE_DIR, 'tmp', department_file.filename)
  hired_employees_path = os.path.join(BASE_DIR, 'tmp', hired_employees_file.filename)
  jobs_path = os.path.join(BASE_DIR, 'tmp', jobs_file.filename)

  department_file.save(department_path)
  hired_employees_file.save(hired_employees_path)
  jobs_file.save(jobs_path)
  
  #Reading the file with pandas
  department_df = pd.read_csv(department_path, sep=',',header=None, names=['id','department'],
                 encoding = "ISO-8859-1",dtype={'id': 'int','department': 'str'},engine='python')
  
  jobs_df = pd.read_csv(jobs_path, sep=',',header=None, names=['id','job'],
                 encoding = "ISO-8859-1",dtype={'id': 'int','job': 'str'},engine='python')
  
  hired_employees_df = pd.read_csv(hired_employees_path, sep=',',header=None, names=['id','name','datetime','department_id','job_id'],
                 encoding = "ISO-8859-1",dtype={'id':'int','name':'str','datetime':'str','department_id':'str','job_id':'str'},engine='python').head(1000)
  
  #Replace Empty values with Nulls 
  hired_employees_df['department_id'] = hired_employees_df['department_id'].fillna(0).astype(int)
  hired_employees_df['job_id'] = hired_employees_df['job_id'].fillna(0).astype(int)


  #Create a SQLAlchemy Engine
  engine = create_engine_connection_string()


  # Create a metadata object and reflect the tables from the database
  metadata = MetaData()
  metadata.reflect(bind=engine)


  if 'departments' not in metadata.tables:
    departments_table = Table('departments', metadata,
                   Column('id', Integer, primary_key=True),
                   Column('department', String)
                   )
  
  if 'jobs' not in metadata.tables:
    jobs_table = Table('jobs', metadata,
                   Column('id', Integer, primary_key=True),
                   Column('job', String)
                   )
    
  if 'employees' not in metadata.tables:
    employees_table = Table('employees', metadata,
                   Column('id', Integer, primary_key=True),
                   Column('name', String),
                   Column('datetime', String),
                   Column('department', Integer),
                   Column('job_id', Integer)
                  )

  # Insert the DataFrame into the Azure SQL database
  department_df.to_sql(name='departments', con=engine, if_exists='replace', index=False,chunksize=50)
  jobs_df.to_sql(name='jobs', con=engine, if_exists='replace', index=False,chunksize=50)
  hired_employees_df.to_sql(name='employees', con=engine, if_exists='replace', index=False,chunksize=50)

  # Create the table in the database
  metadata.create_all(engine)  

  return {'mensaje': 'Se procesó correctamente', 'status': '200'}, 200
  #if file and allowed_file(file.filename):  
    #filename = secure_filename(file.filename)
    #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    #return redirect(url_for('download_file', name=filename))

@app.route('/api/employees_hired_quarter', defaults={'year': 2021})
@app.route('/api/employees_hired_quarter/<int:year>')
def get_employees_hired_per_quarter(year):
 
  engine = create_engine_connection_string()

  query = """
    SELECT 
    d.department,
    j.job,
    SUM(CASE WHEN MONTH(datetime) IN (1,2,3) THEN 1 ELSE 0 END)  AS Q1,
    SUM(CASE WHEN MONTH(datetime) IN (4,5,6) THEN 1 ELSE 0 END)  AS Q2,
    SUM(CASE WHEN MONTH(datetime) IN (7,8,9) THEN 1 ELSE 0 END)  AS Q3,
    SUM(CASE WHEN MONTH(datetime) IN (10,11,12) THEN 1 ELSE 0 END)  AS Q4
    FROM employees e 
    INNER JOIN jobs j
    ON e.job_id = j.id
    INNER JOIN departments d
    ON e.department_id = d.id
    WHERE YEAR(e.datetime) = :year
    GROUP BY d.department,j.job
    ORDER BY d.department, j.job ASC
  """

  json_result = run_sql_query(engine,query,{"year": year})

  return json_result,200
@app.route('/api/employees_by_department',defaults={'mean_year_ref': 2021})
@app.route('/api/employees_by_department/<int:mean_year_ref>')
def employees_by_department(mean_year_ref):
 
  engine = create_engine_connection_string()

  query = """
  DECLARE @mean_2021 INT 
SELECT 
@mean_2021 = AVG(x.cant)
FROM (
	SELECT
	department_id,
	COUNT(1) AS cant
	FROM employees
	WHERE YEAR(datetime) = :mean_year_ref
	AND department_id <> 0
	GROUP BY department_id
) x
SELECT 
  d.id as id,
  d.department as department,
  COUNT(1) as hired
  FROM employees e
  INNER JOIN departments d
  ON e.department_id = d.id
  GROUP BY d.id, d.department
  HAVING COUNT(1) > @mean_2021
  ORDER BY COUNT(1) DESC
  """

  json_result = run_sql_query(engine,query,{'mean_year_ref' : mean_year_ref})

  return json_result,200


if __name__ == '__main__':
  app.run(debug=True)




