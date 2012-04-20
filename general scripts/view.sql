create view work_study_student as
select `work_study_studentworker`.`student_ptr_id` AS `student_ptr_id`,`work_study_studentworker`.`day` AS `day`,`work_study_studentworker`.`fax` AS `fax`,`work_study_studentworker`.`work_permit_no` AS `work_permit_no`,`work_study_studentworker`.`placement_id` AS `placement_id`,`work_study_studentworker`.`school_pay_rate` AS `school_pay_rate`,`work_study_studentworker`.`student_pay_rate` AS `student_pay_rate`,`work_study_studentworker`.`primary_contact_id` AS `primary_contact_id`,`work_study_studentworker`.`personality_Type_id` AS `personality_Type_id`,`sis_student`.`mdluser_ptr_id` AS `mdluser_ptr_id`,`sis_student`.`mname` AS `mname`,`sis_student`.`sex` AS `sex`,`sis_student`.`bday` AS `bday`,`sis_student`.`year` AS `year`,`sis_student`.`pic` AS `pic`,`sis_student`.`unique_id` AS `unique_id`,`sis_student`.`ssn` AS `ssn`,`sis_student`.`parent_guardian` AS `parent_guardian`,`sis_student`.`street` AS `street`,`sis_student`.`state` AS `state`,`sis_student`.`zip` AS `zip`,`sis_student`.`parent_email` AS `parent_email`,`sis_student`.`alt_email` AS `alt_email`,`sis_student`.`notes` AS `notes`,`sis_student`.`reason_left` AS `reason_left`,`sis_mdluser`.`id` AS `id`,`sis_mdluser`.`deleted` AS `deleted`,`sis_mdluser`.`username` AS `username`,`sis_mdluser`.`fname` AS `fname`,`sis_mdluser`.`lname` AS `lname`,`sis_mdluser`.`email` AS `email`,`sis_mdluser`.`city` AS `city` from ((`work_study_studentworker` left join `sis_student` on((`sis_student`.`mdluser_ptr_id` = `work_study_studentworker`.`student_ptr_id`))) left join `sis_mdluser` on((`sis_mdluser`.`id` = `sis_student`.`mdluser_ptr_id`))) where (`sis_mdluser`.`deleted` = 0) ;


create view moodle_users as 
select sis_mdluser.id, username, "!" as password, fname, lname, email, city, street, "USA" as country, number
from  sis_mdluser
left join sis_student on sis_student.mdluser_ptr_id = sis_mdluser.id
left join sis_studentnumber on sis_studentnumber.student_id = sis_mdluser.id
where sis_mdluser.deleted = 0
group by sis_mdluser.id;

