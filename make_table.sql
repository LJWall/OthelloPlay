drop table if exists othello_data;
create table othello_data(
    game_key varchar(255),
    move_id int,
    last_hit timestamp(6),
    game blob ,
    PRIMARY KEY (game_key, move_id)
)
