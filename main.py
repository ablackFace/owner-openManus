import asyncio

from app.llm import LLM
from app.logger import logger


async def main():
    while True:
        try:
            prompt = input("输入你的问题 (输入 exit, quit, bye 退出): ")

            if prompt.lower() in ["exit", "quit", "bye"]:
                logger.info("Goodbye!")
                break

            logger.warning("Processing your request...")
            print(f"Assistant: {prompt}")
        except KeyboardInterrupt:
            print("Goodbye!")
            break


async def test():
    llm = LLM()
    response = await llm.ask("你是谁？")
    print(response)

if __name__ == "__main__":
    # asyncio.run(main())
    asyncio.run(test())