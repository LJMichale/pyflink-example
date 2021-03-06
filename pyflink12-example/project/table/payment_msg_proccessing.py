# -*- coding: utf-8 -*-#

# -------------------------------------------------------------------------------
# Name:         payment_msg_proccessing
# Description:
# Author:       orange
# Date:         2021/6/14
# -------------------------------------------------------------------------------

from pyflink.datastream import StreamExecutionEnvironment, TimeCharacteristic
from pyflink.table import StreamTableEnvironment, DataTypes, EnvironmentSettings
from pyflink.table.udf import udf

provinces = ("Beijing", "Shanghai", "Hangzhou", "Shenzhen", "Jiangxi", "Chongqing", "Xizang")


@udf(input_types=[DataTypes.STRING()], result_type=DataTypes.STRING())
def province_id_to_name(id):
    return provinces[id]


def log_processing():
    env = StreamExecutionEnvironment.get_execution_environment()
    env_settings = EnvironmentSettings.Builder().use_blink_planner().build()
    t_env = StreamTableEnvironment.create(stream_execution_environment=env, environment_settings=env_settings)
    t_env.get_config().get_configuration().set_boolean("python.fn-execution.memory.managed", True)

    source_ddl = """
            CREATE TABLE payment_msg(
                createTime VARCHAR,
                orderId BIGINT,
                payAmount DOUBLE,
                payPlatform INT,
                provinceId INT
            ) WITH (
              'connector.type' = 'kafka',
              'connector.version' = 'universal',
              'connector.topic' = 'payment_msg',
              'connector.properties.bootstrap.servers' = 'kafka:9092',
              'connector.properties.group.id' = 'test_3',
              'connector.startup-mode' = 'latest-offset',
              'format.type' = 'json'
            )
            """

    es_sink_ddl = """
            CREATE TABLE es_sink (
                province VARCHAR PRIMARY KEY,
                pay_amount DOUBLE
            ) with (
                'connector.type' = 'elasticsearch',
                'connector.version' = '7',
                'connector.hosts' = 'http://elasticsearch:9200',
                'connector.index' = 'platform_pay_amount_1',
                'connector.document-type' = 'payment',
                'update-mode' = 'upsert',
                'connector.flush-on-checkpoint' = 'true',
                'connector.key-delimiter' = '$',
                'connector.key-null-literal' = 'n/a',
                'connector.bulk-flush.max-size' = '42mb',
                'connector.bulk-flush.max-actions' = '32',
                'connector.bulk-flush.interval' = '1000',
                'connector.bulk-flush.backoff.delay' = '1000',
                'format.type' = 'json'
            )
    """

    t_env.sql_update(source_ddl)
    t_env.sql_update(es_sink_ddl)
    t_env.register_function('province_id_to_name', province_id_to_name)

    t_env.from_path("payment_msg") \
        .select("province_id_to_name(provinceId) as province, payAmount") \
        .group_by("province") \
        .select("province, sum(payAmount) as pay_amount") \
        .insert_into("es_sink")

    t_env.execute("payment_demo")


if __name__ == '__main__':
    log_processing()