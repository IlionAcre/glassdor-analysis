import asyncio
from playwright.async_api import async_playwright

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, GD_JOB


GD_REMOTE = "https://www.glassdoor.com/Job/remote-us-data-analyst-jobs-SRCH_IL.0,9_IS11047_KO10,22.htm?remoteWorkType=1&sortBy=date_desc&fromAge=7"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
}

db_url = ("sqlite:///jobs.db")
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)

async def get_more_jobs(page):
    while True:
        try:
            await page.wait_for_timeout(2000)
            close_button = await page.query_selector("xpath=/html/body/div[11]/div[2]/div[2]/div[1]/div[1]/button")
            if close_button:
                await close_button.click()
                await page.wait_for_timeout(2000)
            else:

                load_button = await page.query_selector("[data-test='load-more']")
                if load_button:
                    await load_button.click()
                    await page.wait_for_timeout(2000)
                else:
                    break
        except Exception as e:
            print(f"Error getting more jobs {e}")
            break

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await browser.new_page()
        page.set_default_timeout(60000)
        await page.goto(GD_REMOTE)

        await get_more_jobs(page)

        jobs = await page.query_selector_all(".JobsList_jobListItem__wjTHv")
        counter = 1
        for job in jobs:
            try:
                title = await job.query_selector("[data-test$='job-title']")
                location = await job.query_selector('[data-test$="emp-location"]')
                salary = await job.query_selector('[data-test$="detailSalary"]')
                

                title_text = await title.inner_text()
                location_text = await location.inner_text()
                link_text = await title.get_attribute('href')

                if salary:
                    salary_text = await salary.inner_text()
                else:
                    salary_text = "n/a"

                new_job = GD_JOB(title=title_text, location=location_text, salary=salary_text, link=link_text)
                session.add(new_job)
                session.commit()
                
                print(title_text, location_text, salary_text, link_text)
                print(counter)
                counter += 1
            except Exception as e:
                print(f"We couldn't retrieve the information: {e}")
        await browser.close()

asyncio.run(main())