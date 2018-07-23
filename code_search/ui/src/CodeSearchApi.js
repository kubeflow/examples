import request from 'superagent';

const SEARCH_URL='//localhost:8008/query'

function code_search_api(str) {
  return request.get(SEARCH_URL).query({'q': str});
}

export default code_search_api;
