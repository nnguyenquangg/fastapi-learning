-- =========================================================
-- SQL 01 — Cơ bản
-- Mục tiêu: gõ tay từng query trong psql hoặc GUI
-- =========================================================

-- Kết nối:
--   docker exec -it learn-pg psql -U postgres -d phase3
-- Hoặc mở TablePlus/DBeaver, tạo SQL editor


-- ================================================
-- 1. Tạo schema & table
-- ================================================

DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS categories;

CREATE TABLE categories (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE products (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(200) NOT NULL,
    price         NUMERIC(10, 2) NOT NULL CHECK (price > 0),
    stock         INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    category_id   INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Kiểm tra:
\dt     -- list tables (psql meta-command)
\d products


-- ================================================
-- 2. INSERT
-- ================================================

INSERT INTO categories (name) VALUES
    ('Electronics'),
    ('Books'),
    ('Clothing');

INSERT INTO products (name, price, stock, category_id) VALUES
    ('iPhone 15',        25000000, 10, 1),
    ('MacBook Air M3',   28000000,  5, 1),
    ('Clean Code',         500000, 30, 2),
    ('Áo thun trắng',      250000, 50, 3),
    ('Quần jeans',         650000, 25, 3),
    ('Sách Python',        350000, 20, 2);

-- RETURNING để lấy dữ liệu vừa insert
INSERT INTO products (name, price, stock, category_id) VALUES
    ('Galaxy S24', 22000000, 8, 1)
RETURNING id, name, created_at;


-- ================================================
-- 3. SELECT cơ bản
-- ================================================

-- Tất cả
SELECT * FROM products;

-- Chọn column
SELECT id, name, price FROM products;

-- Alias
SELECT name AS product_name, price AS cost FROM products;

-- Tính toán trên column
SELECT name, price, price * 1.1 AS price_with_vat FROM products;


-- ================================================
-- 4. WHERE
-- ================================================

SELECT * FROM products WHERE price > 1000000;
SELECT * FROM products WHERE category_id = 1 AND stock > 0;
SELECT * FROM products WHERE name LIKE '%Book%';
SELECT * FROM products WHERE name ILIKE '%book%';     -- case-insensitive
SELECT * FROM products WHERE category_id IN (1, 2);
SELECT * FROM products WHERE stock BETWEEN 10 AND 30;
SELECT * FROM products WHERE category_id IS NULL;


-- ================================================
-- 5. ORDER BY, LIMIT, OFFSET
-- ================================================

SELECT * FROM products ORDER BY price DESC;
SELECT * FROM products ORDER BY category_id, price DESC;

-- Pagination: page 2, size 3
SELECT * FROM products ORDER BY id LIMIT 3 OFFSET 3;


-- ================================================
-- 6. UPDATE
-- ================================================

UPDATE products SET price = 24000000 WHERE id = 1;
UPDATE products SET stock = stock + 10 WHERE category_id = 1;
UPDATE products SET is_active = FALSE WHERE stock = 0 RETURNING *;

-- ⚠ Luôn nhớ WHERE. UPDATE không có WHERE → update TOÀN BỘ bảng


-- ================================================
-- 7. DELETE
-- ================================================

DELETE FROM products WHERE is_active = FALSE;

-- ⚠ Luôn SELECT trước để confirm rồi mới DELETE


-- ================================================
-- 8. Aggregate
-- ================================================

SELECT COUNT(*) FROM products;
SELECT COUNT(*) AS total, SUM(stock) AS total_stock, AVG(price) AS avg_price FROM products;
SELECT MIN(price), MAX(price) FROM products;

-- GROUP BY
SELECT category_id, COUNT(*) AS product_count, AVG(price) AS avg_price
FROM products
GROUP BY category_id;

-- HAVING (filter sau khi group)
SELECT category_id, AVG(price) AS avg_price
FROM products
GROUP BY category_id
HAVING AVG(price) > 1000000;


-- ================================================
-- 9. Bài tập
-- ================================================

-- 1. Tìm 3 sản phẩm đắt nhất
-- 2. Đếm số sản phẩm mỗi category, chỉ lấy category có > 1 sản phẩm
-- 3. Tổng giá trị kho = SUM(price * stock) của toàn bộ sản phẩm active
-- 4. Sản phẩm nào có giá > giá trung bình của category đó (subquery)
-- 5. Insert 5 sản phẩm mới, mỗi cái thuộc 1 category khác nhau
-- 6. Update tất cả sản phẩm có stock < 5 → is_active = false
-- 7. Xoá các category không có sản phẩm nào

-- Khi làm xong → sang 02_joins.sql
