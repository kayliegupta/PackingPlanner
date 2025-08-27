DROP TABLE IF EXISTS clothes;
DROP TABLE IF EXISTS outfits;
DROP TABLE IF EXISTS outfit_items;

CREATE TABLE clothes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    image TEXT NOT NULL
);

CREATE TABLE outfits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE outfit_items (
    outfit_id INTEGER,
    clothing_id INTEGER,
    FOREIGN KEY(outfit_id) REFERENCES outfits(id),
    FOREIGN KEY(clothing_id) REFERENCES clothes(id)
);