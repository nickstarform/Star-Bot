sqlite3 Data.db;
select * from discord_macro;
select * from discord_quote;



drop table discord_quote;
drop table discord_macro;

CREATE TABLE discord_quote (
uniq integer PRIMARY KEY autoincrement,
quoteContent text NOT NULL,
hits integer NOT NULL,
userID text NOT NULL,
guildID text NOT NULL,
date text NOT NULL
);

CREATE TABLE discord_macro (
macro text NOT NULL,
user_created text NOT NULL,
date_created text NOT NULL,
content text NOT NULL,
hits integer NOT NULL,
user_id text NOT NULL
);
.exit
cd ../