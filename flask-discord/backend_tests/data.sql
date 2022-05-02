DROP TABLE IF EXISTS user;
CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  username TEXT NOT NULL UNIQUE CHECK( length(username) <= 32),
  password TEXT NOT NULL
);
INSERT INTO user (email, username, password)
VALUES
	("test@gmail.com","myspaceTom","pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79");

