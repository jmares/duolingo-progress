import logging
import duolingoapi
# Had to stop using duolingo-api becuase Duolingo removed 'points_rank' from api, 
# which resulted in error. Am no longer using pypi package, but downloaded the file
# from GitHub and removed 'points_rank' [https://github.com/KartikTalwar/Duolingo/blob/master/duolingo.py](https://github.com/KartikTalwar/Duolingo/blob/master/duolingo.py)
import sqlite3
import sys
from datetime import datetime, date
from time import time

class DLImport:


    def __init__(self, db_file, dl_name, dl_pwd):
        self.__dl_langs = []
        self.__db_langs = []
        self.__db_data = {}
        self.__dl_data = {}
        self.__db_status = {}

        this_function = self.__class__.__name__ + '.' + sys._getframe().f_code.co_name
        logging.info(f"{this_function}: start")

        try:
            self.__lingo = duolingoapi.Duolingo(dl_name, password=dl_pwd)
            logging.debug(f"{this_function}: connected to duolingo")
        except Exception as e:
            msg = f"{this_function}: could not connect to duolingo - {e}"
            logging.critical(msg)
            raise Exception(msg)

        try:
            self.__dbc = sqlite3.connect(db_file)
            cur = self.__dbc.cursor()
            logging.debug(f"{this_function}: connected to database")
        except Exception as e:
            msg = f"{this_function}: could not connect to database - {e}"
            logging.critical(msg)
            raise Exception(msg)


    def import_duo(self):
        this_function = self.__class__.__name__ + '.' + sys._getframe().f_code.co_name
        logging.info(f"{this_function}: start")

        try:
            self.__get_dl_langs()
            self.__get_db_langs()
            self.__compare_langs()
            self.__import_dl_langs()
            self.__update_db_data()
            self.__get_db_status()
            self.__compare_lang_status()
        except Exception as e:
            msg = f"{this_function}: {e}"
            logging.error(msg)
            raise Exception(msg)


    def __get_dl_langs(self):
        this_function = self.__class__.__name__ + '.' + sys._getframe().f_code.co_name
        logging.info(f"{this_function}: start")

        try:
            self.__dl_langs = self.__lingo.get_languages(abbreviations=True)
        except Exception as e:
            msg = f"{this_function}: {e}"
            logging.error(msg)
            raise Exception(msg)


    def __get_db_langs(self):
        this_function = self.__class__.__name__ + '.' + sys._getframe().f_code.co_name
        logging.info(f"{this_function}: start")

        try:
            crs = self.__dbc.cursor()
        except Exception as e:
            msg = f"{this_function} failed to connect to database: {e}"
            logging.error(msg)
            raise Exception(msg)

        try:
            sql = '''SELECT id FROM duo_langs'''
            crs.execute(sql)
            langs = crs.fetchall()
            for lang in langs:
                self.__db_langs.append(lang[0])
        except Exception as e:
            msg = f"{this_function}: {e}"
            logging.error(msg)
            raise Exception(msg)

        crs.close()


    def __compare_langs(self):
        this_function = self.__class__.__name__ + '.' + sys._getframe().f_code.co_name
        logging.info(f"{this_function}: start")

        try:
            for abbr in self.__dl_langs:
                if abbr not in self.__db_langs:
                    self.__add_language(abbr)
        except Exception as e:
            msg = f"{this_function}: {e}"
            logging.error(msg)
            raise Exception(msg)


    def __add_language(self, abbr):
        this_function = self.__class__.__name__ + '.' + sys._getframe().f_code.co_name
        logging.info(f"{this_function}: start")
        sql = '''INSERT INTO duo_langs (id, lang, taal) VALUES (?,?,?)'''
        lang = self.__lingo.get_language_from_abbr(abbr)

        try:
            crs = self.__dbc.cursor()
        except Exception as e:
            msg = f"{this_function} failed to connect to database: {e}"
            logging.error(msg)
            raise Exception(msg)

        try:
            crs.execute(sql, (abbr, lang, lang))
            self.__dbc.commit()
        except Exception as e:
            msg = f"{this_function}: {e}"
            logging.error(msg)
            raise Exception(msg)

        crs.close()


    def __import_dl_langs(self):
        this_function = self.__class__.__name__ + '.' + sys._getframe().f_code.co_name
        logging.info(f"{this_function}: start")

        try:
            for l in self.__dl_langs:
                self.__dl_data[l] = self.__lingo.get_language_progress(l)
        except Exception as e:
            msg = f"{this_function}: {e}"
            logging.error(msg)
            raise Exception(msg)


    def __update_db_data(self):

        this_function = self.__class__.__name__ + '.' + sys._getframe().f_code.co_name
        logging.info(f"{this_function}: start")
        res = True
        now = datetime.now()
        day = now.strftime('%Y-%m-%d')

        try:
            crs = self.__dbc.cursor()
        except Exception as e:
            msg = f"{this_function} failed to connect to database: {e}"
            logging.error(msg)
            raise Exception(msg)

# As 2021-12-04 'points_rank' was no longer available from Duolingo API
#        sql ='''REPLACE INTO duo_data (id, date, points, level, level_progress,
#            level_percent, level_points, level_left, next_level,
#            num_skills_learned, points_rank)
#            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

        sql ='''REPLACE INTO duo_data (id, date, points, level, level_progress,
            level_percent, level_points, level_left, next_level,
            num_skills_learned)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

        for key in self.__dl_data:
            try:
                dld = self.__dl_data[key]
# As 2021-12-04 'points_rank' was no longer available
#                crs.execute(sql,
#                    (key, day, dld["points"], dld["level"],
#                    dld["level_progress"], dld["level_percent"],
#                    dld["level_points"], dld["level_left"],
#                    dld["next_level"], dld["num_skills_learned"],
#                    dld["points_rank"]))
                crs.execute(sql,
                    (key, day, dld["points"], dld["level"],
                    dld["level_progress"], dld["level_percent"],
                    dld["level_points"], dld["level_left"],
                    dld["next_level"], dld["num_skills_learned"]))
                self.__dbc.commit()
            except Exception as e:
                msg = f"{this_function} - language {key}: {e}"
                logging.error(msg)
                raise Exception(msg)

        crs.close()


    def __get_db_status(self):
        this_function = self.__class__.__name__ + '.' + sys._getframe().f_code.co_name
        logging.info(f"{this_function}: start")

        try:
            self.__dbc.row_factory = sqlite3.Row
            crs = self.__dbc.cursor()
        except Exception as e:
            msg = f"{this_function} failed to connect to database: {e}"
            logging.error(msg)
            raise Exception(msg)

        try:
            sql = '''SELECT * FROM duo_status ORDER BY points DESC'''
            crs.execute(sql)
            langs = crs.fetchall()
            if not langs:
                self.__db_status = {}
            else:
                for lang in langs:
                    d =  dict(lang)
                    self.__db_status[d["id"]] = d
        except Exception as e:
            msg = f"{this_function}: {e}"
            logging.error(msg)
            raise Exception(msg)

        crs.close()


    def __compare_lang_status(self):
        this_function = self.__class__.__name__ + '.' + sys._getframe().f_code.co_name
        logging.info(f"{this_function}: start")
        currday = date.today()
        currdaystr = date.today().isoformat()

        try:
            langs =  self.__dl_data
            for key in langs:
                lang = langs[key]
                if (not self.__db_status or key not in self.__db_status):
# As 2021-12-04 'points_rank' was no longer available from Duolingo API
#                    sql = '''REPLACE INTO duo_status (id, points, level,
#                        level_progress, level_percent, level_points, level_left,
#                        next_level, num_skills_learned, points_rank, streak_start,
#                        streak_end)
#                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
#                    lst = (key, lang["points"], lang["level"], lang["level_progress"],
#                        lang["level_percent"], lang["level_points"], lang["level_left"],
#                        lang["next_level"], lang["num_skills_learned"],
#                        lang["points_rank"], currday, currday)
                    sql = '''REPLACE INTO duo_status (id, points, level,
                        level_progress, level_percent, level_points, level_left,
                        next_level, num_skills_learned, streak_start,
                        streak_end)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
                    lst = (key, lang["points"], lang["level"], lang["level_progress"],
                        lang["level_percent"], lang["level_points"], lang["level_left"],
                        lang["next_level"], lang["num_skills_learned"],
                        currday, currday)
                    self.__update_lang_status(sql, lst)
                elif (lang["points"] != self.__db_status[key]["points"]):
                    strklst = self.__db_status[key]["streak_end"].split('-')
                    streakend = date(int(strklst[0]), int(strklst[1]), int(strklst[2]))
                    delta = (currday - streakend).days

                    if (delta > 1):
                        # streak was discontinued, first day of new streak
# As 2021-12-04 'points_rank' was no longer available from Duolingo API
#                        sql = '''REPLACE INTO duo_status (id, points, level,
#                            level_progress, level_percent, level_points,
#                            level_left, next_level, num_skills_learned,
#                            points_rank, streak_start, streak_end)
#                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
#                        lst = (key, lang["points"], lang["level"],
#                            lang["level_progress"], lang["level_percent"],
#                            lang["level_points"], lang["level_left"],
#                            lang["next_level"], lang["num_skills_learned"],
#                            lang["points_rank"], currdaystr, currdaystr)
                        sql = '''REPLACE INTO duo_status (id, points, level,
                            level_progress, level_percent, level_points,
                            level_left, next_level, num_skills_learned,
                            streak_start, streak_end)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
                        lst = (key, lang["points"], lang["level"],
                            lang["level_progress"], lang["level_percent"],
                            lang["level_points"], lang["level_left"],
                            lang["next_level"], lang["num_skills_learned"],
                            currdaystr, currdaystr)
                        self.__update_lang_status(sql, lst)
                    else:
                        # streak continues, streak_start doesn't change
#                        sql = '''REPLACE INTO duo_status (id, points, level,
#                            level_progress, level_percent, level_points,
#                            level_left, next_level, num_skills_learned,
#                            points_rank, streak_start, streak_end)
#                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
#                        lst = (key, lang["points"], lang["level"],
#                            lang["level_progress"], lang["level_percent"],
#                            lang["level_points"], lang["level_left"],
#                            lang["next_level"], lang["num_skills_learned"],
#                            lang["points_rank"],
#                            self.__db_status[key]["streak_start"],
#                            currdaystr)
                        sql = '''REPLACE INTO duo_status (id, points, level,
                            level_progress, level_percent, level_points,
                            level_left, next_level, num_skills_learned,
                            streak_start, streak_end)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
                        lst = (key, lang["points"], lang["level"],
                            lang["level_progress"], lang["level_percent"],
                            lang["level_points"], lang["level_left"],
                            lang["next_level"], lang["num_skills_learned"],
                            self.__db_status[key]["streak_start"],
                            currdaystr)
                        self.__update_lang_status(sql, lst)
            else:
                    # doe voorlopig niks
                    # moet iets misgelopen zijn
                    pi = 3.14
        except Exception as e:
            msg = f"{this_function}: {e}"
            logging.error(msg)
            raise Exception(msg)


    def __update_lang_status(self, sql, lst):
        this_function = self.__class__.__name__ + '.' + sys._getframe().f_code.co_name
        logging.info(f"{this_function}: start")

        try:
            crs = self.__dbc.cursor()
        except Exception as e:
            msg = f"{this_function} failed to connect to database: {e}"
            logging.error(msg)
            raise Exception(msg)

        try:
            crs.execute(sql, lst)
            self.__dbc.commit()
        except Exception as e:
            msg = f"{this_function}: {e}"
            logging.error(msg)
            raise Exception(msg)

        crs.close()


    def export_html(self, template, destination):
        this_function = self.__class__.__name__ + '.' + sys._getframe().f_code.co_name
        logging.info(f"{this_function}: start")
        table = ''

        try:
            crs = self.__dbc.cursor()
        except Exception as e:
            msg = f"{this_function} failed to connect to database: {e}"
            logging.error(msg)
            raise Exception(msg)

        sql = '''SELECT l.lang, s.level, s.points, s.streak_start, s.streak_end,
                        s.level_percent, s.num_skills_learned
                FROM duo_status AS s INNER JOIN duo_langs AS l ON l.id = s.id
                ORDER BY level DESC, points DESC '''

        try:
            crs.execute(sql)
            for row in crs:
                #print(row)
                start_l = str(row[3]).split('-')
                end_l = str(row[4]).split('-')
                start_d = date(int(start_l[0]), int(start_l[1]), int(start_l[2]))
                end_d = date(int(end_l[0]), int(end_l[1]), int(end_l[2]))
                streak = (end_d - start_d).days + 1
                table += '  <tr>\n'
                #table += '    <td>'+ str(row[0].encode('utf-8')) +'</td>'
                table += '    <td>'+ str(row[0]) +'</td>'
                table += '    <td>'+ str(row[1]) +'</td>'
                table += '    <td>'+ str(row[2]) +'</td>'
                table += '    <td>'+ str(row[5]) +'&#37;</td>'
                table += '    <td>'+ str(row[6]) +'</td>'
                table += '    <td>'+ str(streak) +'</td>'
                table += '    <td>'+ str(row[4]) +'</td>'
                table += '  </tr>\n'
        except Exception as e:
            msg = f"{this_function}: {e}"
            logging.error(msg)
            raise Exception(msg)

        now = datetime.now()
        last_update = 'Last update: ' + now.strftime('%d/%m/%Y %H:%M')
        try:
            ftemp = open(template, 'r')
            html = ftemp.read()
            html = html.replace('<!-- insert_data -->', table)
            html = html.replace('<!-- insert_update -->', last_update)
            fpage = open(destination, 'w')
            fpage.write(html)
            ftemp.close()
            fpage.close()
        except Exception as e:
            msg = f"{this_function}: {e}"


    def __del__(self):
        this_function = self.__class__.__name__ + '.' + sys._getframe().f_code.co_name
        logging.info(f"{this_function}: start")

        self.__dbc.close()

