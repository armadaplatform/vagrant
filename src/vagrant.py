import web


class Health(object):
    def GET(self):
        return 'ok'


class ArmadaBox(object):
    def GET(self):
        raise web.seeother('/static/armada.box')


class ArmadaVagrantfile(object):
    def GET(self):
        raise web.seeother('/static/ArmadaVagrantfile.rb')


def main():
    urls = (
        '/health', Health.__name__,
        '/armada.box', ArmadaBox.__name__,
        '/ArmadaVagrantfile.rb', ArmadaVagrantfile.__name__,
    )
    app = web.application(urls, globals())
    app.run()


if __name__ == '__main__':
    main()
