INSERT INTO params (param_name, param_value, description)
VALUES ('db_version'::param_name, '00.01', 'Database version number')
ON CONFLICT (param_name) 
DO UPDATE SET 
    param_value = EXCLUDED.param_value,
    description = EXCLUDED.description;
