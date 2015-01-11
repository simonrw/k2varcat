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
        filename = 'k2var-{epicid}.fits'.format(epicid=kwargs['epicid'])
        return '/'.join([self.root, 'download', filename])

    def index_url(self, **kwargs):
        return '/'.join([self.root, ''])


def build_stsci_url(epicid):
    return "https://archive.stsci.edu/k2/preview.php?dsn=KTWO{epicid}-C00&type=LC".format(
        epicid=epicid)
