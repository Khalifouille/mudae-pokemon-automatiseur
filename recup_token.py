from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Edge()  
driver.get("https://discord.com/login")

input("Connecte-toi puis appuie sur Entrée")

token = driver.execute_script("""
    return (webpackChunkdiscord_app.push([
        [Math.random()], {}, 
        (req) => { window.req = req; }
    ]), window.req.c)
    [Object.keys(window.req.c).find(k => window.req.c[k]?.exports?.default?.getToken)]
    .exports.default.getToken();
""")

print("Token:", token)
driver.quit()
