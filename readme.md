# Submission for GovTech's 2025 Product Operations Tooling Internship

## Check out the docs and test the site live at: <a href="https://sleepy-woodpecker.xyz/docs">https://sleepy-woodpecker.xyz/docs</a>

### Setup instructions (local)

1. using `.env.sample`, fill in the environment variables
   - you can get a free postgres instance <a href="https://neon.tech/">here</a>
2. create a virtual environment using `python -m venv <env_folder_name>`
3. activate the virtual environment
   - MacOs / Unix: `source <env_folder_name>/bin/activate`
   - Windows: `<env_folder_name>\Scripts\activate.bat`
4. install dependencies using `pip install -r requirements.txt`
5. go into the src folder using `cd src`
6. start the server using `uvicorn main:app --host 0.0.0.0 --port 3003`

### Setup instructions (Using Docker)

1. using `.env.sample`, fill in the environment variables
   - you can get a free postgres instance <a href="https://neon.tech/">here</a>
2. ensure that docker is open on your device
3. run `docker compose up --build`

### Explanation of decisions

1. Python makes the most sense to me, because it has great support for data analysis and processing with libraries like pandas -- something which may be required in a future update to this web service
2. FastAPI as my backend service because it supports input validation and has auto-generated documetation for its endpoints
3. Used an ORM instead of raw SQL queries because
   - Gives me a single source of truth for database tables
   - I am a huge fan of typing support
   - Based on what I have read online, I believe the biggest drawback of ORMs is that they cannot handle complex queries well. If performance really becomes an issue in the future, I would then convert the queries to raw SQL. I don't think there is a need to optimize for that yet
4. Choice of SQLModel as the ORM
   - Native support for FastAPI type validation, so I dont have to maintian 2 copies of types (which seems to be the suggested approach for using SQLAlchemy and FastAPI)
   - If there is a need to add in more complex queries, it helps that SQLModel is built on top of SQLAlchemy. This enables me to tap on SQLAlchemy functionalities if need be
5. Store end_date instead of start_date in the course_record table to:
   - reduce data redundancy: you can always find start_date, given an end_date, so there is no need to add another column
   - searches are currently made by end_date, so storing end_date better supports the queries that I will make
   - end_date is known once the course record is made
6. Further normalize the table to store raw grades only
   - enables greater flexibility for grade to GPA range in the future to support curving (I know too well)

### In creating this backend service, here are the assumptions I have made:

1. Semester start and end times:
   - Sem 1: Aug 1 to Nov 1
   - Sem 2: Jan 1 to April 1
2. Each semester, the single course that the students take are the same. Changing their teacher only changes the teacher they are taking the class from.
3. Each student only receives their GPA for that semester at the end of the semester
4. Raw scores can only fall in between 0 and 100

### DB Diagram

![DB-Diagram For School Management](assets/db-diagram.png?)
