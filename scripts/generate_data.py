# scripts/generate_data.py
# Generates the COMPLETE seed.sql: schema + dummy data, in one reproducible file.
import random
from datetime import datetime, timedelta

try:
    from faker import Faker
    fake = Faker()
except ImportError:
    fake = None

STATUSES = ['delivered', 'shipped', 'cancelled', 'pending']
STATUS_WEIGHTS = [0.65, 0.15, 0.10, 0.10]
PAYMENT_METHODS = ['card', 'cash', 'online', 'wallet']
CITIES = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio']


def random_date(start_days_ago, end_days_ago):
    """Random date between two day offsets relative to today."""
    days = random.randint(end_days_ago, start_days_ago)
    return (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')


def generate_seed_sql(filename="data/seed.sql"):
    sql = []

    sql.append("""-- ================= SCHEMA =================
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    city TEXT,
    signup_date DATE NOT NULL
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    order_date DATE NOT NULL,
    status TEXT CHECK (status IN ('delivered','shipped','cancelled','pending'))
);

CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(order_id),
    amount NUMERIC(10,2) NOT NULL,
    payment_date DATE NOT NULL,
    method TEXT CHECK (method IN ('card','cash','online','wallet'))
);
""")

    # ---------------- 1. Customers (~50) ----------------
    num_customers = 50
    customer_signup_dates = {}

    for c_id in range(1, num_customers + 1):
        if fake:
            name = fake.name().replace("'", "''")
            email = fake.unique.email()
        else:
            name = f"Customer_{c_id}"
            email = f"user_{c_id}@example.com"

        city = random.choice(CITIES)
        signup_date = random_date(start_days_ago=180, end_days_ago=30)
        customer_signup_dates[c_id] = signup_date

        sql.append(
            f"INSERT INTO customers (customer_id, name, email, city, signup_date) "
            f"VALUES ({c_id}, '{name}', '{email}', '{city}', '{signup_date}');"
        )

    # ---------------- 2. Orders (~200) ----------------
    num_orders = 200
    order_dates = {}
    valid_order_ids = []

    # FIX: Restored missing terminal integer '+ 1'
    for o_id in range(1, num_orders + 1):
        customer_id = random.randint(1, num_customers)
        signup_dt = datetime.strptime(customer_signup_dates[customer_id], '%Y-%m-%d')
        days_since_signup = (datetime.now() - signup_dt).days
        order_date = random_date(start_days_ago=max(days_since_signup, 1), end_days_ago=0)

        status = random.choices(STATUSES, weights=STATUS_WEIGHTS)[0]
        order_dates[o_id] = order_date

        if status != 'cancelled':
            valid_order_ids.append(o_id)

        sql.append(
            f"INSERT INTO orders (order_id, customer_id, order_date, status) "
            f"VALUES ({o_id}, {customer_id}, '{order_date}', '{status}');"
        )

    # ---------------- 3. Payments (~180) ----------------
    num_payments = 180
    paid_order_ids = random.sample(valid_order_ids, min(num_payments, len(valid_order_ids)))

    for p_id, order_id in enumerate(paid_order_ids, start=1):
        amount = round(random.uniform(15.00, 450.00), 2)
        order_dt = datetime.strptime(order_dates[order_id], '%Y-%m-%d')

        # FIX: Corrected method call from 'days.randint' to 'random.randint'
        payment_dt = order_dt + timedelta(days=random.randint(0, 3))
        if payment_dt > datetime.now():
            payment_dt = datetime.now()
        payment_date = payment_dt.strftime('%Y-%m-%d')

        method = random.choice(PAYMENT_METHODS)

        sql.append(
            f"INSERT INTO payments (payment_id, order_id, amount, payment_date, method) "
            f"VALUES ({p_id}, {order_id}, {amount}, '{payment_date}', '{method}');"
        )

    # ---------------- 4. Sequence Resets ----------------
    sql.append("""-- ============ SEQUENCE RESETS ============
SELECT setval('customers_customer_id_seq', (SELECT MAX(customer_id) FROM customers));
SELECT setval('orders_order_id_seq',       (SELECT MAX(order_id)     FROM orders));
SELECT setval('payments_payment_id_seq',   (SELECT MAX(payment_id)   FROM payments));
""")

    with open(filename, "w") as f:
        f.write("\n".join(sql) + "\n")

    print(f"Wrote schema + {len(sql)} statements to {filename} "
          f"({num_customers} customers, {num_orders} orders, {len(paid_order_ids)} payments).")


if __name__ == "__main__":
    generate_seed_sql()