import psycopg2
import os
from sqlalchemy import create_engine
import boto3
import json

ssm = boto3.client('ssm')
parameter = ssm.get_parameter(Name='team1', WithDecryption=True)
secret_json = json.loads(parameter['Parameter']['Value'])

HOST=secret_json['host']
USER=secret_json['username']
PASSWORD=secret_json['password']
DB_NAME=secret_json['database']
PORT=secret_json['port']

DB_DATA = 'postgresql+psycopg2://' + USER + ':' + PASSWORD + '@' + HOST + ':5439/' \
       + DB_NAME


def setup_db_connection(host=HOST, user=USER, password=PASSWORD, port=PORT, db_name=DB_NAME):

    connection = psycopg2.connect(host=host, user=user, password=password, port=port, database=db_name)
    cursor = connection.cursor()
    
    return connection, cursor

def create_db_tables(connection, cursor):
    create_temp_orders_table= \
    """
        CREATE TABLE IF NOT EXISTS "public"."temp_orders"( 
            "order_id" INTEGER NOT NULL IDENTITY (1,1), 
            "product" VARCHAR(1000) NULL,
            "total_price" NUMERIC(18,2) NULL,
            "branch" VARCHAR NULL,
            "time" TIMESTAMP NULL,
            "payment_type" VARCHAR NULL,
        PRIMARY KEY("order_id") ) ENCODE AUTO;
    """

    create_item_basket_data_table = \
    """
        CREATE TABLE IF NOT EXISTS "public"."item_basket"(
            "order_id" INTEGER NOT NULL ,
            "product" text,
            "product_id" INTEGER)
         ENCODE AUTO;
    """
    create_basket_data_table = \
    """
         CREATE TABLE IF NOT EXISTS "public"."baskets"(
             "order_id" INTEGER,
             "product_id" INTEGER)
         ENCODE AUTO;
    """
    create_product_data_table = \
     """
         CREATE TABLE IF NOT EXISTS "public"."products"( 
         "product_id" INTEGER NOT NULL IDENTITY (1,1),
         "product" VARCHAR NULL,
         "price" NUMERIC(18,2) NULL,
         PRIMARY KEY("product_id") ) 
         ENCODE AUTO;
     """
    create_order_data_table = \
    """
        CREATE TABLE IF NOT EXISTS "public"."orders"( 
        "order_id" INTEGER NOT NULL,
        "total_price" NUMERIC(18,2) NULL,
        "branch" VARCHAR NULL,
        "time" TIMESTAMP NULL,
        "payment_type" VARCHAR NULL,
        PRIMARY KEY("order_id") ) ENCODE AUTO;
    """
    cursor.execute(create_item_basket_data_table)
    cursor.execute(create_basket_data_table)
    cursor.execute(create_product_data_table)
    cursor.execute(create_order_data_table)
    cursor.execute(create_temp_orders_table)
    connection.commit()
    cursor.close()
    connection.close()

def create_engine_for_load_step(db_data=DB_DATA):
    return create_engine(db_data)
