-- This trigger updates SWORD when a test is scanned into quexf. Also hacks on que because it fails
delimiter //
drop trigger if exists trig_answers ;
CREATE TRIGGER trig_answers after insert on quexf_crb.formboxverifychar
for each row
IF NEW.val is NOT NULL THEN
begin
    DECLARE current_bid BIGINT(20) unsigned;
    DECLARE no_more_bids INT DEFAULT 0;
    DECLARE bid_cursor CURSOR FOR SELECT quexf_crb.boxes.bid from quexf_crb.boxes WHERE quexf_crb.boxes.bgid =
        (SELECT quexf_crb.boxes.bgid from quexf_crb.boxes WHERE quexf_crb.boxes.bid = NEW.bid);
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET no_more_bids = 1;
    set @test_instance_id = (
        SELECT DISTINCT `val` *1 from quexf_crb.formboxverifytext where quexf_crb.formboxverifytext.fid = NEW.fid
    );
    set @question_id = (
        SELECT DISTINCT boxgroupstype.varname from quexf_crb.boxgroupstype JOIN quexf_crb.boxes
            ON quexf_crb.boxgroupstype.bgid=quexf_crb.boxes.bgid
            WHERE quexf_crb.boxes.bid = NEW.bid
    );
    set @answer_fill = 1.0;
    OPEN bid_cursor;
    FETCH bid_cursor INTO current_bid;
    set @answer_bid := current_bid;
    REPEAT
        set @current_fill = (SELECT quexf_crb.formboxes.filled from quexf_crb.formboxes
        where quexf_crb.formboxes.bid = current_bid and quexf_crb.formboxes.fid = NEW.fid);
        IF (@current_fill*1.0) < (@answer_fill*1.0) THEN set @answer_fill := @current_fill, @answer_bid :=current_bid;
        END IF;
        FETCH bid_cursor INTO current_bid;
        UNTIL no_more_bids = 1
    END REPEAT;
    close bid_cursor;
    set @answer_id =(
        SELECT DISTINCT boxes.value from quexf_crb.boxes WHERE quexf_crb.boxes.bid = @answer_bid
    );
    set @points_earned = (
        SELECT sword_lourdesacademyhs.omr_answer.point_value from sword_lourdesacademyhs.omr_answer where sword_lourdesacademyhs.omr_answer.id = @answer_id
    );
set @points_possible = (
        SELECT sword_lourdesacademyhs.omr_question.point_value from sword_lourdesacademyhs.omr_question
            where sword_lourdesacademyhs.omr_question.id = (SELECT DISTINCT boxgroupstype.varname from quexf_crb.boxgroupstype
            JOIN quexf_crb.boxes
            ON quexf_crb.boxgroupstype.bgid=quexf_crb.boxes.bgid
            JOIN quexf_crb.formboxverifychar
            ON quexf_crb.boxes.bid=quexf_crb.formboxverifychar.bid
            WHERE quexf_crb.formboxverifychar.bid = NEW.bid)
    );
    INSERT INTO sword_lourdesacademyhs.omr_answerinstance(test_instance_id,question_id,answer_id, points_earned, points_possible)
    values (@test_instance_id, @question_id, @answer_id, @points_earned, @points_possible)
    on duplicate key
    update answer_id = @answer_id, points_earned = @points_earned;

    update sword_lourdesacademyhs.omr_testinstance SET sword_lourdesacademyhs.omr_testinstance.results_recieved = True
    WHERE sword_lourdesacademyhs.omr_testinstance.id = @test_instance_id;
end;
end if;
//