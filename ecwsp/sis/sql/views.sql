-- Moodle views

create view sword.mdl_user as
select * from moodle.mdl_user;

create view sword.mdl_enrol as
select * from moodle.mdl_enrol;

create view sword.mdl_user_enrolments as
select * from moodle.mdl_user_enrolments;

create view sword.mdl_course as
select * from moodle.mdl_course;

create view sword.mdl_course_sections as
select * from moodle.mdl_course_sections;

create view sword.mdl_assignment as
select * from moodle.mdl_assignment;

create view sword.mdl_assignment_submissions as
select * from moodle.mdl_assignment_submissions;

create view sword.mdl_event as
select * from moodle.mdl_event;

create view sword.mdl_course_categories as
select * from moodle.mdl_course_categories;

create view sword.mdl_context as
select * from moodle.mdl_context;

create view sword.mdl_role_assignments as
select * from moodle.mdl_role_assignments;

create view sword.mdl_role as
select * from moodle.mdl_role;
