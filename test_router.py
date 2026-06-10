from amiii.config import AMIIIConfig
from amiii.llm import create_chat_provider
from amiii.tools.intent_router import LLMIntentRouter

provider = create_chat_provider(
    AMIIIConfig.from_env()
)

router = LLMIntentRouter(provider)

intent = router.parse(
    "Could you please open Postman for me?"
)

print(intent)