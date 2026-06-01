import json
from channels.generic.websocket import AsyncWebsocketConsumer


class SensorConsumer(AsyncWebsocketConsumer):
    """
    WebSocket: ws://localhost:8000/ws/sensor/<device_id>/
    The browser connects here and receives live PPG + SpO2 updates.
    """

    async def connect(self):
        self.device_id  = self.scope['url_route']['kwargs']['device_id']
        self.group_name = f"sensor_{self.device_id}"

        # Join the group for this device
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Confirm connection to the browser
        await self.send(text_data=json.dumps({
            'type'  : 'connection',
            'status': 'connected',
            'device': self.device_id,
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Triggered by IngestReadingView when bracelet sends new data
    async def sensor_update(self, event):
        await self.send(text_data=json.dumps({
            'type'      : 'sensor_update',
            'ppg_value' : event['ppg_value'],
            'spo2'      : event['spo2'],
            'heart_rate': event['heart_rate'],
            'timestamp' : event['timestamp'],
        }))