#!/usr/bin/env python

import os
import sys
import psycopg2
from psycopg2 import sql
import redis
from app import userDefinedFunction
from app import BUCKET_NAME
import base64


def get_DB_connection():
    print(os.environ.get("DB_NAME"))
    print(os.environ.get("DB_USER"))
    print(os.environ.get("DB_PASSWORD"))
    print(os.environ.get("DB_HOST"))
    print(os.environ.get("DB_PORT"))
    print(os.environ.get("QUEUE"))
    print(BUCKET_NAME)
    try:
        conn = psycopg2.connect(
            dbname=os.environ.get("DB_NAME"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            host=os.environ.get("DB_HOST"),
            port=os.environ.get("DB_PORT"),
        )
        return conn
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL:", error)
        return None


def get_cell_data(conn, row_id):
    try:
        if conn:
            cursor = conn.cursor()
            query = sql.SQL("SELECT {} FROM {} WHERE file_id = %s").format(
                sql.Identifier("image"), sql.Identifier(BUCKET_NAME)
            )
            cursor.execute(query, (row_id,))
            result = cursor.fetchone()
            cursor.close()
            conn.commit()
            if result:
                return base64.b64encode(result[0]).decode("utf-8")
            else:
                return None
    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL:", error)
        return None


def update_cell_data(conn, row_id, image_base64):
    try:
        if conn:
            cursor = conn.cursor()
            query = sql.SQL("UPDATE {} SET {} = %s, {} = %s WHERE file_id = %s").format(
                sql.Identifier(BUCKET_NAME),
                sql.Identifier("additional_info"),
                sql.Identifier("additional_info_type"),
            )
            cursor.execute(query, (image_base64, "IMAGE", row_id))
            conn.commit()
            cursor.close()
            print("Cells updated successfully!")
    except (Exception, psycopg2.Error) as error:
        print("Error while updating data in PostgreSQL:", error)


def pop_redis_queue(redis_conn):
    try:
        queue_name = os.environ.get("QUEUE")
        return redis_conn.lpop(queue_name)
    except Exception as e:
        print("Error while popping from Redis queue:", e)
        return None


def establish_redis_connection():
    try:
        redis_host = os.environ.get("REDIS_HOST")
        redis_port = os.environ.get("REDIS_PORT")

        return redis.Redis(host=redis_host, port=redis_port)
    except Exception as e:
        print("Error while establishing Redis connection:", e)
        return None


if __name__ == "__main__":

    db_conn = get_DB_connection()
    if db_conn:
        print("Successfully established Database connection.")
    else:
        print("Failed to establish Database connection.")
        sys.exit(1)

    redis_conn = establish_redis_connection()
    if redis_conn:
        print("Successfully established Redis connection.")
    else:
        print("Failed to establish Redis connection.")
        sys.exit(1)

    while True:
        image_id = pop_redis_queue(redis_conn)
        print("")
        if image_id:
            image_id = image_id.decode("utf-8")
            print("Popped image_id from Redis queue:", image_id)

        if image_id:
            image_old = get_cell_data(db_conn, image_id)
            image_new = userDefinedFunction(image_old)
            update_cell_data(db_conn, image_id, image_new)
        else:
            print("No data popped from Redis queue. Exiting.")
            db_conn.close()
            break
