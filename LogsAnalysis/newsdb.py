#!/usr/bin/env python3

import psycopg2

# get 3 most popular articles of all time
db = psycopg2.connect(database="news")
c = db.cursor()
sql_art = '''
            SELECT articles.title, log2.cnt
            FROM (
                SELECT log.path AS path, count(*) AS cnt
                FROM log
                GROUP BY log.path
            ) AS log2, articles
            WHERE log2.path = CONCAT('/article/', articles.slug)
            ORDER BY cnt DESC
            LIMIT 3
          '''
c.execute(sql_art)
most_pop_art = c.fetchall()

# authors listed by popularity
sql_auth = '''
             SELECT authors.name AS author, SUM(sub.cnt) AS total_views
             FROM (
               SELECT articles.author, articles.title, log2.cnt as cnt
               FROM articles, (
                   SELECT log.path AS path, COUNT(*) AS cnt
                   FROM log
                   GROUP BY log.path
                   ) AS log2
               WHERE log2.path = CONCAT('/article/', articles.slug)
               GROUP BY articles.author, articles.title, log2.cnt
             ) AS sub, authors
             WHERE sub.author = authors.id
             GROUP BY authors.name
             ORDER BY total_views DESC
           '''
c.execute(sql_auth)
author_by_pop = c.fetchall()

# which dates had more than 1% failed requests
sql_log = '''
            SELECT sub.date, sub.fail::float/sub.total*100
            FROM (
              SELECT DATE(time) AS date,
              SUM(CASE WHEN status='404 NOT FOUND' THEN 1 ELSE 0 END) AS fail,
              COUNT(*) AS total
              FROM log GROUP BY date
            ) AS sub
            WHERE sub.fail::float/sub.total*100 > 1
          '''

c.execute(sql_log)
failed_req = c.fetchall()
c.close()

# print results
print('Three Most popular articles:')
i = 0
for t, c in most_pop_art:
    i += 1
    print('{i}. {title}: {count} views'.format(title=t, count=c, i=i))

print('\nAuthors sorted by popularity:')
i = 0
for a, c in author_by_pop:
    i += 1
    print('{i}. {author}: {count} views'.format(author=a, count=c, i=i))

print('\nDays with more than 1% failed requests:')
i = 0
for d, p in failed_req:
    i += 1
    print('{date}: {perc}% requests failed'.format(date=d, perc=p, i=i))
