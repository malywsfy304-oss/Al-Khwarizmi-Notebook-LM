from playwright.async_api import async_playwright
from flask import Flask, request, jsonify
import asyncio, os, json

app = Flask(__name__)

def load_cookies():
    raw = os.environ.get("COOKIES_JSON", "[]")
    return json.loads(raw)

async def ask_notebooklm(file_url: str, question: str) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        await context.add_cookies(load_cookies())
        page = await context.new_page()
        await page.goto("https://notebooklm.google.com")
        await page.wait_for_load_state("networkidle")
        await page.click("[aria-label='New notebook']")
        await page.click("text=Add source")
        await page.fill("input[type='url']", file_url)
        await page.click("text=Insert")
        await page.wait_for_timeout(4000)
        await page.fill("[placeholder*='Ask']", question)
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(6000)
        answer = await page.inner_text(".response-text")
        await browser.close()
        return answer

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    result = asyncio.run(
        ask_notebooklm(data["file_url"], data["question"])
    )
    return jsonify({"answer": result})

@app.route("/")
def home():
    return jsonify({"status": "Al-Khwarizmi Bot is running"})
