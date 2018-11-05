
class ConfigObserver(object):
    def __init__(self):
        pass

    def alarm_added(self, alarm):
        raise NotImplemented("alarm_added is not implemented")

    def alarm_deleted(self, id):
        raise NotImplemented("alarm_deleted is not implemented")

    def alarm_changed(self, alarm):
        raise NotImplemented("alarm_changed is not implemented")


