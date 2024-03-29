from . import paths


class UrlFor(object):

    def __init__(self, root):
        self.root = root

    def __call__(self, endpoint, **kwargs):
        method_name = '{}_url'.format(endpoint)
        try:
            method = getattr(self, method_name)
        except AttributeError:
            raise AttributeError('No dispatch method `{}`, you may need to define it'.format(
                method_name))

        return method(**kwargs)

    def static_url(self, **kwargs):
        return '/'.join([self.root, 'static', kwargs['filename']])

    def download_url(self, **kwargs):
        filename = paths.lightcurve_filename(
            kwargs['epicid'], kwargs['campaign'])
        return '/'.join([self.root, 'download', filename])

    def index_url(self, **kwargs):
        return '/'.join([self.root, ''])


def build_stsci_url(epicid, campaign):
    root = "https://archive.stsci.edu/k2/preview.php"
    return "{root}?dsn=KTWO{epicid}-C{campaign:02d}&type=LC".format(
        epicid=epicid, root=root, campaign=campaign)
