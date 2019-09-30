# -*- coding: utf-8 -*-
"""
CDDA 自动翻译帮助库
全局变量定义
"""

from __future__ import print_function
from __future__ import unicode_literals

from io import open
import os
import json
import re
import time
import sys

if sys.version > '3':
	PY3 = True
else:
	PY3 = False


ROOK_DIR = os.path.abspath(os.getcwd())
LANG_DIR = os.path.join(ROOK_DIR, 'lang')
MO_DIR = os.path.join(LANG_DIR, 'mo')
PO_DIR = os.path.join(LANG_DIR, 'po')
MODINFO_FILE = 'modinfo.json'
NotId = 'Notid'

def is_include_chinese(string):
    """检测字符串中是否包含中文字符
        
    Arguments:
        string {str} -- 需要检查的字符串
    
    Returns:
        bool -- 包含中文返回True. 不包含中文返回False
    """
    if PY3:
        return re.search('[\u4e00-\u9fa5]', string) is not None
    else:
        return re.search('[\u4e00-\u9fa5]', string.decode('utf8')) is not None


def get_all_json_file(path, files):
    """遍历获取全部JSON文件
    
    Arguments:
        path {src} -- 需要遍历获取JSON文件的路径
        files {list} -- 获取到的JSON文件结果列表
    """
    for json_file in os.listdir(path):
        json_file = os.path.join(path, json_file)
        if os.path.isdir(json_file):
            get_all_json_file(json_file, files)
        else:
            if os.path.splitext(json_file)[1] == '.json':
                files.append(json_file)


def get_string(file, strings):
    """从JSON文件中提取所有需要汉化的字符串
    
    Arguments:
        file {str} -- JSON文件
        string {dict} -- 存放获取到的字符串
    """
    with open(file, 'r', encoding='utf8') as _file:
        items = json.loads(_file.read())

        for item in items:
            type = item['type']
            if type in ignorable:
                # 不需要翻译的数据
                continue

            _id = item.get('id', NotId)
            if _id != NotId:
                strings[_id] = {}
            if type in automatically_convertible:
                for type in auto_string:
                    string = item.get(type, None)
                    if string is None:
                        continue
                    if NotId == _id:
                        strings[NotId].append(string)
                        continue
                    strings[_id][type] = string


def get_all_string(files):
    """获取全部JSON文件中需要翻译的字符串
    
    Arguments:
        files {list} -- JSON文件列表
    
    Returns:
        list -- 获取到的json文件数据
    """
    strings = {NotId: []}
    for file_name in files:
        get_string(file_name, strings)
    return strings


def str_to_po_str(string):
    """字符串转po字符串
    
    Arguments:
        string {str}} -- str
    """
    if string == '':
        return '""'
    if '\n' in string:
        tmp = ''
        for s in string.split('\n'):
            tmp += '"%s\\n"\n' % s.replace('"', r'\"')
            string = '\n%s' % tmp
            string = '""\n%s""' % tmp
    else:
        string = '"%s"' % string.replace('"', r'\"')

    return string


pot_header = '''\
# SOME DESCRIPTIVE TITLE.
# Copyright (C) YEAR ORGANIZATION
# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.
#
msgid ""
msgstr ""
"Project-Id-Version: PACKAGE VERSION\\n"
"POT-Creation-Date: %(time)s\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
"Language-Team: Chinese (China) (https://cdda-base.github.io/mainpage-cn/index.html)\\n"
"Language: zh_CN\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=%(charset)s\\n"
"Content-Transfer-Encoding: %(encoding)s\\n"
"Generated-By: %(version)s\\n"

'''


# 这些对象可以自动提取其字符串
# these objects can have their strings automatically extracted.
# 在这里插入对象类型
# insert object "type" here IF AND ONLY IF
# 他们所有可以翻译的字符串均采用一下格式
# all of their translatable strings are in the following form:
#   "name" member
#   "description" member
#   "name_plural" member
#   "text" member
#   "sound" member
#   "messages" member containing an array of translatable strings


auto_string = {
    'name',
    'description',
    'name_plural',
    'text',
    'sound',
    'messages'
}

automatically_convertible = {
    "activity_type",
    "AMMO",
    "ammunition_type",
    "ARMOR",
    "BATTERY",
    "bionic",
    "BIONIC_ITEM",
    "BOOK",
    "COMESTIBLE",
    "construction_category",
    "CONTAINER",
    "dream",
    "ENGINE",
    "epilogue",
    "faction",
    "fault",
    "furniture",
    "GENERIC",
    "item_action",
    "ITEM_CATEGORY",
    "json_flag",
    "keybinding",
    "MAGAZINE",
    "map_extra",
    "MOD_INFO",
    "MONSTER",
    "morale_type",
    "morale_type",
    "npc",
    "npc_class",
    "overmap_land_use_code",
    "overmap_terrain",
    "PET_ARMOR",
    "score",
    "skill",
    "snippet",
    "speech",
    "SPELL",
    "start_location",
    "STATIONARY_ITEM",
    "terrain",
    "TOOL",
    "TOOLMOD",
    "TOOL_ARMOR",
    "tool_quality",
    "tutorial_messages",
    "VAR_VEH_PART",
    "vehicle",
    "vehicle_part",
    "vitamin",
    "WHEEL",
    "help"
}


# 这些对象没有可翻译字符串
# these objects have no translatable strings
ignorable = {
    "behavior",
    "BULLET_PULLING",
    "city_building",
    "colordef",
    "emit",
    "enchantment",
    "event_transformation",
    "event_statistic",
    "EXTERNAL_OPTION",
    "GAME_OPTION",
    "ITEM_BLACKLIST",
    "item_group",
    "ITEM_OPTION",
    "ITEM_WHITELIST",
    "MIGRATION",
    "mod_tileset",
    "monitems",
    "monster_adjustment",
    "MONSTER_BLACKLIST",
    "MONSTER_FACTION",
    "monstergroup",
    "MONSTER_WHITELIST",
    "mutation_type",
    "obsolete_terrain",
    "overlay_order",
    "overmap_connection",
    "overmap_location",
    "overmap_special",
    "profession_item_substitutions",
    "palette",
    "region_overlay",
    "region_settings",
    "requirement",
    "rotatable_symbol",
    "skill_boost",
    "SPECIES",
    "trait_group",
    "uncraft",
    "vehicle_group",
    "vehicle_placement",
    "WORLD_OPTION",
    "enchantment"
}
