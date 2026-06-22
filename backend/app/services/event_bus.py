"""Event Bus service for real-time pub/sub messaging and Kafka/in-memory routing."""

import asyncio
import json
import logging
from typing import Dict, Any, List, Callable, Awaitable

from app.config import get_settings

logger = logging.getLogger("omniflow.event_bus")
settings = get_settings()

class EventBusService:
    """Publishes and subscribes to system events, with Kafka and in-memory modes."""

    def __init__(self):
        self.use_kafka = settings.kafka_mode == "kafka"
        self.producer = None
        self.listeners: Dict[str, List[Callable[[Dict[str, Any]], Awaitable[None]]]] = {}
        
        if self.use_kafka:
            try:
                from aiokafka import AIOKafkaProducer
                self.producer = AIOKafkaProducer(bootstrap_servers=settings.kafka_bootstrap_servers)
                logger.info("Connected to Kafka Bootstrap Servers")
            except Exception as e:
                logger.warning(f"⚠️ Kafka producer connection failed: {e}. Falling back to In-Memory mode.")
                self.use_kafka = False

    async def start(self):
        """Starts Kafka producer if enabled."""
        if self.use_kafka and self.producer:
            try:
                await self.producer.start()
                logger.info("🚀 Kafka Event Bus started")
            except Exception as e:
                logger.error(f"❌ Failed to start Kafka: {e}")
                self.use_kafka = False

    async def stop(self):
        """Stops Kafka producer if enabled."""
        if self.use_kafka and self.producer:
            await self.producer.stop()
            logger.info("🛑 Kafka Event Bus stopped")

    def subscribe(self, topic: str, callback: Callable[[Dict[str, Any]], Awaitable[None]]):
        """Subscribe to a specific topic with an async callback."""
        if topic not in self.listeners:
            self.listeners[topic] = []
        self.listeners[topic].append(callback)
        logger.debug(f"Subscribed listener to topic '{topic}'")

    async def publish(self, topic: str, payload: Dict[str, Any]):
        """Publish a message to a topic."""
        message = {
            "topic": topic,
            "payload": payload,
        }
        
        # In-Memory Routing
        if topic in self.listeners:
            tasks = [cb(payload) for cb in self.listeners[topic]]
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

        # Real-Time UI Broadcast
        # Import dynamically to avoid circular dependencies
        try:
            from app.api.websocket import manager
            await manager.broadcast({
                "type": "event_bus_msg",
                "topic": topic,
                "data": payload
            })
        except Exception as e:
            logger.debug(f"WS broadcast failed: {e}")

        # Kafka Routing
        if self.use_kafka and self.producer:
            try:
                await self.producer.send_and_wait(
                    topic,
                    json.dumps(payload).encode("utf-8")
                )
            except Exception as e:
                logger.error(f"❌ Kafka publish error on topic '{topic}': {e}")

# Global event bus instance
event_bus = EventBusService()
