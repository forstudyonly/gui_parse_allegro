from fastapi import FastAPI
import uvicorn
import aiofiles
app = FastAPI()


@app.get("/")
async def read_root(code: str):
    async with aiofiles.open("assets/code.txt", 'w', encoding="utf-8") as out_file:
        await out_file.write(code)  # async write

    return {"code": code}


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()