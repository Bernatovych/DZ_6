import os
import re
import shutil
import sys
import datetime

def normalize(name):
    letters = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
               'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
               'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ъ': 'y', 'ы': 'y', 'ь': "'",
               'э': 'e', 'ю': 'yu', 'я': 'ya', 'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
               'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P',
               'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch',
               'Ъ': 'Y', 'Ы': 'Y', 'Ь': "'", 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya', }
    for key in letters:
        name = name.replace(key, letters[key])
    return re.sub(r'\W', '_', name)

def remove_folders(path):
    folders = list(os.walk(path))
    for path, _, _ in folders[::-1]:
        if len(os.listdir(path)) == 0:
            os.rmdir(path)

def rename_exists_files(name):
    return name + '_edit_' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')

def sort(path):
    categories = {'images': ('JPEG', 'PNG', 'JPG', 'SVG'), 'documents': ('DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'),
                  'audio': ('MP3', 'OGG', 'WAV', 'AMR'), 'video': ('AVI', 'MP4', 'MOV', 'MKV'),
                  'archives': ('ZIP', 'GZ', 'TAR')}
    known_extension_list = []
    unown_extension_list = []
    file_log = []
    ignore = []
    for k in categories.keys():
        ignore.append(k)
    for root, dirs, files in os.walk(path, topdown=False):
        dirs[:] = [d for d in dirs if d not in ignore]
        for name in dirs:
            try:
                os.rename(os.path.join(root, name), os.path.join(root, normalize(name)))
            except FileExistsError:
                os.rename(os.path.join(root, name), os.path.join(root, rename_exists_files(normalize(name))))
        for name in files:
            f_name = os.path.splitext(name)[0]
            f_extension = os.path.splitext(name)[1]
            normolazed_f_name = normalize(f_name)
            new_f = normolazed_f_name + f_extension
            try:
                os.rename(os.path.join(root, f_name + f_extension), os.path.join(root, new_f))
            except FileExistsError:
                os.rename(os.path.join(root, f_name + f_extension),
                          os.path.join(root, rename_exists_files(normolazed_f_name + f_extension)))
            extension = os.path.splitext(name)[1].upper().replace('.', '')
            for k, v in categories.items():
                if extension in v and k == 'archives':
                    if extension not in known_extension_list:
                        known_extension_list.append(extension)
                    os.makedirs(path + '/' + k, exist_ok=True)
                    shutil.unpack_archive(os.path.join(root, new_f), path + '/' + k + '/' + os.path.splitext(new_f)[0])
                    files = os.listdir(path + '/' + k + '/' + os.path.splitext(normolazed_f_name)[0])
                    file_log.append({k: ', '.join(files)})
                    os.remove(os.path.join(root, new_f))
                elif extension in v:
                    if extension not in known_extension_list:
                        known_extension_list.append(extension)
                    os.makedirs(path + '/' + k, exist_ok=True)
                    if os.path.exists(os.path.join(path + '/' + k, new_f)):
                        new_f_renamed = rename_exists_files(normolazed_f_name) + f_extension
                        shutil.move(os.path.join(root, new_f), os.path.join(path + '/' + k, new_f_renamed))
                        file_log.append({k: new_f_renamed})
                    else:
                        shutil.move(os.path.join(root, new_f), os.path.join(path + '/' + k, new_f))
                        file_log.append({k: new_f})
                else:
                    if extension not in unown_extension_list:
                        unown_extension_list.append(extension)
    remove_folders(path)
    final_dict = {}
    for i in file_log:
        for k, v in i.items():
            final_dict.setdefault(k, []).append(v)
    print(f'Известные расширения: {known_extension_list}')
    print(f'Неизвестные расширения: {list(set(unown_extension_list) - set(known_extension_list))}')
    for k, v in final_dict.items():
        print(f'-{k}' + '-'*100)
        print(', '.join(v))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Принимает только один аргумент!')
    else:
        if os.path.exists(sys.argv[1]):
            sort(sys.argv[1])
        else:
            print('Неправильный путь!')
