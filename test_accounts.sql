delete from account_actor;
delete from actor_properties;
delete from actor;
delete from account;

insert into account (username, "password", realname, email) values ('Ruthven', 'Ruthven', 'Hugo Mills', 'Hugo@carfax.org');
insert into account (username, "password", realname, email) values ('Mongo', 'Mongo', 'David Merritt', 'DavidBMerritt@yahoo.com');
insert into account (username, "password", realname, email) values ('Thog', 'Thog', '', '');
insert into account (username, "password", realname, email) values ('PotatoEngineer', 'PotatoEngineer', 'Paul Marshall', '');

insert into actor (name) values ('Ruthven');
insert into actor (name) values ('Mongo');
insert into actor (name) values ('Thog');
insert into actor (name) values ('PotatoEngineer');

insert into account_actor (account_id, actor_id) select account.account_id, actor.actor_id from account, actor where account.username = actor.name