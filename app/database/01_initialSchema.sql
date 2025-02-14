create database french;

-- ALTER DATABASE french CHARACTER SET utf8 COLLATE utf8_unicode_ci;
SET NAMES utf8;

use french;

CREATE TABLE phrases (
    id int NOT NULL AUTO_INCREMENT,
    english varchar(512) NOT NULL,
    french varchar(512) NOT NULL,
    status ENUM('Known', 'Learning', 'Todo') NOT NULL,
    PRIMARY KEY (id),
    INDEX (status)
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8
  COLLATE utf8_unicode_ci;

CREATE TABLE phrase_attempts (
    id int NOT NULL AUTO_INCREMENT,
    phrase_id int NOT NULL,
    created_on DATETIME NOT NULL,
    correct bit NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (phrase_id) REFERENCES phrases(id)
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8
  COLLATE utf8_unicode_ci;

INSERT INTO phrases (english, french, status)
VALUES 
    ('Do you speak English', 'Parlez-vous anglais?', 'Learning'),
    ('Whats is your name?', 'Comment tu t’appelles?', 'Learning'),
    ('How are you?', 'Comment allez-vous?', 'Learning'),
    ('How are you? You good?', 'Ça va? En forme?', 'Learning'),
    ('I speak a little French', 'Je parle un peu français.', 'Learning'),
    ('Where is the hotel', 'Où est l’hôtel?', 'Learning'),
    ('It’s beautiful weather today', 'Il fait beau aujourd’hui', 'Learning'),
    ('Its raining', 'Il pleut', 'Learning'),
    ('Table for 6 with 2 children and a baby', 'Table pour 6 avec 2 enfants et un bébé', 'Learning'),
    ('Can you help me?', 'Pouvez-vous m’aider', 'Learning'),
    ('How much do I owe you?', 'Je vous dois combien?', 'Learning'),
    ('I dont understand', 'Je ne comprends pas.', 'Learning'),
    ('Can I have this, please?', 'Puis-je avoir ceci, s’il vous plaît?', 'Learning'),
    ('This one', 'Celui-là', 'Learning'),
    ('Please', 'S’il vous plaît', 'Learning'),
    ('It’s hot', 'Il fait chaud', 'Learning'),
    ('It’s cold', 'Il fait froid', 'Learning'),
    ('It’s sunny', 'Il fait soleil', 'Learning'),
    ('It’s windy', 'Il fait venteux', 'Learning');