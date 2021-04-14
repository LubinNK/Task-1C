import itertools
import bisect

# Создал бинарные файлы и записал туда закодированные строки для самопроверки методов diff и recover
file1 = "orig11.bin"
file2 = "update11.bin"

f = open(file1, 'wb')
f.write(bytes('Trip', 'utf8'))
f.close()

f = open(file2, 'wb')
f.write(bytes('triip', 'utf8'))
f.close()


def diff(file1, file2):
    # Открываем файлы
    with open(file1, 'br') as of1, open(file2, 'br') as of2:
        orig = of1.read()
        upd = of2.read()

    # Создаем словарь (элементы - позиции) для оригинала
    orig_matchlist = {}
    for index, elem in enumerate(orig):
        indexes = orig_matchlist.setdefault(elem, [])
        indexes.append(index)
        orig_matchlist[elem] = indexes

    # Ищем longest common sequense по алгоритму Ханта-Шуманского
    upd_length, orig_length = len(upd), len(orig)
    min_length = min(upd_length, orig_length)
    temp_list = list(itertools.repeat(orig_length, min_length + 1))
    lcs = dict()
    temp_list[0] = -1
    temp = 0
    list_of_orig = []  # Сюда будем записывать индексы из оргинала, которые попали в lcs
    list_of_upd = []  # Сюда будем записывать индексы из измененного, которые попали в lcs

    for upd_index, upd_elem in enumerate(upd):

        orig_indexes = orig_matchlist.get(upd_elem, [])

        for orig_index in reversed(orig_indexes):

            pos_start = bisect.bisect_left(temp_list, orig_index, 1, temp)
            pos_end = bisect.bisect_right(temp_list, orig_index, pos_start, temp)
            prev = -1

            for pos in range(pos_start, pos_end + 2):

                if temp_list[pos - 1] < orig_index and orig_index < temp_list[pos]:
                    temp_list[pos] = orig_index
                    lcs[pos] = (orig_index, upd_elem, upd_index)
                    list_of_orig.append(orig_index)
                    list_of_upd.append(upd_index)

                if pos > temp:
                    temp = pos

    deleted_from_orig = list(set(range(len(orig))) - set(list_of_orig))  # Список удаленных из оригинала
    new_elems = list(set(range(len(upd))) - set(list_of_upd))  # Список появившихся элементов

    del_from_orig = dict()  # Словарь для удаленных из оргинала (позиция - элемент)
    for elem in deleted_from_orig:
        del_from_orig[elem] = orig.decode('utf8')[elem]

    new_in_file = dict()  # Словарь для новых элементов в файле (позиция - элемент)
    for elem in new_elems:
        new_in_file[elem] = upd.decode("utf8")[elem]

    # занесем все в difference, затем можно записать этот дифф в другой файл, если очень хочется
    difference = [del_from_orig, new_in_file]

    return difference


def recover(file1, difference):
    # Берем из difference словарь удаленнных и новых элементов
    del_from_orig = difference[0]
    new_in_file = difference[1]

    # Открываем оригинал
    with open(file1, 'br') as of1:
        orig_n = of1.read()

    # Раскодируем его для выполнения исправлений
    orig_n = orig_n.decode('utf8')

    # Исправляем файл
    orig_n = list(orig_n)
    for i in del_from_orig:
        orig_n[i] = ""
    for key in new_in_file:
        orig_n.insert(key, new_in_file[key])
    orig_n = "".join(orig_n)

    # Создаем новое имя восстановленного файла и записываем туда измененный вариант
    recovered_file = 'recovered.bin'
    f = open(recovered_file, 'wb')
    f.write(bytes(orig_n, 'utf8'))
    f.close()

    # Результат будет в файле, так что вернем название файла, куда мы их записали

    return recovered_file, orig_n
