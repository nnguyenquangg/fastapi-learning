-- =========================================================
-- SQL 02 — JOIN, Subquery, Index, Transaction
-- =========================================================

-- Chuẩn bị: chạy sau 01_basics.sql (đã có categories, products)
-- Thêm bảng orders + order_items để thực hành join

DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    email      VARCHAR(200) UNIQUE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE orders (
    id          SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    status      VARCHAR(20) NOT NULL DEFAULT 'pending',
    total       NUMERIC(12, 2) NOT NULL DEFAULT 0,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE order_items (
    id         SERIAL PRIMARY KEY,
    order_id   INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity   INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL
);

INSERT INTO customers (name, email) VALUES
    ('An',    'an@x.com'),
    ('Bình',  'binh@x.com'),
    ('Châu',  'chau@x.com');

INSERT INTO orders (customer_id, status, total) VALUES
    (1, 'paid',    25500000),
    (1, 'pending', 850000),
    (2, 'paid',    700000);

INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    (1, 1, 1, 25000000),
    (1, 3, 1,   500000),
    (2, 4, 2,   250000),
    (2, 5, 1,   350000),
    (3, 3, 1,   500000),
    (3, 6, 1,   200000);


-- ================================================
-- INNER JOIN
-- ================================================

-- Liệt kê order kèm tên customer
SELECT o.id, c.name AS customer, o.status, o.total
FROM orders o
INNER JOIN customers c ON c.id = o.customer_id;

-- Order items kèm product name
SELECT oi.order_id, p.name AS product, oi.quantity, oi.unit_price
FROM order_items oi
JOIN products p ON p.id = oi.product_id;


-- ================================================
-- LEFT JOIN (lấy tất cả bảng trái, null nếu không match)
-- ================================================

-- Tất cả customer + số order (kể cả customer chưa order)
SELECT c.name, COUNT(o.id) AS order_count
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
GROUP BY c.id, c.name;


-- ================================================
-- Multiple JOIN
-- ================================================

-- Chi tiết từng order item kèm customer + product
SELECT
    o.id         AS order_id,
    c.name       AS customer,
    p.name       AS product,
    oi.quantity,
    oi.unit_price,
    oi.quantity * oi.unit_price AS line_total
FROM orders o
JOIN customers c   ON c.id = o.customer_id
JOIN order_items oi ON oi.order_id = o.id
JOIN products p    ON p.id = oi.product_id
ORDER BY o.id;


-- ================================================
-- Subquery
-- ================================================

-- Product có giá > trung bình toàn bảng
SELECT * FROM products
WHERE price > (SELECT AVG(price) FROM products);

-- Customer có > 1 order
SELECT * FROM customers
WHERE id IN (
    SELECT customer_id FROM orders GROUP BY customer_id HAVING COUNT(*) > 1
);


-- ================================================
-- CTE (Common Table Expression) - dễ đọc hơn subquery
-- ================================================

WITH customer_stats AS (
    SELECT
        customer_id,
        COUNT(*)   AS order_count,
        SUM(total) AS total_spent
    FROM orders
    GROUP BY customer_id
)
SELECT c.name, cs.order_count, cs.total_spent
FROM customers c
LEFT JOIN customer_stats cs ON cs.customer_id = c.id;


-- ================================================
-- Window functions (hay dùng)
-- ================================================

-- Xếp hạng sản phẩm theo giá trong mỗi category
SELECT
    name,
    price,
    category_id,
    ROW_NUMBER() OVER (PARTITION BY category_id ORDER BY price DESC) AS rank_in_category
FROM products;


-- ================================================
-- Index
-- ================================================

-- Tại sao cần index? → query nhanh hơn trên column thường dùng để WHERE/JOIN

-- Xem plan trước khi có index:
EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 1;

-- Tạo index:
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_products_category_id ON products(category_id);

-- Composite index (cho query thường filter theo nhiều column cùng lúc):
CREATE INDEX idx_orders_customer_status ON orders(customer_id, status);

-- Xem plan sau khi có index:
EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 1;

-- ⚠ Index không phải cứ thêm là tốt:
-- - Mỗi index tốn disk + chậm INSERT/UPDATE
-- - Chỉ thêm cho column thực sự query nhiều
-- - Column UNIQUE đã có index ngầm


-- ================================================
-- Transaction
-- ================================================

BEGIN;

UPDATE products SET stock = stock - 1 WHERE id = 1;
INSERT INTO orders (customer_id, status, total) VALUES (1, 'pending', 25000000);
-- Nếu gặp lỗi → ROLLBACK;
-- Nếu OK → COMMIT;

COMMIT;

-- Savepoint (nested transaction):
BEGIN;
    UPDATE products SET stock = 0 WHERE id = 1;
    SAVEPOINT sp1;
    UPDATE products SET stock = -999 WHERE id = 2;   -- sẽ fail vì CHECK
    ROLLBACK TO sp1;
    -- update id=2 rollback, update id=1 vẫn giữ
COMMIT;


-- ================================================
-- Bài tập
-- ================================================

-- 1. Top 3 sản phẩm bán chạy nhất (theo quantity)
-- 2. Doanh thu theo tháng (dùng date_trunc)
-- 3. Customer có total spent cao nhất
-- 4. Product chưa từng được bán
-- 5. Average order value của từng customer
-- 6. Tạo index hợp lý cho 3 query trên. Dùng EXPLAIN ANALYZE để confirm
-- 7. Viết 1 transaction: giảm stock + tạo order_item, rollback nếu stock âm
