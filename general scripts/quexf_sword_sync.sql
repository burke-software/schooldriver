-- This trigger updates SWORD when a test is scanned into quexf. Also hacks on que because it fails
delimiter //
drop trigger if exists trig_answers ;
CREATE TRIGGER trig_answers after insert on quexf_crny.formboxverifychar
for each row
IF NEW.val is NOT NULL THEN
begin
    DECLARE current_bid BIGINT(20) unsigned;
    DECLARE no_more_bids INT DEFAULT 0;
    DECLARE bid_cursor CURSOR FOR SELECT quexf_crny.boxes.bid from quexf_crny.boxes WHERE quexf_crny.boxes.bgid =
        (SELECT quexf_crny.boxes.bgid from quexf_crny.boxes WHERE quexf_crny.boxes.bid = NEW.bid);
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET no_more_bids = 1;
    set @test_instance_id = (
        SELECT `val` *1 from quexf_crny.formboxverifytext where quexf_crny.formboxverifytext.fid = NEW.fid
    );
    set @question_id = (
        SELECT DISTINCT boxgroupstype.varname from quexf_crny.boxgroupstype JOIN quexf_crny.boxes
            ON quexf_crny.boxgroupstype.bgid=quexf_crny.boxes.bgid
            WHERE quexf_crny.boxes.bid = NEW.bid
    );
    set @answer_fill = 1.0;
    OPEN bid_cursor;
    FETCH bid_cursor INTO current_bid;
    set @answer_bid := current_bid;
    REPEAT
        set @current_fill = (SELECT quexf_crny.formboxes.filled from quexf_crny.formboxes
        where quexf_crny.formboxes.bid = current_bid and quexf_crny.formboxes.fid = NEW.fid);
        IF (@current_fill*1.0) < (@answer_fill*1.0) THEN set @answer_fill := @current_fill, @answer_bid :=current_bid;
        END IF;
        FETCH bid_cursor INTO current_bid;
        UNTIL no_more_bids = 1
    END REPEAT;
    close bid_cursor;
    set @answer_id =(
        SELECT DISTINCT boxes.value from quexf_crny.boxes WHERE quexf_crny.boxes.bid = @answer_bid
    );
    set @points_earned = (
        SELECT crny.omr_answer.point_value from crny.omr_answer where crny.omr_answer.id = @answer_id
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
    values (@test_instance_id, @question_id, @answer_id, @points_earned, @points_possible)
    on duplicate key
    update answer_id = @answer_id, points_earned = @points_earned;

    update crny.omr_testinstance SET crny.omr_testinstance.results_recieved = True
    WHERE crny.omr_testinstance.id = @test_instance_id;
end;
end if;
//