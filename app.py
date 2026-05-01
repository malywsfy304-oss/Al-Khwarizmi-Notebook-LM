from playwright.async_api import async_playwright
from flask import Flask, request, jsonify
import asyncio, os

app = Flask(__name__)

async def ask_notebooklm(file_url: str, question: str) -> str:
    async with async_playwright() as p:
        # فتح متصفح مخفي (Headless)
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # تسجيل الدخول بـ Google (يستخدم cookies محفوظة)
        await page.context.add_cookies(load_cookies())

        # فتح NotebookLM
        await page.goto("https://notebooklm.google.com")
        await page.wait_for_load_state("networkidle")

        # إنشاء Notebook جديد
        await page.click("[aria-label='New notebook']")

        # إضافة الملف من Drive
        await page.click("text=Add source")
        await page.fill("input[type='url']", file_url)
        await page.click("text=Insert")
        await page.wait_for_timeout(4000)  # انتظر التحليل

        # إرسال السؤال
        await page.fill("[placeholder*='Ask']", question)
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(6000)

        # سحب الجواب
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
