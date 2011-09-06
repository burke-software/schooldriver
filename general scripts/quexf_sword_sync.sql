-- This trigger updates SWORD when a sugarcrm contact is updated. Does not include email
delimiter //
drop trigger trig_answers if exists;
CREATE TRIGGER trig_answers after insert on quexf_crny.formboxverifychar
for each row
begin
    set @test_instance_id = (
        SELECT `val` *1 from quexf_crny.formboxverifytext WHERE vid=NEW.vid and bid = NEW.bid and fid=NEW.fid
    );
    set @question_id = (
        SELECT boxgroupstype.varname from quexf_crny.boxgroupstype JOIN quexf_crny.boxes
            ON quexf_crny.boxgroupstype.bgid=quexf_crny.boxes.bgid
            WHERE bid = NEW.bid
    );
    set @answer_id = (
        SELECT boxes.value from quexf_crny.boxes JOIN boxgroupstype ON boxes.bgid = boxgroupstype.bgid
            JOIN formboxverifychar ON boxes.bid=formboxverifychar.bid
            WHERE formboxverifychar.bid = NEW.bid and quexf_crny.formboxverifychar.val is NOT NULL
    );
    set @points_earned = (
        SELECT crny.omr_answer.point_value from crny.omr_answer where crny.omr_answer.id =
            (SELECT boxes.value from quexf_crny.boxes JOIN boxgroupstype ON boxes.bgid = boxgroupstype.bgid
            JOIN formboxverifychar ON boxes.bid=formboxverifychar.bid
            WHERE formboxverifychar.bid = NEW.bid and quexf_crny.formboxverifychar.val is NOT NULL)
    );
    set @points_possible = (
        SELECT crny.omr_question.point_value from crny.omr_question
        where crny.omr_question.id = (SELECT boxgroupstype.varname from quexf_crny.boxgroupstype JOIN quexf_crny.boxes
            ON quexf_crny.boxgroupstype.bgid=quexf_crny.boxes.bgid
            WHERE bid = NEW.bid)
    );
    INSERT INTO crny.omr_answerinstance(test_instance_id,question_id,answer_id, points_earned, points_possible)
    values (@test_instance_id, @question_id, @answer_id, @points_earned, @points_possible);
end;
//
