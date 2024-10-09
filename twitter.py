import json
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class TwitterScraper:
    """
    用于抓取Twitter数据的类。

    属性:
        chromedriver_path (str): ChromeDriver可执行文件的路径。
        driver (WebDriver): Selenium WebDriver实例。
    """
    def __init__(self, chromedriver_path):
        """
        初始化TwitterScraper实例。

        参数:
            chromedriver_path (str): ChromeDriver可执行文件的路径。
        """
        self.chromedriver_path = chromedriver_path
        self.driver = None
        self.initialize_driver()

    def initialize_driver(self):
        """
        使用ChromeDriver初始化Selenium WebDriver。
        """
        service = Service(executable_path=self.chromedriver_path)
        self.driver = webdriver.Chrome(service=service)

    def close_driver(self):
        """
        关闭Selenium WebDriver。
        """
        if self.driver:
            self.driver.quit()

    def scrape_tweet(self, url):
        """
        从Twitter URL抓取数据。

        参数:
            url (str): 要抓取的Twitter帖子的URL。

        返回:
            dict: 包含抓取到的推文数据的字典，如果发生错误则返回None。
        """
        try:
            self.driver.get(url)
            wait = WebDriverWait(self.driver, 10)

            # 等待推文文本元素加载并提取其内容。
            div_element_tweetText = wait.until(
                EC.presence_of_element_located((By.XPATH, '//div[@data-testid="tweetText"]')))
            span_element = div_element_tweetText.find_element(By.XPATH, './/span')
            text = span_element.text

            # 提取推文的UTC时间戳。
            time_element = self.driver.find_element(By.CSS_SELECTOR, "time")
            datetime_attribute = time_element.get_attribute("datetime")

            # 提取推文作者的用户名。
            div_element_username = wait.until(
                EC.presence_of_element_located((By.XPATH, '//div[@data-testid="User-Name"]')))
            username = div_element_username.find_element(By.XPATH, './/span/span').text

            # 提取用户的个人资料URL。
            div_element_username_email = wait.until(
                EC.presence_of_element_located((By.XPATH, '//div[@data-testid="User-Name"]//a')))
            username_email_url = div_element_username_email.get_attribute("href")
            parsed_url = urlparse(username_email_url)
            path = parsed_url.path
            username_email = path.strip('/')

            # 提取推文的图片URL（如果有）。
            div_element_tweetPhoto = wait.until(
                EC.presence_of_element_located((By.XPATH, '//div[@data-testid="tweetPhoto"]/img')))
            tweetPhoto_url = div_element_tweetPhoto.get_attribute("src")

            # 提取用户的头像URL。
            div_UserAvatar = wait.until(EC.presence_of_element_located(
                (By.XPATH, f'//div[@data-testid="UserAvatar-Container-{username_email}"]//img')))
            UserAvatar_url = div_UserAvatar.get_attribute("src")

            # 将抓取的数据作为字典返回。
            return {
                'text': text,
                'datetime': datetime_attribute,
                'username': username,
                'username_email': username_email,
                'tweetPhoto_url': tweetPhoto_url,
                'UserAvatar_url': UserAvatar_url
            }

        except Exception as e:
            # 如果发生异常，打印错误信息并返回None。
            print(f"Error: {e}")
            return None

    def save_to_json(self, data, filename):
        """
        将数据保存到JSON文件。

        参数:
            data (dict): 要保存的数据。
            filename (str): 要保存的JSON文件名。
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

# 示例用法
if __name__ == "__main__":
    scraper = TwitterScraper("/path/to/chromedriver")
    url = 'https://twitter.com/elonmusk/status/1838809177549914529'
    result = scraper.scrape_tweet(url)
    if result:
        scraper.save_to_json(result, 'tweet_data.json')
        print("Data saved to tweet_data.json")
    scraper.close_driver()
