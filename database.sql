CREATE TABLE restaurants (
    name TEXT PRIMARY KEY,
    cuisine TEXT NOT NULL,
    location TEXT NOT NULL,
    review_date DATE,
    review_score INTEGER,
    review_text TEXT,
    image BLOB
 );
INSERT INTO restaurants (name, cuisine, location, review_date, review_score, review_text, image) VALUES
('Pasta Palace', 'Italian', 'Downtown', '2024-05-10', 5, 'Amazing pasta and great atmosphere!', NULL),
('Sushi Central', 'Japanese', 'Uptown', '2024-05-12', 4, 'Fresh sushi but a bit pricey.', NULL),
('Curry Corner', 'Indian', 'Midtown', '2024-05-15', 3, 'Good flavors but service was slow.', NULL);