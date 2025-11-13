import asyncio

from app.agent.manus import Manus
from app.llm import LLM
from app.logger import logger


async def main():

    manus = Manus()

    while True:
        try:
            prompt = input("输入你的问题 (输入 exit, quit, bye 退出): ")

            if prompt.lower() in ["exit", "quit", "bye"]:
                logger.info("Goodbye!")
                break

            await manus.run(prompt)
        except KeyboardInterrupt:
            print("Goodbye!")
            break


async def test():
    llm = LLM()
    response = await llm.ask(
        [
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "system",
                "content": "你是一个 ReAct Agent 智能体、你可以执行一些工具来完成任务。",
            },
            {"role": "user", "content": "你是谁？,你必须使用 markdown 格式回答"},
        ]
    )
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
    # asyncio.run(test())
