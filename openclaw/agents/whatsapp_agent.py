#!/usr/bin/env python3
"""
WhatsApp Agent for OpenClaw
Handles WhatsApp messaging integration
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class WhatsAppAgent:
    """Agent for WhatsApp messaging integration"""

    def __init__(self):
        """Initialize WhatsApp agent"""
        self.whatsapp_number = os.getenv("WHATSAPP_NUMBER", "5511956612953")
        self.provider = os.getenv("WHATSAPP_PROVIDER", "evolution-api")

        # Evolution API config
        self.evolution_url = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
        self.evolution_key = os.getenv("EVOLUTION_API_KEY")
        self.instance_name = os.getenv("EVOLUTION_INSTANCE_NAME", "openclaw")

        # Twilio config
        self.twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_number = os.getenv("TWILIO_WHATSAPP_NUMBER")

        # WhatsApp Business API config
        self.business_account_id = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID")
        self.access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

    async def send_message(
        self,
        to: str,
        message: str,
        message_type: str = "text"
    ) -> Dict[str, Any]:
        """
        Send a WhatsApp message

        Args:
            to: Recipient phone number (with country code)
            message: Message content
            message_type: Type of message (text, image, document, etc.)

        Returns:
            Response from WhatsApp API
        """
        if self.provider == "evolution-api":
            return await self._send_evolution_api(to, message, message_type)
        elif self.provider == "twilio":
            return await self._send_twilio(to, message)
        elif self.provider == "whatsapp-business-api":
            return await self._send_business_api(to, message)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    async def _send_evolution_api(
        self,
        to: str,
        message: str,
        message_type: str = "text"
    ) -> Dict[str, Any]:
        """Send message via Evolution API"""
        if not self.evolution_key:
            raise ValueError("Evolution API key not configured")

        url = f"{self.evolution_url}/message/sendText/{self.instance_name}"
        headers = {
            "Content-Type": "application/json",
            "apikey": self.evolution_key
        }

        payload = {
            "number": to,
            "text": message
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                result = await response.json()
                return {
                    "success": response.status == 200,
                    "provider": "evolution-api",
                    "response": result
                }

    async def _send_twilio(self, to: str, message: str) -> Dict[str, Any]:
        """Send message via Twilio"""
        if not all([self.twilio_sid, self.twilio_token, self.twilio_number]):
            raise ValueError("Twilio credentials not configured")

        import aiohttp
        from aiohttp import BasicAuth

        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_sid}/Messages.json"
        auth = BasicAuth(self.twilio_sid, self.twilio_token)

        data = {
            "From": f"whatsapp:{self.twilio_number}",
            "To": f"whatsapp:{to}",
            "Body": message
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, auth=auth) as response:
                result = await response.json()
                return {
                    "success": response.status == 201,
                    "provider": "twilio",
                    "response": result
                }

    async def _send_business_api(self, to: str, message: str) -> Dict[str, Any]:
        """Send message via WhatsApp Business API"""
        if not all([self.access_token, self.phone_number_id]):
            raise ValueError("WhatsApp Business API credentials not configured")

        url = f"https://graph.facebook.com/v17.0/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {
                "body": message
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                result = await response.json()
                return {
                    "success": response.status == 200,
                    "provider": "whatsapp-business-api",
                    "response": result
                }

    async def receive_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming webhook from WhatsApp

        Args:
            webhook_data: Webhook payload from WhatsApp provider

        Returns:
            Processed message data
        """
        if self.provider == "evolution-api":
            return self._process_evolution_webhook(webhook_data)
        elif self.provider == "twilio":
            return self._process_twilio_webhook(webhook_data)
        elif self.provider == "whatsapp-business-api":
            return self._process_business_webhook(webhook_data)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def _process_evolution_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Evolution API webhook"""
        return {
            "from": data.get("key", {}).get("remoteJid", "").replace("@s.whatsapp.net", ""),
            "message": data.get("message", {}).get("conversation", ""),
            "timestamp": data.get("messageTimestamp"),
            "type": "text"
        }

    def _process_twilio_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Twilio webhook"""
        return {
            "from": data.get("From", "").replace("whatsapp:", ""),
            "message": data.get("Body", ""),
            "timestamp": data.get("Timestamp"),
            "type": "text"
        }

    def _process_business_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process WhatsApp Business API webhook"""
        entry = data.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [{}])[0]

        return {
            "from": messages.get("from", ""),
            "message": messages.get("text", {}).get("body", ""),
            "timestamp": messages.get("timestamp"),
            "type": messages.get("type", "text")
        }

    def get_config_info(self) -> Dict[str, Any]:
        """Get current configuration information"""
        return {
            "whatsapp_number": self.whatsapp_number,
            "provider": self.provider,
            "configured": self._is_configured()
        }

    def _is_configured(self) -> bool:
        """Check if agent is properly configured"""
        if self.provider == "evolution-api":
            return bool(self.evolution_key)
        elif self.provider == "twilio":
            return bool(self.twilio_sid and self.twilio_token and self.twilio_number)
        elif self.provider == "whatsapp-business-api":
            return bool(self.access_token and self.phone_number_id)
        return False


# Example usage
async def main():
    """Example usage of WhatsApp agent"""
    agent = WhatsAppAgent()

    # Print configuration
    print("WhatsApp Agent Configuration:")
    print(json.dumps(agent.get_config_info(), indent=2))

    # Send a test message (uncomment to use)
    # result = await agent.send_message(
    #     to="5511999999999",  # Replace with recipient number
    #     message="Hello from OpenClaw! 🦀"
    # )
    # print("\nMessage sent:")
    # print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
