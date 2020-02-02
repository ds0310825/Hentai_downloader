import requests
import sys
import re
import os
import threading
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.QtCore import *
from nhentai_downloader_ui import Ui_Dialog


class AppWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.ok_button.clicked.connect(self.ok_button_Click)

        script_dir = os.path.dirname(__file__)
        abs_file_path = os.path.join(script_dir, "download_path_cache")
        try:
            if not os.path.exists(abs_file_path):
                os.mknod(abs_file_path)
            with open(abs_file_path, 'r') as cache:
                self.ui.output_path.setText(cache.readline().strip())
        except:
            pass
        global doujin_num
        global i
        global folder_path
        doujin_num = ""
        i = 0
        folder_path = ""

        self.show()

    def ok_button_Click(self):
        global html_for_filter
        input_url = self.ui.input_url.text()
        output_path = self.ui.output_path.text()
        filter_state = self.ui.filter_switch.isChecked()
        chinese_only_state = self.ui.chinese_switch.isChecked()
        print("Filter State：" + str(filter_state))
        print("Chinese Only State：" + str(chinese_only_state))
        self.ui.progress.setText("")
        self.ui.is_done.setText("")
        self.ui.percent.setText("進度：0%")
        if check_web_exist(input_url):
            self.ui.progress.setText("開始下載：" + input_url.split("/")[-2])

            o_url = input_url
            o_url = o_url.strip()
            root_path = output_path

            script_dir = os.path.dirname(__file__)
            abs_file_path = os.path.join(script_dir, "download_path_cache")
            try:
                with open(abs_file_path, "w") as cache:
                    cache.write(output_path)
            except:
                pass

            nh = requests.get(o_url)
            html = BeautifulSoup(nh.text, 'html.parser')

            self.ui.progress.append("解析完成")

            doujin_counter = html.find('span', {'class': 'count'})
            doujin_counter = int(
                re.search('\d*\d',
                          doujin_counter.text.strip().replace(",", "")).group())
            page_counter = int(doujin_counter / 25) + 1

            tag_name = html.find('title').text.replace("\n", "")
            tag_name = tag_name.replace("\t", "")
            tag_name = tag_name.replace(" » nhentai: hentai doujinshi and manga", "")
            tag_name = tag_name.replace(":", "-")
            folder_path = root_path + "\\" + tag_name

            self.ui.progress.append("搜尋完成：" + tag_name)

            if not os.path.isdir(folder_path):
                os.mkdir(folder_path)
                self.ui.progress.append("已建立資料夾：" + folder_path)

            for page in range(1, page_counter + 1):
                url = o_url + r"?page=" + str(page)
                nh = requests.get(url)
                html = BeautifulSoup(nh.text, 'html.parser')

                doujin_urls = html.find_all('a', {'class': 'cover'})
                doujin_nums = html.find_all('img', {'src': re.compile('//t.nhentai.net/galleries/\d*\d/thumb*')})
                doujin_names = html.find_all('div', {'class': 'caption'})

                doujin_urls = [doujin_url['href'].strip() for doujin_url in doujin_urls]
                doujin_names = [doujin_name.text for doujin_name in doujin_names]


                cnt = 0
                for doujin_url, doujin_name in zip(doujin_urls, doujin_names):
                    six_num = re.search('\d*\d',
                                        doujin_url
                                        ).group()

                    print("Scanning：" + "({}) {}".format(six_num, doujin_name))

                    nh_for_filter = requests.get(r"https://nhentai.net/g/" + six_num)
                    html_for_filter = BeautifulSoup(nh_for_filter.text, 'html.parser')

                    if filter_state and chinese_only_state:
                        gay_search = html_for_filter.find_all('a', {'href': '/tag/guro/'})
                        guro_search = html_for_filter.find_all('a', {'href': '/tag/yaoi/'})
                        chinese_search = html_for_filter.find_all('a', {'href': '/language/chinese/'})
                        if gay_search != []:
                            self.ui.progress.append("已成功過濾：" + six_num)
                            print("過濾：" + six_num)
                            cnt += 1
                            continue
                        if guro_search != []:
                            self.ui.progress.append("已成功過濾：" + six_num)
                            print("過濾：" + six_num)
                            cnt += 1
                            continue
                        if chinese_search == []:
                            self.ui.progress.append("已成功過濾：" + six_num)
                            print("過濾：" + six_num)
                            cnt += 1
                            continue
                    elif filter_state:
                        gay_search = html_for_filter.find_all('a', {'href': '/tag/guro/'})
                        guro_search = html_for_filter.find_all('a', {'href': '/tag/yaoi/'})

                        if gay_search != []:
                            self.ui.progress.append("已成功過濾：" + six_num)
                            print("過濾：" + six_num)
                            cnt += 1
                            continue
                        if guro_search != []:
                            self.ui.progress.append("已成功過濾：" + six_num)
                            print("過濾：" + six_num)
                            cnt += 1
                            continue
                    elif chinese_only_state:
                        chinese_search = html_for_filter.find_all('a', {'href': '/language/chinese/'})

                        if chinese_search == []:
                            self.ui.progress.append("已成功過濾：" + six_num)
                            print("過濾：" + six_num)
                            cnt += 1
                            continue

                    not_available_words = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
                    for not_available_word in not_available_words:
                        doujin_name = doujin_name.replace(not_available_word, "!")

                    folder_path = root_path \
                                  + "\\" + tag_name + "\\" \
                                  + "({}) {}".format(six_num, doujin_name)


                    if not os.path.isdir(folder_path):
                        os.mkdir(folder_path)
                        self.ui.progress.append("已建立資料夾：" + six_num)
                    else:
                        cnt += 1
                        self.ui.is_done.append(six_num)
                        continue

                    doujin_num = re.search('\d*\d',
                                           doujin_nums[cnt]['src'].strip()
                                           ).group()
                    threads = []
                    for i in range(1, 50):
                        self.i = i
                        try:
                            QApplication.processEvents()
                            threads.append(threading.Thread(
                                target=download_func, args=(doujin_num, i, folder_path)))

                        except Exception as e:
                            print(e)
                            break
                    for t in threads:
                        t.start()
                    for t in threads:
                        t.join()
                    print(six_num + " done")
                    self.ui.percent.setText("進度：{0: .2f}%"
                                            .format((((cnt + 1) + ((page - 1) * 25)) * 100) / doujin_counter))
                    self.ui.progress.append("已完成下載：" + six_num)
                    self.ui.is_done.append(six_num)
                    cnt += 1
        self.ui.percent.setText("進度：100%")


def check_web_exist(url):
    request = requests.get(url)
    if request.status_code == 200:
        return True
    else:
        return False


def download_func(doujin_num, i, folder_path):
    r = requests.get(
        "https://i.nhentai.net/galleries/"
        + doujin_num + "/" + str(i) + ".jpg")
    if r.ok:
        path = folder_path + "\\" + str(i) + ".jpg"
        with open(path, 'wb') as f:
            f.write(r.content)
    elif check_web_exist("https://i.nhentai.net/galleries/"
                         + doujin_num + "/" + str(i) + ".png"):
        r = requests.get(
            "https://i.nhentai.net/galleries/"
            + doujin_num + "/" + str(i) + ".png")
        if r.ok:
            path = folder_path + "\\" + str(i) + ".png"
            with open(path, 'wb') as f:
                f.write(r.content)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = AppWindow()
    w.show()
    sys.exit(app.exec_())
