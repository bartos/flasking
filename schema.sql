/*drop table if exists entries;*/
create table if not exists entries (
    id integer primary key autoincrement,
    title text not null,
    text text not null
);
