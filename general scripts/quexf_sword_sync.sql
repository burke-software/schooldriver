-- This trigger updates SWORD when a sugarcrm contact is updated. Does not include email
delimiter //
CREATE TRIGGER answers after insert on quexf.formboxverifychar
for each row
begin
    INSERT INTO sword.omr_answerinstance(test_instance_id,question_id,answer_id, points_earned, points_possible)
    values
    (
        --test_instance
        (SELECT val*1 from quexf.formboxverifytext WHERE vid=NEW.vid and bid = NEW.bid and fid=NEW.fid),
        --question_id
        (SELECT boxgroupstype.varname from quexf.boxgroupstype JOIN quexf.boxes
            ON quexf.boxgroupstype.bgid=quexf.boxes.bgid
            WHERE bid = NEW.bid),
        --answer_id
        (SELECT boxes.value from quexf.boxes JOIN boxgroupstype ON boxes.bgid = boxgroupstype.bgid
            JOIN formboxverifychar ON boxes.bid=formboxverifychar.bid
            WHERE formboxverifychar.bid = NEW.bid and quexf.formboxverifychar.val is NOT NULL),
        --points earned
        (SELECT sword.omr_answer.point_value from sword.omr_answer where sword.omr_answer.id =
            (SELECT boxes.value from quexf.boxes JOIN boxgroupstype ON boxes.bgid = boxgroupstype.bgid
            JOIN formboxverifychar ON boxes.bid=formboxverifychar.bid
            WHERE formboxverifychar.bid = NEW.bid and quexf.formboxverifychar.val is NOT NULL)),
        --points possible:
        (SELECT sword.omr_question.point_value from sword.omr_question
        where sword.omr_question.id = (SELECT boxgroupstype.varname from quexf.boxgroupstype JOIN quexf.boxes
            ON quexf.boxgroupstype.bgid=quexf.boxes.bgid
            WHERE bid = NEW.bid))
    );
end;
//