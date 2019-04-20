#! /usr/bin/env python

import psycopg2


# Collect data about the three most popular articles all time
def pop_art():
    art = """
        SELECT articles.title, COUNT(log.id) AS num
          FROM log
          JOIN articles
            ON log.path = CONCAT('/article/', articles.slug)
      GROUP BY articles.title
      ORDER BY num DESC
         LIMIT 3;
    """

    db = psycopg2.connect("dbname=news")
    c = db.cursor()
    c.execute(art)
    r = c.fetchall()
    db.close()

    print("\nThe three most popular articles of all time are:")
    for a in r:
        print('\t* "{}" - {} views'.format(a[0], a[1]))

    # OPTIONAL - generate text file with log output
    # with open('logs_analysis.txt', 'w') as f:
    #     f.write("The three most popular articles of all time are:\n")
    #     for a in r:
    #         f.write('\t* "{}" - {} views\n'.format(a[0], a[1]))


# Collect data about the most popular article authors
def pop_auth():
    auth = """
        SELECT authors.name, COUNT(*) AS num
          FROM log
          JOIN articles
            ON log.path = CONCAT('/article/', articles.slug)
          JOIN authors
            ON authors.id = articles.author
      GROUP BY authors.name
      ORDER BY num DESC;
    """

    db = psycopg2.connect("dbname=news")
    c = db.cursor()
    c.execute(auth)
    r = c.fetchall()
    db.close()

    print("\nThe most popular article authors of all times are:")
    for a in r:
        print('\t* {} - {} views'.format(a[0], a[1]))

    # OPTIONAL - generate text file with log output
    # with open('logs_analysis.txt', 'a') as f:
    #     f.write("\nThe most popular article authors of all times are:\n")
    #     for a in r:
    #         f.write('\t* {} - {} views\n'.format(a[0], a[1]))


# Collect data about errors
def error_days():
    err = """
        WITH t1 AS (
            SELECT DATE_TRUNC('day', log.time) AS e_date,
                   log.status AS e_status,
                   COUNT(log.status) AS e_count
              FROM log
             GROUP BY 1, 2
            HAVING log.status != '200 OK'),
        t2 AS (
            SELECT DATE_TRUNC('day', log.time) AS ok_date,
                   log.status AS ok_status,
                   COUNT(log.status) AS ok_count
              FROM log
             GROUP BY 1, 2
            HAVING log.status = '200 OK')

        SELECT DATE_TRUNC('day', log.time) AS main_date,
               t1.e_count * 100 / t2.ok_count AS e_ratio
          FROM log
          JOIN t1
            ON t1.e_date = DATE_TRUNC('day', log.time)
          JOIN t2
            ON t2.ok_date = DATE_TRUNC('day', log.time)
         GROUP BY 1, t1.e_count, t2.ok_count
        HAVING t1.e_count * 100 / t2.ok_count > 1;
    """

    db = psycopg2.connect("dbname=news")
    c = db.cursor()
    c.execute(err)
    r = c.fetchall()
    db.close()

    months = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']

    print('\nThese days had more than 1% request errors:')
    for a in r:
        the_date = a[0]
        month = months[the_date.month - 1]
        print('\t* {} {}, {} - {}% errors\n'.format(
            month, the_date.day, the_date.year, a[1]))

    # OPTIONAL - generate text file with log output
    # with open('logs_analysis.txt', 'a') as f:
    #     f.write("\nThese days had more than 1% request errors:'")
    #     for a in r:
    #         the_date = a[0]
    #         month = months[the_date.month - 1]
    #         f.write('\n\t* {} {}, {} - {}% errors'.format(\
    #             month, the_date.day, the_date.year, a[1]))


if __name__ == '__main__':
    pop_art()
    pop_auth()
    error_days()
