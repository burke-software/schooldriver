-- This trigger updates SWORD when a sugarcrm contact is updated. Does not include email
delimiter //
drop trigger if exists trig_answers ;
CREATE TRIGGER trig_answers after insert on quexf_crny.formboxverifychar
for each row
IF NEW.val is NOT NULL THEN
begin
    set @test_instance_id = (
        SELECT `val` *1 from quexf_crny.formboxverifytext where quexf_crny.formboxverifytext.fid = NEW.fid
    );
    set @question_id = (
        SELECT DISTINCT boxgroupstype.varname from quexf_crny.boxgroupstype JOIN quexf_crny.boxes
            ON quexf_crny.boxgroupstype.bgid=quexf_crny.boxes.bgid 
            WHERE quexf_crny.boxes.bid = NEW.bid
    );
    set @answer_id = (
        SELECT DISTINCT boxes.value from quexf_crny.boxes JOIN quexf_crny.boxgroupstype
            ON quexf_crny.boxes.bgid = quexf_crny.boxgroupstype.bgid
            JOIN quexf_crny.formboxverifychar ON quexf_crny.boxes.bid=quexf_crny.formboxverifychar.bid
            WHERE quexf_crny.formboxverifychar.bid = NEW.bid and quexf_crny.formboxverifychar.fid = NEW.fid
    );
    set @points_earned = (
        SELECT crny.omr_answer.point_value from crny.omr_answer where crny.omr_answer.id =
            (SELECT boxes.value from quexf_crny.boxes JOIN quexf_crny.boxgroupstype
            ON quexf_crny.boxes.bgid = quexf_crny.boxgroupstype.bgid
            JOIN quexf_crny.formboxverifychar ON quexf_crny.boxes.bid=quexf_crny.formboxverifychar.bid
            WHERE quexf_crny.formboxverifychar.bid = NEW.bid and quexf_crny.formboxverifychar.fid = NEW.fid)
    );
    set @points_possible = (
        SELECT crny.omr_question.point_value from crny.omr_question
            where crny.omr_question.id = (SELECT DISTINCT boxgroupstype.varname from quexf_crny.boxgroupstype
            JOIN quexf_crny.boxes
            ON quexf_crny.boxgroupstype.bgid=quexf_crny.boxes.bgid
            JOIN quexf_crny.formboxverifychar
            ON quexf_crny.boxes.bid=quexf_crny.formboxverifychar.bid
            WHERE quexf_crny.formboxverifychar.bid = NEW.bid)
    );
    INSERT INTO crny.omr_answerinstance(test_instance_id,question_id,answer_id, points_earned, points_possible)
    values (@test_instance_id, @question_id, @answer_id, @points_earned, @points_possible);
end;
end if;
//

