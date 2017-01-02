drop table if exists posts;
create table posts (
  id integer primary key autoincrement,
  title text not null,
  medium_url not null,
  content text not null
);

drop table if exists projects;
create table projects (
  id integer primary key autoincrement,
  name text not null,
  image_url not null,
  description text not null
);

drop table if exists quotes;
create table quotes (
  id integer primary key autoincrement,
  author text not null,
  quote text not null,
  context_url not null
);

drop table if exists groups;
create table groups (
  id integer primary key autoincrement,
  name text not null,
  mission text not null
);
