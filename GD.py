import asyncio
from playwright.async_api import async_playwright

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, GD_JOB, GD_JOBS_USA


GD_REMOTE = "https://www.glassdoor.com/Job/wyoming-mi-us-data-jobs-SRCH_IL.0,13_IC1134822_KO14,18.htm"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0',
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

async def extract_text(page, div_selector):
    outer_div = await page.query_selector(div_selector)
    if outer_div:
        text_content = await outer_div.inner_text()
        return text_content
    else:
        return None

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0'
            )
        page = await browser.new_page()
        page.set_default_timeout(60000)
        await page.goto(GD_REMOTE)
        await page.wait_for_timeout(10000)
        await get_more_jobs(page)

        jobs = await page.query_selector_all(".JobsList_jobListItem__wjTHv")
        counter = 1
        for job in jobs:
            try:
                title = await job.query_selector("[data-test$='job-title']")
                location = await job.query_selector('[data-test$="emp-location"]')
                salary = await job.query_selector('[data-test$="detailSalary"]')
                

                if salary is not None:
                    salary_text = await salary.inner_text()
                else:
                    salary_text = "n/a"
                
                await title.click(force=True)
                await page.wait_for_selector(".JobDetails_showMore___Le6L")
                show_more_button = await page.query_selector(".JobDetails_showMore___Le6L")
                await show_more_button.click(force=True)



                title_text = await title.inner_text()
                location_text = await location.inner_text()
                link_text = await title.get_attribute('href')
                description_text = await extract_text(page, ".JobDetails_jobDescription__uW_fK")
                
                new_job = GD_JOB(title=title_text, location=location_text, salary=salary_text, link=link_text, description=description_text)
                
                

                company = await page.query_selector(".JobDetails_companyOverviewGrid__3t6b4")
                

                if company is not None:
                    company_text =  await extract_text(page, ".JobDetails_companyOverviewGrid__3t6b4")
                    size = company_text.split("\n")[1]
                    founded = company_text.split("\n")[3]
                    type = company_text.split("\n")[5]
                    industry = company_text.split("\n")[7]
                    sector = company_text.split("\n")[9]
                    revenue = company_text.split("\n")[11]

                    new_job.add_company(size=size, founded=founded, type=type, industry=industry, sector=sector, revenue=revenue)

                
                rating = await page.query_selector(".RatingHeadline_sectionRatingScoreLeft__di1of")
                
                if rating is not None:
                    rating_text = await rating.inner_text()
                    new_job.add_rating(rating=rating_text)
                
                session.add(new_job)

                session.commit()
                
                counter += 1
            except Exception as e:
                print(f"We couldn't retrieve the information: {e}")
        await browser.close()

asyncio.run(main())