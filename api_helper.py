import aiohttp

async def get_free_ai_response(text: str) -> str:
    url = f"https://pollinations.ai{text}?system=Ти крутий ШІ-помічник для учнів 7 класу. Спілкуйся молодіжною українською мовою з емодзі, пояснюй просто."
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.text()
    except Exception:
        pass
    return "⚠️ Не вдалося зв'язатися з сервером ШІ. Спробуй пізніше!"
