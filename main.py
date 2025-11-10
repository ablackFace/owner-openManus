import asyncio

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


if __name__ == "__main__":
    asyncio.run(main())
