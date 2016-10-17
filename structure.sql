CREATE TABLE page (
    id serial PRIMARY KEY,
    page_name varchar UNIQUE
);

CREATE TABLE page_content (
    id serial PRIMARY KEY,
    page_id integer REFERENCES page (id),
    content text,
    timestamp timestamp
);

CREATE TABLE user_auth (
  id serial PRIMARY KEY,
  username varchar UNIQUE,
  password varchar
);
