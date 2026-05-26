create table market_prices (
  symbol text primary key,
  price numeric,
  volume numeric,
  updated_at timestamptz default now()
);
