class ChatbotService:
    def __init__(self, model):
        self.model = model

    async def query(self, message):
        result = await self.model.generate(message)
        return {**result.model_dump(), "business_actions": 0}
