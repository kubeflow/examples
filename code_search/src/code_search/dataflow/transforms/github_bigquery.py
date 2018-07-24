import code_search.dataflow.transforms.bigquery as bigquery


class ReadGithubDataset(bigquery.BigQueryRead):
  """Read original Github files from BigQuery.

  This utility Transform reads Python files
  from a BigQuery public dump which are smaller
  than 15k lines of code, contain at least one
  function definition and its repository has been
  watched at least twice since 2017.

  NOTE: Make sure to modify the `self.limit` property
  as desired.
  """

  @property
  def limit(self):
    return 100

  @property
  def query_string(self):
    query = """
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
    """

    if self.limit:
      query += '\nLIMIT {}'.format(self.limit)
    return query


class WriteFailedTokenizedData(bigquery.BigQueryWrite):
  @property
  def column_list(self):
    return [
      ('nwo', 'STRING'),
      ('path', 'STRING'),
      ('content', 'STRING')
    ]


class WriteTokenizedData(bigquery.BigQueryWrite):
  @property
  def column_list(self):
    return [
      ('nwo', 'STRING'),
      ('path', 'STRING'),
      ('function_name', 'STRING'),
      ('lineno', 'STRING'),
      ('original_function', 'STRING'),
      ('function_tokens', 'STRING'),
      ('docstring_tokens', 'STRING'),
    ]


class ReadProcessedGithubData(bigquery.BigQueryRead):
  @property
  def limit(self):
    return 100

  @property
  def query_string(self):
    query = """
      SELECT 
        nwo, path, function_name, lineno, original_function, function_tokens
      FROM
        code_search.function_docstrings
    """

    if self.limit:
      query += '\nLIMIT {}'.format(self.limit)
    return query


class WriteGithubIndexData(bigquery.BigQueryWrite):
  @property
  def column_list(self):
    return [
      ('nwo', 'STRING'),
      ('path', 'STRING'),
      ('function_name', 'STRING'),
      ('lineno', 'INTEGER'),
      ('original_function', 'STRING'),
      ('function_embedding', 'STRING')
    ]
