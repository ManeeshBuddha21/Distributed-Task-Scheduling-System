
INSERT INTO jobs (name) VALUES ('hello-world');
INSERT INTO tasks (job_id, priority, status, payload) VALUES 
  (1, 10, 'pending', '{"cmd":"echo low"}'),
  (1, 90, 'pending', '{"cmd":"echo HIGH"}');
