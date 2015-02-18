drop table if exists othello_data;
create table othello_data(
    `key` varchar(255) primary key,
    `last_hit` timestamp(6),
    `value` blob 
)
