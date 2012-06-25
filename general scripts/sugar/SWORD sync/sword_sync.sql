-- -------------------------- SUGARCRM ----------------------------------------------------

-- This trigger updates SWORD when a sugarcrm contact is added. Does not include email
delimiter //
drop trigger if exists !!!SUGAR DB!!!.sync_contact_to_sword_insert;
//
create trigger !!!SUGAR DB!!!.sync_contact_to_sword_insert after insert on !!!SUGAR DB!!!.contacts
for each row
begin
 insert into !!!SWORD DB!!!.work_study_contact (guid, fname, lname, title, fax, phone, phone_cell)  
 (
  select contacts.id, first_name, last_name, title, phone_fax, phone_work, phone_mobile from !!!SUGAR DB!!!.contacts 
  left join !!!SUGAR DB!!!.contacts_cstm on contacts_cstm.id_c = contacts.id
  where supervisor_c=1 and contacts.id=new.id
 );
end;
//

-- This trigger updates SWORD when a sugarcrm contact is updated. Does not include email
drop trigger if exists !!!SUGAR DB!!!.sync_contact_to_sword;
//
create trigger !!!SUGAR DB!!!.sync_contact_to_sword after update on !!!SUGAR DB!!!.contacts
for each row
begin
 if new.deleted=0 then
  set @email = (
   select email_address from email_addresses where id = (
    select email_address_id from email_addr_bean_rel where bean_id = new.id and deleted=0 and primary_address=1
   )
  );
  insert into !!!SWORD DB!!!.work_study_contact (guid, fname, lname, title, fax, phone, phone_cell, email)
  values (new.id, new.first_name, new.last_name, new.title, new.phone_fax, new.phone_work, new.phone_mobile, @email)
  on duplicate key update
  fname=new.first_name, lname=new.last_name, title=new.title, fax=new.phone_fax, phone=new.phone_work, phone_cell=new.phone_mobile, email=@email;
 end if;
end;
//

-- This trigger updates SWORD contact's email field when a sugarcrm contact email is changed. 
drop trigger if exists !!!SUGAR DB!!!.sync_contact_to_sword_email;
//
create trigger !!!SUGAR DB!!!.sync_contact_to_sword_email after insert on !!!SUGAR DB!!!.email_addr_bean_rel
for each row
begin
 update !!!SWORD DB!!!.work_study_contact 
 set email =
 (
  select email_address from !!!SUGAR DB!!!.email_addresses
  where email_addresses.id = new.email_address_id
 ) 
 where guid = new.bean_id and new.deleted = 0 and new.primary_address = 1;
end;
//

-- This trigger updates SWORD contact's email field when a sugarcrm contact email is updated. 
drop trigger if exists !!!SUGAR DB!!!.sync_contact_to_sword_email_update;
//
create trigger !!!SUGAR DB!!!.sync_contact_to_sword_email_update after update on !!!SUGAR DB!!!.email_addr_bean_rel
for each row
begin
 update !!!SWORD DB!!!.work_study_contact 
 set email = 
 (
  select email_address from !!!SUGAR DB!!!.email_addresses
  where email_addresses.id = new.email_address_id
 ) 
 where guid = new.bean_id and new.deleted = 0 and new.primary_address = 1;
end;
//


-- -------------------- SWORD ------------------------------
-- Called from SWORD, syncs entire contact to sugarcrm.

drop procedure if exists !!!SWORD DB!!!.sync_contact_to_sugar;
//
create procedure !!!SWORD DB!!!.sync_contact_to_sugar(guid varchar(255))
begin
 declare update_in varchar(40);
 set @fname := (select fname from !!!SWORD DB!!!.work_study_contact where work_study_contact.guid = guid);
 set @lname := (select lname from !!!SWORD DB!!!.work_study_contact where work_study_contact.guid = guid);
 set @title := (select title from !!!SWORD DB!!!.work_study_contact where work_study_contact.guid = guid);
 set @fax := (select fax from !!!SWORD DB!!!.work_study_contact where work_study_contact.guid = guid);
 set @phone := (select phone from !!!SWORD DB!!!.work_study_contact where work_study_contact.guid = guid);
 set @phone_cell := (select phone_cell from !!!SWORD DB!!!.work_study_contact where work_study_contact.guid = guid);
 set @email := (select email from !!!SWORD DB!!!.work_study_contact where work_study_contact.guid = guid);
 
 set @cpemail := (
  select email_address from !!!SUGAR DB!!!.contacts
  left join !!!SUGAR DB!!!.email_addr_bean_rel on email_addr_bean_rel.bean_id = contacts.id
  left join !!!SUGAR DB!!!.email_addresses on email_addresses.id = email_addr_bean_rel.email_address_id
  where contacts.id = guid and !!!SUGAR DB!!!.email_addr_bean_rel.primary_address = 1
  limit 1
 );
 
 insert into !!!SUGAR DB!!!.contacts (id, first_name, last_name, title, phone_fax, phone_work, phone_mobile)
 values (guid, @fname, @lname, @title, @fax, @phone, @phone_cell)
 on duplicate key 
 update first_name = @fname, last_name = @lname, title = @title, phone_fax = @fax, phone_work = @phone, phone_mobile = @phone_cell;
 
 insert into !!!SUGAR DB!!!.contacts_cstm (id_c, supervisor_c)
 values ((select id from !!!SUGAR DB!!!.contacts where !!!SUGAR DB!!!.contacts.id = guid), 1)
 on duplicate key
 update supervisor_c=1;
 
 if @email is not null and @email != "" and @email != @cpemail then
  set @emailID := (select id from !!!SUGAR DB!!!.email_addresses where email_address = @email);
  if @emailID is null then
   insert into !!!SUGAR DB!!!.email_addresses (id, email_address, email_address_caps)
   values (uuid(), @email, upper(@email));
   set @emailID := (select id from !!!SUGAR DB!!!.email_addresses where email_address = @email);
  end if;
  
  select email_address_id into update_in
   from !!!SUGAR DB!!!.contacts 
   left join !!!SUGAR DB!!!.contacts_cstm on contacts_cstm.id_c = contacts.id
   left join !!!SUGAR DB!!!.email_addr_bean_rel on email_addr_bean_rel.bean_id = contacts.id 
   left join !!!SUGAR DB!!!.email_addresses on email_addresses.id = email_addr_bean_rel.email_address_id 
   where primary_address=1 and contacts.id = guid limit 1;
  
  update !!!SUGAR DB!!!.email_addr_bean_rel 
  set primary_address=0
  where bean_id = guid and email_address_id in (update_in);
  
  insert into !!!SUGAR DB!!!.email_addr_bean_rel (id, email_address_id, bean_id, primary_address, bean_module)
  values (uuid(), @emailID, guid, 1, "Contacts")
  on duplicate key
  update primary_address=1, bean_id=guid;
 end if;
end;
//
delimiter ;
