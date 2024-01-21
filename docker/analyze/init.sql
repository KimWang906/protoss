DROP DATABASE protoss_db;
CREATE DATABASE protoss_db;

USE protoss_db;
CREATE TABLE pt_account(
    acc_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    username varchar(32) NOT NULL,
    password varchar(64) NOT NULL,
    unique(username)
);

CREATE TABLE pt_uservault(
    id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    acc_id BIGINT NOT NULL,
    KRW_amount BIGINT NOT NULL,
    BTC_amount BIGINT NOT NULL,
    ETH_amount BIGINT NOT NULL,
    XRP_amount BIGINT NOT NULL,
    SOL_amount BIGINT NOT NULL,
    timestamp BIGINT NOT NULL,
    unique(acc_id)
);

CREATE TABLE pt_coininfo (
    id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    symbol varchar(10),
    current_price BIGINT NOT NULL,
    qty BIGINT NOT NULL,
    unique(symbol)
);

INSERT INTO pt_coininfo VALUES (
    NULL,
    'BTC',
    50000000,
    10
);

INSERT INTO pt_coininfo VALUES (
    NULL,
    'ETH',
    2735000,
    100
);

INSERT INTO pt_coininfo VALUES (
    NULL,
    'XRP',
    863,
    10000
);

INSERT INTO pt_coininfo VALUES (
    NULL,
    'SOL',
    72000,
    1000
);


CREATE TABLE pt_tradehistory (
    id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    acc_id BIGINT NOT NULL,
    symbol varchar(10),
    price BIGINT NOT NULL, -- 매수/매도 금액
    amount BIGINT NOT NULL, -- 수량
    total_price BIGINT NOT NULL, -- 매수/매도 총 금액 
    type BIGINT NOT NULL,
    trade_time BIGINT,
    unique(trade_time)  -- 트레이딩봇 방지 (최소 수량 매수/매도 반복)
); 

CREATE TABLE pt_addressbook (
    id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    acc_id BIGINT NOT NULL,
    symbol varchar(10) NOT NULL,
    address varchar(255) NOT NULL,
    memo varchar(10) NOT NULL, 
    create_at BIGINT NOT NULL,
    unique(address, symbol, create_at)
); 
