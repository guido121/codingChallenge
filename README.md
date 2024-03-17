# Globant Coding Challenge

## Introduction
The present proyect is related to the implementation of one Rest API and two Endpoints where the first loads data and the two last get query results in json format.

  ### 1. REST API AND ENDPOINTS:
  
  #### 1.1. /api/upload_csvs (POST): 
  This api loads the information of the following csv files into a azure sql database. The files and its structure are the following:

  - **hired_employees.csv:** this file must be attached to the request with **hired_employees_file** key to the recognized by the API. 
  
    Column name | Type | Description 
    --- | ---  | --
    id | INTEGER | Id of the employee
    name | STRING | Name and surname of the employee
    datetime | STRING | Hire datime in ISO format
    department_id | INTEGER | Id of the department which the employee was hired for
    job_id | INTEGER | Id of the job which the employee was hired for

    **Sample data:**

      4535,Marcelo Gonzalez,2021-07-27T16:02:08Z,1,2

      4572,Lidia Mendez,2021-07-27T19:04:09Z,1,2

  - **departments.csv:** this file must be attached to the request with **"department_file"** key to the recognized by the API. 

      Column name | Type | Description 
      --- | ---  | --
      id | INTEGER | Id of the department
      department | STRING | Name of the department

      Sample data:
      
      1, Supply Chain

      2, Maintenance

      3, Staff
        
  - **jobs.csv:** this file must be attached to the request with **"jobs_file"** key to the recognized by the API. 

      Column name | Type | Description 
      --- | ---  | --
      id | INTEGER | Id of the job
      job | STRING | Name of the job
      
      Sample data:

      1, Recruiter

      2, Manager

      3, Analyst

  #### 1.2. /api/employees_hired_quarter/{int:year} (GET):
  This endpoint gets the number of employees hired for each job and department in 2021 divided by quarter. The table is ordered alphabetically by department and job.

  - Params: The param {year} gets the information time scope.

  - Headers: No additional header is required

  - Sample returned data:

```json

  [ { 
      "department": "Accounting",
      "job": "Actuary",
      "Q1": 0,
      "Q2": 1,
      "Q3": 0,
      "Q4": 0
    }, 
    { 
      "department": "Accounting",
      "job":
      "Budget/Accounting Analyst III",
      "Q1": 0,
      "Q2": 1,
      "Q3": 0,
      "Q4": 0
    }
  ]
```

#### 1.3. /api/employees_by_department/{int:year} (GET):
  This endpoint gets the number of employees hired for each job and department in 2021 divided by quarter. The table is ordered alphabetically by department and job.

  - Params: The param {year} gets the information time scope.

  - Headers: No additional header is required

  - Sample returned data:

```json

  [
    {
      "id": 8,
      "department": "Support",
      "hired": 136
    },
    {
      "id": 6,
      "department": "Human Resources",
      "hired": 127
    }
  ]
```
## Requirements and considerations
1. Deploy and Azure SQL Database and Server using an Azure Subscription. Make sure your IP address is added to the SQL Server.
2. Based on the deployment, configure the config.ini file.
3. In the files folder you can find the 3 CSV's data to populate the empty database. This can be achieved using the Rest API.
4. The Rest API creates automatically the tables for the first time.
5. Every time you send a request to the Rest API, it rewrite the entire table with the new data.
6. Make sure to install the python dependencies running pip install -r requests.txt


## Automated Testing
The testing is included in the test_todo_api.py file. You can run the tests by executing: pytest command to check the results.

## Libraries 
- Flask==2.0.3
- iniconfig==1.1.1
- packaging==21.3
- pandas==1.1.5
- py==1.11.0
- pyodbc==4.0.39
- pyparsing==3.1.2
- pytest==7.0.1
- SQLAlchemy==1.4.52




