SELECT
  MAX(CONCAT(f.repo_name, ' ', f.path)) AS repo_path,
  c.content
FROM
  `bigquery-public-data.github_repos.files` AS f
JOIN
  `bigquery-public-data.github_repos.contents` AS c
ON
  f.id = c.id
JOIN (
    --this part of the query makes sure repo is watched at least twice since 2017
  SELECT
    repo
  FROM (
    SELECT
      repo.name AS repo
    FROM
      `githubarchive.year.2017`
    WHERE
      type="WatchEvent"
    UNION ALL
    SELECT
      repo.name AS repo
    FROM
      `githubarchive.month.2018*`
    WHERE
      type="WatchEvent" )
  GROUP BY
    1
  HAVING
    COUNT(*) >= 2 ) AS r
ON
  f.repo_name = r.repo
WHERE
  f.path LIKE '%.py' AND --with python extension
  c.size < 15000 AND --get rid of ridiculously long files
  REGEXP_CONTAINS(c.content, r'def ') --contains function definition
GROUP BY
  c.content
-- for development purposes only
LIMIT
  1000000
