

-- -- -- Insert dummy data into users
-- INSERT INTO users (username, firstname, lastname, email, postcode, hash) VALUES 
-- ('johndoe', 'John', 'Doe', 'johndoe@example.com', '12345', 'hashed_password_1'),
-- ('janedoe', 'Jane', 'Doe', 'janedoe@example.com', '12345', 'hashed_password_2'),
-- ('alice', 'Alice', 'Smith', 'alice@example.com', '67890', 'hashed_password_3'),
-- ('bob', 'Bob', 'Johnson', 'bob@example.com', '67890', 'hashed_password_4'),
-- ('charlie', 'Charlie', 'Brown', 'charlie@example.com', '54321', 'hashed_password_5'),
-- ('david', 'David', 'Williams', 'david@example.com', '12345', 'hashed_password_6'),
-- ('emma', 'Emma', 'Jones', 'emma@example.com', '54321', 'hashed_password_7'),
-- ('frank', 'Frank', 'Garcia', 'frank@example.com', '67890', 'hashed_password_8'),
-- ('grace', 'Grace', 'Martinez', 'grace@example.com', '12345', 'hashed_password_9'),
-- ('henry', 'Henry', 'Lopez', 'henry@example.com', '67890', 'hashed_password_10');


-- Insert sample data into groups
INSERT INTO groups (name, postcode) VALUES 
('Newcastle Renovations', '12345'),
('Villeneuve Apartments', '12345'),
('Mountain Cabins', '67890');

INSERT INTO user_groups (user_id, group_id, status) VALUES 
(1, 1, 'creator'),   -- John Doe is the creator of Group A
(1, 3, 'member'),   -- John Doe is the creator of Group A
(2, 1, 'member'),   -- Jane Doe is a member of Group A
(3, 1, 'member'),   -- Alice Smith is a member of Group A
(3, 2, 'member'),   -- Alice Smith is a member of Group A
(4, 1, 'member'),   -- Bob Johnson is a member of Group A
(5, 1, 'member'),   -- Charlie Brown is a member of Group A
(6, 2, 'creator'),  -- David Williams is the creator of Group B
(7, 2, 'member'),   -- Emma Jones is a member of Group B
(8, 2, 'member'),   -- Frank Garcia is a member of Group B
(9, 2, 'member'),   -- Grace Martinez is a member of Group B
(10, 3, 'creator'); -- Henry Lopez is the creator of Group C


-- Insert dummy data into tradesmen
INSERT INTO tradesmen (trade, name, address, postcode, phone_number, email) VALUES 
('Electrician', 'John Smith', '123 Electric Ave', '12345', '555-1234', 'johnsmith@example.com'),
('Plumber', 'Jane Doe', '456 Plumbing St', '12345', '555-5678', 'janedoe@example.com'),
('Carpenter', 'Alice Johnson', '789 Woodwork Rd', '67890', '555-8765', 'alicejohnson@example.com'),
('Painter', 'Bob Brown', '321 Paint Blvd', '67890', '555-4321', 'bobbrown@example.com'),
('Mason', 'Charlie White', '654 Brick Ln', '54321', '555-1357', 'charliewhite@example.com'),
('Electrician', 'Michael Scott', '123 Scranton St', '12345', '555-1234', 'michael@example.com'),
('Plumber', 'Pam Beesly', '456 Scranton St', '12345', '555-5678', 'pam@example.com'),
('Carpenter', 'Jim Halpert', '789 Scranton St', '67890', '555-8765', 'jim@example.com'),
('Painter', 'Dwight Schrute', '321 Scranton St', '67890', '555-4321', 'dwight@example.com'),
('Mason', 'Angela Martin', '654 Scranton St', '54321', '555-1357', 'angela@example.com');


-- Insert dummy data into group_tradesmen
INSERT INTO group_tradesmen (group_id, tradesman_id) VALUES 
(1, 1),  -- Group A with John Smith (Electrician)
(1, 2),  -- Group A with Jane Doe (Plumber)
(1, 6),  -- Group A with Michael Scott (Electrician)
(1, 7),  -- Group A with Pam Beesly (Plumber)
(1, 8),  -- Group A with Jim Halpert (Carpenter)
(1, 9),  -- Group A with Dwight Schrute (Painter)
(1, 10), -- Group A with Angela Martin (Mason)
(2, 3),  -- Group B with Alice Johnson (Carpenter)
(2, 4),  -- Group B with Bob Brown (Painter)
(2, 6),  -- Group B with Michael Scott (Electrician)
(2, 7),  -- Group B with Pam Beesly (Plumber)
(2, 8),  -- Group B with Jim Halpert (Carpenter)
(2, 9),  -- Group B with Dwight Schrute (Painter)
(2, 10), -- Group B with Angela Martin (Mason)
(3, 5),  -- Group C with Charlie White (Mason)
(3, 6),  -- Group C with Michael Scott (Electrician)
(3, 7),  -- Group C with Pam Beesly (Plumber)
(3, 8),  -- Group C with Jim Halpert (Carpenter)
(3, 9),  -- Group C with Dwight Schrute (Painter)
(3, 10); -- Group C with Angela Martin (Mason)


-- Insert dummy data into jobs
INSERT INTO jobs (user_id, tradesman_id, date, title, description, call_out_fee, hourly_rate, daily_rate, total_cost, rating) VALUES 
(1, 1, '2023-10-01', 'Electrical Repair', 'Fixing the wiring in the living room.', 50, 100, NULL, 150, 5),
(2, 2, '2023-10-02', 'Plumbing Installation', 'Installing a new sink in the kitchen.', 30, 80, NULL, 110, 4),
(1, 3, '2023-10-03', 'Carpentry Work', 'Building a custom bookshelf.', 40, 90, NULL, 130, 5),
(3, 4, '2023-10-04', 'Interior Painting', 'Painting the living room and hallway.', 20, 70, NULL, 90, 3),
(2, 5, '2023-10-05', 'Masonry Repair', 'Repairing the brick wall in the backyard.', 25, 85, NULL, 115, 4),
(1, 2, '2023-10-06', 'Garden Landscaping', 'Designing and planting a new garden layout.', 40, 75, NULL, 115, 5),
(2, 3, '2023-10-07', 'Roof Repair', 'Fixing leaks in the roof.', 60, 120, NULL, 180, 4),
(3, 1, '2023-10-08', 'Electrical Inspection', 'Inspecting the electrical system for safety.', 50, 100, NULL, 150, 5),
(1, 4, '2023-10-09', 'Drywall Installation', 'Installing drywall in the new office.', 30, 70, NULL, 100, 4),
(2, 5, '2023-10-10', 'Tile Installation', 'Installing new tiles in the bathroom.', 20, 60, NULL, 80, 5),
(1, 6, '2023-10-11', 'Wiring Upgrade', 'Upgrading the wiring in the entire house.', 50, 100, NULL, 150, 5),  -- Michael Scott
(2, 7, '2023-10-12', 'Pipe Replacement', 'Replacing old pipes in the kitchen.', 30, 80, NULL, 110, 4),  -- Pam Beesly
(1, 8, '2023-10-13', 'Custom Furniture', 'Building a custom dining table.', 40, 90, NULL, 130, 5),  -- Jim Halpert
(3, 9, '2023-10-14', 'Exterior Painting', 'Painting the exterior of the house.', 20, 70, NULL, 90, 3),  -- Dwight Schrute
(2, 10, '2023-10-15', 'Brick Wall Construction', 'Constructing a new brick wall.', 25, 85, NULL, 115, 4),  -- Angela Martin
(1, 1, '2023-10-16', 'Ceiling Fan Installation', 'Installing a new ceiling fan in the living room.', 30, 70, NULL, 100, 5),
(2, 2, '2023-10-17', 'Sewer Line Inspection', 'Inspecting the sewer line for blockages.', 40, 90, NULL, 130, 4),
(1, 3, '2023-10-18', 'Deck Construction', 'Building a new deck in the backyard.', 50, 100, NULL, 200, 5),
(3, 4, '2023-10-19', 'Wallpaper Removal', 'Removing old wallpaper from the bedroom.', 20, 60, NULL, 80, 3),
(2, 5, '2023-10-20', 'Concrete Pouring', 'Pouring concrete for a new patio.', 25, 85, NULL, 115, 4),
(1, 6, '2023-10-21', 'Faucet Installation', 'Installing a new kitchen faucet.', 30, 75, NULL, 105, 5),
(2, 7, '2023-10-22', 'Gutter Cleaning', 'Cleaning out the gutters.', 20, 50, NULL, 70, 4),
(1, 8, '2023-10-23', 'Window Installation', 'Installing new windows in the living room.', 40, 90, NULL, 130, 5),
(3, 9, '2023-10-24', 'Roof Inspection', 'Inspecting the roof for damage.', 30, 80, NULL, 110, 4),
(2, 10, '2023-10-25', 'Fence Repair', 'Repairing the backyard fence.', 25, 65, NULL, 90, 5),
(1, 1, '2023-10-26', 'Electrical Panel Upgrade', 'Upgrading the electrical panel.', 50, 100, NULL, 150, 5),
(2, 2, '2023-10-27', 'Water Heater Installation', 'Installing a new water heater.', 40, 90, NULL, 130, 4),
(1, 3, '2023-10-28', 'Cabinet Installation', 'Installing new kitchen cabinets.', 50, 100, NULL, 200, 5),
(3, 4, '2023-10-29', 'Floor Tiling', 'Tiling the kitchen floor.', 20, 70, NULL, 90, 3),
(2, 5, '2023-10-30', 'Dryer Vent Cleaning', 'Cleaning the dryer vent.', 25, 85, NULL, 115, 4),
(1, 6, '2023-10-31', 'Insulation Installation', 'Installing insulation in the attic.', 30, 75, NULL, 105, 5),
(2, 7, '2023-11-01', 'Siding Repair', 'Repairing the siding on the house.', 20, 50, NULL, 70, 4),
(1, 8, '2023-11-02', 'Patio Construction', 'Building a new patio.', 40, 90, NULL, 130, 5),
(3, 9, '2023-11-03', 'Chimney Cleaning', 'Cleaning the chimney.', 30, 80, NULL, 110, 4),
(2, 10, '2023-11-04', 'Landscaping', 'Landscaping the front yard.', 25, 65, NULL, 90, 5),
(1, 1, '2023-11-05', 'Smart Home Installation', 'Installing smart home devices.', 50, 100, NULL, 150, 5),
(2, 2, '2023-11-06', 'Garage Door Repair', 'Repairing the garage door.', 40, 90, NULL, 130, 4),
(1, 3, '2023-11-07', 'Home Theater Installation', 'Installing a home theater system.', 50, 100, NULL, 200, 5),
(3, 4, '2023-11-08', 'Pressure Washing', 'Pressure washing the driveway.', 20, 70, NULL, 90, 3),
(2, 5, '2023-11-09', 'Pest Control', 'Pest control treatment for the house.', 25, 85, NULL, 115, 4),
(1, 6, '2023-11-10', 'Air Conditioning Repair', 'Repairing the air conditioning unit.', 30, 75, NULL, 105, 5),
(2, 7, '2023-11-11', 'Heating System Installation', 'Installing a new heating system.', 20, 50, NULL, 70, 4),
(1, 8, '2023-11-12', 'Septic Tank Cleaning', 'Cleaning the septic tank.', 40, 90, NULL, 130, 5),
(3, 9, '2023-11-13', 'Tree Trimming', 'Trimming the trees in the yard.', 30, 80, NULL, 110, 4),
(2, 10, '2023-11-14', 'Home Security Installation', 'Installing a home security system.', 25, 65, NULL, 90, 5);


-- Insert dummy data into join_requests
INSERT INTO join_requests (user_id, group_id) VALUES 
(6, 1),  -- John Doe requests to join Group A
(6, 3),  -- John Doe requests to join Group B
(8, 1),  -- Frank requests to join Group A
(7, 3),  -- Alice Smith requests to join Group C
(7, 1),  -- Bob Johnson requests to join Group B
(9, 1);  -- Bob Johnson requests to join Group B

