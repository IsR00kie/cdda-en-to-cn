# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
import os
import re
import sys
import json
import gettext
from lib.helper import *

# 导入mo文件数据
zh = gettext.translation("cataclysm-dda", "lang/mo", languages=["zh_CN"])
zh.install()


class CreateDcit(object):
    """
    创建自动翻译字典文件
    """

    def __init__(self, old_mod_path, new_mod_path):
        """
        Arguments:
            old_mod_path {str} -- 已汉化过的mod文件夹
            new_mod_path {str} -- 未汉化过的mod文件夹
        """

        with open(os.path.join(new_mod_path, MODINFO_FILE)) as _file:
            _tmp = json.load(_file)[0]
            self.name = _tmp['name']
            self.__output = os.path.join(PO_DIR, self.name + '.po')
            try:
                self.version = _tmp['version']
            except KeyError:
                print('[-] 未获取到%s项目版本信息. 默认设置为 0.1版本' % self.name)
                self.version = 0.1

        self.__old_all_json_file = []
        self.__new_all_json_file = []
        # 获取JSON文件
        get_all_json_file(old_mod_path, self.__old_all_json_file)
        get_all_json_file(new_mod_path, self.__new_all_json_file)

    @staticmethod
    def en_to_cn(string):
        mo_string = _(string)
        # print('原文:%s\n译文:%s' % (string, mo_string))
        if is_include_chinese(mo_string):
            return mo_string

        return ''

    def update_po_data(self, string):
        result = []
        if isinstance(string, list):
            for s in string:
                result.append({'msgid': s, 'msgstr': self.en_to_cn(s)})
        else:
            result.append({'msgid': string, 'msgstr': self.en_to_cn(string)})
        return result

    @staticmethod
    def deletion_duplicated_sort(data):
        """去重并按照汉化数据排序"""
        msgid_chche = []
        result = {}
        for item in data:
            if item['msgid'] in msgid_chche:
                if item['msgstr'] != '' and result[item['msgid']] == '':
                    result[item['msgid']] = item['msgstr']
                continue
            msgid_chche.append(item['msgid'])
            result[item['msgid']] = item['msgstr']

        print('原始数据长度: %d\n去重后数据长度: %d' % (len(data), len(result)))
        return [{'msgid': key, 'msgstr': result[key]} for key in result.keys()]

    @staticmethod
    def not_id_deletion_duplicated(data):
        """ 移除notid数据重复项 """
        cache = []
        result = []
        for item in data:
            if isinstance(item, list):
                _item = json.dumps(item)
            else:
                _item = item

            if _item in cache:
                continue
            cache.append(_item)
            result.append(item)
        return result

    def run(self):
        dict_data = []
        print('[+] 正在提取文本中.')
        old_strings = get_all_string(self.__old_all_json_file)
        new_strings = get_all_string(self.__new_all_json_file)
        print('[+] 文本提取成功.\n[+] 正在对照翻译中.')

        for string in self.not_id_deletion_duplicated(new_strings[NotId]):
            dict_data += self.update_po_data(string)

        for new_key, new_value in new_strings.items():
            if new_key == NotId:
                continue
            tmp_data = old_strings.get(new_key, {})

            if len(new_value) != 0:
                for _key, _value in new_value.items():
                    dict_data.append({'msgid': _value, 'msgstr': ''})

            for old_key, old_string in tmp_data.items():
                src_string = new_value.get(old_key, None)
                if src_string is None:
                    continue

                if isinstance(src_string, list):
                    dict_data += self.update_po_data(src_string)
                    continue

                mo_string = self.en_to_cn(src_string)

                # 匹配任意中文.
                if not (is_include_chinese(old_string) or is_include_chinese(mo_string)):
                    dict_data.append({'msgid': src_string, 'msgstr': ''})
                    continue

                if is_include_chinese(mo_string):
                    dict_data.append(
                        {'msgid': src_string, 'msgstr': mo_string})
                    continue

                if is_include_chinese(old_string):
                    dict_data.append(
                        {'msgid': src_string, 'msgstr': old_string})
                    continue
                dict_data.append({'msgid': src_string, 'msgstr': ''})

        dict_data = self.deletion_duplicated_sort(dict_data)
        print('[+] 数据写出到: %s' % self.__output)
        with open(self.__output, 'w', encoding='utf8') as _file:
            timestamp = time.strftime('%Y-%m-%d %H:%M%z')
            encoding = 'UTF-8'
            print(pot_header % {'time': timestamp, 'version': self.version,
                                'charset': encoding,
                                'encoding': '8bit', 'packname': self.name}, file=_file)
            for line in dict_data:
                # print(line)
                for key, value in line.items():
                    _file.write('%s %s\n' % (key, str_to_po_str(value)))
                _file.write('\n')
