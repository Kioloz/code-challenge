import re
import sys

import requests


def get_args():
    try:
        month, year, res = sys.argv[1:]
    except ValueError:
        print('Неверное колличество аргументов')
        exit()
    if re.match('^0[1-9]{1}|1[012]{1}$', month):
        if re.match('(19|20)\d\d$', year):
            if not re.match('^[1-9][0-9]{2,3}x[1-9][0-9]{2,3}$', res):
                print('Неверный формат разрешения')
                exit()
        else:
            print('Неверный формат года')
            exit()
        month = int(month) - 1
        if 0 < month < 10:
            month = '0{}'.format(str(month))
        elif month == 0:
            month = '12'
    else:
        print('Неверный формат месяца')
        exit()
    return month, year, res


def find_publication(month, year):
    regex = r"www.smashingmagazine.com\/{}\/{}\/([^/]+)".format(year, month)
    page = 1
    print('Получение публикации')
    while True:
        try:
            response = requests.get(
                "https://www.smashingmagazine.com/tag/wallpapers/page/{}/".format(page))
        except requests.exceptions.RequestException:
            print('Не удалось соедениться с smashingmagazine.com')
            exit()
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            print('Публикаций не найдено')
            exit()
        publication = re.findall(regex, response.text)
        if publication:
            link = "https://www.smashingmagazine.com/{}/{}/{}/".format(
                year, month, publication[0])
            return link
        else:
            page += 1
            continue


def get_pictures(link, res):
    print('Поиск изображений')
    try:
        response = requests.get(link, allow_redirects=False)
    except requests.exceptions.RequestException:
        print('Не удалось получить публикацию')
        exit()
    regex = r"http[s]?:\/\/files\.smashingmagazine\.com\/wallpapers\/\S+{}\.(?:jpg|png)".format(
        res)
    if response.status_code == 301:
        print('Публикация устарела')
        exit()
    else:
        links = set(re.findall(regex, response.text))
        saved_images = 0
        if len(links) > 0:
            for link in links:
                filename = link.split("/")[-1]
                try:
                    r = requests.get(link)
                except requests.exceptions.RequestException:
                    print('Не удалось получить изображение {}'.format(filename))
                    continue
                if r.status_code == 200:
                    with open(filename, 'wb') as f:
                        print('Скачивается {}'.format(filename))
                        f.write(r.content)
                        saved_images += 1
            print('Скачено {}'.format(saved_images))
        else:
            print('Изображений в данном разрешении не найдено')
            exit()


if __name__ == "__main__":
    try:
        month, year, res = get_args()
        link = find_publication(month, year)
        get_pictures(link, res)
    except KeyboardInterrupt:
        print('Остановлено по требованию')
        exit()
