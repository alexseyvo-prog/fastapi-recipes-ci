-- RESULT: 1
-- Информация обо всех заказах

SELECT
    c.full_name AS customer_name,
    m.full_name AS manager_name,
    o.purchase_amount,
    o.date
FROM "order" AS o
JOIN customer AS c
    ON o.customer_id = c.customer_id
LEFT JOIN manager AS m
    ON o.manager_id = m.manager_id
ORDER BY o.order_no;


-- RESULT: 2
-- Покупатели без заказов

SELECT
    c.full_name AS customer_name
FROM customer AS c
LEFT JOIN "order" AS o
    ON c.customer_id = o.customer_id
WHERE o.order_no IS NULL
ORDER BY c.full_name;


-- RESULT: 3
-- Заказы, где города покупателя и менеджера различаются

SELECT
    o.order_no,
    m.full_name AS manager_name,
    c.full_name AS customer_name
FROM "order" AS o
JOIN customer AS c
    ON o.customer_id = c.customer_id
JOIN manager AS m
    ON o.manager_id = m.manager_id
WHERE m.city <> c.city
ORDER BY o.order_no;


-- RESULT: 4
-- Заказы, сделанные покупателями напрямую,
-- без помощи менеджеров

SELECT
    c.full_name AS customer_name,
    o.order_no
FROM "order" AS o
JOIN customer AS c
    ON o.customer_id = c.customer_id
WHERE o.manager_id IS NULL
ORDER BY c.full_name, o.order_no;


-- RESULT: 5
-- Уникальные пары покупателей,
-- живущих в одном городе и имеющих одного менеджера

SELECT
    c1.full_name AS customer_1,
    c2.full_name AS customer_2,
    c1.city,
    m.full_name AS manager_name
FROM customer AS c1
JOIN customer AS c2
    ON c1.city = c2.city
   AND c1.manager_id = c2.manager_id
   AND c1.customer_id < c2.customer_id
LEFT JOIN manager AS m
    ON c1.manager_id = m.manager_id
ORDER BY c1.city, customer_1, customer_2;