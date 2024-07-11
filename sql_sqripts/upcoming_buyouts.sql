CREATE OR REPLACE VIEW upcoming_buyouts AS
SELECT b.date_plan,
       b.feedback,
       p.good_link,
       p.type,
       p.request,
       b.id
FROM buyouts AS b
         JOIN plans AS p ON p.id = b.plan
WHERE date_plan >= CURRENT_TIMESTAMP AT TIME ZONE 'MSK'
  AND date_plan <= CURRENT_TIMESTAMP AT TIME ZONE 'MSK' + INTERVAL '1 day'
  AND user_id IS NULL;
