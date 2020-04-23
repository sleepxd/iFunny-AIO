import requests, threading, ctypes
import random, time, json, string, os
from colorama import Fore, init, Style
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

init(convert=True, autoreset=True)
lock = threading.Lock()

created = 0
followed = 0
liked = 0
counter = 0

def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def safe_print(args):
    lock.acquire()
    print(args)
    lock.release()

class SendComment():
    def __init__(self, api_key="", email="", password="", message="", scraped_posts=[], proxy=""):
        self.api_key = api_key
        self.email = email
        self.password = password
        self.message = message
        self.proxy = proxy
        self.scraped_posts = scraped_posts
        self.session = requests_retry_session()
        self.session.proxies.update({"https":"https://"+proxy})

    def set_title(self):
        ctypes.windll.kernel32.SetConsoleTitleW("Sleeps iFunny AIO | Commenter | Commented %s times" % (str(counter)))

    def solve_captcha(self, site_key, url):
        API_KEY = self.api_key
        captcha_id = requests.post("http://2captcha.com/in.php?key={}&method=userrecaptcha&googlekey={}&pageurl={}".format(API_KEY, site_key, url)).text.split('|')[1]
        recaptcha_answer = requests.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(API_KEY, captcha_id)).text
        while 'CAPCHA_NOT_READY' in recaptcha_answer:
            time.sleep(5)
            recaptcha_answer = requests.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(API_KEY, captcha_id)).text
        recaptcha_answer = recaptcha_answer.split('|')[1]
        return recaptcha_answer

    def scrape_post(self):
        scraped_post = []
        r = requests.get('https://ifunny.co/')
        for line in r.iter_lines():
            if "data-id" in line.decode('utf-8'):
                post = line.decode("utf-8").split("data-id=\"")[-1].split(" ")[0].replace("\"",'')
                if 'error' not in post:
                    scraped_post.append(post)
        return scraped_post

    def sign_in(self):
        try:
            headers = {
            "Connection": "keep-alive",
            "Accept": "application/json, text/plain, */*",
            "Sec-Fetch-Dest": "empty",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://ifunny.co",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Referer": "https://ifunny.co/tags/login",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            }
            form_data = {"username":self.email, "password":self.password}
            login = self.session.post('https://ifunny.co/oauth/login', headers=headers, json=form_data)
            if ':200' in login.text:
                safe_print(Style.BRIGHT + Fore.GREEN + 'Logged in with %s' % (self.email))
                return "success"
            else:
                safe_print(Fore.RED + 'Error while logging in')
                return "failed"
        except:
            return "failed"

    def leave_comment(self):
        global counter
        headers = {
		"Host": "ifunny.co",
		"Connection": "keep-alive",
		"Accept": "application/json, text/plain, */*",
		"Sec-Fetch-Dest": "empty",
		"X-Requested-With": "XMLHttpRequest",
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36",
		"Content-Type": "application/json;charset=UTF-8",
		"Origin": "https://ifunny.co",
		"Sec-Fetch-Site": "same-origin",
		"Sec-Fetch-Mode": "cors",
		"Accept-Encoding": "gzip, deflate, br"
        }
        form_data = {"text":self.message}
        post_id = random.choice(self.scraped_posts)
        send_post = self.session.post("https://ifunny.co/api/content/%s/comments" % (post_id), headers=headers, json=form_data)
        if 'comment_show_replies' in send_post.text:
            safe_print(Style.BRIGHT + Fore.YELLOW + 'Commented on post %s with message %s%s' % (post_id, Fore.WHITE, self.message))
            counter += 1
            self.set_title()
        else:
            safe_print(Fore.RED + 'Error posting on %s with message %s' % (post_id, self.message))
            safe_print(send_post.text)

class CreateAccount():
    def __init__(self, api_key="", proxy=""):
        self.api_key = api_key
        self.session = requests_retry_session()
        self.session.proxies.update({"https":"https://"+proxy})

    def save_account(self, email, password, username):
        lock.acquire()
        with open('created.txt', 'a', encoding='utf-8', errors='ignore') as f:
            f.write('%s:%s:%s\n' % (email, username, password))
        lock.release()

    def set_title(self):
        ctypes.windll.kernel32.SetConsoleTitleW("Sleeps iFunny AIO | Account Creator | Created %s accounts" % (str(created)))

    def generate_creds(self):
        email = ('').join(random.choices(string.ascii_letters.upper() + string.digits.upper(), k=10)) + '@gmail.com'
        username = ('').join(random.choices(string.ascii_letters.upper() + string.digits.upper(), k=10))
        password = 'b!1' + ('').join(random.choices(string.ascii_letters.upper() + string.digits.upper(), k=7))
        return email, username, password

    def start_registration(self):
        try:
            global created
            email, username, password = self.generate_creds()
            captcha_response = SendComment(api_key=self.api_key).solve_captcha('6LflIwgTAAAAAElWMFEVgr9zs2UpH0eiFsVN_KfF', 'https://ifunny.co/users')
            headers = {
                'Accept':'application/json, text/plain, */*',
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
                'Content-Type': 'application/json;charset=UTF-8'
            }
            data = {
                'captchaToken':captcha_response,
                'email':email,
                'mailing':'False',
                'nick':username,
                'password':password,
                'regType':'pwd'
            }
            send_register = self.session.post('https://ifunny.co/users', headers=headers, json=data)
            if 'status\":200' in send_register.text:
                self.save_account(email, username, password)
                safe_print('%s%s[Account Created] %s%s' % (Style.BRIGHT, Fore.GREEN, Fore.WHITE, email))
                created += 1
                self.set_title()
            else:
                safe_print('Error creating account')
        except:
            pass

class LikePost():
    def __init__(self, api_key="", email="", password="", proxy="", content=""):
        self.api_key = api_key
        self.email = email
        self.password = password
        self.content = content
        self.session = requests_retry_session()
        self.session.proxies.update({"https":"https://"+proxy})

    def set_title(self):
        ctypes.windll.kernel32.SetConsoleTitleW("Sleeps iFunny AIO | Liking Post | Liked %s times" % (str(liked)))

    def sign_in(self):
        try:
            headers = {
            "Connection": "keep-alive",
            "Accept": "application/json, text/plain, */*",
            "Sec-Fetch-Dest": "empty",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://ifunny.co",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Referer": "https://ifunny.co/tags/login",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            }
            form_data = {"username":self.email, "password":self.password}
            login = self.session.post('https://ifunny.co/oauth/login', headers=headers, json=form_data)
            if ':200' in login.text:
                safe_print(Style.BRIGHT + Fore.GREEN + 'Logged in with %s' % (self.email))
                return "success"
            else:
                safe_print(Fore.RED + 'Error while logging in')
                return "failed"
        except:
            return "failed"

    def send_like(self):
        global liked
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Sec-Fetch-Dest": "empty",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36",
            "Origin": "https://ifunny.co",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9"
        }
        send_like = self.session.put('https://ifunny.co/api/content/%s/smiles' % (self.content), headers=headers)
        if 'num_smiles' in send_like.text:
            safe_print('%sLiked post %s%s%s on %s%s' % (Fore.YELLOW, Fore.WHITE, self.content, Fore.YELLOW, Fore.WHITE, self.email))
            liked += 1
            self.set_title()

class FollowUser():
    def __init__(self, api_key="", email="", password="", proxy="", user="", username=""):
        self.api_key = api_key
        self.email = email
        self.password = password
        self.user = user
        self.username = username
        self.session = requests_retry_session()
        self.session.proxies.update({"https":"https://"+proxy})

    def set_title(self):
        ctypes.windll.kernel32.SetConsoleTitleW("Sleeps iFunny AIO | Following %s | Followed %s times" % (self.username.title(), str(followed)))

    def sign_in(self):
        try:
            headers = {
            "Connection": "keep-alive",
            "Accept": "application/json, text/plain, */*",
            "Sec-Fetch-Dest": "empty",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://ifunny.co",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Referer": "https://ifunny.co/tags/login",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            }
            form_data = {"username":self.email, "password":self.password}
            login = self.session.post('https://ifunny.co/oauth/login', headers=headers, json=form_data)
            if ':200' in login.text:
                safe_print(Style.BRIGHT + Fore.GREEN + 'Logged in with %s' % (self.email))
                return "success"
            else:
                safe_print(Fore.RED + 'Error while logging in')
                return "failed"
        except:
            return "failed"

    def send_follow(self):
        global followed
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Sec-Fetch-Dest": "empty",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://ifunny.co",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9"
        }
        data = {'userId':self.user}
        follow = self.session.put('https://ifunny.co/api/subscriptions', headers=headers, json=data)
        if follow.text == '{}':
            safe_print('%sFollowed user %s%s%s with ID %s%s' % (Fore.YELLOW, Fore.WHITE, self.username.title(), Fore.YELLOW, Fore.WHITE, self.user))
            followed += 1
            self.set_title()

def loadData():
    accounts = []
    with open('accounts.txt', 'r') as f:
        for x in f.readlines():
            accounts.append(x.replace('\n',''))
    config = open('config.json', 'r')
    data = json.load(config)
    captcha_key = data['captcha-key']
    return accounts, captcha_key

def main_menu():
    proxies = [line.replace('\n','') for line in open('proxies.txt', 'r').readlines()]

    ctypes.windll.kernel32.SetConsoleTitleW("Sleeps iFunny AIO | Main Menu")
    print('[1] Account Creation')
    print('[2] Mass Comment Features')
    print('[3] Mass Like')
    print('[4] Mass Follow')
    mode = str(input())
    threads = int(input('Threads: '))

    if mode == '1':
        API_KEY = loadData()[-1]
        os.system('cls')

        def account_thread_start():
            creator = CreateAccount(api_key=API_KEY, proxy=random.choice(proxies))
            creator.start_registration()
        
        while True:
            if threading.active_count() <= threads:
                threading.Thread(target=account_thread_start, args=(),).start()

    elif mode == '2':
        scraped = SendComment().scrape_post()
        safe_print("Scraped %s post" % (len(scraped)))
        os.system('cls')
        messages = ['hey', 'hello', 'hi123']
        accounts, API_KEY = loadData()

        def comment_thread_starter():
            account = random.choice(accounts)
            Commenter = SendComment(message=random.choice(messages), api_key=API_KEY, email=account.split(':')[0], password=account.split(':')[1], scraped_posts=scraped, proxy=random.choice(proxies))
            login = Commenter.sign_in()
            if login == "success":
                Commenter.leave_comment()

        while True:
            if threading.active_count() <= threads:
                threading.Thread(target=comment_thread_starter, args=(),).start()

    elif mode == '3':
        content = str(input('Photo URL: '))
        content = content.split('/')[-1].split('?')[0]
        accounts, API_KEY = loadData()
        os.system('cls')
        
        def like_thread_starter(email, password):
            liker = LikePost(content=content, api_key=API_KEY, email=email, password=password, proxy=random.choice(proxies))
            login = liker.sign_in()
            if login == "success":
                liker.send_like()

        counter = 0
        while True:
            if threading.active_count() <= threads:
                account = accounts[counter]
                try:
                    threading.Thread(target=like_thread_starter, args=(account.split(':')[0], account.split(':')[1],)).start()
                    counter += 1
                except:
                    input()

    elif mode == '4':
        user = str(input('Profile: '))
        user = user.split('/')[-1]

        safe_print('Parsing UID for %s' % (user.title()))

        get_user_info = requests.get('https://ifunny.co/user/%s' % (user))
        info_list = get_user_info.text.split('data-dwhevent-props=\"id=')
        uid = info_list[-1].split('\">')[0]
        accounts, API_KEY = loadData()
        os.system('cls')

        def follow_thread_starter(email, password):
            follow = FollowUser(username=user, user=uid, api_key=API_KEY, email=email, password=password, proxy=random.choice(proxies))
            login = follow.sign_in()
            if login == "success":
                follow.send_follow()
        
        counter = 0
        while True:
            if threading.active_count() <= threads:
                account = accounts[counter]
                try:
                    threading.Thread(target=follow_thread_starter, args=(account.split(':')[0], account.split(':')[1],)).start()
                    counter += 1
                except:
                    input()

    else:
        safe_print('Invalid mode selected. Redirecting to main menu.')
        time.sleep(2)
        main_menu()

main_menu()
