import os
import re
import shutil
import sys
import datetime


LETTERS = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
           'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
           'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ъ': 'y', 'ы': 'y', 'ь': "'",
           'э': 'e', 'ю': 'yu', 'я': 'ya', 'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
           'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P',
           'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch',
           'Ъ': 'Y', 'Ы': 'Y', 'Ь': "'", 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya', }

CATEGORIES = {'images': ('JPEG', 'PNG', 'JPG', 'SVG'), 'documents': ('DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'),
              'audio': ('MP3', 'OGG', 'WAV', 'AMR'), 'video': ('AVI', 'MP4', 'MOV', 'MKV'), 'archives': ('ZIP', 'GZ', 'TAR')}

file_log = []
known_extension_list = []
unown_extension_list = []


def folder_p(path):
    global base_path
    base_path = path
    return sort(path)


def rename_exists_files(name):
    return name + '_edit_' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')


def normalize(name):
    for key in LETTERS:
        name = name.replace(key, LETTERS[key])
    return re.sub(r'\W', '_', name)


def ignore_list():
    ignore = []
    for k in CATEGORIES.keys():
        ignore.append(k)
    return ignore


def remove_folders(path):
    folders = list(os.walk(path))
    for path, _, _ in folders[::-1]:
        if len(os.listdir(path)) == 0:
            os.rmdir(path)


def log():
    final_dict = {}
    for i in file_log:
        for k, v in i.items():
            final_dict.setdefault(k, []).append(v)
    for k, v in final_dict.items():
        print(f'-{k}' + '-' * 100)
        print(', '.join(v))
    print(f'Известные расширения: {known_extension_list}')
    print(f'Неизвестные расширения: {list(set(unown_extension_list) - set(known_extension_list))}')


def move(file_path):
    dirname, fname = os.path.split(file_path)
    extension = os.path.splitext(fname)[1].upper().replace('.', '')
    for k, v in CATEGORIES.items():
        if extension in v and k == 'archives':
            if extension not in known_extension_list:
                known_extension_list.append(extension)
            os.makedirs(base_path + '/' + k, exist_ok=True)
            shutil.unpack_archive(os.path.join(file_path), base_path + '/' + k + '/' + os.path.splitext(fname)[0])
            files = os.listdir(base_path + '/' + k + '/' + os.path.splitext(fname)[0])
            file_log.append({k: ', '.join(files)})
            os.remove(os.path.join(file_path))
        elif extension in v:
            if extension not in known_extension_list:
                known_extension_list.append(extension)
            os.makedirs(base_path + '/' + k, exist_ok=True)
            if os.path.exists(os.path.join(base_path + '/' + k, fname)):
                new_f_renamed = rename_exists_files(os.path.splitext(fname)[0]) + os.path.splitext(fname)[1]
                shutil.move(os.path.join(file_path), os.path.join(base_path + '/' + k, new_f_renamed))
                file_log.append({k: new_f_renamed})
            else:
                shutil.move(os.path.join(file_path), os.path.join(base_path + '/' + k, fname))
                file_log.append({k: fname})
        else:
            if extension not in unown_extension_list:
                unown_extension_list.append(extension)


def sort(path):
    subfolders = []
    files = []
    ignore = ignore_list()
    for i in os.scandir(path):
        if i.is_dir():
            if i.name not in ignore:
                old_path = os.path.dirname(i.path)
                new_name = normalize(i.name)
                os.rename(os.path.join(old_path, i.name), os.path.join(old_path, new_name))
                subfolders.append(os.path.join(old_path, new_name))
        if i.is_file():
            name = os.path.splitext(i.name)[0]
            extension = os.path.splitext(i.name)[1]
            new_name = normalize(name) + extension
            old_path = os.path.dirname(i.path)
            os.rename(os.path.join(old_path, i.name), os.path.join(old_path, new_name))
            files.append(os.path.join(old_path, new_name))
            move(os.path.join(old_path, new_name))
    for dir in list(subfolders):
        sf, i = sort(dir)
        subfolders.extend(sf)
        files.extend(i)
    return subfolders, files


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Принимает только один аргумент!')
    else:
        if os.path.exists(sys.argv[1]):
            folder_p(sys.argv[1])
            remove_folders(base_path)
            log()
        else:
            print('Неправильный путь!')
