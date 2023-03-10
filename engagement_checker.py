import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from time import sleep

chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9459")

chrome_driver = "chromedriver.exe"
driver = selenium.webdriver.Chrome(chrome_driver, options=chrome_options)


def check_post(link, user):
    print(f"checking post: {link}")
    driver.get(link)
    # boot-complete
    # check for boot complete
    body_element = driver.find_element(By.TAG_NAME, "body")
    while (not element_contains_class(body_element, "boot-complete")):
        print("not done loading")
        sleep(0.5)

    # open reactions list
    reaction_button = driver.find_element(
        By.CLASS_NAME, "social-details-social-counts__count-value")
    reaction_button.click()
    sleep(0.5)

    # identify reaction list
    reaction_list = driver.find_element(
        By.CLASS_NAME, "artdeco-list--offset-1")

    # check total reaction count
    # social-details-reactors-tab__reaction-tab
    reaction_count_text = driver.find_element(
        By.CSS_SELECTOR, ".social-details-reactors-tab__reaction-tab span:nth-child(2)").get_attribute("innerHTML")
    reaction_count_text = reaction_count_text.replace(
        ",", "").replace("\n", "").replace(" ", "")
    reaction_count = int(reaction_count_text)
    # breaks for larger numbers
    # needs to do replace() for spaces \n and ,

    if reaction_count < 500:
        # count li tags in list
        li_list = reaction_list.find_elements(By.TAG_NAME, "li")
        stuck_check = 0
        last_count = 0
        # scroll reaction list until all reactions are shown
        while (len(li_list) < reaction_count):
            last_count = len(li_list)
            print(f"{len(li_list)}/{reaction_count}")
            driver.execute_script(
                "arguments[0].scrollIntoView();", li_list[len(li_list)-1])
            sleep(0.1)
            li_list = reaction_list.find_elements(By.TAG_NAME, "li")
            if (last_count == len(li_list)):
                stuck_check += 1
            else:
                stuck_check = 0
            if (stuck_check > 5):
                break

        # check for user
        reaction_list = driver.find_element(
            By.CLASS_NAME, "artdeco-list--offset-1")
        full_reaction_text = reaction_list.get_attribute("innerHTML")
        if (full_reaction_text.find(user) > -1):
            return True
        else:
            return False
    return True


def element_contains_class(e, _class):
    class_list = e.get_attribute("class").split(" ")
    for i in range(0, len(class_list)):
        if (class_list[i] == _class):
            return True
    return False


# link = "https://www.linkedin.com/posts/zarazamani_blockchain-event-community-activity-7036995006389227521-Rw9c"
# user = "larsylundin"


# # social-details-social-counts__count-value


# def test():
#     result = check_post(link, user)
#     print(result)


# test()
