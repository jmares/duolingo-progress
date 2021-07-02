import logging
import duolingo
import sqlite3
from datetime import datetime, date
from time import time

class DLImport:

# --------------------------------------------------

    def __init__(self, db_file, dl_name, dl_pwd):
        self.__dl_langs = []
        self.__db_langs = []
        self.__db_data = {}
        self.__dl_data = {}
        self.__db_status = {}

        try:
            self.__lingo = duolingo.Duolingo(dl_name, password=dl_pwd)
            logging.debug('connected to duolingo')
        except:
            logging.critical('could not connect to duolingo')
            raise Exception('Could not connect to duolingo')

        try:
            self.__dbc = sqlite3.connect(db_file)
            cur = self.__dbc.cursor()
            logging.debug('connected to database')
        except:
            logging.critical('could not connect to database')
            raise Exception('Could not connect to database')

# --------------------------------------------------

    def import_duo(self):
        orig = "import_duo"
        try:
            self.__get_dl_langs()
            self.__get_db_langs()
            self.__compare_langs()
            self.__import_dl_langs()
            self.__update_db_data()
            self.__get_db_status()
            self.__compare_lang_status()
        except Exception as e:
            mess = orig + ' - ' + str(e)
            logging.error(mess)
            raise Exception(mess)

# --------------------------------------------------

    def __get_dl_langs(self):
        orig = "get_dl_langs"
        try:
            self.__dl_langs = self.__lingo.get_languages(abbreviations=True)
        except Exception as e:
            mess = orig + ' - ' + str(e)
            logging.error(mess)
            raise Exception(mess)

# --------------------------------------------------

    def __get_db_langs(self):
        orig ='get_langs_db'

        try:
            crs = self.__dbc.cursor()
        except Exception as e:
            mess = orig + ' failed to connect to database: ' + str(e)
            logging.error(mess)
            raise Exception(mess)

        try:
            sql = '''SELECT id FROM duo_langs'''
            crs.execute(sql)
            langs = crs.fetchall()
            #res = list()
            for lang in langs:
                self.__db_langs.append(lang[0])
        except Exception as e:
            mess = orig + ' - ' + str(e)
            logging.error(mess)
            raise Exception(mess)

        crs.close()

# --------------------------------------------------

    def __compare_langs(self):
        orig ='compare_langs'
        try:
            for abbr in self.__dl_langs:
                if abbr not in self.__db_langs:
                    self.__add_language(abbr)
        except Exception as e:
            mess = orig + ' - ' + str(e)
            logging.error(mess)
            raise Exception(mess)

# --------------------------------------------------

    def __add_language(self, abbr):
        orig ='add_language'
        sql = '''INSERT INTO duo_langs (id, lang, taal) VALUES (?,?,?)'''
        lang = self.__lingo.get_language_from_abbr(abbr)

        try:
            crs = self.__dbc.cursor()
        except Exception as e:
            mess = orig + ' failed to connect to database: ' + str(e)
            logging.error(mess)
            raise Exception(mess)

        try:
            crs.execute(sql, (abbr, lang, lang))
            self.__dbc.commit()
        except Exception as e:
            mess = orig + ' - ' + str(e)
            logging.error(mess)
            raise Exception(mess)

        crs.close()

# --------------------------------------------------

    def __import_dl_langs(self):
        orig ='import_dl_langs'

        try:
            for l in self.__dl_langs:
                self.__dl_data[l] = self.__lingo.get_language_progress(l)
        except Exception as e:
            mess = orig + ' - ' + str(e)
            logging.error(mess)
            raise Exception(mess)

# --------------------------------------------------

    def __update_db_data(self):

        orig ='update_db_data'
        res = True
        now = datetime.now()
        day = now.strftime('%Y-%m-%d')

        try:
            crs = self.__dbc.cursor()
        except Exception as e:
            mess = orig + ' failed to connect to database: ' + str(e)
            logging.error(mess)
            raise Exception(mess)

        sql ='''REPLACE INTO duo_data (id, date, points, level, level_progress,
            level_percent, level_points, level_left, next_level,
            num_skills_learned, points_rank)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

        for key in self.__dl_data:
            try:
                dld = self.__dl_data[key]
                crs.execute(sql,
                    (key, day, dld["points"], dld["level"],
                    dld["level_progress"], dld["level_percent"],
                    dld["level_points"], dld["level_left"],
                    dld["next_level"], dld["num_skills_learned"],
                    dld["points_rank"]))
                self.__dbc.commit()
            except Exception as e:
                mess = orig + ' - ' + ' lang ' + key + ' - ' + str(e)
                logging.error(mess)
                raise Exception(mess)

        crs.close()

# --------------------------------------------------

    def __get_db_status(self):
        orig ='get_db_statuses'

        try:
            self.__dbc.row_factory = sqlite3.Row
            crs = self.__dbc.cursor()
        except Exception as e:
            mess = orig + ' failed to connect to database: ' + str(e)
            logging.error(mess)
            raise Exception(mess)

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
            mess = orig + ' - ' + str(e)
            logging.error(mess)
            raise Exception(mess)

        crs.close()

# --------------------------------------------------

    def __compare_lang_status(self):
        orig ='compare_lang_status'
        currday = date.today()
        currdaystr = date.today().isoformat()

        try:
            langs =  self.__dl_data
            for key in langs:
                lang = langs[key]
                if (not self.__db_status or key not in self.__db_status):
                    sql = '''REPLACE INTO duo_status (id, points, level,
                        level_progress, level_percent, level_points, level_left,
                        next_level, num_skills_learned, points_rank, streak_start,
                        streak_end)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
                    lst = (key, lang["points"], lang["level"], lang["level_progress"],
                        lang["level_percent"], lang["level_points"], lang["level_left"],
                        lang["next_level"], lang["num_skills_learned"],
                        lang["points_rank"], currday, currday)
                    self.__update_lang_status(sql, lst)
                elif (lang["points"] != self.__db_status[key]["points"]):
                    strklst = self.__db_status[key]["streak_end"].split('-')
                    streakend = date(int(strklst[0]), int(strklst[1]), int(strklst[2]))
                    delta = (currday - streakend).days

                    if (delta > 1):
                        # streak was discontinued, first day of new streak
                        sql = '''REPLACE INTO duo_status (id, points, level,
                            level_progress, level_percent, level_points,
                            level_left, next_level, num_skills_learned,
                            points_rank, streak_start, streak_end)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
                        lst = (key, lang["points"], lang["level"],
                            lang["level_progress"], lang["level_percent"],
                            lang["level_points"], lang["level_left"],
                            lang["next_level"], lang["num_skills_learned"],
                            lang["points_rank"], currdaystr, currdaystr)
                        self.__update_lang_status(sql, lst)
                    else:
                        # streak continues, streak_start doesn't change
                        sql = '''REPLACE INTO duo_status (id, points, level,
                            level_progress, level_percent, level_points,
                            level_left, next_level, num_skills_learned,
                            points_rank, streak_start, streak_end)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
                        lst = (key, lang["points"], lang["level"],
                            lang["level_progress"], lang["level_percent"],
                            lang["level_points"], lang["level_left"],
                            lang["next_level"], lang["num_skills_learned"],
                            lang["points_rank"],
                            self.__db_status[key]["streak_start"],
                            currdaystr)
                        self.__update_lang_status(sql, lst)
            else:
                    # doe voorlopig niks
                    # moet iets misgelopen zijn
                    pi = 3.14
        except Exception as e:
            mess = orig + ' - ' + str(e)
            logging.error(mess)
            raise Exception(mess)

# --------------------------------------------------

    def __update_lang_status(self, sql, lst):
        orig ='update_lang_status'

        try:
            crs = self.__dbc.cursor()
        except Exception as e:
            mess = orig + " failed to connect to database: " + str(e)
            logging.error(mess)
            raise Exception(mess)

        try:
            crs.execute(sql, lst)
            self.__dbc.commit()
        except Exception as e:
            mess = orig + ' - ' + str(e)
            logging.error(mess)
            raise Exception(mess)

        crs.close()

# --------------------------------------------------

    def export_html(self, template, destination):
        orig ='export_html'
        table = ''

        try:
            crs = self.__dbc.cursor()
        except Exception as e:
            mess = orig + ' failed to connect to database: ' + str(e)
            logging.error(mess)
            raise Exception(mess)

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
            logging.error(orig + ' - ' + str(e))
            table = '<tr><td colspan="7">' + str(e) + '</td></tr>'
            res = False

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
            logging.error(orig + ' - ' + str(e))

# --------------------------------------------------

    def __del__(self):
        self.__dbc.close()

# --------------------------------------------------
