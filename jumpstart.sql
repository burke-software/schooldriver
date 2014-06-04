-- To use:
-- git checkout sample_db
-- sqlite3 sample_db
-- .read jumpstart.sql

-- Pretty, if desired
-- .mode column
.headers on

-- Grade levels
INSERT INTO "sis_gradelevel" VALUES(12,"Senior");
INSERT INTO "sis_gradelevel" VALUES(11,"Junior");
INSERT INTO "sis_gradelevel" VALUES(10,"Sophomore");
INSERT INTO "sis_gradelevel" VALUES(9,"Freshman");

-- Class of 20x6
INSERT INTO "sis_classyear" VALUES(1,2011,"Class of 2011");
INSERT INTO "sis_classyear" VALUES(2,2012,"Class of 2012");
INSERT INTO "sis_classyear" VALUES(3,2013,"Class of 2013");
INSERT INTO "sis_classyear" VALUES(4,2014,"Class of 2014");
INSERT INTO "sis_classyear" VALUES(5,2015,"Class of 2015");
INSERT INTO "sis_classyear" VALUES(6,2016,"Class of 2016");
INSERT INTO "sis_classyear" VALUES(7,2017,"Class of 2017");
INSERT INTO "sis_classyear" VALUES(8,2018,"Class of 2018");
INSERT INTO "sis_classyear" VALUES(9,2019,"Class of 2019");
INSERT INTO "sis_classyear" VALUES(10,2020,"Class of 2020");

-- Cohorts
-- id | name    | long_name | primary
INSERT INTO "sis_cohort" VALUES(1,"Senior A","",1);
INSERT INTO "sis_cohort" VALUES(2,"Senior B","",1);
INSERT INTO "sis_cohort" VALUES(3,"Junior A","",1);
INSERT INTO "sis_cohort" VALUES(4,"Sophomore A","",1);
INSERT INTO "sis_cohort" VALUES(5,"Freshman A","",1);

-- Auth Users
-- id|password|last_login|is_superuser|username|first_name|last_name|email|is_staff|is_active|date_joined
INSERT INTO "auth_user" VALUES(4,"pbkdf2_sha256$12000$FckkHEJkcsKn$ENPYtfsPzcmfmo47euBq72WFCwIO2VtFnohn27UEDV0=","2014-06-13 17:04:00",0,"ssanders","Sidney","Sanders","ssanders@example.com",0,1,"2014-06-02 17:04:00");
INSERT INTO "auth_user" VALUES(5,"pbkdf2_sha256$12000$FckkHEJkcsKn$ENPYtfsPzcmfmo47euBq72WFCwIO2VtFnohn27UEDV0=","2014-06-13 17:04:00",0,"dgreen","Devon","Green","",0,1,"2014-06-02 17:05:00");
INSERT INTO "auth_user" VALUES(6,"pbkdf2_sha256$12000$FckkHEJkcsKn$ENPYtfsPzcmfmo47euBq72WFCwIO2VtFnohn27UEDV0=","2014-06-13 17:04:00",0,"clee","Cameron","Lee","clee@example.com",0,1,"2014-06-02 17:06:00");
INSERT INTO "auth_user" VALUES(7,"pbkdf2_sha256$12000$FckkHEJkcsKn$ENPYtfsPzcmfmo47euBq72WFCwIO2VtFnohn27UEDV0=","2014-06-13 17:04:00",0,"djenkins","Drew","Jenkins","djenkins@example.com",0,1,"2014-06-02 17:07:00");
INSERT INTO "auth_user" VALUES(8,"pbkdf2_sha256$12000$FckkHEJkcsKn$ENPYtfsPzcmfmo47euBq72WFCwIO2VtFnohn27UEDV0=","2014-06-13 17:04:00",0,"cjohnson","Chris","Johnson","cjohnson@example.com",0,1,"2014-06-02 17:08:00");
INSERT INTO "auth_user" VALUES(9,"pbkdf2_sha256$12000$FckkHEJkcsKn$ENPYtfsPzcmfmo47euBq72WFCwIO2VtFnohn27UEDV0=","2014-06-13 17:04:00",0,"asmith","Agent","Smith","asmith@example.com",1,1,"2014-06-02 17:09:00");
INSERT INTO "auth_user" VALUES(10,"pbkdf2_sha256$12000$FckkHEJkcsKn$ENPYtfsPzcmfmo47euBq72WFCwIO2VtFnohn27UEDV0=","2014-06-13 17:04:00",0,"ajones","Agent","Jones","ajones@example.com",1,1,"2014-06-02 17:10:00");
INSERT INTO "auth_user" VALUES(11,"pbkdf2_sha256$12000$FckkHEJkcsKn$ENPYtfsPzcmfmo47euBq72WFCwIO2VtFnohn27UEDV0=","2014-06-13 17:04:00",0,"abrown","Agent","Brown","abrown@example.com",1,1,"2014-06-02 17:11:00");
INSERT INTO "auth_user" VALUES(12,"pbkdf2_sha256$12000$FckkHEJkcsKn$ENPYtfsPzcmfmo47euBq72WFCwIO2VtFnohn27UEDV0=","2014-06-13 17:04:00",0,"apace","Agent","Pace","apace@example.com",1,1,"2014-06-02 17:12:00");
INSERT INTO "auth_user" VALUES(13,"pbkdf2_sha256$12000$FckkHEJkcsKn$ENPYtfsPzcmfmo47euBq72WFCwIO2VtFnohn27UEDV0=","2014-06-13 17:04:00",0,"aperry","Agent","Perry","aperry@example.com",1,1,"2014-06-02 17:13:00");

-- SIS Students
-- user_ptr_id | mname | grad_date | pic | alert | sex | bday | year_id | class_of_year_id | date_dismissed | reason_left_id | unique_id | ssn | parent_guardian | street | state | city | zip | parent_email | family_preferred_language_id | alt_email | notes | cache_cohort_id | individual_education_program | cached_gpa | gpa_recalculation_needed
-- 3|||||||||||||mr ppp||||||||||0||0
INSERT INTO "sis_student" VALUES(4,?,?,?,"","F",?,12,?,?,?,?,?,"Fozzie Bear","123 Main Street","PA","Smalltown",12345,"fbear@example.com",?,"ssanders@example.com","",1,0,?,0);
INSERT INTO "sis_student" VALUES(5,?,?,?,"","F",?,10,?,?,?,?,?,"Animal","234 Main Street","PA","Smalltown",12345,"animal@example.com",?,"dgreen@example.com","",4,0,?,0);
INSERT INTO "sis_student" VALUES(6,?,?,?,"","M",?,11,?,?,?,?,?,"Gonzo","456 Main Street","PA","Smalltown",12345,"gonzo@example.com",?,"clee@example.com","",3,0,?,0);
INSERT INTO "sis_student" VALUES(7,?,?,?,"","F",?,12,?,?,?,?,?,"Kermit the Frog","789 Main Street","PA","Smalltown",12345,"",?,"djenkins@example.com","",2,0,?,0);
INSERT INTO "sis_student" VALUES(8,?,?,?,"","M",?,9,?,?,?,?,?,"Miss Piggy","789 Main Street","PA","Smalltown",12345,"mpiggy@example.com",?,"cjohnson@example.com","",5,0,?,0);

-- Departments
-- id|name|order_rank
-- 1 |Math|
-- INSERT INTO "schedule_department" VALUES(1,"Math",?);
INSERT INTO "schedule_department" VALUES(2,"English",?);
INSERT INTO "schedule_department" VALUES(3,"Science",?);
INSERT INTO "schedule_department" VALUES(4,"Social Studies",?);
INSERT INTO "schedule_department" VALUES(5,"Language",?);
INSERT INTO "schedule_department" VALUES(6,"Theology",?);

-- Courses
-- id|is_active|fullname|shortname|homeroom|graded|description|credits|award_credits|department_id|level_id
-- 1 |1        |Math 101|Math 101 |0       |1     |           |6      |1            |1            |
-- INSERT INTO "schedule_course" VALUES(1,1,"Math 101","Math 101",0,1,?,6,1,1,?);
-- INSERT INTO "schedule_course" VALUES(2,1,"readin","readin",0,1,?,1,1,5,?);
INSERT INTO "schedule_course" VALUES(3,1,"Math 102","Math 102",0,1,"",1,1,1,9);
INSERT INTO "schedule_course" VALUES(4,1,"Math 201","Math 201",0,1,"Math for Sophomores",1,1,1,10);
INSERT INTO "schedule_course" VALUES(5,1,"Math 301","Math 301",0,1,"",1,1,1,11);
INSERT INTO "schedule_course" VALUES(6,1,"Math 401","Math 401",0,1,"",1,1,1,12);
INSERT INTO "schedule_course" VALUES(7,1,"Earth Science","Earth Science",0,1,"",1,1,3,?);
INSERT INTO "schedule_course" VALUES(8,1,"Life Science","Life Science",0,1,"",1,1,3,?);
INSERT INTO "schedule_course" VALUES(9,1,"Biology","Biology",0,1,"",1,1,3,?);
INSERT INTO "schedule_course" VALUES(10,1,"AP Biology","AP Bio",0,1,"",1,1,3,?);
INSERT INTO "schedule_course" VALUES(11,1,"Chemistry","Chemistry",0,1,"",1,1,3,?);
INSERT INTO "schedule_course" VALUES(12,1,"AP Chemistry","AP Chem",0,1,"",1,1,3,?);
INSERT INTO "schedule_course" VALUES(13,1,"Spanish 101","Spanish 101",0,1,"¡Este clase esta muy importante!",1,1,5,9);
INSERT INTO "schedule_course" VALUES(14,1,"French 101","French 101",0,1,"",1,1,5,9);
INSERT INTO "schedule_course" VALUES(15,1,"German 101","German 101",0,1,"",1,1,5,9);
INSERT INTO "schedule_course" VALUES(16,1,"Latin 101","Latin 101",0,1,"",1,1,5,?);
INSERT INTO "schedule_course" VALUES(17,1,"Spanish 102","Spanish 102",0,1,"",1,1,5,?);
INSERT INTO "schedule_course" VALUES(18,0,"Spanish 511","Spanish 511",0,1,"",8,1,5,?);
INSERT INTO "schedule_course" VALUES(19,1,"Homeroom A","Homeroom A",1,0,"",0,0,?,?);
INSERT INTO "schedule_course" VALUES(20,1,"Homeroom B","Homeroom B",1,0,"",0,0,?,?);
INSERT INTO "schedule_course" VALUES(21,1,"Homeroom C","Homeroom C",1,0,"",0,0,?,?);
INSERT INTO "schedule_course" VALUES(22,1,"Homeroom D","Homeroom D",1,0,"",0,0,?,?);
INSERT INTO "schedule_course" VALUES(23,0,"Homeroom X","Homeroom X",1,0,"",0,0,?,?);

-- Course sections
-- id|course_id|is_active|name        |last_grade_submission
-- 1 |1        |1        |Math Group A|
-- INSERT INTO "schedule_coursesection" VALUES(1,1,1,"Math Group A",?);
-- INSERT INTO "schedule_coursesection" VALUES(2,1,1,"Math Group B",?);
INSERT INTO "schedule_coursesection" VALUES(3,1,1,"Math Group C",?);
INSERT INTO "schedule_coursesection" VALUES(4,1,1,"Math Group D",?);
INSERT INTO "schedule_coursesection" VALUES(5,1,0,"Math Group X",?);
INSERT INTO "schedule_coursesection" VALUES(6,7,1,"Period 1A",?);
INSERT INTO "schedule_coursesection" VALUES(7,7,1,"Period 1B",?);
INSERT INTO "schedule_coursesection" VALUES(8,3,1,"Group A",?);
INSERT INTO "schedule_coursesection" VALUES(9,3,1,"Group B",?);
INSERT INTO "schedule_coursesection" VALUES(10,13,1,"Clase Uno",?);
INSERT INTO "schedule_coursesection" VALUES(11,13,1,"Clase Tres",?);
INSERT INTO "schedule_coursesection" VALUES(12,13,1,"Clase Siete",?);