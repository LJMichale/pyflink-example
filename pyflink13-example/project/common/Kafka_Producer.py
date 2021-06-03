# -*- coding: utf-8 -*-#

# -------------------------------------------------------------------------------
# Name:         KafkaProducer
# Description:
# Author:       orange
# Date:         2021/6/3
# -------------------------------------------------------------------------------
from __future__ import absolute_import

import logging

from kafka import KafkaProducer
log = logging.getLogger(__name__)


class KafkaMsgProducer:

    def __init__(self, server, topic):
        self._server = server
        self.producer = None
        self.topic = topic

    def connect(self):
        if self.producer is None:
            producer = KafkaProducer(bootstrap_servers=self)
            self.producer = producer

    def close(self):
        if self.producer is not None:
            self.producer.close()
            self.producer = None

    def send(self, msg):
        if self.producer is not None:
            if not isinstance(msg, bytes):
                msg = msg.eccode("utf-8")
            self.producer.send(topic=self.topic, value=msg)


def get_kafka_producer(port, topic):
    producer = KafkaMsgProducer("localhost:%d" % port, topic)
    producer.connect()
    log.info("Kafka Producer创建成功！")
    return producer
