CREATE DATABASE IF NOT EXISTS BANCO_DE_DADOS;
USE BANCO_DE_DADOS;

CREATE TABLE IF NOT EXISTS tb_dados()
    id INT NOT NULL AUTO_INCREMENT,
    group_id INT NOT NULL,
    material_id INT NOT NULL,
    item_qty FLOAT NOT NULL,
    item_dim_1 VARCHAR(100),
    item_dim_2 VARCHAR(100),
    item_dim_3 VARCHAR(100),
    item_class VARCHAR(100),
    PRIMARY KEY(id),
    UNIQUE KEY(group_id, material_id, item_qty)
);