from __future__ import print_function

import logging

import tornado.web
from tornado import gen
from tornado.options import define, options, parse_command_line
from keras.models import load_model
import dill as dpickle
from seq2seq_utils import Seq2Seq_Inference

define("port", default=8888, help="run on the given port", type=int)
define("instances_key", default='instances', help="requested instances json object key")


class PredictHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def post(self):
        request_key = self.settings['request_key']
        request_data = tornado.escape.json_decode(self.request.body)
        model = self.settings['model']
        predictions = [model.generate_issue_title(body)[1] for body in request_data[request_key]]
        self.write(dict(predictions=predictions))


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('Hello World')


def main():
    parse_command_line()
    with open('body_pp.dpkl', 'rb') as f:
        body_pp = dpickle.load(f)
    with open('title_pp.dpkl', 'rb') as f:
        title_pp = dpickle.load(f)
        model = Seq2Seq_Inference(encoder_preprocessor=body_pp,
                                  decoder_preprocessor=title_pp,
                                  seq2seq_model=load_model('seq2seq_model_tutorial.h5'))
    app = tornado.web.Application(
        [
            (r"/predict", PredictHandler),
            (r"/", IndexHandler),
        ],
        xsrf_cookies=False,
        request_key=options.instances_key,
        model=model)
    app.listen(options.port)
    logging.info('running at http://localhost:%s' % options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
