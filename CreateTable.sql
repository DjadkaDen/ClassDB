-- People
CREATE TABLE people (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    description VARCHAR(255)
);
COMMENT ON TABLE people IS 'люди';
COMMENT ON COLUMN people.id IS 'Код';
COMMENT ON COLUMN people.full_name IS 'ФИО';
COMMENT ON COLUMN people.description IS 'Описание';

-- Goals
CREATE TABLE goals (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    priority INT
);
COMMENT ON TABLE goals IS 'цели';
COMMENT ON COLUMN goals.id IS 'Код';
COMMENT ON COLUMN goals.title IS 'Цель';
COMMENT ON COLUMN goals.description IS 'Описание';
COMMENT ON COLUMN goals.priority IS 'Приоритет';

-- Money
CREATE TABLE money (
    id SERIAL PRIMARY KEY,
    person_id INT REFERENCES people(id) ON DELETE SET NULL,
    amount NUMERIC(12,2),
    date TIMESTAMP,
    goal_id INT REFERENCES goals(id) ON DELETE SET NULL
);
COMMENT ON TABLE money IS 'деньги';
COMMENT ON COLUMN money.id IS 'Код';
COMMENT ON COLUMN money.person_id IS 'ФИО';
COMMENT ON COLUMN money.amount IS 'Сумма';
COMMENT ON COLUMN money.date IS 'Дата';
COMMENT ON COLUMN money.goal_id IS 'Цель';

-- Plan
CREATE TABLE plan (
    id SERIAL PRIMARY KEY,
    goal_id INT REFERENCES goals(id) ON DELETE CASCADE,
    details VARCHAR(255),
    cost NUMERIC(12,2),
    quantity INTEGER
    isready boolean;
);
COMMENT ON TABLE plan IS 'план';
COMMENT ON COLUMN plan.id IS 'Код';
COMMENT ON COLUMN plan.goal_id IS 'Цель';
COMMENT ON COLUMN plan.details IS 'Детализация';
COMMENT ON COLUMN plan.cost IS 'Стоимость';
COMMENT ON COLUMN plan.quantity IS 'Количество';
COMMENT ON COLUMN plan.isready IS 'Выполнено';

-- Fact
CREATE TABLE fact (
    id SERIAL PRIMARY KEY,
    goal_id INT REFERENCES goals(id) ON DELETE CASCADE,
    details VARCHAR(255),
    cost NUMERIC(12,2),
    price NUMERIC(12,2),
    quantity INTEGER
);
COMMENT ON TABLE fact IS 'факт';
COMMENT ON COLUMN fact.id IS 'Код';
COMMENT ON COLUMN fact.goal_id IS 'Цель';
COMMENT ON COLUMN fact.details IS 'Детализация';
COMMENT ON COLUMN fact.cost IS 'Стоимость';
COMMENT ON COLUMN fact.price IS 'Цена';
COMMENT ON COLUMN fact.quantity IS 'Количество';

-- Subscriptions
CREATE TABLE subscriptions (
    person_id INT REFERENCES people(id) ON DELETE CASCADE,
    goal_id INT REFERENCES goals(id) ON DELETE CASCADE,
    PRIMARY KEY (person_id, goal_id)
);
COMMENT ON TABLE subscriptions IS 'подписки';
COMMENT ON COLUMN subscriptions.person_id IS 'ФИО';
COMMENT ON COLUMN subscriptions.goal_id IS 'Цель';