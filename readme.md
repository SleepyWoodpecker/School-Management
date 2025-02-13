# Submission for GovTech's 2025 Product Operations Tooling Internship

## Explanation of decisions

1. Python makes the most sense to me, because it has great support for data analysis and processing with libraries like pandas -- something which may be required in a future update to this web service
2. FastAPI as my backend service because it supports input validation and has auto-generated documetation for its endpoints

## In creating this backend service, here are the assumptions I have made:

1. Semester start and end times:
   - Sem 1: Aug 1 to Nov 1
   - Sem 2: Jan 1 to April 1
2. Each semester, the single course that the students take are the same. Changing their teacher only changes the teacher they are taking the class from.

### DB Diagram

![DB-Diagram For School Management](assets/db-diagram.png)
