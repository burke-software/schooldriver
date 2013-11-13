-- This script should sync answers from QueXF to django-sis.omr
delimiter //
drop trigger if exists quexf_to_omr ;
CREATE TRIGGER quexf_to_omr after insert on quexf_crny.formboxverifytext
-- for each newly inserted row
for each row
-- new.val is the OMR TestInstance.id
IF new.val is NOT NULL THEN
begin
 DECLARE current_bid BIGINT(20) unsigned;
 DECLARE no_more_bids INT DEFAULT 0;
 DECLARE bid_cursor CURSOR FOR select boxes.bid from boxes join formboxes on formboxes.bid = boxes.bid where fid = new.fid group by bgid;
 DECLARE CONTINUE HANDLER FOR NOT FOUND SET no_more_bids = 1;
 set @form_id = new.fid;
 -- formboxverifytext.val is a longtext;
 -- convert it to an int to match OMR's TestInstance.id
 set @test_instance_id = (
  SELECT new.val * 1
 );
 OPEN bid_cursor;
 FETCH bid_cursor INTO current_bid;
 -- for each box id in all box group ids.
 REPEAT
  set @box_id = current_bid;
  
  -- OMR Question.id for this box group as stored in boxgroupstype.varname
  set @question_id = (
   SELECT DISTINCT boxgroupstype.varname from quexf_crny.boxgroupstype JOIN quexf_crny.boxes
    ON quexf_crny.boxgroupstype.bgid=quexf_crny.boxes.bgid
    WHERE quexf_crny.boxes.bid = @box_id
  );

  -- QueXF box group id
  set @box_group_id = (
   SELECT quexf_crny.boxes.bgid from quexf_crny.boxes WHERE quexf_crny.boxes.bid = @box_id
  );
  
  -- quexf can come up with answers, but doesn't consider if 2 are filled out taking
  -- the more filled one. This takes the most filled answer but it must be more than
  -- 15% filled 
  set @answer_bid = (
   SELECT bid FROM formboxes WHERE fid = @form_id AND bid in (
    SELECT quexf_crny.boxes.bid FROM quexf_crny.boxes WHERE quexf_crny.boxes.bgid = @box_group_id
   ) AND filled < 0.85 ORDER BY filled ASC LIMIT 1 
  );
  
  if @answer_bid is not null then
   -- OMR Answer.id as stored in boxes.value for the most filled formbox in our box group
   set @answer_id =(
    SELECT DISTINCT boxes.value from quexf_crny.boxes WHERE quexf_crny.boxes.bid = @answer_bid
   );
   
   -- Pure OMR; get the point_value of the chosen answer
   set @points_earned = (
    SELECT sword_crny.omr_answer.point_value from sword_crny.omr_answer where sword_crny.omr_answer.id = @answer_id
   );
   
   -- Pure OMR; get the point_value of the whole question
   set @points_possible = (
    SELECT sword_crny.omr_question.point_value from sword_crny.omr_question
     where sword_crny.omr_question.id = @question_id
   );
   
   -- Do the damage unto OMR
   INSERT INTO sword_crny.omr_answerinstance(test_instance_id,question_id,answer_id, points_earned, points_possible)
   values (@test_instance_id, @question_id, @answer_id, @points_earned, @points_possible)
   on duplicate key
   update answer_id = @answer_id, points_earned = @points_earned;
  
  FETCH bid_cursor INTO current_bid;
  UNTIL no_more_bids = 1
 END REPEAT;
 close bid_cursor;
 
end;
end if;
//
delimiter ;
