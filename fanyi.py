# -*- coding: utf-8 -*-

"""
CDDA MOD 自动提取string 并且 对照翻译
"""
from __future__ import unicode_literals
from __future__ import print_function

import os
import re
import copy
import json
import gettext
from lib.helper import *
from lib.create_dict import CreateDcit
from io import open
if PY3:
    import sys
else:
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')


def help():
    print('%s <opt>' % sys.argv[0])
    print('\t-i <已汉化过的mod文件路径> <准备汉化的MOD文件地址>\n\t\t自动创建对应的MOD翻译文件. 如果填写一样的地址.那么将只使用mo文件进行自动翻译')
    print('\t-d <准备汉化的MOD文件地址>\n\t\t记得备份MOD文件......导出汉化数据. 发布和测试汉化使用这个. 会自动修改mod对应的json文件')


def en_to_cn(string):
    # print('原文:%s\n译文:%s' % (string, _(string)))
    return _(string)


def get_mo_data(string):
    result = []
    if isinstance(string, list):
        return [en_to_cn(s) for s in string]
    return en_to_cn(string)


def dump(lang_path, mod_path):
    packname = os.path.splitext(lang_path)[0].split('/')[-1]
    print('[+] 准备汉化 %s 项目中. ' % packname)

    if not os.path.exists(lang_path):
        print('[-] %s 没有这个mod的汉化数据\n请使用-i命令建立对应数据' % mod_name)
        return
    
    # 导入mo文件数据
    mo_file_name = './lang/mo/zh_CN/LC_MESSAGES/%s.mo' % packname
    if PY3:
        command_line = 'python3 lib/msgfmt_py3.py -o "%s" "%s"' % (mo_file_name, lang_path)
    else:
        command_line = 'python2 lib/msgfmt_py2.py -o "%s" "%s"' % (mo_file_name, lang_path)
    print(command_line)
    os.system(command_line)

    zh = gettext.translation(packname, "lang/mo", languages=["zh_CN"])
    zh.install()

    if not os.path.exists(mo_file_name):
        print('[-] 生成mo文件失败. 请联系: 开发人员')
        return

    all_json_file = []
    get_all_json_file(mod_path, all_json_file)
    # strings=get_all_string(all_json_file)
    for path in all_json_file:
        with open(path, 'r', encoding='utf8') as _file:
            items = json.load(_file)

        new_items = copy.copy(items)
        for i, _ in enumerate(items):
            _type = items[i]['type']
            if _type in ignorable:
                # 不需要翻译的数据
                continue

            if _type in automatically_convertible:
                for type in auto_string:
                    string = items[i].get(type, None)
                    if string is None:
                        continue
                    new_items[i][type] = get_mo_data(string)

        with open(path, 'w', encoding='utf8') as _file:
            _file.write(json.dumps(new_items , ensure_ascii=False, indent=4, separators=(', ', ': ')))
    print('[+] 项目: %s 汉化成功. ' % packname)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        help()
        exit(-1)
        
    if not os.path.exists(PO_DIR):
        os.makedirs(PO_DIR)

    if '-i' == sys.argv[1]:
        if len(sys.argv) < 4:
            help()
            exit(-1)
        CreateDcit(sys.argv[2], sys.argv[3]).run()
    elif '-d' == sys.argv[1]:
        with open(os.path.join(sys.argv[2], MODINFO_FILE), 'r', encoding='utf8') as _file:
            mo_path = os.path.join(os.path.join(ROOK_DIR, PO_DIR), json.load(_file)[0]['name'] + '.po')
        dump(mo_path, sys.argv[2])
    else:
        help()
        exit(-1)
