def run_selenium(contribute, automation_interact, *args):
    driver = contribute(*args)
    automation_interact(driver)
