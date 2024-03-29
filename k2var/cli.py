#!/usr/bin/env python
# -*- coding: utf-8 -*-


import argparse
from os import path
import os
import logging
import shutil

from .data_store import Database
from .paths import BASE_DIR, PACKAGE_DIR, detail_output_path
from .rendering import LightcurvePlotter, TableRenderer
from .tasks import render_page
from .templates import RendersTemplates
from .urls import build_stsci_url

logging.basicConfig(
    level=logging.DEBUG, format='%(asctime)s|%(name)s|%(levelname)s|%(message)s')
logger = logging.getLogger(__name__)


class K2Var(object):

    def __init__(self, args):
        self.args = args
        self.renderer = RendersTemplates(self.args.root)
        self.db = Database(self.args.metadata_csv)
        self.output_paths = self.build_output_paths()

    def build_output_paths(self):
        root = path.realpath(self.args.output_dir)
        return [path.join(root, 'objects'),
                path.join(root, 'static')]

    def ensure_output_dir(self):
        for p in self.output_paths:
            self.ensure_path(p)

    @staticmethod
    def ensure_path(p):
        if not path.isdir(p):
            os.makedirs(p, exist_ok=True)

    def render(self):
        logger.debug('Arguments: %s', self.args)
        self.ensure_output_dir()
        self.copy_csv_file()
        self.render_static()
        self.render_index_page()
        self.render_detail_pages()

    def copy_csv_file(self):
        shutil.copyfile(self.args.metadata_csv,
                        path.join(self.args.output_dir, 'K2VarCat.csv'))

    def render_static(self):
        logger.info('Rendering static files')
        source_dir = path.join(PACKAGE_DIR, 'static')
        for subdir in os.listdir(source_dir):
            full_path = path.join(source_dir, subdir)
            dest_dir = path.join(self.args.output_dir, 'static',
                                 path.basename(subdir))
            logger.debug('Copying {} => {}'.format(full_path, dest_dir))
            try:
                shutil.copytree(full_path, dest_dir)
            except OSError:
                shutil.rmtree(dest_dir)
                shutil.copytree(full_path, dest_dir)

    def render_index_page(self):
        logger.info('Rendering index page')
        outfile_name = path.join(self.args.output_dir, 'index.html')
        return self.renderer.render_to('index', outfile_name, app_root=self.args.root)

    def render_detail_pages(self):
        logger.info('Rendering detail pages')
        results = []

        for epicid, campaign in self.db.valid_epic_ids():
            logger.info('Submitting task for {}'.format(epicid))
            outfile_name = detail_output_path(epicid, self.args.output_dir)
            if not path.lexists(outfile_name):
                results.append(render_page.delay(
                    metadata=self.db.get(epicid),
                    output_dir=self.args.output_dir,
                    root_url=self.args.root,
                    epicid=epicid,
                    campaign=campaign,
                ))
            else:
                logger.debug('Not rendering {}, file exists'.format(
                    outfile_name))

        logger.info('Waiting for job completion')
        for result in results:
            epicid, _ = result.wait()
            logger.debug('Job {} complete'.format(epicid))


def main():
    default_output = path.join(BASE_DIR, 'build')
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-r', '--root', default='', help='Application root. For phsnag: /phsnag/')
    parser.add_argument(
        '-o', '--output-dir', default=default_output, required=False)
    parser.add_argument('-d', '--metadata-csv', required=True)
    K2Var(parser.parse_args()).render()
