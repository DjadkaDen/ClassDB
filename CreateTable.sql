-- People
CREATE TABLE people (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    description VARCHAR(255)
);
COMMENT ON TABLE people IS '����';
COMMENT ON COLUMN people.id IS '���';
COMMENT ON COLUMN people.full_name IS '���';
COMMENT ON COLUMN people.description IS '��������';

-- Goals
CREATE TABLE goals (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    priority INT
);
COMMENT ON TABLE goals IS '����';
COMMENT ON COLUMN goals.id IS '���';
COMMENT ON COLUMN goals.title IS '����';
COMMENT ON COLUMN goals.description IS '��������';
COMMENT ON COLUMN goals.priority IS '���������';

-- Money
CREATE TABLE money (
    id SERIAL PRIMARY KEY,
    person_id INT REFERENCES people(id) ON DELETE SET NULL,
    amount NUMERIC(12,2),
    date TIMESTAMP,
    goal_id INT REFERENCES goals(id) ON DELETE SET NULL
);
COMMENT ON TABLE money IS '������';
COMMENT ON COLUMN money.id IS '���';
COMMENT ON COLUMN money.person_id IS '���';
COMMENT ON COLUMN money.amount IS '�����';
COMMENT ON COLUMN money.date IS '����';
COMMENT ON COLUMN money.goal_id IS '����';

-- Plan
CREATE TABLE plan (
    id SERIAL PRIMARY KEY,
    goal_id INT REFERENCES goals(id) ON DELETE CASCADE,
    details VARCHAR(255),
    cost NUMERIC(12,2)
);
COMMENT ON TABLE plan IS '����';
COMMENT ON COLUMN plan.id IS '���';
COMMENT ON COLUMN plan.goal_id IS '����';
COMMENT ON COLUMN plan.details IS '�����������';
COMMENT ON COLUMN plan.cost IS '���������';

-- Fact
CREATE TABLE fact (
    id SERIAL PRIMARY KEY,
    goal_id INT REFERENCES goals(id) ON DELETE CASCADE,
    details VARCHAR(255),
    cost NUMERIC(12,2)
);
COMMENT ON TABLE fact IS '����';
COMMENT ON COLUMN fact.id IS '���';
COMMENT ON COLUMN fact.goal_id IS '����';
COMMENT ON COLUMN fact.details IS '�����������';
COMMENT ON COLUMN fact.cost IS '���������';

-- Subscriptions
CREATE TABLE subscriptions (
    person_id INT REFERENCES people(id) ON DELETE CASCADE,
    goal_id INT REFERENCES goals(id) ON DELETE CASCADE,
    PRIMARY KEY (person_id, goal_id)
);
COMMENT ON TABLE subscriptions IS '��������';
COMMENT ON COLUMN subscriptions.person_id IS '���';
COMMENT ON COLUMN subscriptions.goal_id IS '����';