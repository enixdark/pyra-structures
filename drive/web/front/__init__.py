from drive.utils.settings import pyramid_config_from_settings

def main(global_config, **app_settings):
    config = pyramid_config_from_settings(global_config, app_settings)

    config.include('drive.services')

    config.include('.routes')
    config.include('.security')
    config.include('.session')
    config.include('.templating')

    config.scan('.views')

    return config.make_wsgi_app()
