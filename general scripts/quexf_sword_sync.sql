-- This script should sync answers from QueXF to django-sis.omr
delimiter //
drop trigger if exists quexf_to_omr ;
CREATE TRIGGER quexf_to_omr after insert on quexf_crny.formboxverifytext
for each row
IF new.val is NOT NULL THEN
begin
 DECLARE current_bid BIGINT(20) unsigned;
 DECLARE no_more_bids INT DEFAULT 0;
 DECLARE bid_cursor CURSOR FOR select boxes.bid from boxes join formboxes on formboxes.bid = boxes.bid where fid = new.fid group by bgid;
 DECLARE CONTINUE HANDLER FOR NOT FOUND SET no_more_bids = 1;
 INSERT INTO d (a) values ('here12');
 set @form_id = new.fid;
 OPEN bid_cursor;
 FETCH bid_cursor INTO current_bid;
 -- for each box id in all box group ids.
 REPEAT
  INSERT INTO d (a) values ('here13');
  
  FETCH bid_cursor INTO current_bid;
  
  set @box_id = current_bid;
  
  set @test_instance_id = (
   SELECT DISTINCT `val` *1 from quexf_crny.formboxverifytext where quexf_crny.formboxverifytext.fid = @form_id
    and quexf_crny.formboxverifytext.bid = @box_id
  );
  
  set @question_id = (
   SELECT DISTINCT boxgroupstype.varname from quexf_crny.boxgroupstype JOIN quexf_crny.boxes
    ON quexf_crny.boxgroupstype.bgid=quexf_crny.boxes.bgid
    WHERE quexf_crny.boxes.bid = @box_id
  );
  
  -- quexf can come up with answers, but doesn't consider if 2 are filled out taking
  -- the more filled one. This takes the most filled answer but it must be at least
  -- 20% filled 
  set @lowest_filled = (
   select MIN(filled) from formboxes where fid = @form_id and bid in (
    SELECT quexf_crny.boxes.bid from quexf_crny.boxes WHERE quexf_crny.boxes.bgid = (
     SELECT quexf_crny.boxes.bgid from quexf_crny.boxes WHERE quexf_crny.boxes.bid = @box_id
    )
   )
  );
  
  set @answer_bid = (
   select bid from formboxes where fid = @form_id and filled = @lowest_filled and filled < 0.85 limit 1
  );
  
  INSERT INTO d(a,b,c)
   values (@lowest_filled, @answer_bid, '');
  
  if @answer_bid is not null then
   set @answer_id =(
    SELECT DISTINCT boxes.value from quexf_crny.boxes WHERE quexf_crny.boxes.bid = @answer_bid
   );
   
   set @points_earned = (
    SELECT sword_crny.omr_answer.point_value from sword_crny.omr_answer where sword_crny.omr_answer.id = @answer_id
   );
   
   set @omr_question_id = (
    SELECT DISTINCT boxgroupstype.varname from quexf_crny.boxgroupstype
     JOIN quexf_crny.boxes
     ON quexf_crny.boxgroupstype.bgid=quexf_crny.boxes.bgid
     JOIN quexf_crny.formboxverifychar
     ON quexf_crny.boxes.bid=quexf_crny.formboxverifychar.bid
     WHERE quexf_crny.formboxverifychar.bid = @box_id
   );
   
   set @points_possible = (
    SELECT sword_crny.omr_question.point_value from sword_crny.omr_question
     where sword_crny.omr_question.id = @omr_question_id
   );
   
   INSERT INTO sword_crny.omr_answerinstance(test_instance_id,question_id,answer_id, points_earned, points_possible)
   values (@test_instance_id, @question_id, @answer_id, @points_earned, @points_possible)
   on duplicate key
   update answer_id = @answer_id, points_earned = @points_earned;
  end if;
  
  UNTIL no_more_bids = 1
 END REPEAT;
 close bid_cursor;
end;
end if;
//
delimiter ;