---------------------------- SUGARCRM ----------------------------------------------------

-- This trigger updates SWORD when a sugarcrm contact is updated. Does not include email
delimiter //
drop trigger if exists sugar_depaul.sync_contact_to_sword;//
create trigger sugar_depaul.sync_contact_to_sword after update on sugar_depaul.contacts
for each row
begin
 if new.deleted=0 then
  insert into sword_depaul.work_study_contact (guid, fname, lname, phone, phone_cell)
  values (new.id, new.first_name, new.last_name, new.phone_work, new.phone_mobile)
  on duplicate key update
  fname=new.first_name, lname=new.last_name, phone=new.phone_work, phone_cell=new.phone_mobile;
 else
  delete from sword_depaul.work_study_contact
  where guid=new.id;
 end if;
end;
//
delimiter ;

-- This trigger updates SWORD when a sugarcrm contact is added. Does not include email
delimiter //
drop trigger if exists sugar_depaul.sync_contact_to_sword_insert;//
create trigger sugar_depaul.sync_contact_to_sword_insert after insert on sugar_depaul.contacts
for each row
begin
 insert into sword_depaul.work_study_contact (guid, fname, lname, phone, phone_cell)  
 (
  select contacts.id, first_name, last_name, phone_work, phone_mobile from sugar_depaul.contacts 
  left join sugar_depaul.contacts_cstm on contacts_cstm.id_c = contacts.id
  where supervisor_c=1 and contacts.id=new.id
 );
end;
//
delimiter ;

-- This trigger updates SWORD contact's email field when a sugarcrm contact email is changed. 
delimiter //
drop trigger if exists sugar_depaul.sync_contact_to_sword_email;//
create trigger sugar_depaul.sync_contact_to_sword_email after insert on sugar_depaul.email_addr_bean_rel
for each row
begin
 update sword_depaul.work_study_contact 
 set email =
 (
  select email_address from sugar_depaul.email_addresses
  where email_addresses.id = new.email_address_id
 ) 
 where guid = new.bean_id and new.deleted = 0 and new.primary_address = 1;
end;
//
delimiter ;

-- This trigger updates SWORD contact's email field when a sugarcrm contact email is updated. 
delimiter //
drop trigger if exists sugar_depaul.sync_contact_to_sword_email_update;//
create trigger sugar_depaul.sync_contact_to_sword_email_update after update on sugar_depaul.email_addr_bean_rel
for each row
begin
 update sword_depaul.work_study_contact 
 set email = 
 (
  select email_address from sugar_depaul.email_addresses
  where email_addresses.id = new.email_address_id
 ) 
 where guid = new.bean_id and new.deleted = 0 and new.primary_address = 1;
end;
//
delimiter ;


---------------------- SWORD ------------------------------
-- Called from SWORD, syncs entire contact to sugar_depaul.

delimiter //
drop procedure if exists sword_depaul.sync_contact_to_sugar;//
create procedure sword_depaul.sync_contact_to_sugar(guid varchar(255))
begin
 declare update_in varchar(40);
 set @fname := (select fname from sword_depaul.work_study_contact where work_study_contact.guid = guid);
 set @lname := (select lname from sword_depaul.work_study_contact where work_study_contact.guid = guid);
 set @phone := (select phone from sword_depaul.work_study_contact where work_study_contact.guid = guid);
 set @phone_cell := (select phone_cell from sword_depaul.work_study_contact where work_study_contact.guid = guid);
 set @email := (select email from sword_depaul.work_study_contact where work_study_contact.guid = guid);
 
 insert into sugar_depaul.contacts (id, first_name, last_name, phone_work, phone_mobile)
 values (guid, @fname, @lname, @phone, @phone_cell)
 on duplicate key 
 update first_name = @fname, last_name = @lname, phone_work = @phone, phone_mobile = @phone_cell;
 
 insert into sugar_depaul.contacts_cstm (id_c, supervisor_c)
 values ((select id from sugar_depaul.contacts where sugar_depaul.contacts.id = guid), 1)
 on duplicate key
 update supervisor_c=1;
 
 if @email is not null and @email != "" then
  set @emailID := (select id from sugar_depaul.email_addresses where email_address = @email);
  if @emailID is null then
   insert into sugar_depaul.email_addresses (id, email_address, email_address_caps)
   values (uuid(), @email, upper(@email));
   set @emailID := (select id from sugar_depaul.email_addresses where email_address = @email);
  end if;
  
  select email_address_id into update_in
   from sugar_depaul.contacts 
   left join sugar_depaul.contacts_cstm on contacts_cstm.id_c = contacts.id
   left join sugar_depaul.email_addr_bean_rel on email_addr_bean_rel.bean_id = contacts.id 
   left join sugar_depaul.email_addresses on email_addresses.id = email_addr_bean_rel.email_address_id 
   where primary_address=1 and contacts.id = guid limit 1;
  
  update sugar_depaul.email_addr_bean_rel 
  set primary_address=0
  where bean_id = guid and email_address_id in (update_in);
  insert into sugar_depaul.email_addr_bean_rel (id, email_address_id, bean_id, primary_address, bean_module)
  values (uuid(), @emailID, guid, 1, "Contacts")
  on duplicate key
  update primary_address=1, bean_id=guid;
 end if;
end;
//
delimiter ;
