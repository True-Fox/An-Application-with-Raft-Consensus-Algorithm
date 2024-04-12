CREATE TABLE Users (
    user_id INT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL
);

CREATE TABLE Projects (
    project_id INT PRIMARY KEY,
    project_name VARCHAR(255) NOT NULL,
    project_description TEXT,
    start_date DATE,
    end_date DATE,
    status VARCHAR(50) NOT NULL
);

CREATE TABLE Tasks (
    task_id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT,
    task_name VARCHAR(255) NOT NULL,
    task_description TEXT,
    due_date DATE,
    priority VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    assigned_to INT,
    FOREIGN KEY (project_id) REFERENCES Projects(project_id),
    FOREIGN KEY (assigned_to) REFERENCES Users(user_id)
);

CREATE TABLE Comments (
    comment_id INT PRIMARY KEY,
    task_id INT,
    user_id INT,
    comment_text TEXT,
    comment_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES Tasks(task_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE Attachments (
    attachment_id INT PRIMARY KEY,
    task_id INT,
    attachment_name VARCHAR(255) NOT NULL,
    attachment_path VARCHAR(255) NOT NULL,
    attachment_type VARCHAR(50) NOT NULL,
    FOREIGN KEY (task_id) REFERENCES Tasks(task_id)
);

INSERT INTO Users (user_id, username, email, password, role)
VALUES
    (1, 'admin', 'admin@example.com', 'password', 'admin'),
    (2, 'manager1', 'manager1@example.com', 'password', 'manager'),
    (3, 'employee1', 'employee1@example.com', 'password', 'employee');

INSERT INTO Projects (project_id, project_name, project_description, start_date, end_date, status)
VALUES
    (1, 'Project A', 'Development of product A', '2024-01-01', '2024-06-30', 'in progress'),
    (2, 'Project B', 'Marketing campaign for product B', '2024-03-15', '2024-09-30', 'pending'),
    (3, 'Project C', 'Research and development for C', '2024-02-01', '2024-05-31', 'completed');

INSERT INTO Tasks (task_id, project_id, task_name, task_description, due_date, priority, status, assigned_to)
VALUES
    (1, 1, 'Design UI', 'Design user interface', '2024-02-15', 'high', 'completed', 2),
    (2, 1, 'Develop backend', 'Implement server-side logic', '2024-03-31', 'high', 'in progress', 3),
    (3, 2, 'Create ad content', 'Design advertisements', '2024-04-30', 'medium', 'pending', 2),
    (4, 3, 'Conduct market research', 'Analyze market trends', '2024-03-15', 'high', 'in progress', 3);
