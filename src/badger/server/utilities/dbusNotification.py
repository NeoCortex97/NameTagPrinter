import dbus


session_bus = dbus.SessionBus()
interface = dbus.Interface(session_bus.get_object('org.freedesktop.Notifications', '/org/freedesktop/Notifications'),
                           'org.freedesktop.Notifications')

icon = 'file:///home/stefan/PycharmProjects/Thermalprinter/NameTagger2/assets/images/logos/flipdot.png'
interface.Notify('Badger', 0, icon, 'Badger - PrintJob complete', 'The print job 1 was complete', [], {}, 3000)
